import serial
import time
import base64

def deploy():
    try:
        print("Connecting to Uno Q on /dev/ttyACM0...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        
        # Wake up / Login if needed
        ser.write(b'\n')
        time.sleep(0.5)
        ser.write(b'root\n')
        time.sleep(1)
        ser.write(b'\n')
        
        print("Setting up directories...")
        ser.write(b'mkdir -p templates\n')
        time.sleep(0.5)

        # Read app.py
        with open('app.py', 'rb') as f:
            app_b64 = base64.b64encode(f.read()).decode()
        
        print("Transferring app.py...")
        # Send in chunks to avoid overwhelming the serial buffer
        ser.write(f'echo "{app_b64}" | base64 -d > app.py\n'.encode())
        time.sleep(2)

        # Read index.html
        with open('templates/index.html', 'rb') as f:
            idx_b64 = base64.b64encode(f.read()).decode()
            
        print("Transferring templates/index.html...")
        ser.write(f'echo "{idx_b64}" | base64 -d > templates/index.html\n'.encode())
        time.sleep(2)

        print("Installing dependencies on Uno Q...")
        ser.write(b'apt-get update && apt-get install -y python3-pip python3-flask\n')
        ser.write(b'pip3 install flask python-periphery\n')
        time.sleep(2)
        
        print("Starting the Flask server on Uno Q...")
        ser.write(b'python3 app.py &\n')
        time.sleep(1)
        
        print("Deployment sequence completed over serial.")
        ser.close()
    except Exception as e:
        print(f"Error deploying: {e}")

if __name__ == "__main__":
    deploy()
