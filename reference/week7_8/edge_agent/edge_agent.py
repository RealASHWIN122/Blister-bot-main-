import json
import os
import sys
import cv2
import numpy as np
from llama_cpp import Llama

# Add sibling directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
ocr_dir = os.path.join(parent_dir, 'ocr')
face_dir = os.path.join(parent_dir, 'facerecog-unoq')
sys.path.append(ocr_dir)
sys.path.append(face_dir)

# Initialize OCR
try:
    from benchmark_ocr import load_ppocrv5, run_rapidocr, run_tesseract, extract_patterns, HAS_RAPIDOCR, HAS_TESSERACT
    if HAS_RAPIDOCR:
        print("[INFO] Loading RapidOCR engine...")
        ocr_engine = load_ppocrv5()
    else:
        ocr_engine = None
except ImportError:
    print("[WARNING] Could not load OCR modules.")
    ocr_engine = None
    HAS_RAPIDOCR = False
    HAS_TESSERACT = False
    extract_patterns = lambda x: {"medicine": "Error", "dosage": "Error", "batch": "Error", "exp": "Error"}

# Initialize Face Recognition
try:
    import database
    database.DB_NAME = os.path.join(face_dir, 'attendance.db') # Fix path context
    
    face_cascade_path = os.path.join(face_dir, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    users = database.get_all_users()
    faces_list = []
    ids_list = []
    id_to_name = {}
    
    for user in users:
        db_id, name, face_path = user[0], user[1], user[2]
        if not face_path.startswith('/'):
            face_path = os.path.join(face_dir, face_path)
            
        if os.path.exists(face_path):
            img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces_list.append(img)
                ids_list.append(db_id)
                id_to_name[db_id] = name
                
    if len(faces_list) > 0:
        print(f"[INFO] Training Face Recognizer on {len(faces_list)} known faces...")
        face_recognizer.train(faces_list, np.array(ids_list))
except Exception as e:
    print(f"[WARNING] Face Recog init failed: {e}")
    face_recognizer = None
    id_to_name = {}

def capture_image(filename):
    """Helper to capture a single frame from the Uno Q USB camera."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False
    ret, frame = cap.read()
    cap.release()
    if ret:
        cv2.imwrite(filename, frame)
        return True
    return False

def scan_prescription():
    """Tool: Scan a medical prescription using the camera and extract text via OCR."""
    print("[Action] Capturing and scanning prescription...")
    
    img_path = "/tmp/rx_capture.jpg"
    if not capture_image(img_path):
        return {"status": "error", "message": "Failed to access camera."}
        
    text = ""
    if HAS_RAPIDOCR and ocr_engine is not None:
        text = run_rapidocr(img_path, ocr_engine)
    elif HAS_TESSERACT:
        text = run_tesseract(img_path)
    else:
        return {"status": "error", "message": "No OCR engine installed on board."}
        
    if not text:
        return {"status": "success", "extracted_text": "No text detected."}
        
    patterns = extract_patterns(text)
    
    return {
        "status": "success",
        "raw_text": text.replace('\n', ' '),
        "detected_medicine": patterns["medicine"],
        "detected_dosage": patterns["dosage"]
    }

def activate_facial_recognition():
    """Tool: Activate the facial recognition system to verify the patient's identity."""
    print("[Action] Scanning face...")
    
    img_path = "/tmp/face_capture.jpg"
    if not capture_image(img_path):
        return {"status": "error", "message": "Failed to access camera."}
        
    if face_recognizer is None:
        return {"status": "error", "message": "Face recognizer not initialized."}
        
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return {"status": "error", "message": "Image read failed."}
        
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
    if len(faces) == 0:
        return {"status": "success", "recognized_user": "No face detected in camera view."}
        
    (x, y, w, h) = faces[0] # Just take the first face for the assistant
    face_roi = img[y:y+h, x:x+w]
    
    if len(id_to_name) > 0:
        db_id, distance = face_recognizer.predict(face_roi)
        if distance < 110:
            name = id_to_name.get(db_id, "Unknown")
            return {"status": "success", "recognized_user": name}
            
    return {"status": "success", "recognized_user": "Unknown User"}

def check_time():
    """Tool: Get the current time."""
    from datetime import datetime
    return {"current_time": datetime.now().strftime("%I:%M %p")}

# Map of available tools
TOOLS = {
    "scan_prescription": scan_prescription,
    "activate_facial_recognition": activate_facial_recognition,
    "check_time": check_time
}

# --- 2. Load the Edge LLM ---
def load_model():
    print("[INFO] Loading LLM into RAM... (This may take a few seconds)")
    # n_ctx is the context window. Keeping it small (2048) ensures it fits in 2GB RAM.
    llm = Llama(
        model_path="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        n_ctx=2048,
        n_threads=4, # Optimize for 4-core ARM CPU (Arduino Uno Q)
        verbose=False # Set to True to see memory usage logs
    )
    return llm

# --- 3. The Agent Loop ---
def run_agent(llm, user_prompt):
    # System prompt forces the model to choose between natural language or a JSON tool call
    system_prompt = """You are an offline edge-AI medical assistant running on an Arduino Uno Q. You have access to the following tools:
1. scan_prescription(): Scans a prescription using the camera and returns the OCR text. Use this when the user asks you to read or scan their prescription.
2. activate_facial_recognition(): Turns on the facial recognition camera to identify the patient. Use this when you need to verify who is speaking or dispense medication.
3. check_time(): Returns the current time.

To use a tool, output exactly this JSON format and nothing else:
{"tool": "tool_name"}

If you do not need to use a tool, just respond naturally to the patient."""

    # Format prompt for Qwen 2.5
    prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    print(f"\n[User]: {user_prompt}")
    print("[Agent Thinking...]")
    
    response = llm(
        prompt,
        max_tokens=256,
        stop=["<|im_end|>"],
        temperature=0.1 # Low temperature for more deterministic reasoning
    )
    
    output = response["choices"][0]["text"].strip()
    
    # --- 4. Parse output for Tool Calls ---
    try:
        if output.startswith("{") and "tool" in output:
            tool_call = json.loads(output)
            tool_name = tool_call.get("tool")
            
            if tool_name in TOOLS:
                print(f"[Agent Action]: Calling tool -> {tool_name}()")
                tool_result = TOOLS[tool_name]()
                print(f"[Tool Result]: {tool_result}")
                
                # Feed the tool result back to the model so it can answer the user
                follow_up_prompt = prompt + output + f"<|im_end|>\n<|im_start|>user\nTool result: {json.dumps(tool_result)}<|im_end|>\n<|im_start|>assistant\n"
                
                print("[Agent Thinking...]")
                final_response = llm(
                    follow_up_prompt,
                    max_tokens=256,
                    stop=["<|im_end|>"],
                    temperature=0.1
                )
                final_text = final_response['choices'][0]['text'].strip()
                print(f"[Agent]: {final_text}")
                return final_text
            else:
                print(f"[Agent Error]: Attempted to call unknown tool '{tool_name}'")
                return f"Error: unknown tool {tool_name}"
        else:
            # Natural language response
            print(f"[Agent]: {output}")
            return output
    except json.JSONDecodeError:
        print(f"[Agent]: {output}")
        return output

if __name__ == "__main__":
    if not os.path.exists("qwen2.5-1.5b-instruct-q4_k_m.gguf"):
        print("[ERROR] Model file not found. Please run download_model.py first.")
        exit(1)
        
    llm = load_model()
    
    print("\n" + "="*50)
    print("Edge Agent Initialized. Ready for testing.")
    print("="*50)
    
    # Test 1: Simple Knowledge (No tool needed)
    run_agent(llm, "Hello, what kind of hardware are you running on?")
    
    # Test 2: Sensor Tool Call
    run_agent(llm, "It feels hot in here. What is the temperature right now?")
    
    # Test 3: Camera Tool Call
    run_agent(llm, "Someone is at the door, can you check who it is?")
