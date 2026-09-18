#!/bin/bash
# setup.sh
# Downloads the required memory-optimized models and installs dependencies

# 0. Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y libportaudio2 portaudio19-dev

# 1. Install dependencies
echo "Installing pip dependencies..."
pip install --upgrade pip
pip install sherpa-onnx llama-cpp-python piper-tts sounddevice numpy

# 2. Download Sherpa-ONNX STT model (Indian English Streaming Zipformer)
echo "Downloading Sherpa-ONNX Indian English model..."
rm -rf sherpa-onnx-streaming-zipformer-ar_en*
mkdir -p STT-streaming-zipformer-indian-en
cd STT-streaming-zipformer-indian-en
wget -q https://huggingface.co/Akshatkasera007/STT-streaming-zipformer-indian-en/resolve/main/tokens.txt
wget -q https://huggingface.co/Akshatkasera007/STT-streaming-zipformer-indian-en/resolve/main/encoder-epoch-10-avg-5-chunk-64-left-256.int8.onnx
wget -q https://huggingface.co/Akshatkasera007/STT-streaming-zipformer-indian-en/resolve/main/decoder-epoch-10-avg-5-chunk-64-left-256.int8.onnx
wget -q https://huggingface.co/Akshatkasera007/STT-streaming-zipformer-indian-en/resolve/main/joiner-epoch-10-avg-5-chunk-64-left-256.int8.onnx
cd ..

# 3. Download LLM (Qwen2.5-0.5B-Instruct-Q4_K_M.gguf)
echo "Downloading LLM model..."
wget https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf -O qwen2.5-0.5b-instruct-q4_k_m.gguf

# 4. Download Piper TTS model (low quality, en_US-lessac-low)
echo "Downloading Piper TTS model..."
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/low/en_US-lessac-low.onnx -o en_US-lessac-low.onnx
curl -L https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/low/en_US-lessac-low.onnx.json -o en_US-lessac-low.onnx.json

echo "Setup complete!"
