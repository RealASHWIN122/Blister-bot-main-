# Blister Bot 💊🤖: DIY Edge AI Automated Medicine Dispenser

We can see automated medicine dispensers ranging from simple timed plastic boxes to massive pharmacy robotics. When we generally talk about home dispensers, they usually require the user to manually pop out pills and load them into daily bins. But what if a robot could handle the original packaging directly?

In this project, we challenge ourselves to build a complex mechatronic system that combines rotational indexing with a Cartesian CNC movement to mechanically punch pills right out of their original foil blister packs. Instead of relying on cloud APIs, this robot is powered entirely by Local Edge AI to ensure patient privacy (HIPAA compliance), offline reliability, and low-latency mechanical targeting.

If you're wondering how to make a smart, AI-driven pill dispenser at home using an Arduino Uno Q, this build walks through the full process, from CNC kinematics to the conversational code.

---

## 💡 Motivation
What if you didn't have to manually strip pills from medicine packets every time you had a cold? What if elderly people in nursing homes and living alone at home could be safely monitored and assisted even when there is no one around? And what if all of this was hands-free and handled by speaking as if you were talking to a regular person—and to top it off, all offline, so your private talks remain strictly within your circle?

That's what the Blister Bot is all about.

Not only has AI become more capable, it has also become vastly more efficient. Now, small models that can run on an old laptop with no dedicated GPU can handle complex tasks including conversational chatbots, coding, character recognition, speech-to-text, and facial recognition. All of this opens up the possibilities of creating useful, intelligent devices without needing an internet connection.

Historically, the only limitation was lightweight, powerful, and cheap hardware. We were stuck using TinyML on classic boards like the ESP32 or Arduino Uno R4, which are ultimately just microcontrollers lacking the raw memory to hold complex workflows. Luckily, with the creation of the Arduino Uno Q and similar boards, we finally have the edge hardware to pull off these AI hardware projects without compromise.

---

## 🤖 What is the Blister Bot?
The Blister Bot is a prototype DIY automated medicine dispenser designed to securely manage, schedule, and dispense medication directly from standard foil/plastic blister packs. Unlike traditional automatic dispensers where you must manually extract each pill to load the machine, the Blister Bot takes the entire untouched blister pack. It utilizes a custom-built 3-axis mini CNC machine to scan, target, and plunge the pill out of its casing. 

Furthermore, the Blister Bot acts as an intelligent medical assistant. It features a fully conversational AI interface, allowing patients to simply talk to it. Before dispensing any medication, it uses facial recognition to authenticate the user, cross-referencing their identity with an internal SQLite database to prevent overdosing or dispensing to the wrong patient. All of this runs entirely offline on edge hardware.

---

## ✨ Key Advantages
* **Zero Prep Work:** Dispenses directly from original blister packs using a CNC punch, eliminating the tedious need to pre-sort pills into weekly bins.
* **100% Offline AI:** Uses miniaturized, local AI models (like Qwen 0.5B, Sherpa-ONNX, and Piper) to ensure medical data privacy and zero latency. Absolutely no internet connection is required.
* **Conversational Interface:** Talk to it naturally instead of navigating a complex touchscreen, app, or confusing buttons.
* **Biometric Security:** Prevents accidental or unauthorized overdoses by physically verifying the patient's face before cutting the foil.

---

## 🧰 Components Required

| Parts Used | How Many Units Required | Purpose |
| :--- | :---: | :--- |
| **Arduino Uno Q** | 1 | The main brain. The quad-core Qualcomm side handles AI and web serving, while the ARM Cortex RTOS handles real-time motor control. |
| **ULN2003 Motor Drivers** | 3 | Drives the stepper motors based on GPIO signals from the Uno Q. |
| **28BYJ-48 Stepper Motors** | 3 | Controls the X, Y, and Z axes of the CNC gantry and the rotary wheel indexing. |
| **USB Webcams** | 2 | Camera 1 is for patient Facial Recognition. Camera 2 is for Pill Contour Detection. |
| **16.8V Battery Pack** | 1 | Main power supply for the entire robotic system. |
| **LM2596 Buck Converter** | 1 | Steps down the 16.8V battery voltage to a safe, dedicated 5V rail for the motors. |
| **Custom 3D Printed Parts** | 1 Set | Includes the `blissupport.stl` framing, CNC gantry, and the `medicinewheelstand.stl` rotary wheel. |

---

## ⚡ System Architecture

*(System Architecture Image Placeholder)*
> **Tip:** You can generate this system architecture block diagram using a tool like **Mermaid.js**, **Draw.io**, or **Lucidchart**.
![System Architecture Placeholder](assets/system_architecture.png)

The Blister Bot relies on a highly integrated architecture split between logical AI processing and real-time physical actuation:

1. **Conversational LLM Interface 🗣️**
   When you approach the machine, it utilizes a local **Qwen 2.5 LLM (0.5 Billion parameters)** for reasoning.
   * **Listening:** Uses **Sherpa-ONNX** (fine-tuned on custom voice data) for fast, offline speech-to-text.
   * **Processing:** Evaluates commands against an internal SQLite medical schedule and ruleset.
   * **Speaking:** Replies verbally using **Piper** for high-quality text-to-speech.

2. **Facial Recognition Security 👤**
   To prevent unauthorized dispensing, the system requires biometric authentication.
   * Your medical profile is securely stored using an **LBPH (Local Binary Pattern Histogram)** face recognizer.
   * Authentication must pass before the physical CNC actuates.

3. **Automated Pill Extraction ⚙️**
   * Camera 2 takes a snapshot of the blister pack.
   * **OpenCV contour detection** and **Meta's SAM 2 (Segment Anything Model 2)** locate the exact boundaries of the pill.
   * The software calculates a "Mirror Math" coordinate transformation.

