import os
import time
import psutil
import cv2
import re
import pandas as pd
import warnings
from PIL import Image

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    import pytesseract
    HAS_TESSERACT = True
    if os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    elif os.path.exists(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"):
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
except ImportError:
    HAS_TESSERACT = False

try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_RAPIDOCR = True
except ImportError:
    HAS_RAPIDOCR = False
    class RapidOCR:
        def __init__(self, *args, **kwargs): pass

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    class easyocr_mock:
        class Reader:
            def __init__(self, *args, **kwargs): pass
    easyocr = easyocr_mock()

try:
    from doctr.models import ocr_predictor
    from doctr.io import DocumentFile
    HAS_DOCTR = True
except ImportError:
    HAS_DOCTR = False
    def ocr_predictor(*args, **kwargs): return None
    class DocumentFile: pass

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False
    class PaddleOCR:
        def __init__(self, *args, **kwargs): pass

def load_ppocrv5():
    if not HAS_RAPIDOCR: return None
    try:
        from huggingface_hub import hf_hub_download
        import rapidocr_onnxruntime.utils as utils
        
        # Monkey patch UpdateParameters to properly forward keys_path
        old_update_rec = utils.UpdateParameters.update_rec_params
        def new_update_rec(self, config, rec_dict):
            if 'rec_keys_path' in rec_dict:
                rec_dict['keys_path'] = rec_dict.pop('rec_keys_path')
            return old_update_rec(self, config, rec_dict)
        utils.UpdateParameters.update_rec_params = new_update_rec
        
        det_path = hf_hub_download("monkt/paddleocr-onnx", "detection/v5/det.onnx")
        rec_path = hf_hub_download("monkt/paddleocr-onnx", "languages/english/rec.onnx")
        keys_path = hf_hub_download("monkt/paddleocr-onnx", "languages/english/dict.txt")
        return RapidOCR(det_model_path=det_path, rec_model_path=rec_path, rec_keys_path=keys_path)
    except Exception as e:
        print(f"Error loading PP-OCRv5: {e}")
        return None

try:
    from transformers import AutoProcessor, AutoModelForCausalLM
    import torch
    HAS_PADDLE_VL = True
except ImportError:
    HAS_PADDLE_VL = False
    def AutoProcessor(*args, **kwargs): return None
    def AutoModelForCausalLM(*args, **kwargs): return None

def load_paddle_vl_model():
    if not HAS_PADDLE_VL: return None, None
    try:
        model_path = "PaddlePaddle/PaddleOCR-VL"
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            trust_remote_code=True, 
            torch_dtype=dtype
        ).to(device)
        return processor, model
    except Exception as e:
        print(f"Error loading PaddleOCR-VL: {e}")
        return None, None

def run_paddleocr_vl(image_path, processor, model):
    if not HAS_PADDLE_VL or processor is None or model is None: return "PaddleOCR-VL not installed or failed to load"
    try:
        image = Image.open(image_path).convert("RGB")
        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": "OCR:"}
            ]}
        ]
        prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(images=[image], text=prompt, return_tensors="pt").to(model.device)
        generated_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        if "Assistant:" in generated_text:
            generated_text = generated_text.split("Assistant:")[-1].strip()
        return generated_text
    except Exception as e:
        return f"PaddleOCR-VL error: {str(e)}"

try:
    from surya.ocr import run_ocr
    from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
    from surya.model.recognition.model import load_model as load_rec_model, load_processor as load_rec_processor
    HAS_SURYA = True
except ImportError:
    HAS_SURYA = False
    def load_det_model(): return None
    def load_det_processor(): return None
    def load_rec_model(): return None
    def load_rec_processor(): return None
    def run_ocr(*args, **kwargs): return []

def extract_patterns(text):
    """Extract medicine, dosage, batch, and EXP date patterns from text."""
    dosage_pattern = r'(\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|IU))'
    exp_pattern = r'(?i)(?:EXP|expiry|MFG)[\s\.:]*(\d{2}[/\.-]\d{2,4}|\d{2,4})'
    batch_pattern = r'(?i)(?:BATCH(?: NO)?|LOT|B\.?No)[\s\.:]*([A-Z0-9\-]+)'
    
    # Match capitalized words preceding common medicine forms
    med_pattern = r'(?i)\b([A-Z][A-Za-z0-9\-]+(?:\s+[A-Z][A-Za-z0-9\-]+){0,3})\s*(?:TABLETS?|CAPSULES?|SYRUP|DROPS|OINTMENT|CREAM|GEL|INJECTION|MEDICINE|®|™)\b'
    
    dosages = re.findall(dosage_pattern, text, re.IGNORECASE)
    exps = re.findall(exp_pattern, text)
    batches = re.findall(batch_pattern, text)
    meds = re.findall(med_pattern, text)
    
    clean_meds = list(set([m.strip().upper() for m in meds if len(m.strip()) > 2]))
    
    return {
        "medicine": ", ".join(clean_meds) if clean_meds else "None",
        "dosage": ", ".join(dosages) if dosages else "None",
        "batch": ", ".join(batches) if batches else "None",
        "exp": ", ".join(exps) if exps else "None"
    }

