import gc
import threading
import time
import os
import numpy as np
import sounddevice as sd
from llama_cpp import Llama
import sherpa_onnx
from piper import PiperVoice
import sys

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# STT Configuration
STT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "STT-streaming-zipformer-indian-en")
STT_SAMPLE_RATE = 16000
STT_FEATURE_DIM = 80
MIC_GAIN = 2.5        # Boosts microphone volume (increase if STT is inaccurate)

# LLM Configuration
LLM_MODEL_PATH = os.path.join(os.path.dirname(__file__), "qwen2.5-0.5b-instruct-q4_k_m.gguf")
LLM_N_CTX = 512       # Strictly 512 to save RAM
LLM_N_THREADS = 2     # Strictly 2 to save RAM
LLM_N_BATCH = 128     # Strictly 128 to save RAM

# TTS Configuration
TTS_MODEL_PATH = os.path.join(os.path.dirname(__file__), "en_US-lessac-low.onnx")
TTS_SAMPLE_RATE = 16000

# System Prompt
SYSTEM_PROMPT = "You are a concise medical assistant. Answer in 1 short sentence."

# ==============================================================================
# THREADING & MEMORY MANAGEMENT
# ==============================================================================
mic_active = threading.Event()
mic_active.set()

# ==============================================================================
# INITIALIZATION FUNCTIONS
# ==============================================================================

def init_llm():
    """Initializes the llama.cpp model with strict RAM constraints."""
    print("[INIT] Loading LLM (Qwen2.5-0.5B-Instruct-Q4_K_M)...")
    return Llama(
        model_path=LLM_MODEL_PATH,
        n_ctx=LLM_N_CTX,
        n_threads=LLM_N_THREADS,
        n_batch=LLM_N_BATCH,
        verbose=False  # Reduce console spam
    )

def init_stt():
    """Initializes the Sherpa-ONNX streaming recognizer with 1 thread."""
    print("[INIT] Loading STT (Indian English Streaming Zipformer)...")
    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=f"{STT_MODEL_DIR}/tokens.txt",
        encoder=f"{STT_MODEL_DIR}/encoder-epoch-10-avg-5-chunk-64-left-256.int8.onnx",
        decoder=f"{STT_MODEL_DIR}/decoder-epoch-10-avg-5-chunk-64-left-256.int8.onnx",
        joiner=f"{STT_MODEL_DIR}/joiner-epoch-10-avg-5-chunk-64-left-256.int8.onnx",
        num_threads=1,
        sample_rate=STT_SAMPLE_RATE,
        feature_dim=STT_FEATURE_DIM,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=2.4,
        rule2_min_trailing_silence=1.2,
        rule3_min_utterance_length=300.0,
    )

def init_tts():
    """Initializes the Piper TTS engine with a low-res ONNX model."""
    print("[INIT] Loading TTS (Piper en_US-lessac-low)...")
    return PiperVoice.load(TTS_MODEL_PATH)

# ==============================================================================
# PIPELINE FUNCTIONS
# ==============================================================================

def generate_response(llm, user_text):
    """Generates a text response using the local LLM."""
    prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_text}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    
    response = llm(
        prompt,
        max_tokens=64,
        stop=["<|im_end|>"],
        echo=False
    )
    return response['choices'][0]['text'].strip()

def speak_text(voice, text):
    """Synthesizes and plays audio using Piper TTS and sounddevice."""
    try:
        for chunk in voice.synthesize(text):
            sd.play(chunk.audio_int16_array, samplerate=TTS_SAMPLE_RATE, blocking=True)
    except Exception as e:
        print(f"[AUDIO ERROR] Failed to play audio: {e}")

# ==============================================================================
# MAIN EVENT LOOP
# ==============================================================================

def listen_and_transcribe(recognizer, mic_active):
    """Listens to the microphone and returns transcribed text when an endpoint is reached."""
    stream = recognizer.create_stream()
    
    device_info = sd.query_devices(sd.default.device[0], 'input')
    mic_sample_rate = int(device_info['default_samplerate'])
    
    result_text = None
    
    def audio_callback(indata, frames, time_info, status):
        if mic_active.is_set():
            chunk = indata[:, 0].copy()
            chunk = chunk - np.mean(chunk) # Remove hardware DC offset
            samples = chunk * MIC_GAIN
            samples = np.clip(samples, -1.0, 1.0)
            stream.accept_waveform(mic_sample_rate, samples)
            
    with sd.InputStream(channels=1, dtype="float32", samplerate=mic_sample_rate, callback=audio_callback):
        while True:
            if mic_active.is_set():
                while recognizer.is_ready(stream):
                    recognizer.decode_stream(stream)
                
                is_endpoint = recognizer.is_endpoint(stream)
                text = recognizer.get_result(stream)
                
                if text and is_endpoint:
                    result_text = text
                    recognizer.reset(stream)
                    break
            time.sleep(0.05)
            
    return result_text
