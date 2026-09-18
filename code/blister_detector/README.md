# Blister Boundary Detection using Segment Anything Model 2 (SAM 2)

This is a Flask web application that allows you to upload an image of a medicine blister pack and detects the individual blisters using Meta's SAM 2. The app draws red contours around the detected boundaries.

## Setup & Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install git+https://github.com/facebookresearch/sam2.git
```

### 2. Download SAM 2 Checkpoint
Download the `sam2_hiera_small.pt` weights and place them in the `checkpoints/` directory:
```bash
mkdir checkpoints
curl -o checkpoints/sam2_hiera_small.pt https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_small.pt
```

*(Note: If the checkpoint is missing, the application will still launch using a computer-vision fallback mode.)*

### 3. Run the Application
```bash
python app.py
```
Then open `http://127.0.0.1:5000` in your web browser.
