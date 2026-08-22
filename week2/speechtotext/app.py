import streamlit as st
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import tempfile
import os

st.set_page_config(page_title="Whisper Turbo Transcription", layout="centered")

@st.cache_resource
def load_whisper_pipeline():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    # Fallback to float32 if on CPU, as float16 is mostly for GPU
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

st.title("🎙️ Whisper Tiny (Edge Optimized)")
st.write("Upload an audio file or record from your mic to transcribe using OpenAI's ultra-lightweight Whisper Tiny model (perfect for the Uno Q!).")

with st.spinner("Loading Whisper model (this will take a moment to download weights on first run)..."):
    pipe = load_whisper_pipeline()

uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a", "flac"])
st.write("---")
st.write("Or record directly from your microphone:")
mic_audio = st.audio_input("Record a voice message")

audio_to_process = uploaded_file if uploaded_file else mic_audio

if audio_to_process is not None:
    st.audio(audio_to_process)
    
    if st.button("Transcribe Audio"):
        with st.spinner("Transcribing..."):
            # Save uploaded/recorded file to a temporary file with the correct extension
            ext = os.path.splitext(audio_to_process.name)[1] if hasattr(audio_to_process, "name") else ".webm"
            if not ext: ext = ".webm"  # Browsers often record without extension or as webm
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(audio_to_process.getvalue())
                tmp_path = tmp.name
                
            try:
                # Run transcription with anti-hallucination parameters
                result = pipe(
                    tmp_path, 
                    return_timestamps=True,
                    generate_kwargs={
                        "condition_on_prev_tokens": False,
                        "temperature": (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
                        "no_speech_threshold": 0.6,
                        "logprob_threshold": -1.0,
                        "compression_ratio_threshold": 1.35
                    }
                )
                
                st.success("Transcription Complete!")
                st.subheader("Extracted Text:")
                st.info(result["text"])
                
                # Optional: Show chunks with timestamps
                if "chunks" in result:
                    with st.expander("Show Timestamps"):
                        for chunk in result.get("chunks", []):
                            start = chunk['timestamp'][0]
                            end = chunk['timestamp'][1]
                            start_str = f"{start:.2f}s" if start is not None else "0.00s"
                            end_str = f"{end:.2f}s" if end is not None else "end"
                            st.write(f"**[{start_str} -> {end_str}]** {chunk['text']}")
                            
            except Exception as e:
                st.error(f"Error during transcription: {e}")
                st.error("Note: If you get a 'ffprobe' or 'ffmpeg' error, you may need to install FFmpeg on your Windows machine.")
            finally:
                os.unlink(tmp_path)
