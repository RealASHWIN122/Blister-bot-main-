# Blister Bot: Exhaustive Engineering Specification & Master Document

## 1. Executive Summary & Core Philosophy
The **Blister Bot** is a prototype DIY mechatronic automated medicine dispenser designed for in-home patient care, assisted living, and nursing facilities. 

Unlike traditional smart pillboxes that require caregivers or patients to manually strip pills out of packaging and pre-sort them into daily plastic compartments, the Blister Bot dispenses medication *directly* from the manufacturer's original foil/plastic blister packs. It achieves this using a Cartesian CNC gantry paired with a rotational indexing wheel.

**The Local Edge Mandate:** To ensure 100% HIPAA compliance, patient privacy, and zero-latency mechanical control (impervious to cloud outages or intermittent Wi-Fi), the system strictly utilizes Local Edge AI. No third-party cloud APIs (such as OpenAI or Google Cloud) are used in production. The machine listens, thinks, sees, and actuates entirely offline on embedded hardware.

---

## 2. Core Processing & Power Architecture

### 2.1 The "Brain & Brawn": Arduino Uno Q
The system bypasses the traditional "Raspberry Pi + separate Arduino" dual-board stack by using the **Arduino Uno Q**, a hybrid Single-Board Computer (SBC) featuring an asymmetric multi-processing architecture:
*   **The AI Brain (Linux Host):** Powered by a Qualcomm Dragonwing QRB2210 (Quad-core Arm Cortex-A53 @ 2.0 GHz) with an Adreno GPU and 4GB of LPDDR4 RAM. It runs a full Debian Linux OS, hosting the local Python server, SQLite databases, computer vision models, and heavy AI inference runtimes.
*   **The Motor Brawn (Real-Time MCU):** An integrated ST STM32U585 (Arm Cortex-M33) microcontroller handles deterministic, low-level GPIO timing and pulse-generation for stepper motors without Linux kernel scheduling jitter.

### 2.2 Split-Brain Power Isolation & Direct L293D Driver Architecture
Stepper motors draw substantial current and produce inductive back-EMF voltage spikes that can disrupt sensitive logic boards or trigger sudden brownouts. Instead of using an external LM2596 buck converter, the system employs **three dedicated L293D dual H-bridge motor drivers** (one driver per motor for the 3 stepper motors):
*   **Logic Power:** The Arduino Uno Q is powered safely on its own separated 5.0V circuit via USB-C.
*   **Direct Motor Power:** Motor power connects directly to the motor supply voltage pins (`Vcc2` / `Vs`) of each L293D driver IC, providing clean power directly to the 3 stepper motors without requiring a buck converter.
*   **Logic Separation:** The logic supply pins (`Vcc1` / `Vss`) and control inputs are driven safely by the 5.0V rail and GPIOs of the Arduino Uno Q.
*   **Common Grounding & Clamp Diodes:** Grounds (GND) are tied together to maintain a common logic reference, while internal clamp diodes inside the L293D suppress inductive motor flyback spikes, keeping the microprocessor safe.

### 2.3 Inter-Core Bridge & Motion Protocol
The Linux OS side and the real-time MCU side communicate via two distinct high-reliability interfaces:
1.  **Motion Control TCP Socket Bridge (`127.0.0.1:7500`):** Python scripts (`master_controller.py`, `app.py`, `test_drill.py`) connect to a local socket server on port 7500 to dispatch ASCII motion commands (`X <steps>`, `Y <steps>`, `Z <steps>`). The firmware executes the pulses and responds with acknowledgment packets (`ACK:X`, `ACK:Y`, `ACK:Z`).
2.  **Edge Terminal UART Bridge (`/dev/ttyGS0` @ 115200 baud):** The Python Edge Terminal streams conversational text and prompts (`PRINT:<text>\n`) across the internal serial bridge to an attached physical LCD screen running on the microcontroller.

![Arduino Board Architecture](arduinoboardimage.webp)

---

## 3. Mechanical Design & CNC Actuation
The physical machine utilizes a dual-sided "sandwich" architecture: Camera 2 inspects the transparent plastic bubbles on the front of the medicine pack, while the 3-axis CNC gantry attacks from the rear foil side.

