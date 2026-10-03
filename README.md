# Blister Bot 💊🤖
# Motivation
What if you didnt have to manually strip pils from medicine packets everytime you  had a cold?What if eldery people in nursing homes and living alone at home could be safely monitored and assisted even when there is no one around? And what if all of this was hands free and handled by speaking as if you were talking to a regular person,and to top it off, all offline,so your private talks remain within your circle?




Thats what blister bot was all about.Not only has AI become more capable,it has also become more efficient,and now even small models that can run on your old laptop with no dedicated gpu can run some great models for a variety of tasks including conversational chatbots,coding work,character recognition,speech to text and vice versa and facial recognition.All of this opens up the possibilites of creating useful things with intelligence without having an internet connection.


The only limitation was that we lacked  lightweight but powerful and cheap hardware that could help build these intelligence projects,and we were stuck to using tinyml on classic boards like esp32 and the arduino uno r4 boards which at the end of the day are just microcontrollers and lack the raw memory to hold complex workflows.Luckily,with the creation of the arduino uno q and other boards we finally have the hardware to pull off these ai hardware projects without having to compromise .



# So what is Blister Bot,really?







## Core Features
1. **Conversational LLM Interface**: Talk to Blister Bot naturally. It uses a local Qwen LLM for intelligence, Sherpa-ONNX for fast offline speech-to-text, and Piper for text-to-speech.
2. **Facial Recognition**: Say "add patient" and it will capture your face and store your medical profile using an LBPH face recognizer backed by SQLite.
3. **Automated Pill Extraction**: Say "I need paracetamol" and it will use OpenCV contour detection to locate the pill on the camera, and actuate a 3-axis mini CNC machine to trace and drill the blister out!

## Repository Structure
- **`code/`**: Contains the finalized, working system (Master Controller, CNC driver, AI modules).
- **`docs/`**: Documentation of our weekly progress and attempts.
- **`reference/`**: Deprecated scripts, old CAD models, and isolated experiments from early weeks.

## How to Run
1. Navigate to the `code/` directory.
2. Ensure you have the `STT`, `LLM`, and `TTS` models downloaded in `code/UNO/`.
3. Run the main loop:
   ```bash
   python3 master_controller.py
   ```
