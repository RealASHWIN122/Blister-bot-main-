import streamlit as st
import asyncio
import edge_tts
import os
import tempfile

# Ensure asyncio works on Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(page_title="Text-to-Speech (Uno Q Compatible)", layout="centered")

st.title("🔊 Text-to-Speech Engine")
st.markdown("""
This uses **Edge-TTS**, which is a highly optimized, human-sounding voice model. 
Because it runs purely in Python and uses very little CPU/RAM, it can be run easily on the **Arduino Uno Q** as long as the board is connected to Wi-Fi!
""")

# Voice Options
VOICES = {
    "US Female (Aria)": "en-US-AriaNeural",
    "US Male (Guy)": "en-US-GuyNeural",
    "UK Female (Sonia)": "en-GB-SoniaNeural",
    "Australian Female (Natasha)": "en-AU-NatashaNeural",
    "Indian Male (Prabhat)": "en-IN-PrabhatNeural"
}

voice_name = st.selectbox("Select Voice:", list(VOICES.keys()))
text_input = st.text_area("Enter text for the Medical Dispenser to say:", "Hello! Please take your Amoxicillin now.")

async def generate_speech(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

if st.button("🗣️ Generate Speech"):
    if not text_input.strip():
        st.warning("Please enter some text!")
    else:
        with st.spinner("Generating audio..."):
            # Create a temporary file to hold the generated mp3
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()
            
            try:
                # Generate the TTS
                asyncio.run(generate_speech(text_input, VOICES[voice_name], temp_path))
                
                st.success("Speech generated successfully!")
                
                # Play the audio in Streamlit
                st.audio(temp_path, format="audio/mp3")
                
            except Exception as e:
                st.error(f"Error generating speech: {e}")
