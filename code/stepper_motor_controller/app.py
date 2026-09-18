from flask import Flask, render_template, request, jsonify, Response
import socket
import time
import atexit
import cv2
import threading

app = Flask(__name__)

# --- Socket Connection Management ---
def get_mcu_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 7500))
        s.settimeout(5.0)
        return s
    except Exception as e:
        print(f"Error opening MCU socket: {e}")
        return None

def rotate_steps(axis, steps):
    s = get_mcu_socket()
    if s:
        try:
            command = f"{axis} {steps}\n"
            s.sendall(command.encode('utf-8'))
            
            # Wait for acknowledgment
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
        except Exception as e:
            print(f"Error communicating with MCU: {e}")
            if s:
                s.close()
            return False
    else:
        print(f"MOCK: Sent {steps} steps to {axis} axis")
        time.sleep(abs(steps) * 0.002)
        return True

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    
    while True:
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue
        
        # Draw crosshair in center for drill targeting
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        cv2.line(frame, (cx - 20, cy), (cx + 20, cy), (0, 255, 0), 2)
        cv2.line(frame, (cx, cy - 20), (cx, cy + 20), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), 1)

        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/move', methods=['POST'])
def move():
    data = request.json
    # Frontend sends axis ('X' or 'Y'), direction (1 or -1), and steps (int)
    axis = data.get('axis')
    direction = data.get('direction', 1)
    steps = data.get('steps', 10)
    
    try:
        steps = int(steps)
        direction = int(direction)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid step count"}), 400

    # Calculate signed steps for the Arduino sketch
    signed_steps = steps * direction
    
    if axis in ['X', 'Y', 'Z']:
        success = rotate_steps(axis, signed_steps)
        if success:
            return jsonify({"status": "success", "message": f"Moved {axis} {signed_steps} steps"})
        else:
            return jsonify({"status": "error", "message": "MCU communication failed"}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid axis"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
