import cv2
import face_recognition
import numpy as np
import pickle
import os
import threading

DB_PATH = "face_database.pkl"
TOLERANCE = 0.55  # Lower = stricter match, Higher = looser match

# --- 1. Database Persistence ---
def load_database():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            data = pickle.load(f)
            return data.get("encodings", []), data.get("names", [])
    return [], []

def save_database(encodings, names):
    with open(DB_PATH, "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f)
    print("[INFO] Database successfully updated and saved locally.")

# --- 2. Main Recognition & Registration Pipeline ---
enrollment_active = False

def run_facial_system():
    global enrollment_active
    known_encodings, known_names = load_database()
    print(f"[INFO] Loaded {len(known_names)} profile(s) from database.")

    video_capture = cv2.VideoCapture(0)
    
    # Optimize frame size for fast edge processing
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_count = 0
    process_this_frame = True

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Process every 2nd or 3rd frame to reduce CPU load on edge hardware
        if frame_count % 2 == 0:
            # Resize frame to 1/4 size for fast facial recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert BGR (OpenCV) to RGB (face_recognition)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                name = "Unknown"
                
                if len(known_encodings) > 0:
                    # Calculate Euclidean distance to all known face vectors
                    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if face_distances[best_match_index] < TOLERANCE:
                        name = known_names[best_match_index]

                # --- 3. Dynamic Terminal Enrollment ---
                if name == "Unknown" and not enrollment_active:
                    enrollment_active = True
                    
                    def prompt_for_name(encoding):
                        global enrollment_active
                        print("\n" + "="*50)
                        print("[ALERT] Unknown face detected in camera stream!")
                        user_input = input("Enter the person's name (or press Enter to skip): ").strip()
                        print("="*50 + "\n")

                        if user_input:
                            known_encodings.append(encoding)
                            known_names.append(user_input)
                            save_database(known_encodings, known_names)
                        
                        enrollment_active = False

                    # Start input prompt in a background thread so the video doesn't freeze
                    threading.Thread(target=prompt_for_name, args=(face_encoding,), daemon=True).start()
                    
                    # We can label them as "Enrolling..." while the thread runs
                    name = "Enrolling..."
                elif name == "Unknown" and enrollment_active:
                    name = "Enrolling..."

                face_names.append(name)

        frame_count += 1

        # --- 4. Render Bounding Boxes & Labels ---
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up coordinate positions from 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw box
            box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

            # Draw label background & text
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), box_color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)

        cv2.imshow('Facial Recognition & Registration', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_facial_system()
