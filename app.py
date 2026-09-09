from flask import Flask, render_template, request, jsonify
import serial
import time
import atexit

app = Flask(__name__)

# --- Serial Connection Management ---
ser = None
try:
    ser = serial.Serial('/dev/ttyGS0', 115200, timeout=0.5)
    print("Successfully connected to MCU on /dev/ttyGS0")
except Exception as e:
    print(f"Error opening serial port: {e}")

def rotate_steps(axis, steps):
    if ser and ser.is_open:
        command = f"{axis} {steps}\n"
        ser.write(command.encode('utf-8'))
        ser.flush()
        # Wait for acknowledgment
        start_time = time.time()
        while time.time() - start_time < 5.0:
            if ser.in_waiting > 0:
                resp = ser.readline().decode('utf-8', errors='ignore').strip()
                if resp == f"ACK:{axis}":
                    return True
        return False
    else:
        print(f"MOCK: Sent {steps} steps to {axis} axis")
        time.sleep(abs(steps) * 0.002)
        return True

@app.route('/')
def index():
    return render_template('index.html')

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
    
    if axis in ['X', 'Y']:
        success = rotate_steps(axis, signed_steps)
        if success:
            return jsonify({"status": "success", "message": f"Moved {axis} {signed_steps} steps"})
        else:
            return jsonify({"status": "error", "message": "MCU communication failed"}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid axis"}), 400

def cleanup():
    if ser and ser.is_open:
        ser.close()

atexit.register(cleanup)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
