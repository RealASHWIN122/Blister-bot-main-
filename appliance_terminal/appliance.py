import cv2
import serial
import os
import time
import numpy as np
import threading
from flask import Flask, Response
from rapidocr_onnxruntime import RapidOCR
import re
import glob

ocr = RapidOCR()

app = Flask(__name__)

# Globals for streams
output_frame = None
output_frame_ocr = None
lock = threading.Lock()
last_ocr_text = "Waiting for scan..."
active_mode = "face"  # can be "face" or "ocr"
force_ocr = False

# Voice Globals
stt_pipe = None
is_recording = False

def init_stt():
    global stt_pipe
    print("[INFO] Loading STT (Whisper) model in background...", flush=True)
    try:
        from faster_whisper import WhisperModel
        stt_pipe = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        print("[INFO] STT model loaded successfully.", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to load STT model: {e}")

threading.Thread(target=init_stt, daemon=True).start()

def speak_text(text):
    def _speak():
        print(f"[TTS] Speaking: {text}")
        # Use edge-tts to generate speech and ffplay to play it immediately
        os.system(f"/home/arduino/.local/bin/edge-tts --text '{text}' --write-media /tmp/speech.mp3 && ffplay -nodisp -autoexit /tmp/speech.mp3 >/dev/null 2>&1")
    threading.Thread(target=_speak, daemon=True).start()

def record_and_transcribe():
    global is_recording, stt_pipe, last_ocr_text
    if is_recording or stt_pipe is None:
        return
    is_recording = True
    
    def _worker():
        global is_recording, last_ocr_text
        print("[MIC] Recording for 5 seconds...", flush=True)
        # Record audio from the USB microphone via ALSA using plughw for auto-resampling
        os.system("arecord -D plughw:0,0 -f S16_LE -c1 -r 16000 -d 5 /tmp/capture.wav >/dev/null 2>&1")
        print("[MIC] Recording finished. Transcribing...", flush=True)
        try:
            segments, info = stt_pipe.transcribe("/tmp/capture.wav", beam_size=1)
            transcript = " ".join([segment.text for segment in segments]).strip()
            print(f"[STT] User said: {transcript}")
            if transcript:
                last_ocr_text = f"You said: {transcript}"
                speak_text(f"You said: {transcript}")
        except Exception as e:
            print(f"[ERROR] STT failed: {e}")
        is_recording = False

    threading.Thread(target=_worker, daemon=True).start()

# Face Recognition Globals
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
KNOWN_FACES_DIR = "known_faces"

def load_known_faces():
    print("[INFO] Loading known faces...", flush=True)
    id_to_name = {}
    faces = []
    ids = []
    
    if not os.path.exists(KNOWN_FACES_DIR):
        print("[WARNING] No known_faces directory found.")
        return id_to_name
        
    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue
            
        person_id = len(id_to_name)
        id_to_name[person_id] = person_name
        
        for image_path in glob.glob(os.path.join(person_dir, "*.jpg")):
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                ids.append(person_id)
                
    if len(faces) > 0:
        recognizer.train(faces, np.array(ids))
        print(f"[INFO] Trained {len(faces)} images for {len(id_to_name)} people.", flush=True)
    else:
        print("[WARNING] No images found to train.")
        
    return id_to_name

def init_bridge():
    try:
        bridge = serial.Serial('/dev/ttyGS0', 115200, timeout=1, write_timeout=0.1)
        print("[INFO] Opened /dev/ttyGS0")
        return bridge
    except Exception as e:
        print(f"[ERROR] Could not open /dev/ttyGS0: {e}")
        return None

import difflib

def extract_patterns(text):
    patterns = {
        'medicine': None,
        'dosage': None,
    }
    
    medicine_keywords = ['PARACETAMOL', 'AMOXICILLIN', 'IBUPROFEN', 'ASPIRIN', 'CETIRIZINE', 'LIPITOR']
    text_upper = text.upper()
    
    for keyword in medicine_keywords:
        if keyword in text_upper:
            patterns['medicine'] = keyword
            break
            
    if not patterns['medicine']:
        words = text_upper.split()
        for word in words:
            clean_word = re.sub(r'[^A-Z]', '', word)
            if len(clean_word) >= 5:
                matches = difflib.get_close_matches(clean_word, medicine_keywords, n=1, cutoff=0.7)
                if matches:
                    patterns['medicine'] = matches[0]
                    break
            
    dosage_match = re.search(r'(\d+)\s*(MG|ML)', text, re.IGNORECASE)
    if dosage_match:
        patterns['dosage'] = dosage_match.group(0).upper()
        
    return patterns

def generate_face_video():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
              bytearray(encodedImage) + b'\r\n')