### 3.1 The 3-Axis Cartesian Gantry (`blissupport.stl`)
The CNC gantry operates entirely behind the foil backing of the blister pack:
*   **X-Axis (Horizontal Traverse):** Driven by a 28BYJ-48 stepper motor paired with dedicated L293D Driver #1.
*   **Y-Axis (Vertical / Height Traverse):** Driven by a 28BYJ-48 stepper motor paired with dedicated L293D Driver #2 along linear guide rails. It features a custom 3D-printed Perpendicular L-Bracket Hard Stop to physically arrest gantry overtravel and prevent derailment.
*   **Z-Axis (Punch / Drill Mechanism):** A rack-and-pinion plunger driven by a 28BYJ-48 stepper paired with dedicated L293D Driver #3 that punctures the foil backing. In software, this axis executes both single-strike plunging and full boundary contour tracing to trace around the pill circumference. *(Hardware upgrade roadmap: Drop-in compatibility with high-torque MG995 servos, NEMA 17 steppers, or 12V DC solenoids for high-impulse foil rupturing).*

![CNC Prototype Gantry](cncprototype.jpg)

### 3.2 The Rotary Dispenser & Parametric "Universal Pocket" (`medicinewheelstand.stl` & `main.kcl`)
Rather than requiring bespoke 3D-printed trays for each pill brand, the machine uses a 4-paddle rotary indexing rotor modeled programmatically using **Zoo's KittyCAD Language (KCL)** in `main.kcl`:
*   **Parametric Rotor Dimensions (Verified via CAD `cad/NOTES.md` & `main.kcl`):**
    *   **Blade Array:** 4 blades repeating radially at 90° intervals along the central Z hub axis.
    *   **Blade Length:** 95 mm parallel to the hub axis; base plate thickness is exactly 3 mm.
    *   **Blade Width:** Total outer blade width of 68 mm, consisting of a 64 mm inner packet bay (`packetWidth = 64mm`) bordered by two 2 mm vertical rail walls (`railWall = 2mm`).
    *   **Through-Cut Pocket Window:** Centered rectangular cutout of **50 mm × 80 mm** (`windowWidth = 50mm`, `windowLength = 80mm`), leaving 7.5 mm flush end borders.
    *   **Retention Channels:** Inward-facing slide channels with 2 mm retaining lips (`lipOverhang = 2mm`, `lipThickness = 1.5mm`) offering 3.5 mm vertical clearance above the base plate. The top opening between lips is 60 mm.
    *   **Motor Hub Coupling:** Central hub of Ø20 mm × 97 mm with a blind D-shaft socket (nominal Ø5 mm truncated at 1.5 mm offset, 4 mm flat-to-curve span, 12 mm blind depth) custom-fit to the 28BYJ-48 stepper shaft.
*   **The Suspension Principle:** The rigid perimeter foil of standard 64 mm blister packs slides into the 64 mm channels, suspending the delicate plastic blister bubbles safely over the 50 × 80 mm void.
*   **The Extraction Drop:** When the rear Z-axis plunger strikes or traces the blister foil, the pill is pushed outward through the open 50 × 80 mm aperture into the dispensing chute below.

![Medicine Holder CAD Wheel](medholderphoto.jpg)

#### AI-Based CAD Prompts for Medicine Holder Generation (Zoo Text-to-CAD)
For automated generative modeling in tools like Zoo.dev, the following prompts generate both functional parts of the medicine holder:

*   **Prompt 1 (Rotary Paddle Wheel):**
    ```text
    Create a 3D-printable parametric 4-blade rotary paddle wheel for holding foil blister packs:
    - Cylindrical hub: diameter 20mm, length 97mm along Z-axis.
    - Motor socket: blind D-shaped bore on one end of diameter 5mm, truncated by a flat 1.5mm from center, 12mm depth (fits 28BYJ-48 stepper shaft).
    - 4 radial blades at 90-degree intervals: length 95mm, base thickness 3mm, outer width 68mm.
    - Sliding channels: 2mm side walls with 64mm inner bay, 2mm overhang retaining lips (1.5mm thick, 3.5mm above base, 60mm top opening).
    - Center window: centered rectangular through-cut of 50mm x 80mm leaving 7.5mm flush end borders.
    - Watertight manifold solid, 0.5mm stress fillets on interior corners.
    ```
