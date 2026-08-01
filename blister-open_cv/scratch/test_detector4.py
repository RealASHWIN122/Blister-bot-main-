import cv2
import numpy as np
import os

def imread_unicode(path):
    with open(path, "rb") as f:
        chunk = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(chunk, cv2.IMREAD_COLOR)

def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    is_success, buffer = cv2.imencode(ext, img)
    if is_success:
        with open(path, "wb") as f:
            f.write(buffer)

input_path = r"c:\Users\hampl\OneDrive\ドキュメント\GitHub\Blister-bot-main-\blister-detector\uploads\IMG_20260801_230115.jpg"
output_path = r"c:\Users\hampl\OneDrive\ドキュメント\GitHub\Blister-bot-main-\blister-detector\outputs\test_result4.jpg"

image = imread_unicode(input_path)
h_orig, w_orig = image.shape[:2]

# Downscale for processing
max_dim = 1000.0
scale = max_dim / max(h_orig, w_orig)
proc_img = cv2.resize(image, (int(w_orig * scale), int(h_orig * scale)))
h_proc, w_proc = proc_img.shape[:2]

# 1. Packet Segmentation using LAB / HSV Color Contrast
hsv = cv2.cvtColor(proc_img, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(proc_img, cv2.COLOR_BGR2GRAY)

# Blue/Cyan foil mask in HSV
lower_blue = np.array([80, 40, 40])
upper_blue = np.array([130, 255, 255])
packet_mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Morphological close & open to fill holes inside the packet
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
packet_mask = cv2.morphologyEx(packet_mask, cv2.MORPH_CLOSE, kernel)
packet_mask = cv2.morphologyEx(packet_mask, cv2.MORPH_OPEN, kernel)

# If color mask didn't catch enough area (e.g. silver foil), fallback to Canny envelope
if cv2.countNonZero(packet_mask) < (h_proc * w_proc * 0.05):
    edges_pkt = cv2.Canny(gray, 30, 100)
    edges_pkt = cv2.dilate(edges_pkt, kernel, iterations=3)
    contours_pkt, _ = cv2.findContours(edges_pkt, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours_pkt:
        largest = max(contours_pkt, key=cv2.contourArea)
        cv2.drawContours(packet_mask, [largest], -1, 255, -1)

# Find clean packet contour
contours_pkt, _ = cv2.findContours(packet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pkt_contour = None
if contours_pkt:
    pkt_contour = max(contours_pkt, key=cv2.contourArea)
    packet_area = cv2.contourArea(pkt_contour)

# Masked image (only the blister pack)
masked_gray = cv2.bitwise_and(gray, gray, mask=packet_mask)

# 2. Extract Pill Outlines using Adaptive Threshold & Contour Filtering
# Smooth small textures
blurred = cv2.bilateralFilter(masked_gray, 9, 75, 75)

# Multi-threshold detection (combining adaptive thresholding and gradient edges)
thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, -2
)
thresh = cv2.bitwise_and(thresh, thresh, mask=packet_mask)

# Morphological clean up to get clean pill blobs
ellipse_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, ellipse_kernel, iterations=2)
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, ellipse_kernel, iterations=2)

contours_pills, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

output_img = image.copy()
detected_pills = []

# Packet area for relative scaling
ref_area = packet_area if pkt_contour is not None else (h_proc * w_proc * 0.3)
min_pill_area = ref_area * 0.015
max_pill_area = ref_area * 0.09

for c in contours_pills:
    area = cv2.contourArea(c)
    if min_pill_area <= area <= max_pill_area:
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter * perimeter))
        
        # Check aspect ratio
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h
        
        if 0.45 <= circularity <= 1.4 and 0.6 <= aspect_ratio <= 1.5:
            # Scale contour back to original image size
            c_orig = (c / scale).astype(np.int32)
            detected_pills.append(c_orig)

# Draw strict red outlines on the original image
for c_orig in detected_pills:
    # Option A: Draw exact contour boundary
    # cv2.drawContours(output_img, [c_orig], -1, (0, 0, 255), 5)
    
    # Option B: Draw strict minimum enclosing circle or ellipse around pill
    (x, y), radius = cv2.minEnclosingCircle(c_orig)
    center = (int(x), int(y))
    cv2.circle(output_img, center, int(radius), (0, 0, 255), max(4, int(5 / scale)))

print(f"Detected {len(detected_pills)} pill contours inside blister pack.")
imwrite_unicode(output_path, output_img)
