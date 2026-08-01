# Week 1 Documentation: Intelligent Edge-AI Medicine Dispenser ("Blister Bot")

## 1. Executive Summary & Project Vision

The **Intelligent Edge-AI Medicine Dispenser ("Blister Bot")** is an autonomous, fully offline healthcare system. Unlike conventional pill organizers that require tedious manual sorting or cloud connectivity, Blister Bot operates as an intelligent healthcare assistant. It directly interprets written prescriptions via computer vision (OCR), converses naturally with patients via a localized Large Language Model (LLM), prevents accidental overdoses, and **mechanically extracts medications directly from uncut aluminum blister strips**.

---

## 2. Hardware Architecture & Technical Specifications

The system is built upon the dual-processor architecture of the **Arduino UNO Q** (Qualcomm Dragonwing QRB2210 + STM32U585 MCU):

| Subsystem Component | Hardware / Software | Primary Responsibilities |
| :--- | :--- | :--- |
| **Linux MPU** | Qualcomm Dragonwing QRB2210 | Localized LLM (`llama.cpp` + `TinyLlama`), Voice STT (`Whisper.cpp`), Prescription OCR, Face Recognition, Action Tracking (`MediaPipe`), Database management. |
| **Microcontroller (MCU)** | STM32U585 MCU | Real-time 2-axis CNC gantry motor control (`AccelStepper`), sensor monitoring, safety interlocks, and closed-loop dispensing verification. |
| **Smart Interface** | 7" Portrait TFT/LCD Touchscreen | Displays pill schedules, visual dosage cross-checks, consumption graphs, and system telemetry. |
| **Vision Sensor** | Integrated HD Camera Module | Patient face recognition authentication, pill identification, prescription scanning, and hand-to-mouth action verification. |

---

## 3. Visual Reference Breakdown (From Video Reference)

Analysis of the reference video (`WhatsApp Video 2026-07-20 at 10.29.20 PM.mp4`) revealed the core architectural and mechanical design parameters:

````carousel
![Reference Frame 002: Dual Chamber & Smart Touch Display](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/frames/frame_002.jpg)
<!-- slide -->
![Reference Frame 005: Internal Deblistering CNC Gantry & U-Scoring](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/frames/frame_005.jpg)
<!-- slide -->
![Reference Frame 008: Appliance Presentation Overview](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/frames/frame_008.jpg)
````

### Key Design Insights Extracted:
1. **Dual-Chamber Enclosure**: Left side houses illuminated internal mechanical components behind a transparent acrylic door; right side features the smart touch interface, AI camera, and dispensing tray.
2. **2-Axis CNC Deblistering Gantry**: Precision X/Y motion system carrying a specialized toolhead with a motorized 270-degree rotary cutter wheel and soft silicone plunger.
3. **U-Shaped Scoring Mechanics**: Rather than high-force punching which damages fragile tablets, the tool scores a 270-degree hinged flap in the aluminum foil backing, allowing a soft plunger to push the pill into the chute.

---

## 4. Week 1 3D Model Development & Blender Implementation

A complete, fully detailed 3D model of Blister Bot was procedurally created in **Blender 5.2 LTS** using a Python script (`create_blister_bot_model.py`).

### 3D Render Gallery

```carousel
![3D Render: Isometric Perspective Studio View](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/renders/render_perspective.png)
<!-- slide -->
![3D Render: Deblistering Mechanism Close-Up](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/renders/render_mechanism.png)
<!-- slide -->
![3D Render: Front Presentation View](file:///c:/FARIS/Blister%20Bot/Blister-bot-main-/Week%201/renders/render_front.png)
```

---

## 5. Summary of Built Components in 3D Model

1. **Appliance Body**:
   - Curved-corner desktop enclosure in matte white ABS plastic with dark metallic accents.
   - Hollowed-out left cavity equipped with warm top LED light strip (`Mat_LED_Warm`) and cyan vertical status light bar (`Mat_LED_Cyan`).
   - Beveled acrylic transparent front window door with metallic handle.

2. **Smart Touch Display & Vision Module**:
   - 7" portrait display screen with customized UI overlay (header bar, blister schedule card, action button).
   - Top camera module housing with optical ring and glass lens.
   - Lower RGB LED status indicator bar and sliding pill collection drawer.

3. **Core Deblistering Mechanics**:
   - **Blister Pack Rack**: Multi-slot holder containing aluminum foil cards, transparent PVC bubble pockets, and dual-tone blue/white capsules (`Mat_Pill_Blue`, `Mat_Pill_White`).
   - **2-Axis CNC Gantry**: Upper/lower X aluminum extrusions, vertical Y lead screw, guide rod, and dual NEMA 17 stepper motors (`Mat_Stepper_Body`).
   - **Scoring & Plunger Toolhead**: Motorized rotary steel cutter disc and spring-loaded silicone plunger pin positioned above the funneled delivery chute.

---

## 6. Week 1 Deliverables & File Directory Structure

All files created during Week 1 are organized cleanly in the `Week 1` directory:

```
c:/FARIS/Blister Bot/Blister-bot-main-/
├── LICENSE
├── README.md
└── Week 1/
    ├── Project Blueprint.pdf          # Full technical requirements specification
    ├── WhatsApp Video 2026-07-20...   # Video reference file
    ├── blueprint_text.txt             # Extracted text from PDF blueprint
    ├── create_blister_bot_model.py    # Python procedural 3D model generator for Blender 5.2
    ├── blister_bot.blend              # Native Blender 3D project model file
    ├── Week1_Documentation.md         # Comprehensive documentation report
    ├── frames/                        # Extracted reference frames (frame_000.jpg - frame_009.jpg)
    └── renders/                       # High-resolution rendered 3D preview images
        ├── render_perspective.png
        ├── render_mechanism.png
        └── render_front.png
```

---

## 7. Next Steps & Week 2 Roadmap

1. **Kinematic Animation in Blender**: Animate the 2-axis gantry movement, rotary cutter U-scoring path, and plunger ejection sequence.
2. **CAD Model Refinement**: Export 3D components to STL/STEP formats for parametric 3D printing tolerance checks.
3. **App Lab Firmware Integration**: Prototype basic STM32 C++ motor sketches using `AccelStepper` and Python RPC state machine logic.
