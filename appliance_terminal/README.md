# Blister-Bot Appliance Terminal

The Appliance Terminal is a Flask-based AI system designed to run on the **Arduino Uno Q**. It transforms the board into an intelligent medicine-scanning assistant featuring Optical Character Recognition (OCR), Face Recognition, and an ultra-fast Voice Assistant (Speech-to-Text & Text-to-Speech).

## Core Features

### 1. Medicine Scanner (OCR)
- Uses `rapidocr-onnxruntime` to continuously monitor the camera feed.
- Extracts text dynamically from medicine packets and displays the detected text on the web interface.
- Automatically reads the detected medicine names out loud using the TTS engine.

### 2. Lightning-Fast Voice Assistant (STT & TTS)
The voice pipeline was heavily optimized for the embedded CPU of the Arduino Uno Q:
- **Speech-to-Text (STT)**: 
  - Upgraded from HuggingFace `transformers` to **`faster-whisper`** (powered by `CTranslate2`).
  - Uses `INT8` quantization and the `tiny.en` model to achieve blistering fast **1:1 real-time transcription** (a 5-second voice clip transcribes in ~5 seconds).
  - Implements **ALSA hardware resampling** (`plughw:0,0`) to perfectly convert the USB microphone's native sample rate to the strictly required `16000Hz`. This completely eliminates the "hallucinations" (random ghost phrases) that Whisper models often produce when fed distorted audio.
  - Automatically filters out silence using `faster-whisper`'s advanced Voice Activity Detection (VAD).
- **Text-to-Speech (TTS)**:
  - Uses `edge-tts` to generate natural-sounding speech and `ffplay` to play it immediately through the audio output.
  - The appliance automatically repeats what you say when the microphone is manually triggered, and reads out scanned text.

### 3. Face Recognition & Attendance
- Utilizes OpenCV (`opencv-contrib-python-headless`) with Haar cascades and the `LBPHFaceRecognizer`.
- Detects faces and cross-references them against a trained dataset (`known_faces`).
- Logs attendance and interactions to a local SQLite database (`attendance.db`).

### 4. Flask Web Interface
- The entire system is hosted locally via Flask on port `5000`.
- Serves the live camera feed (MJPEG streaming).
- Provides a `/trigger_mic` REST endpoint to manually initiate a 5-second voice recording and transcription.

## Deployment & Setup

The system is deployed to the Arduino Uno Q using the `setup_appliance.sh` script located in the project root. The setup script performs the following fully automated tasks:

1. **Space Management**: Cleans up unused files (e.g., old Ollama models) on the board's filesystem.
2. **File Transfer**: Uses `scp` to push `appliance.py`, the `attendance.db`, and the face datasets directly to the board.
3. **Dependency Installation**: Installs the optimized dependency stack globally (`--break-system-packages`) including `faster-whisper`, `rapidocr-onnxruntime`, `Flask`, `edge-tts`, and `opencv`.
4. **Systemd Service**: Creates and enables `appliance.service` so the AI terminal automatically starts silently in the background on boot.

## How to Test the Microphone
1. Ensure the board is powered and connected to the network.
2. Open the web interface at `http://<ARDUINO_IP>:5000`.
3. Wait ~10 seconds for the `faster-whisper` model to silently load in the background.
4. Click the **"🎤 Speak"** button, talk into the USB mic for 5 seconds, and watch the text appear on the screen and echo back to you.

## Recent Migrations
- **Migrated away from `transformers`**: Swapping to `faster-whisper` reduced STT processing time by an order of magnitude. An attempt to use `base.en` was made, but the 45-second latency was unacceptable for a voice assistant. Reverting to `tiny.en` within `faster-whisper` solved all latency issues while maintaining VAD accuracy.
- **ALSA `plughw` fix**: Swapped `hw:0,0` for `plughw:0,0` in the `arecord` command to allow the Linux kernel to handle audio resampling, preventing severe Whisper hallucination bugs.
