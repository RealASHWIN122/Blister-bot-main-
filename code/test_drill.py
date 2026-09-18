import cv2
import sys
import os
import socket
import time

# Ensure we can import the blister detector
sys.path.append(os.path.join(os.path.dirname(__file__), 'blister_detector'))
try:
    from detector import get_pill_boundary
except ImportError as e:
    print(f"Error importing detector: {e}")
    sys.exit(1)

# Configuration Parameters
PIXEL_TO_STEP_RATIO = 1.0  # Number of CNC steps per image pixel. Tweak this!
DRY_RUN = False             # Set to False to actually move the motors
CNC_HOST = '127.0.0.1'
CNC_PORT = 7500
DRAG_DELAY = 0.05          # Delay in seconds between boundary steps

# State tracker for absolute CNC position relative to origin (camera center)
current_x_step = 0
current_y_step = 0

def get_mcu_socket():
    if DRY_RUN:
        return None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CNC_HOST, CNC_PORT))
        s.settimeout(5.0)
        return s
    except Exception as e:
        print(f"[!] Error opening CNC socket: {e}")
        return None

def move_axis(axis, steps):
    if steps == 0:
        return True
        
    if DRY_RUN:
        print(f"[DRY-RUN] Move {axis} {steps} steps")
        time.sleep(0.01)
        return True
        
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
            print(f"[!] Timeout waiting for ACK on {axis}")
            return False
        except Exception as e:
            print(f"[!] Error communicating with MCU: {e}")
            if s:
                s.close()
            return False
    else:
        print(f"[ERROR] Could not connect to MCU to move {axis} {steps}")
        return False

def move_to_pixel(px, py, cx, cy):
    """Moves the drill to an absolute pixel coordinate relative to the camera center"""
    global current_x_step, current_y_step
    
    target_x_step = int((px - cx) * PIXEL_TO_STEP_RATIO)
    target_y_step = int((py - cy) * PIXEL_TO_STEP_RATIO)
    
    diff_x = target_x_step - current_x_step
    diff_y = target_y_step - current_y_step
    
    if diff_x != 0: move_axis('X', diff_x)
    if diff_y != 0: move_axis('Y', diff_y)
    
    current_x_step = target_x_step
    current_y_step = target_y_step

def test_drill():
    global current_x_step, current_y_step
    
    print("[1] Opening Camera 1...")
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("[!] Failed to open Camera 1. Trying Camera 0...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[!] Failed to open any camera.")
            return

    # Warm up camera
    for _ in range(10):
        cap.read()
        
    ret, frame = cap.read()
    if not ret:
        print("[!] Failed to capture frame.")
        cap.release()
        return
        
    height, width, _ = frame.shape
    cx, cy = width // 2, height // 2
    print(f"[2] Captured frame ({width}x{height}). Center point: ({cx}, {cy})")
    
    # Save debug image
    cv2.imwrite("debug_capture.jpg", frame)
    
    print("[3] Analyzing for medicine boundaries...")
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Run detector
    try:
        coords_list, contours = get_pill_boundary(image_rgb)
    except Exception as e:
        print(f"[!] Exception during get_pill_boundary: {e}")
        cap.release()
        return
    
    if not contours:
        print("[-] No medicine boundaries detected in view.")
        cap.release()
        return
        
    print(f"[+] Found {len(contours)} potential medicine boundaries.")
    
    # Just take the largest contour for the test
    target_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(target_contour)
    print(f"[+] Selected largest boundary with area: {area}")
    
    # Draw contour on debug image and save
    cv2.drawContours(frame, [target_contour], -1, (0, 255, 0), 2)
    cv2.imwrite("debug_segmented.jpg", frame)
    print("[+] Saved 'debug_segmented.jpg' for verification.")
    
    print("\n--- INITIATING CNC SEQUENCE ---\n")
    
    # Step 1: Retract Z by 2 steps to ensure it is clear
    print("[CNC] Retracting Z-axis by 2 steps")
    move_axis('Z', -2)
    
    # Step 2: Move to the starting point of the boundary contour
    start_pt = target_contour[0][0]
    print(f"[CNC] Moving to start boundary point: ({start_pt[0]}, {start_pt[1]})")
    move_to_pixel(start_pt[0], start_pt[1], cx, cy)
    
    # Step 3: Thrust Z-axis down by 2 steps to pierce
    print("[CNC] Thrusting Z-axis down by 2 steps (PIERCE)")
    time.sleep(0.5)
    move_axis('Z', 2)
    time.sleep(0.5)
    
    # Step 4: Trace the boundary contour
    print(f"[CNC] Tracing boundary ({len(target_contour)} points)...")
    for idx, pt_arr in enumerate(target_contour[1:]):
        pt = pt_arr[0]
        move_to_pixel(pt[0], pt[1], cx, cy)
        time.sleep(DRAG_DELAY)
        
        if idx % 10 == 0:
            print(f"      Tracing... progress {idx}/{len(target_contour)}")
            
    # Step 5: Retract Z-axis by 2 steps to lift the drill
    print("[CNC] Retracting Z-axis by 2 steps (LIFT)")
    move_axis('Z', -2)
    time.sleep(0.5)
    
    # Step 6: Return to origin
    print("[CNC] Returning to origin...")
    move_to_pixel(cx, cy, cx, cy)
    
    print("\n--- CNC SEQUENCE COMPLETE ---\n")
    cap.release()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run live with real motor movements")
    args = parser.parse_args()
    
    if args.live:
        DRY_RUN = False
        print("!!! RUNNING IN LIVE MODE !!!")
    else:
        DRY_RUN = True
        print("--- RUNNING IN DRY-RUN MODE (pass --live to actuate motors) ---")
        
    test_drill()
