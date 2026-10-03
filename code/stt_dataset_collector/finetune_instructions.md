# Fine-Tuning Instructions for Sherpa-ONNX Zipformer

Because our edge model (Sherpa-ONNX Zipformer) is heavily compressed and optimized for C++ inference, we cannot fine-tune it directly on the edge device. Instead, we use the generated dataset to fine-tune the original PyTorch model using the `icefall` framework on a powerful desktop or cloud GPU.

## Prerequisites
You will need a Linux machine (your laptop is fine) with:
- NVIDIA GPU (RTX 3060 or better recommended)
- CUDA Toolkit installed
- Docker (optional but highly recommended)

## Step 1: Install k2 and Icefall
Clone the Icefall repository, which contains the training scripts for our Zipformer model.
```bash
git clone https://github.com/k2-fsa/icefall
cd icefall
pip install -r requirements.txt
export PYTHONPATH=$(pwd):$PYTHONPATH
```

## Step 2: Prepare the Dataset
The data you collected using this web app is currently stored in `dataset/`. It contains `.wav` files and a `transcripts.txt` file.

Icefall uses the `lhotse` library for data preparation. We need to convert our directory into lhotse manifests.
```bash
# Install lhotse
pip install lhotse

# Create manifests
lhotse prepare audio-dir dataset/ custom_corpus
```
This will create `custom_corpus_recordings.jsonl.gz` and `custom_corpus_supervisions.jsonl.gz`.

## Step 3: Download the Pre-trained Checkpoint
Since we are fine-tuning the Indian English Zipformer model, download the pre-trained PyTorch checkpoint:
```bash
wget https://huggingface.co/csukuangfj/icefall-asr-librispeech-zipformer-2023-05-15/resolve/main/exp/pretrained.pt
```
*(Note: Replace with the exact HuggingFace URL of the PyTorch checkpoint matching your ONNX model).*

## Step 4: Run Fine-Tuning
Run the training script, pointing it to your new dataset and the pre-trained checkpoint. 
```bash
# Inside the icefall directory
cd egs/librispeech/ASR
./zipformer/train.py \
  --manifest-dir ../../../custom_corpus \
  --start-epoch 1 \
  --num-epochs 10 \
  --use-fp16 1 \
  --finetune 1 \
  --base-model ../../../pretrained.pt
```

## Step 5: Export Back to ONNX
Once training completes, export the new model weights to ONNX so they can be loaded by our `sherpa-onnx` engine on the Uno Q.
```bash
./zipformer/export.py \
  --epoch 10 \
  --avg 5 \
  --jit 0 \
  --onnx 1 \
  --exp-dir zipformer/exp
```
This will generate the `encoder-*.onnx`, `decoder-*.onnx`, and `joiner-*.onnx` files.

## Step 6: Deploy
Copy the newly generated `.onnx` files and the `tokens.txt` file back to the `code/UNO/STT-streaming-zipformer-indian-en` folder and restart your edge device!
