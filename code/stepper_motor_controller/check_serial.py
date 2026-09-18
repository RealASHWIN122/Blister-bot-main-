import serial
import time

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    
    # Try sending carriage returns
    ser.write(b'\r\n')
    time.sleep(0.5)
    ser.write(b'\r\n')
    time.sleep(1)
    
    # Read whatever comes back
    output = ser.read(1024).decode('utf-8', errors='replace')
    print("--- SERIAL OUTPUT (9600) ---")
    print(repr(output))
    print("----------------------------")
    ser.close()
except Exception as e:
    print(f"Error: {e}")