def generate_ocr_video():
    global output_frame_ocr, lock
    while True:
        with lock:
            if output_frame_ocr is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame_ocr)
            if not flag:
                continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
              bytearray(encodedImage) + b'\r\n')

@app.route("/")
def index():
    html = """
    <html>
      <head>
        <title>Uno Q Web Interface</title>
        <style>
          body { font-family: sans-serif; text-align: center; background: #222; color: #fff; }
          .stream-container { display: flex; justify-content: center; margin-top: 20px; }
          .stream { margin: 0 20px; }
          img { border: 2px solid #555; border-radius: 10px; }
          #ocr_output { font-size: 24px; color: #0f0; margin-top: 15px; font-weight: bold; }
          .toggle-btn { background-color: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 20px; cursor: pointer; margin-top: 20px; margin-right: 10px; }
          .toggle-btn:hover { background-color: #0056b3; }
          .scan-btn { background-color: #28a745; }
          .scan-btn:hover { background-color: #218838; }
        </style>
      </head>
      <body>
        <h1>Uno Q Appliance</h1>
            <div style="margin-top:20px;">
                <button onclick="toggleMode()">Toggle Mode</button>
                <button id="scan_btn" onclick="forceScan()" style="display:none; background-color:#4CAF50; color:white;">Scan Now</button>
                <button id="mic_btn" onclick="triggerMic()" style="display:none; background-color:#2196F3; color:white;">🎤 Speak</button>
            </div>
        <h2 id="mode_display">Current Mode: Face Recognition</h2>
        <div class="stream-container">
            <div class="stream" id="stream_box">
                <img id="stream_img" src="/video_feed/face" width="640" height="480" />
                <div id="ocr_output" style="display: none;">Ready to scan</div>
            </div>
        </div>
        
        <script>
          let currentMode = "face";
          function toggleMode() {
              fetch("/toggle_mode").then(r => r.text()).then(mode => {
                  currentMode = mode;
                  if(mode === "face") {
                      document.getElementById("mode_display").innerText = "Current Mode: Face Recognition";
                      document.getElementById("stream_img").src = "/video_feed/face";
                      document.getElementById("ocr_output").style.display = "none";
                      document.getElementById("scan_btn").style.display = "none";
                      document.getElementById("mic_btn").style.display = "none";
                  } else {
                      document.getElementById("mode_display").innerText = "Current Mode: Medicine Scanner";
                      document.getElementById("stream_img").src = "/video_feed/ocr";
                      document.getElementById("ocr_output").style.display = "block";
                      document.getElementById("scan_btn").style.display = "inline-block";
                      document.getElementById("mic_btn").style.display = "inline-block";
                  }
              });
          }
          function forceScan() {
              document.getElementById("ocr_output").innerText = "Scanning... Please wait.";
              fetch("/force_scan");
          }
          function triggerMic() {
              document.getElementById("ocr_output").innerText = "Recording for 5 seconds...";
              fetch("/trigger_mic");
          }
          setInterval(() => {
              if(currentMode === "ocr") {
                  fetch("/ocr_result")
                    .then(r => r.text())
                    .then(t => { 
                        if(t !== "") document.getElementById("ocr_output").innerText = t; 
                    });
              }
          }, 1000);
        </script>
      </body>
    </html>
    """
    return html

@app.route("/toggle_mode")
def toggle_mode():
    global active_mode
    active_mode = "ocr" if active_mode == "face" else "face"
    return active_mode

@app.route("/force_scan")
def force_scan():
    global force_ocr
    force_ocr = True
    return "OK"

@app.route("/trigger_mic")
def trigger_mic():
    global last_ocr_text
    last_ocr_text = "Recording for 5 seconds..."
    record_and_transcribe()
    return "OK"

