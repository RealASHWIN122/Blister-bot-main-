#!/bin/bash

# Clear the screen for a clean interface
clear

echo "================================================="
echo "   Arduino UNO Q - Master Deployment Script      "
echo "================================================="
echo ""
echo "This script will push your AI facial recognition system"
echo "and all required heavy models directly onto the board."
echo ""
echo "WARNING: The installation on the board's ARM processor"
echo "may take 30-60 minutes to compile dlib. Do not close"
echo "this window!"
echo ""

# Get the IP address from the user
read -p "Please enter the IP address of your Arduino UNO Q: " IP_ADDRESS

echo ""
echo "Step 1: Transferring Python Scripts..."
echo "You may be prompted for the 'root' password."

# Create directory on the board
ssh root@$IP_ADDRESS "mkdir -p ~/facerecog-unoq/faces"

# Secure Copy (SCP) the files to the board
scp database.py recognizer.py root@$IP_ADDRESS:~/facerecog-unoq/

echo ""
echo "Step 2: Installing System Libraries on Arduino..."
echo "You may be prompted for the password again."
ssh -t root@$IP_ADDRESS << 'EOF'
    echo "Updating packages..."
    apt-get update
    echo "Installing C++ compilation tools and OpenBLAS (required for face_recognition)..."
    apt-get install -y build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev libopenblas-dev python3-pip python3-dev
    
    echo ""
    echo "----------------------------------------"
    echo "Step 3: Installing Deep Learning Libraries..."
    echo "THIS STEP CAN TAKE UP TO AN HOUR. DO NOT DISCONNECT."
    echo "----------------------------------------"
    # Install headless OpenCV to avoid missing X11 libraries on the board
    pip3 install --break-system-packages opencv-python-headless face_recognition ollama numpy
    
    echo ""
    echo "----------------------------------------"
    echo "Step 4: Installing Ollama AI Engine..."
    echo "----------------------------------------"
    curl -fsSL https://ollama.com/install.sh | sh
    
    # Start Ollama service in the background
    systemctl start ollama || true
    
    echo ""
    echo "----------------------------------------"
    echo "Step 5: Downloading AI Models..."
    echo "Downloading Gemma 2B (Language)..."
    ollama pull gemma:2b
    echo "Downloading Moondream (Vision)..."
    ollama pull moondream
    
    echo ""
    echo "================================================="
    echo "      DEPLOYMENT & INSTALLATION COMPLETE!        "
    echo "================================================="
    echo "You can now SSH into your board and run the app:"
    echo "1. ssh root@YOUR_IP"
    echo "2. cd ~/facerecog-unoq"
    echo "3. python3 recognizer.py"
    
    # Exit SSH session
    exit
EOF
