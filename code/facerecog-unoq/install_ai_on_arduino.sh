#!/bin/bash

# Clear the screen for a clean interface
clear

echo "================================================="
echo "   Arduino UNO Q - Local AI (Gemma) Installer    "
echo "================================================="
echo ""
echo "This script will connect to your Arduino UNO Q and install"
echo "Ollama and the Gemma 2B AI model automatically."
echo ""

# Get the IP address from the user
read -p "Please enter the IP address of your Arduino UNO Q: " IP_ADDRESS

echo ""
echo "Connecting to $IP_ADDRESS..."
echo "Note: You may be prompted to enter the 'root' password for your board."
echo ""

# Connect via SSH and run the installation commands
ssh -t root@$IP_ADDRESS << 'EOF'
    echo "----------------------------------------"
    echo "Installing Ollama AI Engine..."
    echo "----------------------------------------"
    curl -fsSL https://ollama.com/install.sh | sh
    
    echo ""
    echo "----------------------------------------"
    echo "Downloading and starting Gemma 2B..."
    echo "This may take a few minutes depending on your internet speed."
    echo "----------------------------------------"
    ollama run gemma:2b
    
    # Exit SSH session when they quit Ollama
    exit
EOF

echo ""
echo "================================================="
echo "             Installation Complete!              "
echo "================================================="
