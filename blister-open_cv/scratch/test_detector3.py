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

def non_max_suppression(circles, overlap_thresh=0.3):
    if len(circles) == 0:
        return []

    boxes = []
    for (x, y, r) in circles:
        boxes.append([x - r, y - r, x + r, y + r, r])

    boxes = np.array(boxes, dtype=float)
    pick = []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    r = boxes[:, 4]

    area = (x2 - x1) * (y2 - y1)
    idxs = np.argsort(r)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)

        overlap = (w * h) / area[idxs[:last]]
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

    return [circles[p] for p in pick]

input_path = r"c:\Users\hampl\OneDrive\ドキュメント\GitHub\Blister-bot-main-\blister-detector\uploads\IMG_20260801_230115.jpg"
output_path = r"c:\Users\hampl\OneDrive\ドキュメント\GitHub\Blister-bot-main-\blister-detector\outputs\test_result3.jpg"

image = imread_unicode(input_path)
h_orig, w_orig = image.shape[:2]

# Standardize resolution for processing
max_dim = 1000.0
scale = max_dim / max(h_orig, w_orig)
proc_img = cv2.resize(image, (int(w_orig * scale), int(h_orig * scale)))
h_proc, w_proc = proc_img.shape[:2]

# 1. Packet Masking
gray = cv2.cvtColor(proc_img, cv2.COLOR_BGR2GRAY)
lab = cv2.cvtColor(proc_img, cv2.COLOR_BGR2LAB)
l_channel, a_channel, b_channel = cv2.split(lab)

# CLAHE (Contrast Limited Adaptive Histogram Equalization) on L-channel
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
l_enhanced = clahe.apply(l_channel)

# Blur to remove foil crosshatch pattern
blurred = cv2.medianBlur(l_enhanced, 7)

# Find packet region mask
_, packet_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
kernel_pkt = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
packet_mask = cv2.morphologyEx(packet_mask, cv2.MORPH_CLOSE, kernel_pkt)

contours_pkt, _ = cv2.findContours(packet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pkt_mask_clean = np.zeros((h_proc, w_proc), dtype=np.uint8)
if contours_pkt:
    largest_pkt = max(contours_pkt, key=cv2.contourArea)
    cv2.drawContours(pkt_mask_clean, [largest_pkt], -1, 255, -1)

# 2. Pill Detection via Hough Circles with tuned parameters
min_dim = min(h_proc, w_proc)
min_dist = int(min_dim * 0.12)
min_radius = int(min_dim * 0.055)
max_radius = int(min_dim * 0.11)

circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=min_dist,
    param1=50,
    param2=22,
    minRadius=min_radius,
    maxRadius=max_radius
)

valid_circles = []
if circles is not None:
    for circle in circles[0, :]:
        cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])
        if 0 <= cy < h_proc and 0 <= cx < w_proc:
            # Must be inside blister packet
            if pkt_mask_clean[cy, cx] > 0 or cv2.countNonZero(pkt_mask_clean) == 0:
                valid_circles.append((cx, cy, r))

filtered_circles = non_max_suppression(valid_circles, overlap_thresh=0.2)

output_img = image.copy()
for (cx, cy, r) in filtered_circles:
    orig_cx = int(cx / scale)
    orig_cy = int(cy / scale)
    orig_r = int(r / scale)
    # Draw strict red boundary circle around pill cavity
    cv2.circle(output_img, (orig_cx, orig_cy), orig_r, (0, 0, 255), max(4, int(5 / scale)))

print(f"Detected {len(filtered_circles)} pills with strict boundaries.")
imwrite_unicode(output_path, output_img)
