import gc
import threading
import time
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
STT_MODEL_DIR = "STT-streaming-zipformer-indian-en"
STT_SAMPLE_RATE = 16000
STT_FEATURE_DIM = 80
MIC_GAIN = 2.5        # Boosts microphone volume (increase if STT is inaccurate)

# LLM Configuration
LLM_MODEL_PATH = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
LLM_N_CTX = 512       # Strictly 512 to save RAM
LLM_N_THREADS = 2     # Strictly 2 to save RAM
LLM_N_BATCH = 128     # Strictly 128 to save RAM

# TTS Configuration
TTS_MODEL_PATH = "en_US-lessac-low.onnx"
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
    for chunk in voice.synthesize(text):
        sd.play(chunk.audio_int16_array, samplerate=TTS_SAMPLE_RATE, blocking=True)

# ==============================================================================
# MAIN EVENT LOOP
# ==============================================================================

def main():
    print("=====================================")
    print(" MEDICAL ASSISTANT SETUP")
    print("=====================================")
    
    print("Select Operation Mode:")
    print("1: AI Assistant (Full Medical AI)")
    print("2: Type-to-Speak (Text -> Voice Utility)")
    print("3: Speak-to-Type (Voice -> Text Utility)")
    op_mode = input("Enter choice (1/2/3) [default 1]: ").strip() or "1"

    if op_mode == "1":
        print("\nSelect AI Input Mode:")
        print("1: Voice (Microphone)")
        print("2: Text (Keyboard)")
        input_choice = input("Enter choice (1/2) [default 1]: ").strip() or "1"
        
        print("\nSelect AI Output Mode:")
        print("1: Voice (Speaker)")
        print("2: Text (Console Only)")
        output_choice = input("Enter choice (1/2) [default 1]: ").strip() or "1"
        
        use_stt = (input_choice == "1")
        use_tts = (output_choice == "1")
        use_llm = True
    elif op_mode == "2":
        use_stt = False
        use_tts = True
        use_llm = False
    elif op_mode == "3":
        use_stt = True
        use_tts = False
        use_llm = False
    else:
        print("Invalid choice. Defaulting to AI Assistant.")
        use_stt, use_tts, use_llm = True, True, True
    
    print("\n=====================================")
    
    # 1. Initialize only the required models
    llm = init_llm() if use_llm else None
    recognizer = init_stt() if use_stt else None
    voice = init_tts() if use_tts else None
    
    print("\n[SYSTEM READY]")
    
    if op_mode == "2":
        # Type-to-Speak loop
        print("Type-to-Speak Mode Active. Type text below (type 'exit' to stop).\n")
        while True:
            try:
                user_text = input("[TEXT]: ").strip()
                if not user_text:
                    continue
                if user_text.lower() in ['exit', 'quit']:
                    print("\n[SYSTEM]: Shutting down...")
                    break
                
                print("[SYSTEM]: Speaking...")
                speak_text(voice, user_text)
                
                gc.collect()
            except (KeyboardInterrupt, EOFError):
                print("\n[SYSTEM]: Shutting down...")
                break
                
    elif op_mode == "3":
        # Speak-to-Type loop
        print("Speak-to-Type Mode Active. Listening for speech... (Press Ctrl+C to stop)\n")
        stream = recognizer.create_stream()
        
        device_info = sd.query_devices(sd.default.device[0], 'input')
        mic_sample_rate = int(device_info['default_samplerate'])
        print(f"[SYSTEM]: Capturing at native sample rate: {mic_sample_rate} Hz (Gain: {MIC_GAIN}x)")
        
        def dictation_callback(indata, frames, time_info, status):
            if mic_active.is_set():
                chunk = indata[:, 0].copy()
                chunk = chunk - np.mean(chunk) # Remove hardware DC offset
                samples = chunk * MIC_GAIN
                samples = np.clip(samples, -1.0, 1.0)
                stream.accept_waveform(mic_sample_rate, samples)
                
        try:
            with sd.InputStream(channels=1, dtype="float32", samplerate=mic_sample_rate, callback=dictation_callback):
                while True:
                    if mic_active.is_set():
                        while recognizer.is_ready(stream):
                            recognizer.decode_stream(stream)
                        
                        is_endpoint = recognizer.is_endpoint(stream)
                        text = recognizer.get_result(stream)
                        
                        if text:
                            print(f"\r[Listening...]: {text}                             ", end="", flush=True)
                        
                        if text and is_endpoint:
                            print(f"\n\n[DICTATION]: {text}\n")
                            recognizer.reset(stream)
                            gc.collect()
                            
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[SYSTEM]: Shutting down...")
            sys.exit(0)
            
    elif op_mode == "1" and use_stt:
        print("AI Assistant (Voice Input). Listening for speech... (Press Ctrl+C to stop)\n")
        stream = recognizer.create_stream()
        
        device_info = sd.query_devices(sd.default.device[0], 'input')
        mic_sample_rate = int(device_info['default_samplerate'])
        print(f"[SYSTEM]: Capturing at native sample rate: {mic_sample_rate} Hz (Gain: {MIC_GAIN}x)")
        
        def audio_callback(indata, frames, time_info, status):
            if mic_active.is_set():
                chunk = indata[:, 0].copy()
                chunk = chunk - np.mean(chunk) # Remove hardware DC offset
                samples = chunk * MIC_GAIN
                samples = np.clip(samples, -1.0, 1.0)
                stream.accept_waveform(mic_sample_rate, samples)
                
        try:
            with sd.InputStream(channels=1, dtype="float32", samplerate=mic_sample_rate, callback=audio_callback):
                while True:
                    if mic_active.is_set():
                        while recognizer.is_ready(stream):
                            recognizer.decode_stream(stream)
                        
                        is_endpoint = recognizer.is_endpoint(stream)
                        text = recognizer.get_result(stream)
                        
                        if text:
                            print(f"\r[Listening...]: {text}                             ", end="", flush=True)
                        
                        if text and is_endpoint:
                            print(f"\n\n[USER]: {text}")
                            
                            mic_active.clear()
                            recognizer.reset(stream)
                            
                            print("[SYSTEM]: Generating response...")
                            start_time = time.time()
                            response_text = generate_response(llm, text)
                            print(f"[ASSISTANT]: {response_text} (took {time.time() - start_time:.2f}s)")
                            
                            if use_tts:
                                print("[SYSTEM]: Speaking...")
                                speak_text(voice, response_text)
                            
                            gc.collect()
                            print("[SYSTEM]: Memory cleaned up. Resuming listening...\n")
                            
                            mic_active.set()
                            
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[SYSTEM]: Shutting down...")
            sys.exit(0)

    else:
        # Text Input Mode (AI Assistant)
        print("AI Assistant (Text Input). Type your message below (type 'exit' or 'quit' to stop).\n")
        while True:
            try:
                user_text = input("[USER]: ").strip()
                if not user_text:
                    continue
                if user_text.lower() in ['exit', 'quit']:
                    print("\n[SYSTEM]: Shutting down...")
                    break
                
                print("[SYSTEM]: Generating response...")
                start_time = time.time()
                response_text = generate_response(llm, user_text)
                print(f"[ASSISTANT]: {response_text} (took {time.time() - start_time:.2f}s)")
                
                if use_tts:
                    print("[SYSTEM]: Speaking...")
                    speak_text(voice, response_text)
                    
                gc.collect()
                
            except (KeyboardInterrupt, EOFError):
                print("\n[SYSTEM]: Shutting down...")
                break

if __name__ == "__main__":
    main()
