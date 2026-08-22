#!/bin/bash

# Clear the screen for a clean interface
clear

echo "================================================="
echo "   Edge Impulse C++ Model Deployment Script      "
echo "================================================="
echo ""
echo "This script will push your Edge Impulse C++ server"
echo "to the UNO Q board and compile it."
echo ""

read -p "Please enter the IP address of your UNO Q: " IP_ADDRESS

echo ""
echo "Step 1: Transferring C++ files to the board..."
echo "You may be prompted for the 'root' password."

# Create directory on the board
ssh root@$IP_ADDRESS "mkdir -p ~/action-recog-cpp"

# Secure Copy (SCP) the files to the board
scp -r action-recog-cpp-mcu-v2-impulse-#1/* root@$IP_ADDRESS:~/action-recog-cpp/

echo ""
echo "Step 2: Compiling the model server on the board..."
echo "You may be prompted for the password again."
ssh -t root@$IP_ADDRESS << 'EOF'
    echo "Updating packages and installing C++ tools..."
    apt-get update
    apt-get install -y build-essential make
    
    echo ""
    echo "----------------------------------------"
    echo "Compiling the Edge Impulse Server..."
    echo "THIS STEP MAY TAKE A FEW MINUTES. DO NOT DISCONNECT."
    echo "----------------------------------------"
    
    cd ~/action-recog-cpp
    make clean
    make -j4
    
    echo ""
    echo "================================================="
    echo "      DEPLOYMENT & INSTALLATION COMPLETE!        "
    echo "================================================="
    echo "You can now run the server on your board:"
    echo "1. ssh root@YOUR_IP"
    echo "2. cd ~/action-recog-cpp"
    echo "3. ./model_server"
    
    # Exit SSH session
    exit
EOF
