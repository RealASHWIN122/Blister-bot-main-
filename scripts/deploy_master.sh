#!/bin/bash

echo "================================================="
echo "   Pushing Offline Master Controller to Board    "
echo "================================================="

echo "[1/4] Creating target directories on board..."
adb shell "mkdir -p /home/arduino/Blister-bot-main-/week2/UNO"
adb shell "mkdir -p /home/arduino/Blister-bot-main-/week2/facerecog-unoq"
adb shell "mkdir -p /home/arduino/Blister-bot-main-/week2/blister_detector"
adb shell "mkdir -p /home/arduino/Blister-bot-main-/stepper_motor_controller"
adb shell "mkdir -p /home/arduino/Blister-bot-main-/appliance_terminal"

echo "[2/4] Pushing Master Controller and Medical DB..."
adb push master_controller.py /home/arduino/Blister-bot-main-/
adb push medical_database.json /home/arduino/Blister-bot-main-/

echo "[3/4] Pushing Offline AI Models (This will take a few minutes)..."
adb push week2/UNO/* /home/arduino/Blister-bot-main-/week2/UNO/

echo "[4/4] Pushing Modules..."
adb push week2/facerecog-unoq/* /home/arduino/Blister-bot-main-/week2/facerecog-unoq/
adb push week2/blister_detector/* /home/arduino/Blister-bot-main-/week2/blister_detector/

echo "================================================="
echo "   Transfer Complete!                            "
echo "================================================="
echo "To run the controller on the board, use:"
echo "adb shell"
echo "cd /home/arduino/Blister-bot-main-"
echo "python3 master_controller.py"
echo "================================================="
