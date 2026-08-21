import os
import time
import psutil
import cv2
import re
import pandas as pd
import pytesseract
from rapidocr_onnxruntime import RapidOCR
import easyocr
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from paddleocr import PaddleOCR
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def extract_patterns(text):
    """Extract dosage and EXP date patterns from text."""
    # Dosage: digits followed by mg, g, ml, etc.
    dosage_pattern = r'(\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|IU))'
    # EXP: EXP followed by date patterns like MM/YYYY, DD/MM/YYYY, etc.
    exp_pattern = r'(?i)(?:EXP|expiry)[\s\.:]*(\d{2}[/\.-]\d{2,4})'
    
    dosages = re.findall(dosage_pattern, text, re.IGNORECASE)
    exps = re.findall(exp_pattern, text)
    
    return {
        "dosage": ", ".join(dosages) if dosages else "None",
        "exp": ", ".join(exps) if exps else "None"
    }

def preprocess_image_for_tesseract(image_path):
    """CLAHE + Otsu thresholding for Tesseract"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img)
    
    # Otsu's thresholding
    _, thresh = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def run_tesseract(image_path):
    img = preprocess_image_for_tesseract(image_path)
    if img is None:
        return ""
    text = pytesseract.image_to_string(img)
    return text.strip()

def run_rapidocr(image_path, engine):
    result, _ = engine(image_path)
    if result:
        text = "\n".join([line[1] for line in result])
        return text
    return ""

def run_easyocr(image_path, reader):
    result = reader.readtext(image_path, detail=0)
    return "\n".join(result)

def run_doctr(image_path, predictor):
    doc = DocumentFile.from_images(image_path)
    result = predictor(doc)
    text = ""
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    text += word.value + " "
                text += "\n"
    return text.strip()

def run_paddleocr(image_path, ocr):
    result = ocr.ocr(image_path)
    if result and result[0]:
        text = "\n".join([line[1][0] for line in result[0]])
        return text
    return ""

def benchmark():
    test_dir = os.path.join(os.path.dirname(__file__), "test_images")
    output_csv = os.path.join(os.path.dirname(__file__), "ocr_benchmark_results.csv")
    
    if not os.path.exists(test_dir):
        print(f"Error: {test_dir} not found. Please run download_dataset.py first.")
        return

    images = [f for f in os.listdir(test_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        print(f"No images found in {test_dir}.")
        return

    # Initialize engines
    print("Initializing OCR engines...")
    rapid_engine = RapidOCR()
    easy_reader = easyocr.Reader(['en'], gpu=False) # CPU mode as requested
    doctr_predictor = ocr_predictor(pretrained=True)
    paddle_ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
    
    process = psutil.Process(os.getpid())
    results = []

    print(f"Starting benchmark on {len(images)} images...")
    
    for img_name in images:
        img_path = os.path.join(test_dir, img_name)
        print(f"Processing: {img_name}")
        
        engines = {
            "Tesseract": lambda: run_tesseract(img_path),
            "RapidOCR": lambda: run_rapidocr(img_path, rapid_engine),
            "EasyOCR": lambda: run_easyocr(img_path, easy_reader),
            "DocTR": lambda: run_doctr(img_path, doctr_predictor),
            "PaddleOCR": lambda: run_paddleocr(img_path, paddle_ocr)
        }
        
        for engine_name, func in engines.items():
            # Measure RAM before
            mem_before = process.memory_info().rss / (1024 * 1024)
            
            # Measure Latency
            start_time = time.time()
            extracted_text = func()
            end_time = time.time()
            
            # Measure RAM after
            mem_after = process.memory_info().rss / (1024 * 1024)
            ram_delta = max(0, mem_after - mem_before)
            
            latency_ms = (end_time - start_time) * 1000
            
            patterns = extract_patterns(extracted_text)
            
            results.append({
                "Image": img_name,
                "Engine": engine_name,
                "Extracted_Text": extracted_text.replace('\n', ' | '), 
                "Detected_Dosage": patterns["dosage"],
                "Detected_EXP": patterns["exp"],
                "Latency_ms": round(latency_ms, 2),
                "RAM_Delta_MB": round(ram_delta, 2)
            })
            
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"✅ Benchmark complete! Results saved to {output_csv}")

if __name__ == "__main__":
    benchmark()
