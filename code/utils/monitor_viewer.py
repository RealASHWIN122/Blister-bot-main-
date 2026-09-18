import socket
import struct
import cv2
import numpy as np
import time

def start_viewer(board_ip="192.168.0.100", port=9999):
    print(f"Connecting to Blister Bot at {board_ip}:{port}...")
    
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((board_ip, port))
            print("Connected! Receiving video stream...")
            
            cv2.namedWindow("Blister Bot Live Monitor", cv2.WINDOW_AUTOSIZE)
            
            data = b""
            payload_size = struct.calcsize("<L")
            
            while True:
                while len(data) < payload_size:
                    packet = client.recv(4096)
                    if not packet:
                        break
                    data += packet
                    
                if len(data) < payload_size:
                    break
                    
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("<L", packed_msg_size)[0]
                
                while len(data) < msg_size:
                    data += client.recv(4096)
                    
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    cv2.imshow("Blister Bot Live Monitor", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quitting viewer...")
                        client.close()
                        cv2.destroyAllWindows()
                        return
                        
        except ConnectionRefusedError:
            print("Connection refused. Make sure the board is powered on and running the master controller.")
            time.sleep(3)
        except Exception as e:
            print(f"Connection lost: {e}")
            time.sleep(3)

if __name__ == "__main__":
    ip = input("Enter the board's IP address (leave blank for local testing): ").strip()
    if not ip:
        ip = "127.0.0.1"
    start_viewer(ip)