*   **Prompt 2 (Stationary Stand & Bearing Mount):**
    ```text
    Create a 3D-printable stationary mounting stand and bearing bracket for the rotary wheel:
    - Base: 110mm x 80mm x 6mm with four M4 mounting holes spaced 95mm x 65mm.
    - Upright: 110mm height, 40mm width, 12mm thickness with two 6mm triangular reinforcement gussets.
    - Stepper mount: recessed 28mm circular pocket for 28BYJ-48 motor, central 9mm shaft hole, two M3 slots at 35mm centers.
    - Bearing pocket: concentric recess for 608zz ball bearing (22mm OD, 7mm depth, 0.15mm interference fit).
    - Camera notch for unobstructed internal lens view; watertight manifold solid.
    ```

### 3.3 Low-Level Firmware & Stepper Pinout (`cnc_plotter.ino`)
The firmware implements an 8-step half-stepping sequence (`stepMatrix[8][4]`) to maximize holding torque and eliminate jitter on 28BYJ-48 geared steppers:
*   **X-Axis Pins:** Arduino Digital Pins `2, 3, 4, 5`
*   **Y-Axis Pins:** Arduino Digital Pins `6, 7, 8, 9`
*   **Z-Axis Pins:** Arduino Digital Pins `10, 11, 12, 13`
*   **Half-Step Delay:** Configured to `delay(2)` (2 ms per half-step phase transition).
*   **Thermal Protection (`powerDown()`):** After each coordinated movement, all phase pins on the active axis are immediately driven `LOW`. This eliminates continuous coil current, preventing 28BYJ-48 coil overheating and saving battery capacity during idle periods.

---

## 4. The Dual-Camera Vision System
To avoid exceeding USB host controller bandwidth limits and conserve RAM on the Uno Q, the system deploys two webcams that are managed dynamically by the Python state machine:

### Camera 1: The "Interaction" Camera (External / Patient-Facing)
*   **Location:** Mounted externally on the chassis, facing the room and user.
*   **Function A (Biometric Face ID):** Captures user frames for LBPH facial recognition, ensuring medication is only released to verified patients or caretakers.
*   **Function B (OCR Medication Intake):** During setup mode, patients hold new blister packs up to Camera 1. RapidOCR and Tesseract scan foil text (brand names, active ingredients, dosage strengths) before the pack is inserted into the wheel.

### Camera 2: The "Targeting" Camera (Internal / Machine-Facing)
*   **Location:** Mounted rigidly inside the chassis facing the front (clear plastic bubbles) of the currently indexed blister pack.
*   **Function (SAM 2 & Contour Localization):** Captures high-contrast images of the blister pack. OpenCV and Meta SAM 2 segment pill bubble boundaries, compute geometric centers, and calculate toolpaths for the CNC gantry.

### Video Streaming & Remote Monitoring Infrastructure
*   **Socket Video Server (`0.0.0.0:9999`):** Built into `master_controller.py`, this background daemon encodes camera frames to JPEG (quality 80) and streams them over TCP prefixed with a 4-byte little-endian length header (`<L`) for real-time remote telemetry (`monitor_viewer.py`).
*   **Flask MJPEG Stream (`port 5000`):** The Appliance Terminal serves an interactive HTTP MJPEG stream at `/video_feed` with targeting crosshairs overlaid at the optical center `(cx, cy)`.

---

## 5. Local Edge AI Software Stack & Compilation Pipeline

### 5.1 CAD vs. AI Optimization Tools: Disambiguation
*   **Zoo (Zoo.dev / KCL):** Used exclusively for **parametric mechanical 3D CAD design** (`cad/main.kcl`) to program the rotary wheel, sliding guides, and frame geometry.
*   **Qualcomm AI Hub (`qai_hub`):** Used for **hardware model compilation and optimization**. In `compile_qwen_aihub.py`, PyTorch models are exported via `torch.export` and compiled for Qualcomm target runtimes (Dragonwing RB3 Gen 2 Vision Kit / QCS6490) with `--target_runtime tflite --truncate_64bit_io` to generate optimized LiteRT models (`qwen_optimized.tflite`).

### 5.2 The Conversational LLM & RAG Engine
*   **Qwen 2.5 (0.5B Instruct):** Runs locally via `llama-cpp-python` using a 4-bit quantized GGUF build (`qwen2.5-0.5b-instruct-q4_k_m.gguf`, ~490 MB).
*   **Strict Embedded Memory Constraints (`assistant.py`):**
    *   `n_ctx = 512` (Fixed context window to prevent dynamic RAM bloat)
    *   `n_threads = 2` (Leaves CPU cores free for vision and OS tasks)
    *   `n_batch = 128` (Strict batch limit)
    *   `max_tokens = 64` (Ensures prompt, concise verbal responses)
