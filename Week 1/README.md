# Week 1: Intelligent Edge-AI Medicine Dispenser ("Blister Bot")

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Blender 5.2](https://img.shields.io/badge/Blender-5.2_LTS-E87D0D?style=for-the-badge&logo=blender&logoColor=white)](https://blender.org)
[![Three.js WebGL](https://img.shields.io/badge/Three.js-WebGL-000000?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org)
[![Arduino UNO Q](https://img.shields.io/badge/Arduino-UNO_Q_STM32-00979D?style=for-the-badge&logo=arduino&logoColor=white)](https://arduino.cc)

Welcome to the **Week 1** repository module for **Blister Bot** (Intelligent Edge-AI Medicine Dispenser). This directory contains all technical specifications, 3D CAD/Blender models, interactive WebGL 3D web applications, MP4 video animation demonstrations, Python vision mappers, C++ STM32 MCU firmware sketches, and publication-ready PDF documentation reports generated during Week 1.

---

## 📌 Executive Project Summary

**Blister Bot** is an autonomous, fully offline healthcare dispenser. Unlike conventional pill organizers that require manual sorting into plastic compartments or cloud dependence, Blister Bot operates as an edge-AI healthcare assistant built on the dual-processor **Arduino UNO Q** board (Qualcomm Dragonwing QRB2210 Linux MPU + STM32U585 MCU).

### Core Innovation: Non-Destructive Deblistering
Rather than high-force mechanical punching that crushes fragile pills, Blister Bot utilizes a two-stage mechanism:
1. **270-Degree U-Shaped Foil Scoring**: A motorized rotary cutter wheel scores a 270° U-shaped arc through the aluminum foil backing, creating a hinged flap while leaving the top 90° edge connected.
2. **Soft Silicone Plunger Pin Ejection**: A spring-loaded silicone plunger pin gently pushes against the transparent front PVC bubble, guiding the capsule tablet out through the pre-scored flap into the delivery chute.

---

## 📂 Week 1 File Navigation & Directory Structure

```
Week 1/
├── README.md                             # Navigation guide for GitHub repository (this file)
├── Project Blueprint.pdf                 # Original technical specification document
├── blueprint_text.txt                    # Plaintext extraction of Project Blueprint PDF
├── Week1_Documentation.md               # Main Week 1 technical markdown documentation
├── Week1_Documentation.pdf               # Publication-ready PDF documentation report (2.98 MB)
├── generate_pdf_report.py                # Python script to compile Week1_Documentation.pdf
│
├── blister_bot.blend                     # Native 3D Blender model file for complete Blister Bot
├── create_blister_bot_model.py           # Blender Python script generating full 3D appliance & renders
│
├── frames/                               # Extracted visual reference frames from reference video
│   ├── frame_000.jpg ... frame_009.jpg
│
├── renders/                              # High-resolution rendered 3D preview images
│   ├── render_perspective.png            # Studio isometric view
│   ├── render_mechanism.png              # Internal 2-axis CNC gantry close-up
│   └── render_front.png                  # Front presentation view
│
├── scoring mechanism/                    # Horizontal Scoring & Ejection Mechanism Module
│   ├── 3d_cutting_animation.html         # Interactive 3D WebGL (Three.js) animation web app
│   ├── scoring_mechanism_demo.mp4        # 120-frame MP4 video animation demonstration
│   ├── scoring_mechanism.blend           # Specialized Blender 3D kinematic model file
│   ├── Scoring_Mechanism_Report.pdf      # Dedicated PDF technical report (4.61 MB)
│   ├── Scoring_Mechanism_DeepDive.md     # Markdown technical deep-dive report
│   ├── deblister_vision_mapper.py        # Python front-to-back coordinate transformation & U-trajectory mapper
│   ├── scoring_gantry_controller.ino     # STM32 C++ firmware sketch for 2-axis CNC stepper & plunger
│   ├── animate_scoring_mechanism.py      # Blender Python animation generator
│   ├── compile_scoring_video.py          # Blender PNG frame renderer
│   ├── encode_mp4.py                     # OpenCV MP4 video encoder
│   ├── scoring_toolhead.png              # Still render preview (Step 1)
│   ├── u_flap_scored.png                 # Still render preview (Step 2)
│   └── tablet_ejection.png               # Still render preview (Step 3)
│
└── vertical scoring mechanism/           # Vertical Strip Plunger Ejection Mechanism Module
    ├── vertical_strip_plunger_animation.html # Interactive 3D WebGL (Three.js) animation web app
    ├── vertical_strip_ejection_demo.mp4   # 120-frame MP4 video animation demonstration
    ├── vertical_scoring_mechanism.blend   # Specialized Blender 3D model file (vertical strip orientation)
    ├── Vertical_Scoring_Report.pdf        # Dedicated PDF technical report (1.79 MB)
    ├── animate_vertical_scoring.py        # Blender Python animation generator
    ├── encode_vertical_mp4.py             # OpenCV MP4 video encoder
    ├── generate_vertical_pdf.py           # Python script compiling Vertical_Scoring_Report.pdf
    ├── vertical_strip_toolhead.png        # Still render preview (Phase 1)
    ├── vertical_u_flap.png               # Still render preview (Phase 3)
    └── vertical_plunger_eject.png         # Still render preview (Phase 5)
```

---

## 🚀 Key Modules & How to Use Them

### 1. Interactive 3D WebGL Web Applications (No Blender Required!)
Experience realistic 3D animations directly inside any web browser with orbit controls, step-by-step kinematic phase controls, X-Ray mode, and live telemetry:

- **Horizontal Scoring App**: Open `scoring mechanism/3d_cutting_animation.html` in your web browser.
- **Vertical Strip Plunger App**: Open `vertical scoring mechanism/vertical_strip_plunger_animation.html` in your web browser.

### 2. Video Demonstrations (MP4 Renders)
- **Horizontal Scoring Demo**: `scoring mechanism/scoring_mechanism_demo.mp4`
- **Vertical Strip Plunger Demo**: `vertical scoring mechanism/vertical_strip_ejection_demo.mp4`

### 3. PDF Documentation Reports
- **Week 1 Master Report**: `Week1_Documentation.pdf` (2.98 MB)
- **Horizontal Mechanism Deep-Dive**: `scoring mechanism/Scoring_Mechanism_Report.pdf` (4.61 MB)
- **Vertical Mechanism Deep-Dive**: `vertical scoring mechanism/Vertical_Scoring_Report.pdf` (1.79 MB)

### 4. Software & Firmware Source Code
- **Python Vision Coordinate Mapper**: `scoring mechanism/deblister_vision_mapper.py`  
  *Transforms camera pixel coordinates \((X_{\text{pixel}}, Y_{\text{pixel}})\) to rear aluminum foil gantry space \((X_{\text{gantry}}, Y_{\text{gantry}})\) and calculates 270° U-trajectory waypoints with dynamic safety clearance buffers (\(R_{\text{cut}} = R_{\text{pill}} + 2.0\text{mm}\)).*
- **STM32 Microcontroller Firmware**: `scoring mechanism/scoring_gantry_controller.ino`  
  *Arduino C++ sketch driving X/Y stepper motors smoothly via `AccelStepper`, engaging the rotary cutter wheel solenoid, actuating the silicone plunger pin, and verifying tablet drop via IR optic sensors.*

### 5. Blender 3D CAD & Kinematic Models
To open or re-render 3D models in Blender 5.2 LTS:
```bash
# Re-create and render full Blister Bot appliance model
blender --background --python create_blister_bot_model.py

# Re-create and render horizontal scoring mechanism
blender --background --python "scoring mechanism/compile_scoring_video.py"

# Re-create and render vertical strip mechanism
blender --background --python "vertical scoring mechanism/animate_vertical_scoring.py"
```

---

## 🛠️ Technology Stack & Dependencies

| Tool / Library | Version / Domain | Purpose |
| :--- | :--- | :--- |
| **Blender** | 5.2.0 LTS | 3D CAD modeling, PBR shading, studio lighting, camera tracking, and animation. |
| **Three.js** | r128 (WebGL) | Interactive 3D web application rendering, PBR materials, orbit controls, spark effects. |
| **Python** | 3.13 | Vision mapping mathematics, coordinate transformation, OpenCV video encoding, PDF report building. |
| **OpenCV (`cv2`)** | 4.x | Video frame sequence assembly and MP4 encoding. |
| **ReportLab** | 5.0.0 | Programmatic PDF document compilation with custom styling, tables, and images. |
| **Arduino C++** | STM32 Core | Real-time non-blocking stepper motor control (`AccelStepper.h`) and solenoid actuation. |

---

## 📄 License & Attribution

This project is part of the **Blister Bot** open-hardware healthcare initiative. All 3D models, code, firmware sketches, and documentation in this folder are prepared for open community research and development.
