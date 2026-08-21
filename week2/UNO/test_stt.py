import sherpa_onnx
recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder="sherpa-onnx-whisper-base.en/base.en-encoder.int8.onnx",
    decoder="sherpa-onnx-whisper-base.en/base.en-decoder.int8.onnx",
    tokens="sherpa-onnx-whisper-base.en/base.en-tokens.txt",
    num_threads=1
)
stream = recognizer.create_stream()
import wave
with wave.open("sherpa-onnx-whisper-base.en/test_wavs/0.wav", "rb") as w:
    frames = w.readframes(w.getnframes())
    import numpy as np
    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    stream.accept_waveform(16000, audio)
    recognizer.decode_stream(stream)
    print("RES:", stream.result)
print('text is:', stream.result.text)
