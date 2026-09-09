import os
import sys
import time
import tempfile
import socket
import sounddevice as sd
from scipy.io import wavfile
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Determine the absolute path to the project root ON THE LAPTOP
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(current_dir)

# Import local models from the week2 folder
edge_agent_path = os.path.join(PROJECT_ROOT, 'Blister-bot-main-', 'week2', 'edge_agent')
sys.path.append(edge_agent_path)

try:
    from edge_agent import load_model, run_agent
except ImportError:
    print("[ERROR] Could not find edge_agent. Ensure it was deployed correctly.")
    sys.exit(1)

# --- Audio Config ---
FS = 16000  # Whisper prefers 16kHz
DURATION = 5  # Record for 5 seconds

# --- App Lab Wi-Fi Bridge Config ---
UNO_Q_IP = '192.168.11.101'
UNO_Q_PORT = 5000

def init_bridge():
    try:
        bridge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bridge.settimeout(2.0)
        bridge.connect((UNO_Q_IP, UNO_Q_PORT))
        bridge.settimeout(None) # Remove timeout for long-running connection
        print(f"[INFO] Connected to Uno Q Smart Display at {UNO_Q_IP}:{UNO_Q_PORT}")
        return bridge
    except Exception as e:
        print(f"[WARNING] Could not connect to Uno Q Wi-Fi. Running in console mode. Error: {e}")
        return None

def send_to_lcd(bridge, text):
    """Sends text over the Wi-Fi bridge to the Uno Q to be printed on the LCD."""
    print(f"\n[LCD Output]:\n{text}")
    if bridge:
        try:
            # Sanitize newlines for the simple protocol
            clean_text = text.replace('\n', ' ')
            command = f"PRINT:{clean_text}\n"
            bridge.sendall(command.encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Failed to send to LCD: {e}")

def load_whisper():
    print("[INFO] Loading Whisper Tiny (Edge Optimized)...")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-tiny.en"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )
    return pipe

def record_audio_chunk():
    """Records audio from the USB microphone for a fixed duration."""
    input("\n🎤 Press [ENTER] to start speaking for 5 seconds...")
    print("[RECORDING] Speak now...")
    recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("[DONE] Processing audio...")
    
    # Save to temp file
    temp_wav = tempfile.mktemp(suffix=".wav")
    wavfile.write(temp_wav, FS, recording)
    return temp_wav

def main():
    # Initialize the App Lab Serial Bridge to the Microcontroller
    bridge = init_bridge()
    send_to_lcd(bridge, "Booting AI Terminal...")
    
    # Load Models
    whisper_pipe = load_whisper()
    send_to_lcd(bridge, "Whisper Loaded. Loading LLM...")
    
    # Change working directory so Llama.cpp can find the GGUF model file
    os.chdir(edge_agent_path)
    
    try:
        llm = load_model()
    except Exception as e:
        print(f"[WARNING] Could not load LLM. Make sure qwen2.5.gguf is downloaded! Error: {e}")
        llm = None
    
    send_to_lcd(bridge, "System Ready. Press ENTER to speak.")
    print("\n" + "="*50)
    print("Edge-AI Terminal Ready. Awaiting Voice Input.")
    print("="*50)
    
    while True:
        try:
            # 1. Listen (Record Audio)
            audio_path = record_audio_chunk()
            
            # 2. Transcribe
            send_to_lcd(bridge, "Listening... Transcribing...")
            result = whisper_pipe(
                audio_path,
                return_timestamps=True,
                generate_kwargs={
                    "condition_on_prev_tokens": False,
                    "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                    "no_speech_threshold": 0.6,
                    "logprob_threshold": -1.0,
                    "compression_ratio_threshold": 1.35
                }
            )
            os.unlink(audio_path)
            
            user_text = result.get("text", "").strip()
            if not user_text:
                print("[INFO] No speech detected.")
                send_to_lcd(bridge, "No speech detected. Press ENTER to speak.")
                continue
                
            print(f"[User Said]: {user_text}")
            send_to_lcd(bridge, f"User: {user_text} ...Thinking...")
            
            # 3. Process Intent via Local LLM (edge_agent)
            if llm:
                response_text = run_agent(llm, user_text)
            else:
                response_text = "LLM Offline."
            
            # 4. Display Output to the MCU driven LCD
            send_to_lcd(bridge, response_text)
            
        except KeyboardInterrupt:
            print("\nShutting down terminal...")
            send_to_lcd(bridge, "System Offline.")
            if bridge:
                bridge.close()
            break
        except Exception as e:
            print(f"[ERROR]: {e}")
            send_to_lcd(bridge, f"Error: {str(e)}")

if __name__ == "__main__":
    main()
