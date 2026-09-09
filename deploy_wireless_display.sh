#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./deploy_wireless_display.sh <NEW_UNO_Q_IP_ADDRESS>"
    exit 1
fi

IP_ADDRESS=$1
USER="arduino" # Standard for Uno Q

echo "================================================="
echo "   Pushing Wireless Display Code to Uno Q        "
echo "================================================="

echo "[1/2] Creating target directories on Uno Q..."
ssh $USER@$IP_ADDRESS "mkdir -p ~/edge_terminal"

echo "[2/2] Transferring Wi-Fi Server Script..."
scp app_lab_terminal/lcd_server.py $USER@$IP_ADDRESS:~/edge_terminal/

echo ""
echo "================================================="
echo "   Transfer Complete!                            "
echo "================================================="
echo "Since we moved to the Wireless Architecture, you DO NOT need to"
echo "install all those massive AI libraries on the board anymore!"
echo ""
echo "To run the Display Server on your new Uno Q:"
echo "1. ssh arduino@$IP_ADDRESS"
echo "2. sudo apt-get update && sudo apt-get install -y python3-pip"
echo "3. pip3 install pyserial --break-system-packages"
echo "4. python3 ~/edge_terminal/lcd_server.py"
echo "================================================="
