#!/bin/bash
echo "Installing C++ compilation tools and OpenBLAS (required for face_recognition)..."
apt-get update
apt-get install -y build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev libopenblas-dev python3-pip python3-dev

echo "Installing Deep Learning Libraries..."
pip3 install --break-system-packages opencv-python-headless face_recognition ollama numpy

echo "Installing Ollama AI Engine..."
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama || true

echo "Downloading AI Models (Gemma & Moondream)..."
ollama pull gemma:2b
ollama pull moondream

echo "ALL DONE! You can now run 'python3 recognizer.py' in the facerecog-unoq folder."
