# Week 8: Master Controller & Final System

During Week 8 (Sep 15 - Sep 21), we brought everything together to form the autonomous Blister Bot.

## Accomplishments
- **Master Controller**: Developed `master_controller.py`, which integrates our offline LLM (Qwen), Speech-to-Text (Sherpa-ONNX), Text-to-Speech (Piper), and OpenCV Pill detection.
- **Dynamic CNC Integration**: Merged the CNC controller so the bot can verbally request pills, visually detect their boundary contours, and instruct the gantry to physically pierce and trace the boundary to extract them.
- **Final Hardware Architecture**: Finalized the remaining CAD support files (like `blissupport.stl` and `medicinewheelstand.stl`) which are stored directly in the root `cad/` directory.

The finalized, working system is contained entirely inside the `code/` folder.
