import streamlit as st
import pandas as pd
import altair as alt
import time
import os
import psutil
from PIL import Image

# Import OCR functions from our benchmark module
from benchmark_ocr import (
    run_tesseract, run_rapidocr, run_easyocr, run_doctr, run_paddleocr, run_surya, run_paddleocr_vl, extract_patterns,
    RapidOCR, easyocr, ocr_predictor, PaddleOCR,
    load_det_model, load_det_processor, load_rec_model, load_rec_processor,
    load_paddle_vl_model, load_ppocrv5
)

st.set_page_config(page_title="BlisterBot OCR Evaluation", layout="wide")

# Initialize models (cached so they don't reload every time)
@st.cache_resource
def load_models():
    rapid_engine = RapidOCR()
    ppocrv5_engine = load_ppocrv5()
    easy_reader = easyocr.Reader(['en'], gpu=False)
    doctr_predictor = ocr_predictor(pretrained=True)
    doctr_heavy = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    paddle_ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
    
    surya_det_model = load_det_model()
    surya_det_processor = load_det_processor()
    surya_rec_model = load_rec_model()
    surya_rec_processor = load_rec_processor()
    
    paddle_vl_processor, paddle_vl_model = load_paddle_vl_model()
    
    return rapid_engine, ppocrv5_engine, easy_reader, doctr_predictor, doctr_heavy, paddle_ocr, surya_det_model, surya_det_processor, surya_rec_model, surya_rec_processor, paddle_vl_processor, paddle_vl_model

rapid_engine, ppocrv5_engine, easy_reader, doctr_predictor, doctr_heavy, paddle_ocr, surya_det_model, surya_det_processor, surya_rec_model, surya_rec_processor, paddle_vl_processor, paddle_vl_model = load_models()

def process_image(image_path, selected_engines=None):
    results = []
    process = psutil.Process(os.getpid())
    
    engines = {
        "Tesseract": lambda: run_tesseract(image_path),
        "RapidOCR": lambda: run_rapidocr(image_path, rapid_engine),
        "PP-OCRv5": lambda: run_rapidocr(image_path, ppocrv5_engine),
        "EasyOCR": lambda: run_easyocr(image_path, easy_reader),
        "DocTR": lambda: run_doctr(image_path, doctr_predictor),
        "DocTR-Heavy": lambda: run_doctr(image_path, doctr_heavy),
        "SuryaOCR": lambda: run_surya(image_path, surya_det_model, surya_det_processor, surya_rec_model, surya_rec_processor),
        "PaddleOCR": lambda: run_paddleocr(image_path, paddle_ocr),
        "PaddleOCR-VL": lambda: run_paddleocr_vl(image_path, paddle_vl_processor, paddle_vl_model)
    }
    
    for name, func in engines.items():
        if selected_engines and name not in selected_engines:
            continue
            
        mem_before = process.memory_info().rss / (1024 * 1024)
        start = time.time()
        
        text = func()
        
        latency = (time.time() - start) * 1000
        ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
        
        results.append({
            "Engine": name, 
            "Text": text, 
            "Latency (ms)": latency, 
            "RAM (MB)": ram
        })
        
    return results


st.title("💊 BlisterBot: OCR Engine Evaluation Dashboard")

tab1, tab2 = st.tabs(["Live Scanner", "Benchmark Explorer"])

with tab1:
    st.header("Live Scanner")
    st.write("Hold a blister pack up to your webcam or upload an image to see how the OCR engines perform.")
    
    # Input options
    img_file_buffer = st.camera_input("Take a picture")
    uploaded_file = st.file_uploader("Or upload an image", type=["png", "jpg", "jpeg"])
    
    image_to_process = img_file_buffer if img_file_buffer else uploaded_file
    
    if image_to_process is not None:
        # Save temp image for processing
        temp_path = "temp_capture.jpg"
        with open(temp_path, "wb") as f:
            f.write(image_to_process.getbuffer())
            
        st.image(image_to_process, caption="Captured Image", use_container_width=False, width=400)
        
        available_engines = [
            "Tesseract", "RapidOCR", "PP-OCRv5", "EasyOCR", "DocTR", 
            "DocTR-Heavy", "SuryaOCR", "PaddleOCR", "PaddleOCR-VL"
        ]
        
        selected_engines = st.multiselect(
            "Select OCR Engines to run:", 
            available_engines, 
            default=["PP-OCRv5"]
        )
        
        if st.button("Run OCR Comparison"):
            if not selected_engines:
                st.warning("Please select at least one engine to test.")
            else:
                with st.spinner("Processing with selected engines..."):
                    results = process_image(temp_path, selected_engines)
                
                st.subheader("Comparison")
                # Create a flexible grid based on number of selected engines
                cols = st.columns(min(3, len(results)))
                
                for idx, res in enumerate(results):
                    with cols[idx % min(3, len(results))]:
                        st.markdown(f"### {res['Engine']}")
                        patterns = extract_patterns(res['Text'])
                        
                        # Metrics Card
                        st.metric(label="Latency", value=f"{res['Latency (ms)']:.1f} ms")
                        st.metric(label="RAM Usage", value=f"{res['RAM (MB)']:.1f} MB")
                        
                        st.markdown("**Medical Info Extracted:**")
                        st.write(f"- **Medicine**: `{patterns['medicine']}`")
                        st.write(f"- **Batch**: `{patterns['batch']}`")
                        st.write(f"- **Dosage**: `{patterns['dosage']}`")
                        st.write(f"- **EXP**: `{patterns['exp']}`")
                        
                        st.markdown("**Raw Text:**")
                        st.text_area("Output", res['Text'], height=150, key=res['Engine'])

with tab2:
    st.header("Benchmark Explorer")
    csv_path = "ocr_benchmark_results.csv"
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Performance Trade-offs")
        # Bar charts comparing latency vs RAM
        avg_df = df.groupby("Engine").agg({
            "Latency_ms": "mean",
            "RAM_Delta_MB": "mean"
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_lat = alt.Chart(avg_df).mark_bar().encode(
                x='Engine',
                y='Latency_ms',
                color='Engine'
            ).properties(title='Average Inference Latency (ms) - Lower is better')
            st.altair_chart(chart_lat, use_container_width=True)
            
        with col2:
            chart_ram = alt.Chart(avg_df).mark_bar().encode(
                x='Engine',
                y='RAM_Delta_MB',
                color='Engine'
            ).properties(title='Average RAM Usage (MB) - Lower is better')
            st.altair_chart(chart_ram, use_container_width=True)
            
    else:
        st.info("No benchmark data found. Run `benchmark_ocr.py` first to generate the dataset.")
