#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./deploy_ai_terminal.sh <UNO_Q_IP_ADDRESS>"
    exit 1
fi

IP_ADDRESS=$1
USER="arduino" # Standard for Uno Q

echo "================================================="
echo "   Pushing AI Terminal Code to Arduino UNO Q     "
echo "================================================="

echo "[1/3] Creating target directories on Uno Q..."
ssh $USER@$IP_ADDRESS "mkdir -p ~/edge_terminal/Blister-bot-main-/week2/edge_agent"

echo "[2/3] Transferring Python Orchestrator and Wi-Fi Server..."
scp app_lab_terminal/main.py app_lab_terminal/lcd_server.py requirements_edge_terminal.txt $USER@$IP_ADDRESS:~/edge_terminal/

echo "[3/3] Transferring AI Agents and Tools..."
scp -r Blister-bot-main-/week2/edge_agent/* $USER@$IP_ADDRESS:~/edge_terminal/Blister-bot-main-/week2/edge_agent/
scp -r Blister-bot-main-/week2/speechtotext $USER@$IP_ADDRESS:~/edge_terminal/Blister-bot-main-/week2/ 2>/dev/null
scp -r Blister-bot-main-/week2/facerecog-unoq $USER@$IP_ADDRESS:~/edge_terminal/Blister-bot-main-/week2/ 2>/dev/null
scp -r Blister-bot-main-/week2/ocr $USER@$IP_ADDRESS:~/edge_terminal/Blister-bot-main-/week2/ 2>/dev/null

echo ""
echo "================================================="
echo "   Transfer Complete!                            "
echo "================================================="
echo "To run the AI on your Uno Q:"
echo "1. ssh arduino@$IP_ADDRESS"
echo "2. sudo apt-get update && sudo apt-get install -y python3-pip python3-opencv"
echo "3. cd ~/edge_terminal"
echo "4. pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --break-system-packages"
echo "5. pip3 install --no-cache-dir -r requirements_edge_terminal.txt pyserial transformers sounddevice scipy rapidocr-onnxruntime --break-system-packages"
echo "6. python3 main.py"
echo "================================================="
