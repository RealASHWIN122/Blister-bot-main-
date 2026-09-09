#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./deploy_appliance.sh <NEW_UNO_Q_IP_ADDRESS>"
    exit 1
fi

IP_ADDRESS=$1
USER="arduino"

echo "================================================="
echo "   Deploying Face Recognition Appliance to Uno Q "
echo "================================================="

echo "[1/3] Creating target directories on Uno Q..."
ssh $USER@$IP_ADDRESS "mkdir -p ~/appliance_terminal/Blister-bot-main-/week2/facerecog-unoq/faces"

echo "[2/3] Transferring Appliance Script..."
scp appliance_terminal/appliance.py $USER@$IP_ADDRESS:~/appliance_terminal/

echo "[3/3] Transferring Week 2 Models (Database & Haar Cascade)..."
scp -r Blister-bot-main-/week2/facerecog-unoq/attendance.db \
       Blister-bot-main-/week2/facerecog-unoq/haarcascade_frontalface_default.xml \
       Blister-bot-main-/week2/facerecog-unoq/faces/ \
       $USER@$IP_ADDRESS:~/appliance_terminal/Blister-bot-main-/week2/facerecog-unoq/

echo ""
echo "================================================="
echo "   Transfer Complete!                            "
echo "================================================="
echo "To run the Face Recognition Appliance on your Uno Q:"
echo "1. ssh arduino@$IP_ADDRESS"
echo "2. sudo apt-get update && sudo apt-get install -y python3-pip python3-opencv"
echo "3. pip3 install pyserial numpy --break-system-packages"
echo "4. python3 ~/appliance_terminal/appliance.py"
echo "================================================="