---

## 🔌 Circuit Diagram

*(Circuit Diagram Image Placeholder)*
> **Tip:** You can generate professional circuit schematics using tools like **Fritzing**, **KiCad**, or **Tinkercad**.
![Circuit Diagram Placeholder](assets/circuit_diagram.png)

### Power Isolation
To prevent inductive voltage spikes from the stepper motors from browning out or frying the logic board, the system uses an isolated power design. The 16.8V battery pack is connected to an **LM2596 buck converter** to supply a dedicated 5V rail strictly for the ULN2003 drivers and stepper motors. The Arduino Uno Q is powered safely on its own separated circuit.

---

## 📐 3D Printing & Mechanical Design

The mechanical chassis is built around a Cartesian CNC coordinate system paired with a rotary axis.
* **The Rotary Wheel (`medicinewheelstand.stl`):** Holds the foil blister packs. It indexes rotationally to bring the correct medicine pack to the cutting area.
* **The CNC Gantry:** Actuates on the back of the packet to trace, plunge, and drill the pill out of the foil using a specialized punch tool.
* **The Frame (`blissupport.stl`):** Houses the cameras at fixed focal lengths to ensure OpenCV contour mathematics are consistently accurate.

---

## 💻 Core Capabilities & Software Modules

Because the machine runs offline, memory management on the Uno Q is critical. The state machine (`master_controller.py`) orchestrates loading and unloading AI models dynamically so we don't run out of RAM.

### Dual Interface System
The bot provides two main ways to interact:
1. **Appliance Terminal:** A Flask web UI running on port 5000 that allows caregivers to view the live MJPEG camera feed, monitor logs, and trigger voice commands.
2. **Edge Terminal:** A lightweight serial-based interface (`main_edge_terminal.py`) that uses `faster-whisper` for ultra-low latency STT and outputs the AI's responses to a physical LCD screen via a serial bridge.

### Intelligent Medicine Scanner & RAG
* **Medicine Scanner (OCR):** The appliance terminal uses `rapidocr-onnxruntime` to continuously monitor the camera feed, extract text from medicine packets, and announce the names aloud.
* **Retrieval-Augmented Generation (RAG):** When you ask for medication, the Qwen LLM queries an internal `medical_database.json` to verify schedules, dosages, and interactions before dispensing.

### Mirror Math Kinematics & SAM 2 Vision
By looking at the clear plastic bubbles on the front of the packet, Camera 2 takes a snapshot. We use **Meta's Segment Anything Model 2 (SAM 2)** combined with OpenCV to accurately detect the boundaries of the blister. The Python script applies a scaling factor to convert pixels to millimeters, and then applies a **Mirror Math** formula to tell the rear-mounted CNC plunger exactly where to strike:
```python
X_plunger = X_cam * -1
```

### AI Pipeline
1. **Audio Trigger:** Captured via USB mic (filtered by VAD).
2. **STT (Faster-Whisper / Sherpa-ONNX):** Transcribes audio to text offline.
3. **LLM & RAG (Qwen 2.5):** Processes intent (e.g. "I need paracetamol") against the medical database.
4. **Face ID (LBPH):** Verifies the user against `attendance.db` via OpenCV.
5. **Vision (OpenCV/SAM 2):** Targets the pill boundaries.
6. **CNC Drive (`cnc_driver.py`):** Pulses the stepper motors to punch the pill.
7. **TTS (Piper / Edge-TTS):** Announces "Your medication is dispensed."

---

## 📁 Repository Structure

All project files, drivers, and AI scripts are contained within the main repository.

```
📦 blister-bot
 ┣ 📂 appliance_terminal/          # Flask Web UI, OCR Scanner & HTTP mic triggers
 ┣ 📂 edge_terminal/               # Serial LCD interface & faster-whisper STT
 ┣ 📂 code/
 ┃ ┣ 📜 master_controller.py       # Main state machine & orchestrator
 ┃ ┣ 📜 cnc_driver.py              # Kinematics & tool offsets
 ┃ ┣ 📜 test_stt.py                # Automated testing for finetuned STT
 ┃ ┣ 📜 test_rag.py                # RAG database evaluation scripts
 ┃ ┣ 📜 medical_database.json      # RAG inventory and patient rules
 ┃ ┣ 📜 attendance.db              # SQLite logs for Face ID
 ┃ ┣ 📂 blister_detector/          # Meta SAM 2 vision bounding box scripts
 ┃ ┗ 📂 ai_modules/           
 ┃   ┣ 📜 face_id.py               # LBPH Face Recognizer
 ┃   ┣ 📜 vision.py                # OpenCV contour detection & SAM 
 ┃   ┗ 📜 conversational.py        # Qwen, Sherpa, and Piper loops
 ┣ 📂 scripts/
 ┃ ┣ 📜 deploy_master.sh           # Automated deployment scripts
 ┃ ┗ 📜 rsync.exp                  # Edge syncing
 ┣ 📂 cad/                         # 3D printable STL files
 ┣ 📂 docs/                        # Weekly progress logs
 ┗ 📜 README.md
```

---

## 🎯 Testing & Final Result

*(Video/GIF Placeholder)*
![Final Result Video Placeholder](assets/demo_video.gif)

Once completely assembled, the Blister Bot operates entirely hands-free. A patient simply requests their medicine, looks into the primary camera, and waits. The machine indexes the wheel, lines up the CNC plunger, and perfectly extracts the pill directly from the foil without any human intervention.

---

## 🚀 Running the Bot

To start the Blister Bot system on the Arduino Uno Q, navigate to the `code/` directory and run the main state machine script:
```bash
cd code/
python3 master_controller.py
```
