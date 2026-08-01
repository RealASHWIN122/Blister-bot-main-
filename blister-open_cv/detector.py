import cv2
import numpy as np
import os


def imread_unicode(path):
    with open(path, "rb") as f:
        chunk = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(chunk, cv2.IMREAD_COLOR)


def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    if not ext:
        ext = ".jpg"
    is_success, buffer = cv2.imencode(ext, img)
    if is_success:
        with open(path, "wb") as f:
            f.write(buffer)


def non_max_suppression(circles, overlap_thresh=0.25):
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

        overlap = (w * h) / (area[idxs[:last]] + 1e-6)
        idxs = np.delete(
            idxs,
            np.concatenate(([last], np.where(overlap > overlap_thresh)[0]))
        )

    return [circles[p] for p in pick]


def detect_blisters(input_path, output_path):
    image = imread_unicode(input_path)
    if image is None:
        return

    h_orig, w_orig = image.shape[:2]

    # Normalize image resolution for consistent spatial detection
    max_dim = 1000.0
    scale = max_dim / float(max(h_orig, w_orig))
    if scale < 1.0:
        proc_img = cv2.resize(image, (int(w_orig * scale), int(h_orig * scale)))
    else:
        proc_img = image.copy()
        scale = 1.0

    h_proc, w_proc = proc_img.shape[:2]
    gray = cv2.cvtColor(proc_img, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(proc_img, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]

    # 1. Packet Masking - Isolate medicine strip from table/background
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)

    # Threshold for packet envelope
    _, packet_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel_pkt = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    packet_mask = cv2.morphologyEx(packet_mask, cv2.MORPH_CLOSE, kernel_pkt)

    contours_pkt, _ = cv2.findContours(packet_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pkt_mask_clean = np.zeros((h_proc, w_proc), dtype=np.uint8)
    if contours_pkt:
        largest_pkt = max(contours_pkt, key=cv2.contourArea)
        # Only use packet mask if it covers a reasonable portion of the frame
        if cv2.contourArea(largest_pkt) > (h_proc * w_proc * 0.15):
            cv2.drawContours(pkt_mask_clean, [largest_pkt], -1, 255, -1)
        else:
            pkt_mask_clean.fill(255)
    else:
        pkt_mask_clean.fill(255)

    # 2. Pill Circle Detection using Median Blur & Hough Circles
    blurred = cv2.medianBlur(l_enhanced, 7)
    min_dim = min(h_proc, w_proc)
    min_dist = int(min_dim * 0.11)
    min_radius = int(min_dim * 0.05)
    max_radius = int(min_dim * 0.12)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min_dist,
        param1=50,
        param2=25,
        minRadius=min_radius,
        maxRadius=max_radius
    )

    valid_circles = []
    if circles is not None:
        for circle in circles[0, :]:
            cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])
            if 0 <= cy < h_proc and 0 <= cx < w_proc:
                # Keep circle if center is within blister packet mask
                if pkt_mask_clean[cy, cx] > 0:
                    valid_circles.append((cx, cy, r))

    # Apply Non-Maximum Suppression to remove duplicate overlaps
    filtered_circles = non_max_suppression(valid_circles, overlap_thresh=0.25)

    output_img = image.copy()
    line_thickness = max(4, int(5.0 / scale))

    # 3. Fallback to Pill Contour Detection if circles are sparse
    if len(filtered_circles) < 3:
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 3
        )
        thresh = cv2.bitwise_and(thresh, thresh, mask=pkt_mask_clean)
        kernel_pill = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_pill, iterations=2)

        contours_pills, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours_pills:
            area = cv2.contourArea(c)
            if (h_proc * w_proc * 0.005) <= area <= (h_proc * w_proc * 0.08):
                perimeter = cv2.arcLength(c, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    if circularity >= 0.4:
                        c_orig = (c / scale).astype(np.int32)
                        cv2.drawContours(output_img, [c_orig], -1, (0, 0, 255), line_thickness)
    else:
        # Draw strict red circular boundaries over detected pills
        for (cx, cy, r) in filtered_circles:
            orig_cx = int(cx / scale)
            orig_cy = int(cy / scale)
            orig_r = int(r / scale)
            cv2.circle(output_img, (orig_cx, orig_cy), orig_r, (0, 0, 255), line_thickness)

    imwrite_unicode(output_path, output_img)
