import os
import torch
import numpy as np
import logging

from config import CHECKPOINT_PATH, MODEL_CFG

logger = logging.getLogger(__name__)

class SAM2PredictorWrapper:
    def __init__(self):
        self.model = None
        self.mask_generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam2_available = False

    def load_model(self):
        # Check if SAM2 is installed and checkpoint exists
        try:
            import sam2
            from sam2.build_sam import build_sam2
            from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
        except ImportError:
            logger.warning("SAM2 package not found. Using fallback mode.")
            return

        if not os.path.exists(CHECKPOINT_PATH):
            logger.warning(f"SAM2 checkpoint not found at {CHECKPOINT_PATH}. Using fallback mode.")
            return

        try:
            logger.info("Loading SAM2 model...")
            self.model = build_sam2(MODEL_CFG, CHECKPOINT_PATH, device=self.device)
            self.mask_generator = SAM2AutomaticMaskGenerator(
                model=self.model,
                points_per_side=16,
                points_per_batch=16
            )
            self.sam2_available = True
            logger.info("SAM2 model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading SAM2 model: {e}")
            self.sam2_available = False

    def predict_masks(self, image_rgb):
        if self.sam2_available and self.mask_generator:
            return self.mask_generator.generate(image_rgb)
        else:
            return self._fallback_predict(image_rgb)

    def _fallback_predict(self, image_rgb):
        import cv2
        from config import MIN_AREA, MIN_ASPECT_RATIO, MAX_ASPECT_RATIO
        # A simple fallback segmenter so app.py doesn't break
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        blurred = cv2.GaussianBlur(enhanced, (9, 9), 2)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 15, 5
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        masks = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MIN_AREA:
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            if not (MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO):
                continue

            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            masks.append({
                'segmentation': mask > 0,
                'area': area,
                'bbox': (x, y, w, h)
            })
            
        return masks

predictor_instance = SAM2PredictorWrapper()

def init_model():
    predictor_instance.load_model()

def get_masks(image_rgb):
    return predictor_instance.predict_masks(image_rgb)
