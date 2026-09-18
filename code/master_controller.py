import os
import time
import cv2
import threading
import sys
import json
import sqlite3
import numpy as np
import socket
import struct
import traceback
try:
    import pytesseract
except ImportError:
    print("Warning: pytesseract not installed.")

# Import components
sys.path.append(os.path.join(os.path.dirname(__file__), 'UNO'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'facerecog-unoq'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'blister_detector'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'stepper_motor_controller'))

from assistant import init_llm, init_stt, init_tts, generate_response, speak_text, listen_and_transcribe, mic_active
from database import init_db, add_caretaker, add_patient, add_inventory, get_inventory, decrement_inventory, get_patient_by_name, update_patient

try:
    from detector import get_pill_boundary
except:
    def get_pill_boundary(image): return [], []

try:
    import week2.facerecog_unoq.database as face_db
except:
    pass

FACES_DIR = 'faces'
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

class BlisterBotMaster:
    def __init__(self):
        self.state = 0
        self.llm = None
        self.stt = None
        self.tts = None
        self.medical_db = []
        
        # LBPH Face Recognizer
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.id_to_name = {}
        
        # Cameras (Init lazily)
        self.cap = None
        
        # Streaming Server
        self.stream_conn = None
        self.frame_to_stream = None
        self.lock = threading.Lock()
        
        threading.Thread(target=self.video_stream_server, daemon=True).start()

    def video_stream_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 9999))
        server.listen(1)
        print("[STREAM] Video server listening on port 9999...")
        
        while True:
            conn, addr = server.accept()
            print(f"[STREAM] Laptop connected from {addr}")
            self.stream_conn = conn
            try:
                while True:
                    frame = None
                    with self.lock:
                        if self.frame_to_stream is not None:
                            frame = self.frame_to_stream.copy()
                            self.frame_to_stream = None
                    
                    if frame is not None:
                        result, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if result:
                            data = encoded.tobytes()
                            size = struct.pack('<L', len(data))
                            self.stream_conn.sendall(size + data)
                    time.sleep(0.05)
            except Exception as e:
                print(f"[STREAM] Connection dropped: {e}")
                self.stream_conn = None
    
    def update_stream(self, frame):
        with self.lock:
            self.frame_to_stream = frame

    def capture_face(self, name):
        """Capture 10 frames of a person's face to train LBPH"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            
        print(f"📸 Registering {name}. Please move your head around slowly...")
        speak_text(self.tts, f"Please look at the camera, {name}. Moving your head slightly.")
        
        capture_count = 0
        while capture_count < 10:
            ret, frame = self.cap.read()
            if not ret: continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(50, 50))
            
            for (x, y, w, h) in faces:
                c_face_roi = gray[y:y+h, x:x+w]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.putText(frame, f"Capturing: {capture_count+1}/10", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
                
                final_path = os.path.join(FACES_DIR, f"{name}_{int(time.time()*1000)}.jpg")
                cv2.imwrite(final_path, c_face_roi)
                try:
                    face_db.add_user(name, final_path)
                except:
                    pass
                capture_count += 1
                break
                
            self.update_stream(frame)
            time.sleep(0.5)
            
        speak_text(self.tts, "Facial registration complete.")
        self.load_known_faces()

    def load_known_faces(self):
        try:
            users = face_db.get_all_users()
            faces, ids = [], []
            for user in users:
                db_id, name, face_path = user[0], user[1], user[2]
                if os.path.exists(face_path):
                    img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        ids.append(db_id)
                        self.id_to_name[db_id] = name
            if len(faces) > 0:
                self.recognizer.train(faces, np.array(ids))
        except:
            pass

    def perform_ocr(self):
        """Scans the blister pack and reads text using OCR"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            
        ret, frame = self.cap.read()
        if not ret: return ""
        
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        coords_list, contours = get_pill_boundary(image_rgb)
        
        found_text = ""
        # Draw bounding boxes and run OCR
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            roi = frame[y:y+h, x:x+w]
            try:
                text = pytesseract.image_to_string(roi).strip()
                if text:
                    found_text += text + " "
                    cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            except:
                pass
                
        self.update_stream(frame)
        return found_text

    def boot_sequence(self):
        print("[STATE 0] Boot Sequence Initiated...")
        self.stt = init_stt()
        self.tts = init_tts()
        self.llm = init_llm()
        self.load_known_faces()
        
        speak_text(self.tts, "Hi, I'm awake.")
        
        while True:
            text = listen_and_transcribe(self.stt, mic_active)
            if text:
                if "setup" in text.lower() or "set up" in text.lower():
                    self.state = 1
                    return
                
                prompt = (
                    f"Does the following text contain a command or intent to enter 'setup mode' or 'bot setup'? "
                    f"Answer ONLY 'YES' or 'NO'. Text: '{text}'"
                )
                if "YES" in generate_response(self.llm, prompt).strip().upper():
                    self.state = 1
                    return

    def setup_mode_profiles(self):
        print("[STATE 1] Setup Mode: User Profiles")
        speak_text(self.tts, "Entering voice and visual setup.")
            
        while True:
            speak_text(self.tts, "Please provide caretaker details. What is your name and work shift?")
            response = listen_and_transcribe(self.stt, mic_active)
            if response:
                prompt = f"Extract 'name', 'work_shift', and 'is_patient' (boolean) from this text into valid JSON: {response}"
                json_str = generate_response(self.llm, prompt)
                try:
                    data = json.loads(json_str.replace("```json", "").replace("```", "").strip())
                    data = {k.lower(): v for k, v in data.items()}
                    
                    name = data.get('name', 'Unknown')
                    shift = data.get('work_shift', 'Full Day')
                    
                    # Strict Confirmation
                    speak_text(self.tts, f"I heard {name} and {shift}. Is this correct? Say yes or no.")
                    confirm = listen_and_transcribe(self.stt, mic_active)
                    if confirm and "yes" in confirm.lower():
                        # Strict Facial Capture
                        self.capture_face(name)
                        add_caretaker(name, shift, data.get('is_patient', False), f"{name}.jpg")
                        speak_text(self.tts, f"Caretaker {name} added.")
                    else:
                        speak_text(self.tts, "Let's try again.")
                        continue
                except:
                    print("Failed to parse LLM JSON")
            
            speak_text(self.tts, "Are there more caretakers? Say yes or no.")
            more = listen_and_transcribe(self.stt, mic_active)
            if more and "no" in more.lower(): break
                
        self.state = 2

    def setup_mode_inventory(self):
        print("[STATE 2] Setup Mode: Medication Inventory")
        speak_text(self.tts, "Please load blister packs into the wheel. Say confirm when ready.")
        
        while True:
            text = listen_and_transcribe(self.stt, mic_active)
            if text and "confirm" in text.lower():
                break
        
        speak_text(self.tts, "Scanning medication...")
        med_text = self.perform_ocr()
        print(f"[OCR Scanned] {med_text}")
        
        speak_text(self.tts, "Inventory setup complete. Transitioning to normal mode.")
        if self.cap:
            self.cap.release()
            self.cap = None
        self.state = 3

    def get_mcu_socket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 7500))
            s.settimeout(5.0)
            return s
        except:
            return None

    def move_axis(self, axis, steps):
        if steps == 0: return True
        s = self.get_mcu_socket()
        if s:
            try:
                command = f"{axis} {steps}\n"
                s.sendall(command.encode('utf-8'))
                start_time = time.time()
                buffer = ""
                while time.time() - start_time < 5.0:
                    try:
                        data = s.recv(1024)
                        if data:
                            buffer += data.decode('utf-8', errors='ignore')
                            if f"ACK:{axis}" in buffer:
                                s.close()
                                return True
                    except socket.timeout:
                        break
                s.close()
                return False
            except:
                if s: s.close()
                return False
        return False

    def move_to_pixel(self, px, py, cx, cy):
        target_x_step = int((px - cx) * 1.0)
        target_y_step = int((py - cy) * 1.0)
        
        diff_x = target_x_step - getattr(self, 'current_x_step', 0)
        diff_y = target_y_step - getattr(self, 'current_y_step', 0)
        
        if diff_x != 0: self.move_axis('X', diff_x)
        if diff_y != 0: self.move_axis('Y', diff_y)
        
        self.current_x_step = target_x_step
        self.current_y_step = target_y_step

    def execute_drill(self, medicine_name):
        speak_text(self.tts, f"Locating {medicine_name} for drilling.")
        if self.cap is None:
            self.cap = cv2.VideoCapture(1)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
        
        for _ in range(10): self.cap.read()
        ret, frame = self.cap.read()
        if not ret:
            speak_text(self.tts, "Camera error.")
            return
            
        height, width, _ = frame.shape
        cx, cy = width // 2, height // 2
        
        self.update_stream(frame)
        
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        coords_list, contours = get_pill_boundary(image_rgb)
        
        if not contours:
            speak_text(self.tts, "No medicine boundaries detected.")
            return
            
        target_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(frame, [target_contour], -1, (0, 255, 0), 2)
        self.update_stream(frame)
        
        speak_text(self.tts, "Medicine found. Initiating extraction sequence.")
        
        self.current_x_step = 0
        self.current_y_step = 0
        
        self.move_axis('Z', -2)
        start_pt = target_contour[0][0]
        self.move_to_pixel(start_pt[0], start_pt[1], cx, cy)
        
        time.sleep(0.5)
        self.move_axis('Z', 2)
        time.sleep(0.5)
        
        for idx, pt_arr in enumerate(target_contour[1:]):
            pt = pt_arr[0]
            self.move_to_pixel(pt[0], pt[1], cx, cy)
            time.sleep(0.05)
            
        self.move_axis('Z', -2)
        time.sleep(0.5)
        self.move_to_pixel(cx, cy, cx, cy)
        speak_text(self.tts, f"{medicine_name} has been extracted.")

    def normal_operating_mode(self):
        print("[STATE 3] Normal Operating Mode")
        
        while True:
            text = listen_and_transcribe(self.stt, mic_active)
            if not text: continue
            
            clean_text = text.lower()
            
            # WAKE WORD LOGIC (Fuzzy matching for different pronunciations)
            wake_words = ["bot", "bought", "boat", "but", "pot", "robot", "blister", "blisterbot", "what", "dot"]
            if any(w in clean_text for w in wake_words):
                speak_text(self.tts, "I am listening.")
                cmd_text = listen_and_transcribe(self.stt, mic_active)
                if not cmd_text:
                    continue
                clean_cmd = cmd_text.lower()
                
                # Use LLM to classify the intent to handle all mispronunciations and phrasings!
                intent_prompt = f"""Classify the user's command into one of these exact categories:
1. ADD_PATIENT (e.g. "add patient", "new patient", "ad patient")
2. DRILL_MEDICINE (e.g. "I need paracetamol", "get me advil", "give me medicine")
3. PATIENT_DETAILS (e.g. "details for john", "patient info")
4. UPDATE_PATIENT (e.g. "update john's details", "change patient info")
5. Q_AND_A (any general question)

Command: '{cmd_text}'
Output ONLY the category name."""
                intent = generate_response(self.llm, intent_prompt).strip().upper()
                print(f"[INTENT CLASSIFIED] {intent} from: {cmd_text}")
                
                if "ADD_PATIENT" in intent:
                    speak_text(self.tts, "Let's add a new patient. What is their name, age, and schedule?")
                    details = listen_and_transcribe(self.stt, mic_active)
                    if details:
                        prompt = f"Extract 'name', 'age', 'health_issues', and 'med_schedule' from this text into valid JSON: {details}"
                        try:
                            json_str = generate_response(self.llm, prompt)
                            data = json.loads(json_str.replace("```json", "").replace("```", "").strip())
                            name = data.get('name', 'Unknown')
                            speak_text(self.tts, f"Capturing face for {name}. Please look at the camera.")
                            self.capture_face(name)
                            add_patient(name, data.get('age', 0), "Unknown", data.get('health_issues', ''), data.get('med_schedule', ''), 1, f"{name}.jpg")
                            speak_text(self.tts, f"Patient {name} has been added.")
                        except:
                            speak_text(self.tts, "Sorry, I could not process the patient details.")
                elif "DRILL_MEDICINE" in intent:
                    prompt = f"Extract just the name of the medicine the user needs from this text: '{cmd_text}'. Output ONLY the medicine name."
                    med_name = generate_response(self.llm, prompt).strip()
                    self.execute_drill(med_name)
                elif "PATIENT_DETAILS" in intent:
                    prompt = f"Extract just the name of the patient from this text: '{cmd_text}'. Output ONLY the name."
                    name = generate_response(self.llm, prompt).strip()
                    patient = get_patient_by_name(name)
                    if patient:
                        prompt2 = f"Generate a brief, spoken summary of this patient's details: {json.dumps(patient)}."
                        speak_text(self.tts, generate_response(self.llm, prompt2).strip())
                    else:
                        speak_text(self.tts, f"Sorry, I could not find {name}.")
                elif "UPDATE_PATIENT" in intent:
                    prompt = f"Extract just the name of the patient from this text: '{cmd_text}'. Output ONLY the name."
                    name = generate_response(self.llm, prompt).strip()
                    patient = get_patient_by_name(name)
                    if patient:
                        speak_text(self.tts, f"What details would you like to update for {name}?")
                        update_voice = listen_and_transcribe(self.stt, mic_active)
                        if update_voice:
                            prompt2 = (f"Update patient data.\nData: {json.dumps(patient)}\nSpeech: '{update_voice}'\n"
                                       f"Output ONLY a JSON dictionary of changed fields.")
                            try:
                                updates = json.loads(generate_response(self.llm, prompt2))
                                if update_patient(name, updates):
                                    speak_text(self.tts, f"{name}'s details updated.")
                            except:
                                speak_text(self.tts, "Sorry, I couldn't understand.")
                    else:
                        speak_text(self.tts, f"Sorry, I could not find {name}.")
                else:
                    # General Q&A Fallback
                    inv = get_inventory()
                    prompt = f"Answer this question concisely as a medical assistant. Question: '{cmd_text}'. Context: We have these medicines in inventory: {inv}"
                    answer = generate_response(self.llm, prompt)
                    speak_text(self.tts, answer)

    def run(self):
        try:
            while True:
                if self.state == 0: self.boot_sequence()
                elif self.state == 1: self.setup_mode_profiles()
                elif self.state == 2: self.setup_mode_inventory()
                elif self.state == 3: self.normal_operating_mode()
        except KeyboardInterrupt:
            if self.cap: self.cap.release()
            print("Shutting down Master Controller.")

if __name__ == "__main__":
    bot = BlisterBotMaster()
    bot.run()
