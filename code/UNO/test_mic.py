import sounddevice as sd
import numpy as np
import sys

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # Calculate the audio volume
    volume_norm = np.linalg.norm(indata) * 10
    # Print an ASCII volume meter
    meter = "|" * int(volume_norm)
    print(f"\rVolume: {meter:<50}", end="", flush=True)

if __name__ == "__main__":
    print("=====================================")
    print(" MICROPHONE TEST SCRIPT")
    print("=====================================")
    print("Available devices:")
    print(sd.query_devices())
    
    default_in = sd.default.device[0]
    print(f"\nUsing default input device index: {default_in}")
    
    print("\nTesting microphone... Speak into it! (Press Ctrl+C to stop)")
    try:
        with sd.InputStream(channels=1, samplerate=16000, callback=audio_callback):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n\nTest stopped.")