*   **Retrieval-Augmented Generation (RAG):** The model cross-references user speech against `medical_database.json` to verify indications, maximum dosages, and requirements (e.g., verifying if Ibuprofen requires food before dispensing).

### 5.3 Speech Processing & Fine-Tuning Suite
*   **Primary Streaming STT (Sherpa-ONNX):** Uses `sherpa_onnx.OnlineRecognizer.from_transducer` running an INT8-quantized Indian English streaming Zipformer model (`encoder`, `decoder`, and `joiner` ONNX graphs, 80 feature dimensions, 16 kHz sample rate).
*   **Audio Preprocessing Fixes:**
    *   Hardware resampling via ALSA (`plughw:0,0`).
    *   DC Offset Filter: Software correction `chunk - np.mean(chunk)` removes USB soundcard baseline DC drift.
    *   Dynamic Gain: `MIC_GAIN = 2.5` digital amplification boosts low-volume speech.
*   **Custom STT Fine-Tuning Pipeline (`code/stt_dataset_collector`):**
    *   **Data Collection Web App (Port 5001):** Records custom medical phrases into 91 custom `.wav` files with paired transcripts.
    *   **PyTorch Icefall Training (`finetune.sh`):** Converts collected datasets into `lhotse` manifests (`custom_corpus`), downloads `pretrained.pt`, and runs 10 epochs of FP16 fine-tuning.
    *   **ONNX Export (`export.py`):** Converts fine-tuned PyTorch weights back to INT8 ONNX graphs for direct execution on the Uno Q.
    *   **Parallel Whisper Benchmark App (Port 5002):** A companion tester running `sherpa-onnx-whisper-tiny.en` to benchmark Word Error Rates (WER) against the fine-tuned Zipformer.
*   **Alternative STT (Faster-Whisper):** Used in `edge_terminal/main_edge_terminal.py` and `appliance_terminal/appliance.py` using `tiny.en` with INT8 CTranslate2 execution.
*   **Text-to-Speech (Piper & Edge-TTS):** Piper ONNX (`en_US-lessac-low.onnx`) directly synthesizes 16 kHz audio and plays it via Python `sounddevice`. Edge-TTS serves as an alternate engine via `ffplay`.

### 5.4 Computer Vision, OCR & Biometric Security
*   **Meta SAM 2 & OpenCV Contour Pipeline (`detector.py`):**
    *   Takes RGB camera frames downsampled to a max dimension of 1024 px for real-time CPU speed.
    *   Extracts segmentation masks via SAM 2, converts them to binary masks, and extracts exterior contours.
    *   Applies a multi-stage geometric filter: area threshold (`MIN_AREA`), aspect ratio bounds (`MIN_ASPECT_RATIO <= w/h <= MAX_ASPECT_RATIO`), and ellipse circularity fitting (`cv2.fitEllipse()`, requiring `area_ratio >= MIN_ELLIPSE_SCORE`) to isolate valid pill bubbles from foil artifacts.
*   **Optical Character Recognition (OCR):** Combines `rapidocr_onnxruntime` and `pytesseract` to scan reflective curved foil packaging and extract medication text.
*   **Facial Recognition (LBPH):** `cv2.face.LBPHFaceRecognizer_create()` paired with `haarcascade_frontalface_default.xml`. Captures 10 training frames per user, trains on-device, and stores model weights in `face_model.yml` linked to SQLite profile IDs.

---

## 6. The "Mirror Math" Kinematics & Extraction Trajectory

### 6.1 Coordinate Frame Inversion
Because Camera 2 is positioned in front of the transparent plastic bubbles while the CNC gantry attacks from behind the aluminum foil, coordinates along the horizontal axis are physically inverted:
*   **Z-Axis (Vertical Alignment):** Remains identical between camera frame and rear gantry frame.
*   **X-Axis (Horizontal Alignment):** Must be mirrored across the optical center. If a pill appears to the right (`+X`) of the camera center, the rear plunger must traverse to the left (`-X`) to punch directly behind it.

