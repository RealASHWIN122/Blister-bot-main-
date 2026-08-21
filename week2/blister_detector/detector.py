import cv2
import numpy as np
import os
from config import MIN_AREA, MIN_ASPECT_RATIO, MAX_ASPECT_RATIO, MIN_ELLIPSE_SCORE, CONTOUR_COLOR, CONTOUR_THICKNESS
import predictor

def imread_unicode(path):
    stream = open(path, "rb")
    bytes_arr = bytearray(stream.read())
    np_array = np.asarray(bytes_arr, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image

def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    result, n = cv2.imencode(ext, img)
    if result:
        with open(path, mode='wb') as f:
            n.tofile(f)

def detect_blisters(input_path, output_path) -> list:
    image = imread_unicode(input_path)
    if image is None:
        raise ValueError(f"Could not read image at {input_path}")
        
    # Resize image if too large (massively speeds up inference on CPU)
    max_dim = 1024
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h))
        
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    masks_data = predictor.get_masks(image_rgb)
    
    detected_contours = []
    
    for mask_dict in masks_data:
        seg = mask_dict['segmentation']
        
        # Convert bool mask to uint8
        mask_uint8 = (seg * 255).astype(np.uint8)
        
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MIN_AREA:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            if not (MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO):
                continue
                
            # Ellipse score check (if applicable)
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (ex, ey), (ew, eh), angle = ellipse
                ellipse_area = np.pi * (ew / 2) * (eh / 2)
                if ellipse_area > 0:
                    area_ratio = min(area, ellipse_area) / max(area, ellipse_area)
                    if area_ratio < MIN_ELLIPSE_SCORE:
                        continue
                        
            # It's a valid blister
            detected_contours.append(contour)
            
    # Draw contours
    result_image = image.copy()
    cv2.drawContours(result_image, detected_contours, -1, CONTOUR_COLOR, CONTOUR_THICKNESS)
    
    imwrite_unicode(output_path, result_image)
    
    # Extract coordinate lists
    coords_list = []
    for contour in detected_contours:
        # contour shape is (N, 1, 2)
        pts = [(int(pt[0][0]), int(pt[0][1])) for pt in contour]
        coords_list.append(pts)
        
    return coords_list
