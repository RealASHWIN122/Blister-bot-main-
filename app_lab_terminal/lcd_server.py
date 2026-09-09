import socket
import serial
import time
import sys

BRIDGE_PORT = '/dev/ttyGS0'
BRIDGE_BAUD = 115200
HOST = '0.0.0.0'
PORT = 5000

def init_bridge():
    try:
        bridge = serial.Serial(BRIDGE_PORT, BRIDGE_BAUD, timeout=1)
        time.sleep(2)
        print(f"[INFO] Connected to LCD via {BRIDGE_PORT}")
        return bridge
    except Exception as e:
        print(f"[ERROR] Could not connect to {BRIDGE_PORT}: {e}")
        return None

def main():
    print("="*50)
    print("Uno Q Wireless Smart Display Server")
    print("="*50)
    
    bridge = init_bridge()
    if not bridge:
        print("[WARNING] Running without LCD attached for debugging.")
        
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow port reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"[INFO] Listening for AI commands on {HOST}:{PORT} over Wi-Fi...")
    except Exception as e:
        print(f"[ERROR] Could not bind socket: {e}")
        sys.exit(1)
        
    while True:
        try:
            print("[INFO] Waiting for connection from laptop...")
            client_socket, addr = server_socket.accept()
            print(f"[INFO] Connected to laptop at {addr}")
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break # Client disconnected
                    
                text = data.decode('utf-8').strip()
                print(f"[Wi-Fi RX]: {text}")
                
                if bridge:
                    # The text from the socket is already formatted as "PRINT:xxxxx\n" by the laptop
                    # but we'll ensure it has the newline for the Arduino firmware.
                    if not text.endswith('\n'):
                        text += '\n'
                    bridge.write(text.encode('utf-8'))
                    
                    # Optional: read ack from arduino
                    start_time = time.time()
                    while time.time() - start_time < 0.5:
                        if bridge.in_waiting:
                            response = bridge.readline().decode('utf-8').strip()
                            if response == "ACK:PRINT_DONE":
                                break
                        time.sleep(0.01)
                        
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down server...")
            break
        except Exception as e:
            print(f"[ERROR] Socket error: {e}")
        finally:
            if 'client_socket' in locals():
                client_socket.close()
                
    server_socket.close()
    if bridge:
        bridge.close()

if __name__ == "__main__":
    main()
