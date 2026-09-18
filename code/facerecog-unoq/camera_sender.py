import cv2
import socket
import struct
import numpy as np
import time
import threading

def start_client(host='127.0.0.1', port=9999):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open laptop webcam.")
        return

    print(f"Waiting for UNO Q server on {host}:{port}...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            client_socket.connect((host, port))
            print("Connected to UNO Q!")
            break
        except ConnectionRefusedError:
            time.sleep(1)

    print("Streaming camera feed to UNO Q. Press 'q' in the window to quit.")
    print("WARNING: Check the UNO Q terminal (Terminal 1) for AI messages and prompts!")

    def recvall(sock, count):
        buf = b''
        while count:
            try:
                newbuf = sock.recv(count)
                if not newbuf: return None
                buf += newbuf
                count -= len(newbuf)
            except:
                return None
        return buf

    # Shared variables
    latest_raw_frame = None
    latest_processed_frame = None
    running = True

    # --- RECEIVER THREAD ---
    def receive_thread():
        nonlocal latest_processed_frame, running
        while running:
            lengthbuf = recvall(client_socket, 4)
            if not lengthbuf: break
            size = struct.unpack('<L', lengthbuf)[0]
            
            frame_data = recvall(client_socket, size)
            if not frame_data: break
            
            processed_frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if processed_frame is not None:
                latest_processed_frame = processed_frame

    # --- SENDER THREAD ---
    def send_thread():
        nonlocal latest_raw_frame, running
        while running:
            if latest_raw_frame is not None:
                # Make a copy of the reference so we don't hold up the camera thread
                frame_to_send = latest_raw_frame
                
                try:
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                    _, encoded_frame = cv2.imencode('.jpg', frame_to_send, encode_param)
                    data = encoded_frame.tobytes()
                    # sendall will block here if the server's receive buffer is full (e.g. waiting for input)
                    client_socket.sendall(struct.pack("<L", len(data)) + data)
                except Exception as e:
                    print(f"Failed to send frame: {e}")
                    running = False
                    break
            
            # Tiny sleep to avoid 100% CPU lock when grabbing frames
            time.sleep(0.03)

    t_recv = threading.Thread(target=receive_thread, daemon=True)
    t_send = threading.Thread(target=send_thread, daemon=True)
    t_recv.start()
    t_send.start()

    # --- MAIN UI THREAD ---
    try:
        while running:
            ret, frame = cap.read()
            if not ret:
                break
                
            latest_raw_frame = frame
            
            cv2.imshow('Raw Laptop Camera', frame)
            if latest_processed_frame is not None:
                cv2.imshow('UNO Q Processed Feed', latest_processed_frame)
                
            if cv2.waitKey(30) & 0xFF == ord('q'):
                running = False
                break

    except Exception as e:
        print(f"Connection lost: {e}")
    finally:
        running = False
        cap.release()
        try:
            client_socket.close()
        except:
            pass
        cv2.destroyAllWindows()

if __name__ == "__main__":
    start_client()
