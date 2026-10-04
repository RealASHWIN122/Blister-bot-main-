
Blister Bot 💊🤖
DIY Edge AI Automated Medicine Dispenser
We can see automated medicine dispensers ranging from simple timed plastic boxes to massive pharmacy robotics. When we generally talk about home dispensers, they usually require the user to manually pop out pills and load them into daily bins. But what if a robot could handle the original packaging directly?
In this project, we challenge ourselves to build a complex mechatronic system that combines rotational indexing with a Cartesian CNC movement to mechanically punch pills right out of their original foil blister packs. Instead of relying on cloud APIs, this robot is powered entirely by Local Edge AI to ensure patient privacy (HIPAA compliance), offline reliability, and low-latency mechanical targeting.
If you're wondering how to make a smart, AI-driven pill dispenser at home using an Arduino Uno Q, this build walks through the full process, from CNC kinematics to the conversational code.
📑 Table of Contents
 * Motivation
 * What is the Blister Bot?
 * Key Advantages
 * Components Used
 * How Does the Blister Bot Work?
 * Circuit Architecture
 * 3D Model & Mechanical Design
 * AI and Software Interface
 * Repository Structure
 * Final Result
 * Running the Bot
💡 Motivation
What if you didn't have to manually strip pills from medicine packets every time you had a cold? What if elderly people in nursing homes and living alone at home could be safely monitored and assisted even when there is no one around? And what if all of this was hands-free and handled by speaking as if you were talking to a regular person—and to top it off, all offline, so your private talks remain strictly within your circle?
That's what the Blister Bot is all about.
Not only has AI become more capable, it has also become vastly more efficient. Now, small models that can run on an old laptop with no dedicated GPU can handle complex tasks including conversational chatbots, coding, character recognition, speech-to-text, and facial recognition. All of this opens up the possibilities of creating useful, intelligent devices without needing an internet connection.
Historically, the only limitation was lightweight, powerful, and cheap hardware. We were stuck using TinyML on classic boards like the ESP32 or Arduino Uno R4, which are ultimately just microcontrollers lacking the raw memory to hold complex workflows. Luckily, with the creation of the Arduino Uno Q and similar boards, we finally have the edge hardware to pull off these AI hardware projects without compromise.
🤖 What is the Blister Bot?
The Blister Bot is a prototype DIY automated medicine dispenser designed to securely manage, schedule, and dispense medication directly from standard foil/plastic blister packs. It utilizes a 3-axis mini CNC machine to trace and drill the blister out. It also features a conversational AI interface and facial recognition to authenticate users before dispensing, running entirely offline on edge hardware.
✨ Key Advantages of This Blister Bot
 * Zero Prep Work: Dispenses directly from original blister packs using a CNC punch, eliminating the tedious need to pre-sort pills into weekly bins.
 * 100% Offline AI: Uses miniaturized, local AI models (like Qwen 0.5B and Sherpa) to ensure medical data privacy and zero latency. Absolutely no internet connection is required.
 * Conversational Interface: Talk to it naturally instead of navigating a complex touchscreen, app, or confusing buttons.
 * Biometric Security: Prevents accidental or unauthorized overdoses by physically verifying the patient's face before cutting the foil.
🧰 Components Used
Below is the complete list of components used for making this automated dispenser, along with what each part does in the overall system:
(List of components to be added here—e.g., Arduino Uno Q, ULN2003 Drivers, Stepper Motors, Webcams, 16.8V Battery, LM2596 Buck Converter, etc.)
🛠️ How Does the Blister Bot Work?
The Blister Bot relies on three core operational pillars:
1. Conversational LLM Interface 🗣️
Interact with the Blister Bot naturally. When you approach the machine, it utilizes a local Qwen 2.5 LLM (0.5 Billion parameters) for intelligence.
 * Listening: Uses Sherpa-ONNX for fast, offline speech-to-text.
 * Processing: Checks your medical schedule and internal rules.
 * Speaking: Replies verbally using Piper for high-quality text-to-speech.
2. Facial Recognition 👤
To prevent unauthorized dispensing, the system requires biometric authentication.
 * If you say "add patient", Camera 1 captures your face.
 * Your medical profile is securely stored using an LBPH (Local Binary Pattern Histogram) face recognizer backed by a local SQLite database.
3. Automated Pill Extraction ⚙️
When an authenticated patient says "I need paracetamol":
 * Camera 2 takes a snapshot of the blister pack loaded in the rotary wheel.
 * The software uses OpenCV contour detection and SAM (Segment Anything Model) to locate the exact boundaries of the pill.
 * It then actuates the 3-axis mini CNC machine on the back of the packet to trace, plunge, and drill the pill out of the foil using a custom "Mirror Math" coordinate system.
⚡ Circuit Architecture
The brain of the robot is an Arduino Uno Q, taking advantage of its split-architecture:
 * 🧠 The Brains (Debian Linux): The Qualcomm quad-core side handles the Python web server, SQLite database, OpenCV processing, LBPH Face ID, and LLM inference entirely locally.
 * 💪 The Brawn (RTOS Microcontroller): The ARM Cortex side handles the real-time GPIO signaling to the ULN2003 motor drivers.
Power Isolation:
To prevent voltage spikes from frying the logic board, the system uses an isolated power design. A 16.8V battery pack is connected to an LM2596 buck converter to supply a dedicated 5V rail strictly for the stepper motors, while the Uno Q is powered separately via USB-C.
📐 3D Model & Mechanical Design
(Details about the CAD files, rotary wheel indexing, and 3-axis Cartesian CNC gantry go here. STL files for 3D printing can be found in the repository.)
🧠 AI and Software Interface
Because the machine runs offline, memory management on the Uno Q is critical. The state machine loads and unloads models dynamically:
 * Speech-to-Text: Sherpa-ONNX processes human audio in near real-time without internet access.
 * Text-to-Speech: Piper generates high-quality, offline synthesized voice replies.
 * LLM Engine: Qwen 2.5 (0.5B) acts as the reasoning engine to check SQLite rules (e.g., "Has the patient eaten?").
 * Vision & Targeting: OpenCV Contour Detection / RapidOCR. By looking at the clear plastic bubbles on the front of the packet, it finds the center coordinates. The Python script then applies a Mirror Math formula to tell the rear-mounted CNC plunger exactly where to strike:
   X_plunger = X_cam * -1

 * Security: LBPH Face Recognizer is used to authenticate patients directly on the edge device.
📁 Repository Structure
All project files, drivers, and AI scripts are contained within the main repository.
📦 blister-bot
 ┣ 📂 code/
 ┃ ┣ 📜 master_controller.py  # Main Python state machine orchestrating the workflow
 ┃ ┣ 📜 cnc_driver.py         # Handles "Mirror Math" kinematics & tool offsets
 ┃ ┗ 📂 ai_modules/           
 ┃   ┣ 📜 face_id.py          # LBPH Face Recognizer
 ┃   ┣ 📜 vision.py           # OpenCV contour detection & SAM 
 ┃   ┗ 📜 conversational.py   # Qwen, Sherpa, and Piper conversational loops
 ┗ 📜 README.md

🎯 Final Result
(Insert images, GIFs, or links to a demo video showcasing the Blister Bot successfully authenticating a user and punching a pill out of the blister pack.)
🚀 Running the Bot
To start the Blister Bot system, navigate to the code/ directory and run the main state machine script:
python3 master_controller.py