def preprocess_image_for_tesseract(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl1 = clahe.apply(img)
    _, thresh = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def run_tesseract(image_path):
    if not HAS_TESSERACT: return "Tesseract not installed"
    img = preprocess_image_for_tesseract(image_path)
    if img is None:
        return ""
    try:
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"Tesseract error: {str(e)}"

def sort_boxes_and_join(boxes_texts_scores):
    if not boxes_texts_scores: return ""
    lines = []
    for item in boxes_texts_scores:
        box, text = item[0], item[1]
        center_y = sum(p[1] for p in box) / 4.0
        min_x = min(p[0] for p in box)
        lines.append({"center_y": center_y, "min_x": min_x, "text": text})
        
    lines.sort(key=lambda x: x["center_y"])
    
    grouped_lines = []
    current_line = []
    current_y = None
    
    for box in lines:
        if current_y is None:
            current_y = box["center_y"]
            current_line.append(box)
        elif abs(box["center_y"] - current_y) < 15: # threshold for same line
            current_line.append(box)
        else:
            grouped_lines.append(current_line)
            current_line = [box]
            current_y = box["center_y"]
            
    if current_line:
        grouped_lines.append(current_line)
        
    final_text = []
    for group in grouped_lines:
        group.sort(key=lambda x: x["min_x"])
        line_text = " ".join([b["text"] for b in group])
        final_text.append(line_text)
        
    return "\n".join(final_text)

def run_rapidocr(image_path, engine):
    if not HAS_RAPIDOCR or engine is None: return "RapidOCR not installed or loaded"
    result, _ = engine(image_path)
    if result:
        return sort_boxes_and_join(result)
    return ""

def run_easyocr(image_path, reader):
    if not HAS_EASYOCR: return "EasyOCR not installed"
    result = reader.readtext(image_path, detail=1)
    if result:
        return sort_boxes_and_join(result)
    return ""

def run_doctr(image_path, predictor):
    if not HAS_DOCTR: return "DocTR not installed"
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
    if not HAS_PADDLEOCR: return "PaddleOCR not installed"
    result = ocr.ocr(image_path)
    if result and result[0]:
        text = "\n".join([line[1][0] for line in result[0]])
        return text
    return ""

def run_surya(image_path, det_model, det_processor, rec_model, rec_processor):
    if not HAS_SURYA: return "SuryaOCR not installed"
    try:
        image = Image.open(image_path)
        predictions = run_ocr([image], [["en"]], det_model, det_processor, rec_model, rec_processor)
        text_lines = []
        for pred in predictions:
            for line in pred.text_lines:
                text_lines.append(line.text)
        return "\n".join(text_lines)
    except Exception as e:
        return f"SuryaOCR error: {str(e)}"

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
    ppocrv5_engine = load_ppocrv5()
    easy_reader = easyocr.Reader(['en'], gpu=False) # CPU mode as requested
    doctr_predictor = ocr_predictor(pretrained=True)
    doctr_heavy = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    paddle_ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
    
    surya_det_model = load_det_model()
    surya_det_processor = load_det_processor()
    surya_rec_model = load_rec_model()
    surya_rec_processor = load_rec_processor()
    
    paddle_vl_processor, paddle_vl_model = load_paddle_vl_model()
    
    process = psutil.Process(os.getpid())
    results = []

    print(f"Starting benchmark on {len(images)} images...")
    
    for img_name in images:
        img_path = os.path.join(test_dir, img_name)
        print(f"Processing: {img_name}")
        
        engines = {
            "Tesseract": lambda: run_tesseract(img_path),
            "RapidOCR": lambda: run_rapidocr(img_path, rapid_engine),
            "PP-OCRv5": lambda: run_rapidocr(img_path, ppocrv5_engine),
            "EasyOCR": lambda: run_easyocr(img_path, easy_reader),
            "DocTR": lambda: run_doctr(img_path, doctr_predictor),
            "DocTR-Heavy": lambda: run_doctr(img_path, doctr_heavy),
            "SuryaOCR": lambda: run_surya(img_path, surya_det_model, surya_det_processor, surya_rec_model, surya_rec_processor),
            "PaddleOCR": lambda: run_paddleocr(img_path, paddle_ocr),
            "PaddleOCR-VL": lambda: run_paddleocr_vl(img_path, paddle_vl_processor, paddle_vl_model)
        }
        
        for engine_name, func in engines.items():
            mem_before = process.memory_info().rss / (1024 * 1024)
            start_time = time.time()
            extracted_text = func()
            end_time = time.time()
            
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
