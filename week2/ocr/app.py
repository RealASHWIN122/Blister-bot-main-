import streamlit as st
import pandas as pd
import altair as alt
import time
import os
from PIL import Image
import numpy as np

# Import OCR functions from our benchmark module
from benchmark_ocr import (
    run_tesseract, run_rapidocr, run_easyocr, run_doctr, run_paddleocr, extract_patterns,
    RapidOCR, easyocr, psutil, ocr_predictor, PaddleOCR
)

st.set_page_config(page_title="BlisterBot OCR Evaluation", layout="wide")

# Initialize models (cached so they don't reload every time)
@st.cache_resource
def load_models():
    rapid_engine = RapidOCR()
    easy_reader = easyocr.Reader(['en'], gpu=False)
    doctr_predictor = ocr_predictor(pretrained=True)
    paddle_ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
    return rapid_engine, easy_reader, doctr_predictor, paddle_ocr

rapid_engine, easy_reader, doctr_predictor, paddle_ocr = load_models()

def process_image(image_path):
    results = []
    process = psutil.Process(os.getpid())
    
    # 1. Tesseract
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.time()
    tess_text = run_tesseract(image_path)
    tess_latency = (time.time() - start) * 1000
    tess_ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
    results.append({"Engine": "Tesseract", "Text": tess_text, "Latency (ms)": tess_latency, "RAM (MB)": tess_ram})
    
    # 2. RapidOCR
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.time()
    rapid_text = run_rapidocr(image_path, rapid_engine)
    rapid_latency = (time.time() - start) * 1000
    rapid_ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
    results.append({"Engine": "RapidOCR", "Text": rapid_text, "Latency (ms)": rapid_latency, "RAM (MB)": rapid_ram})
    
    # 3. EasyOCR
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.time()
    easy_text = run_easyocr(image_path, easy_reader)
    easy_latency = (time.time() - start) * 1000
    easy_ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
    results.append({"Engine": "EasyOCR", "Text": easy_text, "Latency (ms)": easy_latency, "RAM (MB)": easy_ram})
    
    # 4. DocTR
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.time()
    doctr_text = run_doctr(image_path, doctr_predictor)
    doctr_latency = (time.time() - start) * 1000
    doctr_ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
    results.append({"Engine": "DocTR", "Text": doctr_text, "Latency (ms)": doctr_latency, "RAM (MB)": doctr_ram})
    
    # 5. PaddleOCR
    mem_before = process.memory_info().rss / (1024 * 1024)
    start = time.time()
    paddle_text = run_paddleocr(image_path, paddle_ocr)
    paddle_latency = (time.time() - start) * 1000
    paddle_ram = max(0, (process.memory_info().rss / (1024 * 1024)) - mem_before)
    results.append({"Engine": "PaddleOCR", "Text": paddle_text, "Latency (ms)": paddle_latency, "RAM (MB)": paddle_ram})
    
    return results


st.title("💊 BlisterBot: OCR Engine Evaluation Dashboard")

tab1, tab2 = st.tabs(["Live Scanner", "Benchmark Explorer"])

with tab1:
    st.header("Live Scanner")
    st.write("Hold a blister pack up to your webcam or upload an image to see how all 5 OCR engines perform side-by-side.")
    
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
        
        if st.button("Run OCR Comparison"):
            with st.spinner("Processing with all 5 engines..."):
                results = process_image(temp_path)
            
            st.subheader("Comparison")
            # 5 engines might be too cramped in one row, split into 3 and 2
            cols1 = st.columns(3)
            cols2 = st.columns(3)
            all_cols = cols1 + cols2
            
            for idx, res in enumerate(results):
                with all_cols[idx]:
                    st.markdown(f"### {res['Engine']}")
                    patterns = extract_patterns(res['Text'])
                    
                    # Metrics Card
                    st.metric(label="Latency", value=f"{res['Latency (ms)']:.1f} ms")
                    st.metric(label="RAM Usage", value=f"{res['RAM (MB)']:.1f} MB")
                    
                    st.markdown("**Dosage / EXP Extracted:**")
                    st.write(f"- Dosage: `{patterns['dosage']}`")
                    st.write(f"- EXP: `{patterns['exp']}`")
                    
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