@app.route("/video_feed/face")
def video_feed_face():
    return Response(generate_face_video(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/video_feed/ocr")
def video_feed_ocr():
    return Response(generate_ocr_video(),
                    mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/ocr_result")
def ocr_result():
    global last_ocr_text
    return last_ocr_text

def process_camera():
    global output_frame, output_frame_ocr, lock, last_ocr_text, active_mode, force_ocr
    bridge = init_bridge()
    id_to_name = load_known_faces()

    if len(id_to_name) == 0:
        print("[WARNING] Proceeding without any known faces.")

    print("[INFO] Finding Cameras...", flush=True)
    camera_indices = []
    
    # Retry forever until cameras are found
    while len(camera_indices) < 1:
        for i in range(10):
            c = cv2.VideoCapture(i)
            if c.isOpened():
                ret, frame = c.read()
                if ret and frame is not None:
                    if i not in camera_indices:
                        camera_indices.append(i)
                        print(f"[INFO] Found camera at index {i}")
                c.release()
        if len(camera_indices) >= 2:
            break
        print(f"[WARN] Cameras found: {len(camera_indices)}. Waiting for USB cameras to be plugged in...")
        time.sleep(1)

    if len(camera_indices) == 1:
        print("[WARNING] Only 1 camera found! Will use it for both modes.")
        camera_indices.append(camera_indices[0])

    current_mode = None
    cap = None
    last_seen_name = None
    last_print_time = 0
    last_frame = None
    motion_stopped_time = 0
    is_stable = False
    stable_frames = 0
    already_scanned = False

    while True:
        if current_mode != active_mode:
            print(f"[INFO] Switching mode to {active_mode}...", flush=True)
            if cap is not None:
                cap.release()
            
            current_mode = active_mode
            idx = camera_indices[0] if current_mode == "face" else camera_indices[1]
            cap = cv2.VideoCapture(idx)
            
            last_frame = None
            is_stable = False
            last_seen_name = None
            time.sleep(1.0)
            
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
            
        if current_mode == "face":
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
            detected_name = "Unknown"
            annotated_frame = frame.copy()

            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                (x, y, w, h) = faces[0]
                face_roi = gray_frame[y:y+h, x:x+w]
                distance_str = ""
                if len(id_to_name) > 0:
                    db_id, distance = recognizer.predict(face_roi)
                    distance_str = f" Dist: {int(distance)}"
                    if distance < 110:
                        detected_name = id_to_name.get(db_id, "Unknown")
                
                color = (0, 255, 0) if detected_name != "Unknown" else (0, 0, 255)
                cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(annotated_frame, detected_name + distance_str, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            if detected_name != "Unknown":
                current_time = time.time()
                if detected_name != last_seen_name or (current_time - last_print_time > 5.0):
                    print(f"[RECOGNIZED]: {detected_name}")
                    if bridge:
                        try:
                            bridge.write(f"PRINT:Hello {detected_name}!\n".encode('utf-8'))
                        except Exception as e:
                            print(f"[ERROR] Bridge write failed: {e}")
                    last_seen_name = detected_name
                    last_print_time = current_time

            with lock:
                output_frame = annotated_frame.copy()

        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if last_frame is None:
                last_frame = gray
            
            diff = cv2.absdiff(last_frame, gray)
            _, thresh_diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            motion_level = cv2.countNonZero(thresh_diff)
            last_frame = gray
            
            if motion_level > 3000:
                stable_frames = 0
                already_scanned = False
                status = "Moving... Hold still."
                # User requested mic triggers only when motion is detected
                record_and_transcribe()
            else:
                stable_frames += 1
                if already_scanned:
                    status = "Stable. Move to scan again."
                else:
                    status = f"Stable ({stable_frames}/10)..."
            
            if stable_frames >= 10 and not already_scanned:
                force_ocr = True
                stable_frames = 0
                already_scanned = True
                status = "Scanning..."
            
            if force_ocr:
                print("[INFO] Running forced OCR...")
                force_ocr = False
                
                result, _ = ocr(frame)
                text = ""
                if result:
                    for line in result:
                        text += line[1] + " "
                
                print(f"[OCR RAW TEXT]: {text}")
                patterns = extract_patterns(text)

                if patterns['medicine'] or patterns['dosage']:
                    found_text = f"{patterns['medicine'] or 'Unknown'} {patterns['dosage'] or ''}"
                    if bridge:
                        try:
                            bridge.write(f"PRINT:Scanned: {found_text}\n".encode('utf-8'))
                        except Exception as e:
                            print(f"[ERROR] Bridge write failed: {e}")
                    last_ocr_text = f"Scanned: {found_text}"
                    speak_text(found_text)
                else:
                    if text.strip():
                        last_ocr_text = f"Read: {text.strip()[:30]}"
                    else:
                        last_ocr_text = "No text found on image."
                        
                # Reset the motion baseline since 2 seconds have passed and lighting/position may have shifted
                last_frame = None
                
                # Clear the stale frames from the OpenCV buffer that piled up while OCR was running
                for _ in range(5):
                    cap.read()

            annotated = frame.copy()
            status = "Ready to scan. Press 'Scan Now'"
            color = (0, 255, 0)
            
            cv2.putText(annotated, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            with lock:
                output_frame_ocr = annotated.copy()

        time.sleep(0.05)

if __name__ == "__main__":
    t = threading.Thread(target=process_camera, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True, use_reloader=False)
