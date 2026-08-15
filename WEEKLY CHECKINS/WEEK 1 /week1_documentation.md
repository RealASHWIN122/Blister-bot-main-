# Weekly Progress Report: Blister Boundary Detection

**Project Phase:** Computer Vision & AI Segmentation  
**Week:** 1  

## Overview of Work Accomplished

During this week, the primary objective was to build a robust computer vision system capable of identifying and outlining the individual medicine tablets (domes) on a blister pack. 

The task presented significant challenges using traditional computer vision methods (like OpenCV edge detection and Hough Circles) due to real-world variables such as reflections, text printed on the foil, shadows, and complex backgrounds.

To overcome these challenges, we transitioned to a Deep Learning approach using Meta's state-of-the-art **Segment Anything Model 2.1 (SAM 2.1)**. 

### Key Deliverables:
1. **Flask Web Application**: Built a modular, responsive web interface (`app.py`, `index.html`, `style.css`) allowing users to upload images and instantly visualize the detected boundaries.
2. **SAM 2.1 Integration**: Integrated the official Meta SAM 2.1 AI model to perform pixel-perfect segmentation of the blister pack domes.
3. **Performance Optimization**: 
   - Configured the system to utilize the NVIDIA RTX 3050 GPU (via PyTorch CUDA).
   - Implemented automatic image downscaling (to a max dimension of 1024px) before inference.
   - Reduced the internal SAM grid search points (from 32x32 to 16x16) to ensure detection happens in a fraction of a second.
4. **Robust Boundary Extraction**: Wrote a custom algorithm in `detector.py` that parses SAM 2's generated masks, filters out noise based on area and shape geometry (aspect ratio), and extracts exact `(x, y)` coordinate paths for each blister.

---

## Model Architecture: Meta SAM 2.1

**Model Used**: `sam2.1_hiera_small` (Segment Anything Model 2.1 - Small version)

The Segment Anything Model (SAM) is a foundation model developed by Meta (Facebook AI Research) designed for generalizable image segmentation. Version 2.1 is the latest release, optimized for zero-shot object segmentation.

### Why SAM 2.1?
Traditional edge-detection filters (like Canny) get confused by the text printed on the foil backing of blister packs, treating the letters as physical boundaries. SAM 2.1, being a deep neural network trained on millions of images, understands the semantic difference between flat text and a 3D dome object, allowing it to correctly segment only the physical blister shapes.

### How it works in our pipeline:
1. **Automatic Mask Generation**: We use SAM's `AutomaticMaskGenerator`. It places a 16x16 grid of points across the image and prompts the neural network to predict a segmentation mask for whatever object lies under each point.
2. **Geometric Filtering**: The raw masks are passed through a filter that checks their aspect ratio and area. This eliminates the outer rim of the blister pack or background objects (like the wooden table).
3. **Contour Extraction**: The remaining, isolated pill masks are converted into strict contour coordinate arrays, which are then drawn on the image in red.

---

## Detection Results

The implementation has achieved high accuracy, consistently outlining the exact blister boundaries despite foil reflections and printed text.

### Processed Output
Below is an example of the SAM 2.1 model perfectly segmenting the 15 tablet domes from the background and the foil text:

![Blister Detection Result](./sample_result.jpg)

*(The red lines indicate the exact boundaries detected by the AI. These coordinates are now mathematically stored in memory and are ready to be passed to a robotic cutter in the next phase of the project.)*