```python
# Z-axis remains positive-up / positive-down
Z_plunger = Z_cam

# X-axis is inverted across the optical center
X_plunger = X_cam * -1
```

### 6.2 Trajectory Execution & Contour Drilling (`test_drill.py` & `master_controller.py`)
Rather than a blind single-point press, the Blister Bot supports precision boundary tracing:
1.  **Optical Calibration:** The image center `(cx, cy)` represents gantry home `(0, 0)`.
2.  **Pixel-to-Step Translation:** Coordinates are scaled via `PIXEL_TO_STEP_RATIO = 1.0` (steps per pixel).
3.  **Approach:** The Z-axis retracts to clearance height (`Z -2`). The X and Y axes traverse to the starting contour pixel `(start_x, start_y)`.
4.  **Plunge:** The Z-axis strikes downward (`Z 2`) to penetrate the foil.
5.  **Contour Cut / Drag:** The gantry steps through the extracted polygon contour points with a `DRAG_DELAY = 0.05s` interval, cutting the foil cleanly around the blister bubble.
6.  **Retract & Reset:** Z retracts (`Z -2`), and X/Y return to center `(cx, cy)`.

---

## 7. Dual Interface Control Architecture

```text
                     +---------------------------------------+
                     |         Arduino Uno Q Brain           |
                     |  (master_controller.py / Qwen LLM)   |
                     +-------------------+-------------------+
                                         |
               +-------------------------+-------------------------+
               |                                                   |
               v                                                   v
   +-----------------------+                           +-----------------------+
   |   Appliance Terminal  |                           |     Edge Terminal     |
   |   (Flask Port 5000)   |                           | (Serial /dev/ttyGS0)  |
   +-----------------------+                           +-----------------------+
   | - Live MJPEG Video    |                           | - Faster-Whisper STT  |
   | - Targeting Reticle   |                           | - Physical LCD Bridge |
   | - Manual Axis Jogging |                           | - Hands-free Voice    |
   | - Web Audio Triggers  |                           | - Standalone Operation|
   +-----------------------+                           +-----------------------+
```

1.  **Appliance Terminal (Caregivers & Technicians):**
    *   Flask web interface on port `5000` accessible via local Wi-Fi.
    *   Streams live video from Camera 1 or Camera 2 with crosshairs at `/video_feed`.
    *   Exposes `/api/move` endpoint for manual X, Y, Z axis calibration and jogging.
    *   Allows caregivers to trigger voice commands, inspect OCR text logs, and view database records.
2.  **Edge Terminal (Patient-Facing On-Device Interface):**
    *   Lightweight headless Python script (`main_edge_terminal.py`).
    *   Interfaces directly with the physical LCD over the `/dev/ttyGS0` serial bridge.
    *   Provides instant visual feedback for patients who are hard of hearing or in noisy environments.

---

## 8. Complete System Workflow States & State Machine

The master orchestrator (`master_controller.py`) executes a 4-state loop designed to conserve RAM by loading vision and speech models only when active:

### State 0: Boot & Peripheral Initialization
1.  System boots Debian Linux and starts `blisterbot.service`.
2.  Initializes STT, TTS, LLM, and loads known faces from `faces/` and `attendance.db`.
3.  Background TCP video server on port `9999` begins listening.
4.  Announces verbally: *"Hi, I'm awake."*
5.  Listens for the wake word `"setup"` or uses Qwen LLM intent classification to detect setup commands.

### State 1: Setup Mode (Caretaker & User Profile Registration)
1.  System prompts: *"Please provide caretaker details. What is your name and work shift?"*
2.  Speech is transcribed and Qwen extracts `{name, work_shift, is_patient}` into structured JSON.
3.  Verbal confirmation loop: *"I heard [Name] and [Shift]. Is this correct? Say yes or no."*
4.  **Facial Registration:** System activates Camera 1, takes 10 face frames via Haar Cascade, extracts grayscale crops into `faces/<name>_<timestamp>.jpg`, trains the LBPH model, and commits the profile to SQLite `caretakers`.
5.  Repeats until user confirms no further caretakers. Transitions to State 2.

### State 2: Setup Mode (Inventory & Medication Intake)
1.  System prompts: *"Please load blister packs into the wheel. Say confirm when ready."*
2.  Upon hearing `"confirm"`, Camera 1 or Camera 2 captures a frame.
3.  `perform_ocr()` identifies pill contour boundaries, crops bounding boxes, and executes OCR to extract medicine names and strengths.
4.  Updates the `inventory` SQLite table with medication name, slot index, and count.
5.  Camera is closed to free RAM. Transitions to State 3.

