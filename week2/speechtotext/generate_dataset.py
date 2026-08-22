import asyncio
import os
import csv
import edge_tts

# List of medicines your dispenser holds
MEDICINES = [
    "Ibuprofen",
    "Amoxicillin",
    "Atorvastatin",
    "Lisinopril",
    "Metformin",
    "Azithromycin",
    "Amlodipine",
    "Albuterol",
    "Omeprazole",
    "Losartan",
    "Gabapentin",
    "Paracetamol",
    "Aspirin",
    "Cetirizine"
]

# Variations of how a user might speak to the dispenser
TEMPLATES = [
    "{}",
    "Dispense {}.",
    "I need {}.",
    "Can I get some {}?",
    "Give me {} please."
]

# A mix of free Edge TTS voices (male/female, different accents)
# This diversity prevents the model from overfitting to one voice type
VOICES = [
    "en-US-AriaNeural",      # US Female
    "en-US-GuyNeural",       # US Male
    "en-GB-SoniaNeural",     # UK Female
    "en-AU-NatashaNeural",   # Australian Female
    "en-IN-PrabhatNeural"    # Indian Male (Great for accent robustness)
]

OUTPUT_DIR = "custom_medical_dataset"

async def generate_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metadata = []
    
    total_files = len(MEDICINES) * len(TEMPLATES) * len(VOICES)
    print(f"Generating synthetic dataset of {total_files} audio files...")
    
    file_counter = 0
    for med in MEDICINES:
        for template in TEMPLATES:
            text = template.format(med)
            
            for voice in VOICES:
                filename = f"audio_{file_counter:04d}.mp3"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                # Generate the audio using Microsoft Azure's TTS (Free via edge-tts)
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(filepath)
                
                # Save the mapping for Hugging Face datasets
                metadata.append({"file_name": filename, "transcription": text})
                
                file_counter += 1
                if file_counter % 50 == 0:
                    print(f"Progress: {file_counter}/{total_files} files generated...")
                    
    # Write the metadata.csv file (This exact format is required by Hugging Face)
    csv_path = os.path.join(OUTPUT_DIR, "metadata.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "transcription"])
        writer.writeheader()
        writer.writerows(metadata)
        
    print(f"\n✅ Done! Generated {file_counter} audio files.")
    print(f"Dataset saved to '{OUTPUT_DIR}' folder.")
    print("Ready to be loaded into the 'datasets' library for Whisper fine-tuning!")

if __name__ == "__main__":
    # Windows specific fix for asyncio
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(generate_dataset())
