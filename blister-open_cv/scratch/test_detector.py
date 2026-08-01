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
output_path = r"c:\Users\hampl\OneDrive\ドキュメント\GitHub\Blister-bot-main-\blister-detector\outputs\test_result.jpg"

image = imread_unicode(input_path)
h_orig, w_orig = image.shape[:2]

# Downscale for fast processing
max_dim = 1000.0
scale = max_dim / max(h_orig, w_orig)
if scale < 1.0:
    proc_img = cv2.resize(image, (int(w_orig * scale), int(h_orig * scale)))
else:
    proc_img = image.copy()
    scale = 1.0

h_proc, w_proc = proc_img.shape[:2]
gray = cv2.cvtColor(proc_img, cv2.COLOR_BGR2GRAY)

# Smooth foil crosshatch pattern
blurred = cv2.medianBlur(gray, 7)

min_dim = min(h_proc, w_proc)
min_dist = int(min_dim * 0.12)
min_radius = int(min_dim * 0.05)
max_radius = int(min_dim * 0.14)

circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=min_dist,
    param1=50,
    param2=26,
    minRadius=min_radius,
    maxRadius=max_radius
)

output_img = image.copy()
detected_count = 0

if circles is not None:
    circles = np.around(circles[0, :]).astype(float)
    for circle in circles:
        # Scale back to original resolution
        cx = int(circle[0] / scale)
        cy = int(circle[1] / scale)
        r = int(circle[2] / scale)

        # Draw strict red circle on original image
        cv2.circle(output_img, (cx, cy), r, (0, 0, 255), max(4, int(6 / scale)))
        # Optional inner center marker or strict outline
        detected_count += 1

print(f"Successfully detected {detected_count} pill boundaries.")
imwrite_unicode(output_path, output_img)
