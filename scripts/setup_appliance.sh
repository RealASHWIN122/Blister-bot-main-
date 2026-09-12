#!/bin/bash

# Clear the screen for a clean interface
clear

echo "================================================="
echo "   Arduino UNO Q - AI Appliance Setup Script     "
echo "================================================="
echo ""
echo "This script will push the updated AI script to the board"
echo "and set it to run automatically on boot."
echo ""

read -p "Please enter the IP address of your Arduino UNO Q: " IP_ADDRESS

echo ""
echo "Step 1: Freeing up space on the board..."
echo "You will be prompted for the 'root' password (try: arduino, root, or just press Enter)."
ssh root@$IP_ADDRESS "rm -rf /usr/share/ollama/.ollama/models /root/.ollama /var/lib/ollama && apt-get clean"

echo ""
echo "Step 2: Transferring AI Scripts to Board..."

# Ensure directories exist
ssh root@$IP_ADDRESS "mkdir -p ~/appliance_terminal"

# SCP the required files
scp /home/me/Videos/arduinohack/appliance_terminal/appliance.py root@$IP_ADDRESS:~/appliance_terminal/
scp /home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/attendance.db root@$IP_ADDRESS:~/appliance_terminal/
scp -r /home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/faces root@$IP_ADDRESS:~/appliance_terminal/

echo ""
echo "Step 2: Installing Dependencies and Creating Service..."
echo "You may be prompted for the password again."
ssh -t root@$IP_ADDRESS << 'EOF'
    echo "Installing Python dependencies (Flask, opencv, rapidocr, edge-tts, transformers, faster-whisper)..."
    # Using --break-system-packages because the Uno Q runs a globally managed environment by default
    pip3 install Flask opencv-contrib-python-headless==4.14.0.94 rapidocr-onnxruntime edge-tts transformers faster-whisper soundfile pyserial numpy face_recognition --break-system-packages

    echo "Creating systemd service for the AI Appliance..."
    cat << 'SVC' > /etc/systemd/system/appliance.service
[Unit]
Description=Arduino Uno Q Face Recognition Appliance
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/appliance_terminal/appliance.py
WorkingDirectory=/root/appliance_terminal
StandardOutput=inherit
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
SVC

    echo "Reloading systemd and starting service..."
    systemctl daemon-reload
    systemctl enable appliance.service
    systemctl restart appliance.service
    
    echo "Checking service status:"
    systemctl status appliance.service --no-pager | head -n 10
    
    echo ""
    echo "================================================="
    echo "      SETUP COMPLETE!                            "
    echo "================================================="
    echo "The AI script is now running in the background as root."
    echo "It will automatically start every time you plug the board into the wall."
    exit
EOF
