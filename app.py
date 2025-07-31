import streamlit as st
from PIL import Image

st.set_page_config(page_title="SonicShare", page_icon="🎙️")

# Display logo
image = Image.open("sonicshare_logo.png")
st.image(image, use_column_width=True)

st.title("🎙️ SonicShare")
st.subheader("Your Portal for Vocal Magic + AI Music Creation")

st.markdown("""
Welcome to **SonicShare**, where vocalists and AI creators collaborate to shape the sound of tomorrow.  
Upload your voice. Tag your vibe. Empower your creativity.

🚧 This is an early-stage prototype. Stay tuned for updates!
""")
st.header("🎵 Upload a Vocal Sample")

uploaded_file = st.file_uploader("Upload your vocal run, riff, or harmony sample:", type=["wav", "mp3", "aiff"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    st.success("✅ Vocal uploaded successfully!")
st.subheader("🧠 Tag This Vibe")

vibe_tags = st.multiselect(
    "Select the tags that describe this vocal sample:",
    ["Falsetto", "Harmony", "Ad-lib", "Run", "Vibrato", "Whisper", "Shout", "Soulful", "Gospel", "Neo-Soul", "R&B", "Ambient", "Layered", "Loop-ready", "Dry", "Wet", "Reverb", "Raw Emotion"]
)

if vibe_tags:
    st.success(f"🎯 Tags selected: {', '.join(vibe_tags)}")
st.subheader("🎧 Generate a Sonic Prompt")

if vibe_tags:
    joined_tags = ", ".join(vibe_tags)
    prompt_output = f"A {joined_tags.lower()} vocal sample, perfect for genre-bending compositions, AI-enhanced music, or soulful loops."

    st.text_area("📝 AI-Ready Prompt", value=prompt_output, height=100)

st.info("✨ Feature Modules Coming Soon:\n- Vocal Upload\n- Prompt Generator\n- Licensing Tool\n- Playback Preview")
import pandas as pd
from datetime import datetime
import os

# Create a folder if it doesn't exist (optional for future file saving)
if not os.path.exists("logs"):
    os.makedirs("logs")

if uploaded_file is not None and vibe_tags:
    # Prepare data to store
    file_info = {
        "filename": uploaded_file.name,
        "tags": ", ".join(vibe_tags),
        "prompt": prompt_output,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Convert to DataFrame
    df = pd.DataFrame([file_info])

    # Append to CSV
    if os.path.exists("logs/data.csv"):
        df.to_csv("logs/data.csv", mode='a', header=False, index=False)
    else:
        df.to_csv("logs/data.csv", index=False)

    st.success("✅ Info saved to archive!")
st.header("📚 Upload Archive")

data_path = "logs/data.csv"

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    st.dataframe(df)
else:
    st.info("📭 No uploads found yet. Upload something soulful to get started!")
