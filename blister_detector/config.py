import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
CHECKPOINT_DIR = os.path.join(BASE_DIR, 'checkpoints')

# Model configuration
CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, 'sam2.1_hiera_small.pt')
MODEL_CFG = 'configs/sam2.1/sam2.1_hiera_s.yaml'

# Mask Filtering Thresholds
MIN_AREA = 500
MIN_ASPECT_RATIO = 0.3
MAX_ASPECT_RATIO = 3.0
MIN_ELLIPSE_SCORE = 0.55

# Contour rendering
CONTOUR_COLOR = (0, 0, 255) # Red in BGR
CONTOUR_THICKNESS = 2

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
