import os
import sys
import time
import tempfile
import serial
import sounddevice as sd
from scipy.io import wavfile
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Blister-bot-main-', 'week2', 'edge_agent')))
from edge_agent import load_model, run_agent

# --- Audio Config ---
FS = 16000  # Whisper prefers 16kHz
DURATION = 5  # Record for 5 seconds

# --- App Lab Serial Bridge Config ---
# The bridge between the Linux side and the STM32 MCU
BRIDGE_PORT = '/dev/ttyGS0'
BRIDGE_BAUD = 115200

def init_bridge():
    try:
        bridge = serial.Serial(BRIDGE_PORT, BRIDGE_BAUD, timeout=1)
        time.sleep(2) # Wait for MCU to reset/connect
        return bridge
    except Exception as e:
        print(f"[WARNING] Could not connect to MCU via {BRIDGE_PORT}: {e}")
        return None

def send_to_lcd(bridge, text):
    """Sends text over the serial bridge to the Arduino sketch to be printed on the LCD."""
    print(f"\n[LCD Output]:\n{text}")
    if bridge:
        # Sanitize newlines for the simple serial protocol
        clean_text = text.replace('\n', ' ')
        command = f"PRINT:{clean_text}\n"
        bridge.write(command.encode('utf-8'))
        
        # Wait for acknowledgment
        start_time = time.time()
        while time.time() - start_time < 2:
            if bridge.in_waiting:
                response = bridge.readline().decode('utf-8').strip()
                if response == "ACK:PRINT_DONE":
                    break
            time.sleep(0.01)

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
    
    # Load LLM from the week2 folder
    os.chdir(os.path.join(os.path.dirname(__file__), 'Blister-bot-main-', 'week2', 'edge_agent'))
    llm = load_model()
    
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
                generate_kwargs={
                    "condition_on_prev_tokens": False,
                    "temperature": (0.0,),
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
            response_text = run_agent(llm, user_text)
            
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
