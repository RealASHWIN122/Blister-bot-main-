import streamlit as st
import cv2
import socket
import numpy as np
import time

st.set_page_config(page_title="AI Medication Tracker", page_icon="💊", layout="wide")

st.title("🤖 Edge Impulse AI Action Tracker")
st.markdown("This Streamlit app captures video from your laptop camera, sends it to your **UNO Q** board for inference, and displays the AI's label in real-time.")

# Sidebar configuration
st.sidebar.header("Configuration")
server_ip = st.sidebar.text_input("UNO Q IP Address", value="127.0.0.1")
server_port = st.sidebar.number_input("UNO Q Port", value=9999, step=1)
start_button = st.sidebar.button("Start Camera & AI Analysis")
stop_button = st.sidebar.button("Stop")

st.sidebar.markdown("---")
st.sidebar.markdown("**Instructions:**\n1. Run `./deploy_model_server.sh` first to start the server on your UNO Q.\n2. Enter the UNO Q's IP address above.\n3. Click Start.")

# Main area
video_placeholder = st.empty()
status_placeholder = st.empty()

# Model input dimensions (from model_metadata.h)
MODEL_WIDTH = 96
MODEL_HEIGHT = 96
FRAME_BYTES = MODEL_WIDTH * MODEL_HEIGHT * 3

if "run_camera" not in st.session_state:
    st.session_state.run_camera = False

if start_button:
    st.session_state.run_camera = True
if stop_button:
    st.session_state.run_camera = False

if st.session_state.run_camera:
    # 1. Connect to the UNO Q Server
    status_placeholder.info(f"Connecting to UNO Q at {server_ip}:{server_port}...")
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(2.0)
        client_socket.connect((server_ip, server_port))
        client_socket.settimeout(None) # Remove timeout for continuous streaming
        status_placeholder.success("Connected to UNO Q AI Server!")
    except Exception as e:
        status_placeholder.error(f"Failed to connect to the board. Is the C++ server running?\nError: {e}")
        st.stop()

    # 2. Open Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        status_placeholder.error("Could not open laptop webcam.")
        st.stop()

    # 3. Continuous Video Loop
    while st.session_state.run_camera:
        ret, frame = cap.read()
        if not ret:
            status_placeholder.error("Failed to grab frame from camera.")
            break
            
        # Pre-process for Edge Impulse: Resize and convert to RGB
        resized_frame = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Get raw bytes
        frame_bytes = rgb_frame.tobytes()
        
        try:
            # Send exactly 27,648 bytes (96*96*3) to the board
            client_socket.sendall(frame_bytes)
            
            # Read the response (Label:Confidence\n)
            response = b""
            while True:
                char = client_socket.recv(1)
                if not char or char == b'\n':
                    break
                response += char
                
            response_text = response.decode('utf-8').strip()
            
            # Format the output on the frame
            cv2.putText(frame, f"AI: {response_text}", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                        
        except Exception as e:
            status_placeholder.error(f"Connection lost during streaming: {e}")
            break
            
        # Display the frame in Streamlit (convert BGR back to RGB for Streamlit image rendering)
        frame_rgb_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb_display, channels="RGB", use_container_width=True)
        
        # Tiny sleep to yield CPU
        time.sleep(0.01)
        
    # Cleanup
    cap.release()
    client_socket.close()
    video_placeholder.empty()
    status_placeholder.warning("Camera stopped.")