### State 3: Normal Operating Mode (The Main Conversational Loop)
1.  **Fuzzy Wake Word Detection:** Listens continuously for phonetically similar wake terms:
    `["bot", "bought", "boat", "but", "pot", "robot", "blister", "blisterbot", "what", "dot"]`.
2.  **LLM Intent Classification:** Classifies speech into one of 10 distinct intents:
    *   `ADD_PATIENT`: Guides voice intake of patient name, age, conditions, and med schedule; captures 10 face frames; adds record to `patients` table.
    *   `DRILL_MEDICINE`: Extracts target medicine name, indexes the rotary wheel, launches Camera 2, computes SAM 2 contour, applies Mirror Math, and executes CNC drilling. Decrements inventory in `attendance.db` and logs event in `painrec/<patient_name>.md`.
    *   `PATIENT_DETAILS`: Queries patient info by name and provides a spoken summary.
    *   `UPDATE_PATIENT`: Voice-driven updates to existing patient database entries.
    *   `DOSAGE_QUERY`: Answers dosage questions using RAG context from `medical_database.json` and `inventory`.
    *   `SCHEDULE_QUERY`: Cross-references patient schedule with requested medication.
    *   `MEDICINE_QUERY`: Explains drug indications, mechanisms, or contraindications.
    *   `PAIN_REPORT`: Detects patient pain or discomfort complaints (e.g., *"I have a severe headache"*). Provides empathetic voice advice and automatically appends a timestamped markdown entry to `painrec/<patient_name>.md`.
    *   `CONVERSATION`: Friendly, casual interaction.
    *   `Q_AND_A`: General medical assistant fallback.

---

## 9. Database Architecture & Health Logging

### 9.1 SQLite Schema (`attendance.db`)
```sql
CREATE TABLE IF NOT EXISTS caretakers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    work_shift TEXT,
    is_patient BOOLEAN,
    face_path TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    health_issues TEXT,
    med_schedule TEXT,
    assigned_caretaker_id INTEGER,
    face_path TEXT,
    FOREIGN KEY(assigned_caretaker_id) REFERENCES caretakers(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    med_name TEXT NOT NULL,
    dosage TEXT,
    slot_index INTEGER,
    med_count INTEGER
);
```

### 9.2 File-Based Clinical Health Logs (`code/painrec/`)
Every patient interaction, pain report, and medication dispensing cycle is persistently logged to markdown documents (`code/painrec/<patient_name>.md`):
```markdown
## Pain Report: 2026-10-11 14:22:10
- **Patient Details**: {'name': 'John Doe', 'age': 72, 'health_issues': 'Hypertension'}
- **Report**: I am feeling sharp pain in my lower back

## Medication Event: 2026-10-11 14:25:30
- **Medicine**: Paracetamol
- **Status**: TAKEN
```

---

## 10. Development Realities, Implementation Status & The "Trash-Bot" Pivot

### 10.1 Successfully Implemented Capabilities
*   **Full Power Isolation:** Operational split-rail grid isolating motor transients from SBC logic.
*   **Fully Offline Multi-Model AI Stack:** Qwen 2.5 (0.5B GGUF), Sherpa-ONNX streaming Zipformer, Faster-Whisper INT8, Piper TTS, Meta SAM 2, and RapidOCR running completely on embedded Linux.
*   **Complete Custom Speech Fine-Tuning Pipeline:** Working data collection web server, 91-sample training corpus, PyTorch Icefall training scripts, and ONNX quantization toolchain.
*   **Kinematic Engine & Protocols:** Mirror Math transformation, contour-tracing motor control, and TCP/UART bridges.
*   **Unified State Machine & Clinical Logging:** 10-class intent classifier, facial authentication, SQLite database schemas, and structured pain reporting logs.

