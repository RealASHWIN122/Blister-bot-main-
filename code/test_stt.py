import sherpa_onnx
import os
import wave
import numpy as np

STT_MODEL_DIR = os.path.join(os.path.dirname(__file__), 'code', 'UNO', 'STT-non-streaming-zipformer-finetuned')

recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
    tokens=f"{STT_MODEL_DIR}/tokens.txt",
    encoder=f"{STT_MODEL_DIR}/encoder-epoch-5-avg-2.onnx",
    decoder=f"{STT_MODEL_DIR}/decoder-epoch-5-avg-2.onnx",
    joiner=f"{STT_MODEL_DIR}/joiner-epoch-5-avg-2.onnx",
    num_threads=1,
    sample_rate=16000,
    feature_dim=80,
)

print("Fine-tuned v2 model loaded. Testing on dataset...")

dataset_dir = os.path.join(os.path.dirname(__file__), 'code', 'stt_dataset_collector', 'dataset')
transcript_path = os.path.join(dataset_dir, 'transcripts.txt')

# Load transcripts
transcripts = {}
with open(transcript_path) as f:
    for line in f:
        parts = line.strip().split(' ', 1)
        if len(parts) >= 2:
            transcripts[parts[0]] = parts[1]

wav_files = sorted([f for f in os.listdir(dataset_dir) if f.endswith('.wav')])

correct = 0
total = 0
for wav_name in wav_files[:15]:
    wav_path = os.path.join(dataset_dir, wav_name)
    with wave.open(wav_path, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Pad short audio to at least 1 second
    min_samples = 16000
    if len(samples) < min_samples:
        samples = np.concatenate([samples, np.zeros(min_samples - len(samples), dtype=np.float32)])
    
    stream = recognizer.create_stream()
    stream.accept_waveform(16000, samples)
    recognizer.decode_stream(stream)
    
    key = wav_name.replace('.wav', '')
    expected = transcripts.get(key, '???')
    result = stream.result.text.strip()
    match = '✓' if result.lower() == expected.lower() else '✗'
    if result.lower() == expected.lower():
        correct += 1
    total += 1
    
    print(f"{match} {wav_name:20s} | Expected: '{expected:30s}' | Got: '{result}'")

print(f"\nAccuracy: {correct}/{total} ({100*correct/total:.1f}%)")
