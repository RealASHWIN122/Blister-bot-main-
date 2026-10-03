import os
import json
import uuid
import wave
import subprocess
import numpy as np
from flask import Flask, render_template, request, jsonify

# Levenshtein distance for WER and CER
def edit_distance(r, h):
    d = np.zeros((len(r)+1)*(len(h)+1), dtype=np.uint8).reshape((len(r)+1, len(h)+1))
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitute = d[i-1][j-1] + 1
                insert = d[i][j-1] + 1
                delete = d[i-1][j] + 1
                d[i][j] = min(substitute, insert, delete)
    return d[len(r)][len(h)]

def calculate_cer(reference, hypothesis):
    ref_len = len(reference)
    if ref_len == 0: return 0.0
    return edit_distance(list(reference), list(hypothesis)) / ref_len

def calculate_wer(reference, hypothesis):
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    if len(ref_words) == 0: return 0.0
    return edit_distance(ref_words, hyp_words) / len(ref_words)

import sherpa_onnx
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'UNO'))
try:
    from assistant import init_stt
    print("Initializing STT Model (Old/Streaming)...")
    recognizer_streaming = init_stt()
    print("Old STT Model Initialized.")
except Exception as e:
    print(f"Error loading old STT model: {e}")
    recognizer_streaming = None

try:
    print("Initializing Finetuned STT Model (New/Offline)...")
    STT_MODEL_DIR_NEW = os.path.join(os.path.dirname(__file__), '..', 'UNO', 'STT-non-streaming-zipformer-finetuned')
    recognizer_offline = sherpa_onnx.OfflineRecognizer.from_transducer(
        tokens=f"{STT_MODEL_DIR_NEW}/tokens.txt",
        encoder=f"{STT_MODEL_DIR_NEW}/encoder-epoch-5-avg-2.onnx",
        decoder=f"{STT_MODEL_DIR_NEW}/decoder-epoch-5-avg-2.onnx",
        joiner=f"{STT_MODEL_DIR_NEW}/joiner-epoch-5-avg-2.onnx",
        num_threads=1,
        sample_rate=16000,
        feature_dim=80,
    )
    print("New STT Model Initialized.")
except Exception as e:
    print(f"Error loading new STT model: {e}")
    recognizer_offline = None

app = Flask(__name__)
DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_dataset")
TRANSCRIPTS_FILE = os.path.join(DATASET_DIR, "transcripts.txt")
finetune_process = None
os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

with open(os.path.join(os.path.dirname(__file__), "phrases.json"), "r") as f:
    PHRASES = json.load(f)

def run_stt(wav_path, model_type="old"):
    try:
        with wave.open(wav_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            
        # Apply the exact same audio processing as assistant.py
        samples = samples - np.mean(samples) # Remove DC offset
        samples = np.clip(samples * 2.5, -1.0, 1.0) # Apply MIC_GAIN of 2.5
        
        # Append 0.8 seconds of silence to flush the model's right-context buffer
        silence = np.zeros(int(16000 * 0.8), dtype=np.float32)
        samples = np.concatenate((samples, silence))
        
        if model_type == "new":
            if not recognizer_offline: return "New model not loaded"
            stream = recognizer_offline.create_stream()
            stream.accept_waveform(16000, samples)
            recognizer_offline.decode_stream(stream)
            return stream.result.text
        else:
            if not recognizer_streaming: return "Old model not loaded"
            stream = recognizer_streaming.create_stream()
            results = []
            
            # Feed audio in chunks so reset() doesn't wipe unprocessed future audio
            chunk_size = int(16000 * 0.1) # 0.1 seconds
            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i+chunk_size]
                stream.accept_waveform(16000, chunk)
                
                while recognizer_streaming.is_ready(stream):
                    recognizer_streaming.decode_stream(stream)
                    if recognizer_streaming.is_endpoint(stream):
                        text = recognizer_streaming.get_result(stream)
                        if text: results.append(text)
                        recognizer_streaming.reset(stream)
                    
            stream.input_finished()
            while recognizer_streaming.is_ready(stream):
                recognizer_streaming.decode_stream(stream)
                if recognizer_streaming.is_endpoint(stream):
                    text = recognizer_streaming.get_result(stream)
                    if text: results.append(text)
                    recognizer_streaming.reset(stream)
                    
            text = recognizer_streaming.get_result(stream)
            if text: results.append(text)
            
            return " ".join(results).strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return f"Error: {e}"

@app.route("/")
def index():
    return render_template("index.html", phrases=json.dumps(PHRASES))

@app.route("/upload", methods=["POST"])
def upload():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
        
    name = request.form.get("name", "unknown").replace(" ", "_")
    target_text = request.form.get("text", "")
    mode = request.form.get("mode", "train")
    
    audio_file = request.files["audio"]
    out_dir = TEST_DIR if mode == "test" else DATASET_DIR
    temp_path = os.path.join(out_dir, f"temp_{uuid.uuid4().hex}.webm")
    audio_file.save(temp_path)
    
    # Determine the next index for this name
    existing_files = [f for f in os.listdir(out_dir) if f.startswith(f"{name}_") and f.endswith(".wav")]
    idx = len(existing_files) + 1
    wav_filename = f"{name}_{idx}.wav"
    wav_path = os.path.join(out_dir, wav_filename)
    
    # Convert to 16kHz Mono WAV using ffmpeg
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_path, 
            "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", wav_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(temp_path)
    except Exception as e:
        return jsonify({"error": f"FFmpeg conversion failed: {e}"}), 500
        
    # Append to transcripts.txt if training
    if mode != "test":
        transcript_path = os.path.join(DATASET_DIR, "transcripts.txt")
        with open(transcript_path, "a", encoding="utf-8") as f:
            f.write(f"{name}_{idx} {target_text}\n")
        
    model_type = request.form.get("model", "old")
    # Run STT
    predicted_text = run_stt(wav_path, model_type)
    
    # Calculate metrics
    clean_target = target_text.lower().replace(",", "").replace(".", "").strip()
    clean_pred = predicted_text.lower().replace(",", "").replace(".", "").strip()
    wer = calculate_wer(clean_target, clean_pred)
    cer = calculate_cer(clean_target, clean_pred)
    
    return jsonify({
        "status": "success",
        "saved_as": wav_filename,
        "predicted_text": predicted_text,
        "wer": wer,
        "cer": cer
    })

@app.route('/finetune', methods=['POST'])
def finetune():
    global finetune_process
    if finetune_process and finetune_process.poll() is None:
        return jsonify({"status": "already running"})
        
    try:
        log_file = open(os.path.join(os.path.dirname(__file__), "finetune.log"), "w")
        script_path = os.path.join(os.path.dirname(__file__), "finetune.sh")
        finetune_process = subprocess.Popen(["bash", script_path], stdout=log_file, stderr=subprocess.STDOUT, cwd=os.path.dirname(__file__))
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/finetune_status', methods=['GET'])
def finetune_status():
    log_path = os.path.join(os.path.dirname(__file__), "finetune.log")
    if not os.path.exists(log_path):
        return jsonify({"log": "No training log found. Click Start to begin."})
    
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            log_tail = "".join(lines[-100:])
            
        status = "running"
        if finetune_process and finetune_process.poll() is not None:
            status = "completed" if finetune_process.returncode == 0 else "failed"
            
        return jsonify({"log": log_tail, "status": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
