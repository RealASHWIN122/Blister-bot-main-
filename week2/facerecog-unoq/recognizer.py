import cv2
import sqlite3
import numpy as np
import socket
import struct
import os
import time
import database

# Video dimensions
WIDTH = 320
HEIGHT = 240

# Initialize face cascade and recognizer
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

FACES_DIR = 'faces'
if not os.path.exists(FACES_DIR):
    os.makedirs(FACES_DIR)

id_to_name = {}

def load_known_faces():
    global id_to_name
    users = database.get_all_users()
    
    faces = []
    ids = []
    for user in users:
        db_id = user[0]
        name = user[1]
        face_path = user[2]
        
        if os.path.exists(face_path):
            img = cv2.imread(face_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                faces.append(img)
                ids.append(db_id)
                id_to_name[db_id] = name
                
    if len(faces) > 0:
        recognizer.train(faces, np.array(ids))

database.init_db()
load_known_faces()

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def main():
    print("Starting TCP Server on port 9999...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 9999))
    server_socket.listen(1)
    
    print("Waiting for laptop to connect via ADB...")
    conn, addr = server_socket.accept()
    print(f"Connected to laptop stream at {addr}!")
    
    cv2.namedWindow("Blister Bot Vision", cv2.WINDOW_AUTOSIZE)
    
    while True:
        lengthbuf = recvall(conn, 4)
        if not lengthbuf: break
        size = struct.unpack('<L', lengthbuf)[0]
        
        frame_data = recvall(conn, size)
        if not frame_data: break
        
        frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None: continue
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
        
        unknown_face_detected = False
        unknown_face_roi = None
        
        for (x, y, w, h) in faces:
            name = "Unknown"
            face_roi = gray_frame[y:y+h, x:x+w]
            
            if len(id_to_name) > 0:
                db_id, distance = recognizer.predict(face_roi)
                if distance < 110:  # Threshold
                    name = id_to_name.get(db_id, "Unknown")
            
            # Draw segmented face box
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            
            if name == "Unknown":
                unknown_face_detected = True
                unknown_face_roi = face_roi
                break  # Stop processing other faces for now
                
        cv2.imshow("Blister Bot Vision", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
            
        if unknown_face_detected:
            # We detected an unknown face. Let's pause and ask for a name in the terminal.
            print("\n" + "="*50)
            print("🛑 Unknown face detected!")
            name = input("Please type the name of this person (or leave blank to skip): ").strip()
            
            if name:
                print(f"📸 Registering {name}. Please move your head around slowly...")
                capture_count = 0
                
                while capture_count < 10:
                    # Keep reading from the stream to capture 10 faces spaced out
                    lengthbuf = recvall(conn, 4)
                    if not lengthbuf: break
                    size = struct.unpack('<L', lengthbuf)[0]
                    frame_data = recvall(conn, size)
                    if not frame_data: break
                    
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is None: continue
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50))
                    
                    if len(faces) > 0:
                        (x, y, w, h) = faces[0]
                        c_face_roi = gray_frame[y:y+h, x:x+w]
                        
                        # Show the user what we are capturing
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                        cv2.putText(frame, f"Capturing: {capture_count+1}/10", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
                        cv2.imshow("Blister Bot Vision", frame)
                        cv2.waitKey(1)
                        
                        final_path = os.path.join(FACES_DIR, f"{name}_{int(time.time()*1000)}.jpg")
                        cv2.imwrite(final_path, c_face_roi)
                        database.add_user(name, final_path)
                        capture_count += 1
                        
                        time.sleep(0.5)  # Pause to ensure varied angles are captured!
                        
                print(f"✅ Training complete for {name}!")
                load_known_faces()  # Retrain LBPH model
                print("="*50 + "\n")
                
                # Clear out any backlogged frames in the socket due to the 5 seconds of sleeping
                # We can do this by making the socket non-blocking momentarily
                conn.setblocking(0)
                try:
                    while conn.recv(65536): pass
                except BlockingIOError:
                    pass
                conn.setblocking(1)
                
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
