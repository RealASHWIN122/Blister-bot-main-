#!/bin/bash
set -e

echo "[1/6] Installing dependencies..."
if ! ~/miniconda3/bin/conda info --envs | grep -q "icefall_env"; then
    echo "Creating Conda environment for training with Python 3.10..."
    ~/miniconda3/bin/conda create -y -n icefall_env python=3.10
fi
source ~/miniconda3/etc/profile.d/conda.sh
conda activate icefall_env

pip install -q "numpy<2" --force-reinstall
pip install -q torch==2.1.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -q k2==1.24.4.dev20240223+cpu.torch2.1.2 -f https://k2-fsa.github.io/k2/cpu.html
pip install -q lhotse soundfile sentencepiece tensorboard

echo "[2/6] Preparing Dataset Manifests..."
# Generate lhotse manifests using a python script
python3 << 'EOF'
import os
import lhotse
from lhotse import RecordingSet, Recording, SupervisionSet, SupervisionSegment

dataset_dir = os.path.abspath("dataset")
recordings = []
supervisions = []

with open(os.path.join(dataset_dir, "transcripts.txt"), "r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split(" ", 1)
    if len(parts) >= 2:
        wav_name = parts[0] + ".wav"
        text = "|".join(parts[1:])
        wav_path = os.path.join(dataset_dir, wav_name)
        
        if os.path.exists(wav_path):
            rec = Recording.from_file(wav_path)
            recordings.append(rec)
            
            sup = SupervisionSegment(
                id=wav_name.replace(".wav", ""),
                recording_id=rec.id,
                start=0.0,
                duration=rec.duration,
                channel=0,
                text=text,
                language="English"
            )
            supervisions.append(sup)

rec_set = RecordingSet.from_recordings(recordings)
sup_set = SupervisionSet.from_segments(supervisions)

os.makedirs("custom_corpus", exist_ok=True)
rec_set.to_file("custom_corpus/custom_corpus_recordings.jsonl.gz")
sup_set.to_file("custom_corpus/custom_corpus_supervisions.jsonl.gz")

from lhotse import CutSet
cuts = CutSet.from_manifests(recordings=rec_set, supervisions=sup_set)
cuts.to_file("custom_corpus/cuts_train.jsonl.gz")

print(f"Prepared {len(recordings)} recordings.")
EOF

echo "[3/6] Setting up Icefall..."
if [ ! -d "icefall" ]; then
    git clone https://github.com/k2-fsa/icefall
fi
cd icefall
pip install -r requirements.txt -q
cd ..

export PYTHONPATH=$(pwd)/icefall:$PYTHONPATH

echo "[4/6] Downloading Pre-trained Checkpoint and BPE model..."
cd icefall/egs/librispeech/ASR
if [ ! -f "../../../pretrained.pt" ]; then
    wget -q --show-progress https://huggingface.co/Zengwei/icefall-asr-librispeech-zipformer-2023-05-15/resolve/main/exp/pretrained.pt -O ../../../pretrained.pt
fi

if [ ! -d "data/lang_bpe_500" ]; then
    mkdir -p data/lang_bpe_500
    wget -q --show-progress https://huggingface.co/Zengwei/icefall-asr-librispeech-zipformer-2023-05-15/resolve/main/data/lang_bpe_500/bpe.model -O data/lang_bpe_500/bpe.model
    wget -q --show-progress https://huggingface.co/Zengwei/icefall-asr-librispeech-zipformer-2023-05-15/resolve/main/data/lang_bpe_500/tokens.txt -O data/lang_bpe_500/tokens.txt
fi
cd ../../../../custom_corpus
cp cuts_train.jsonl.gz cuts_S.jsonl.gz
cp cuts_train.jsonl.gz cuts_DEV.jsonl.gz
cp cuts_train.jsonl.gz librispeech_cuts_dev-clean.jsonl.gz
cp cuts_train.jsonl.gz librispeech_cuts_test-clean.jsonl.gz
cp cuts_train.jsonl.gz librispeech_cuts_dev-other.jsonl.gz
cp cuts_train.jsonl.gz librispeech_cuts_test-other.jsonl.gz
cd ../icefall/egs/librispeech/ASR

# Downgrade numpy right before training to avoid other packages upgrading it
pip install -q "numpy<2" --force-reinstall

echo "[5/6] Running PyTorch Fine-Tuning (v2 - low LR, 4 epochs)..."
python3 ./zipformer/finetune.py \
  --manifest-dir ../../../../custom_corpus \
  --start-epoch 1 \
  --num-epochs 4 \
  --use-fp16 0 \
  --do-finetune 1 \
  --base-lr 0.00045 \
  --enable-musan False \
  --on-the-fly-feats True \
  --input-strategy AudioSamples \
  --drop-last False \
  --exp-dir zipformer/exp_finetune_v2 \
  --finetune-ckpt ../../../pretrained.pt

echo "[6/6] Exporting to ONNX format..."
python3 ./zipformer/export-onnx.py \
  --epoch 4 \
  --avg 2 \
  --use-averaged-model True \
  --exp-dir zipformer/exp_finetune_v2 \
  --tokens data/lang_bpe_500/tokens.txt

echo "[7/7] Deploying fine-tuned model..."
DEPLOY_DIR="../../../../UNO/STT-non-streaming-zipformer-finetuned"
mkdir -p "$DEPLOY_DIR"
cp zipformer/exp_finetune_v2/encoder-*.onnx "$DEPLOY_DIR/"
cp zipformer/exp_finetune_v2/decoder-*.onnx "$DEPLOY_DIR/"
cp zipformer/exp_finetune_v2/joiner-*.onnx "$DEPLOY_DIR/"
cp data/lang_bpe_500/tokens.txt "$DEPLOY_DIR/"
cp data/lang_bpe_500/bpe.model "$DEPLOY_DIR/"

echo "Fine-Tuning v2 Complete! Model deployed to $DEPLOY_DIR"
