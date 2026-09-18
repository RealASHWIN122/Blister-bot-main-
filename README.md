# Blister Bot 💊🤖

Blister Bot is a fully automated, voice-controlled medical assistant and CNC drilling machine designed to help users interact with a medication inventory, add patients using facial recognition, and extract pills from blister packs automatically.

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