### 10.2 Mechanical Hurdles & The "Trash-Bot" Rapid Prototyping Pivot
Building a rigid, high-precision Cartesian CNC machine using low-cost 28BYJ-48 motors and desktop 3D prints presented real-world physical challenges:
*   **Axis Binding & Rigidity:** 3D-printed linear slides can flex or bind under uneven side-loads. The Y-axis required dual motors in parallel and rigid L-bracket hard stops to remain aligned.
*   **Torque Limitations:** 28BYJ-48 stepper motors produce modest torque. If the rotary wheel is heavily loaded, step skipping can occur.
*   **The "Flat-Bed Hack" (MVP Triage):** To decouple mechanical troubleshooting from AI software validation, the rotary wheel can be temporarily detached. Blister packs are secured flat to the chassis bed ("Flat-Bed Hack").
*   **Frame Reinforcement:** Cardboard gussets, hot glue, and triangular braces are utilized during live prototyping to stiffen the chassis (`blissupport.stl`), allowing the entire vision-to-motor coordinate pipeline to be proven and refined before finalizing industrial-grade mechanical components.

### 10.3 Testing & Physical Results
Got the cnc miller working and the facial recog and llm working.Tried to use a bluetooth speaker for the llm output but due to connectivity issues had to switch to an earphone.The cnc miller is able to move successfully,but while drilling,due to the hollow wheel and the fact that the medicine holder wasnt strongly glued or attached to the ground became unstable.

*(Physical trial video available at `assets/cncmovingtrial.mp4`)*

### 10.4 Developer Reflections & Field Notes

#### current status and thoughts on the whole thing:
In the programs last week,i attempted to move from a cardboard DIY setup to a more formal 3d printed version.I had to 3d print the base,designed a custom medicine holder and had to find a way to make the wheel rotate and control its rotation.The drill that was supposed to make a hole in the packets was too short and I had to print the "chain and slide" thing again to increase its length,however  due to some issues with the software/scaling problems the new part came out wrong.The medicine holder also had a hole in it for a shaft piece,but the piece broke and  got stuck ,which kind of paused the project

#### what i should have done:
The drill was the core part of the entire project,and instead of dedicating all my time to fixing it first,i spread my focus too thin and focused on several things at once,especially the ai work on the software side  which could have been done last

#### Edge Segmentation & Vision
Edge segmentation models are pretty good now,and sam3 is especially good.If i remember correctly,i did not have to finetune it and just gave it one or two labelled examples and it was able to find the pill boundaries

#### Speech Models & Fine-Tuning Lessons
Edge based text to speech models  still have a lot to improve,though they are capable.Their weakness was that they were really optimized for us speakers and couldnt always transcribe the audio properly.To fix this,i tried to create a mini dataset consisting of some audio clips of indian english speakers saying common medicines related phrases like "give me paracetamol" etc to finetune the model for my usecase,but as my dataset was tiny,it actually made the model worse.The initial learning rate that was set was also too high,causing the model to forget what it had already learned.I intend to continue this with a larger dataset and more appropriate hyperparameters to see if i can optimize this.

#### Mechanical Observations & Fixes
The medicine holder is hollow in the center,and this was a deliberate choice ,so that the camera could see the front of the medicine and guess where the pill boundaries were,however this made the drilling tricky,as applying too much force on the packet caused it to pop out of the medicine holder,so i intend to solve this  with a translucent but rigid cover in the front

the wheel of the medicine holder that was attached to the medicine stand did not rotate smoothly due to friction,and this would lead to low precision when switching between meds.I intend to explore ways to make the rotation smoother by exploring things like ball bearings to fix this issue

#### Hardware & Resource Constraints
The uno q is a capable board,but it can only fit a few models at once in its 4gb ram,and so i haf to work on a logic that loaded models only at the time of need and released the ones that were not immediately relevant

---

## 11. System Services & Automated Deployment

### 11.1 Systemd Service Unit (`blisterbot.service`)
To ensure automatic startup on system boot, the master controller is registered as a Linux system daemon:
```ini
[Unit]
Description=Blister Bot Master Controller
After=network.target sound.target

[Service]
Type=simple
User=arduino
WorkingDirectory=/home/arduino/Blister-bot-main-/code
ExecStart=/usr/bin/python3 /home/arduino/Blister-bot-main-/code/master_controller.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 11.2 Deployment Scripts
*   `scripts/deploy_master.sh`: Configures environment paths, verifies audio devices, and launches core daemons.
*   `scripts/rsync.exp`: Automated SSH/Rsync synchronization script between development laptops and the Uno Q board.
*   `code/facerecog-unoq/deploy_to_unoq.sh`: Deploys biometric face models and SQLite database migrations.