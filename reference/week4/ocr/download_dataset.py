import os
import cv2
import numpy as np

def generate_sample_images():
    """
    Generates synthetic blister pack images with text for OCR benchmarking.
    This avoids internet connectivity issues or rate limits (429/403).
    """
    save_dir = os.path.join(os.path.dirname(__file__), "test_images")
    os.makedirs(save_dir, exist_ok=True)
    
    samples = [
        {"name": "sample_blister_1.jpg", "text1": "PARACETAMOL 500mg", "text2": "EXP 11/2026", "bg": (200, 200, 200)},
        {"name": "sample_blister_2.jpg", "text1": "IBUPROFEN 200 mg", "text2": "EXP: 05/2025", "bg": (180, 190, 210)},
        {"name": "sample_blister_3.jpg", "text1": "AMOXICILLIN 250mg", "text2": "expiry 12-2024", "bg": (220, 220, 220)}
    ]
    
    for sample in samples:
        filepath = os.path.join(save_dir, sample["name"])
        
        # Create a background image
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:] = sample["bg"]
        
        # Add some noise to simulate a shiny foil texture
        noise = np.random.normal(0, 15, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        # Add text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, sample["text1"], (50, 150), font, 1.2, (30, 30, 30), 3, cv2.LINE_AA)
        cv2.putText(img, sample["text2"], (50, 250), font, 1.2, (30, 30, 30), 3, cv2.LINE_AA)
        
        # Save image
        cv2.imwrite(filepath, img)
        print(f"✅ Generated {filepath}")

if __name__ == "__main__":
    generate_sample_images()
