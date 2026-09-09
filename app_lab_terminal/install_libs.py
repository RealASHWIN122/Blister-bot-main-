import os
import subprocess

print("=========================================")
print("Installing Adafruit Libraries to Uno Q...")
print("=========================================")

libraries = [
    "Adafruit GFX Library",
    "Adafruit ST7735 and ST7789 Library",
    "Adafruit BusIO"
]

for lib in libraries:
    print(f"\nInstalling: {lib}")
    res = subprocess.run(["arduino-cli", "lib", "install", lib], capture_output=True, text=True)
    if res.returncode == 0:
        print("[SUCCESS]")
    else:
        print("[FAILED]")
        print(res.stderr)

print("\n=========================================")
print("Done! You can now click 'Deploy' on the sketch.")
print("=========================================")
