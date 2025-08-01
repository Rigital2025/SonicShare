import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="SonicShare", page_icon="🎙️")

# Display logo
image = Image.open("sonicshare_logo.png")
st.image(image, use_column_width=True)

# Title
st.title("🎙️ SonicShare")

st.markdown("Use this archive file to save your vocal metadata, share it with producers, or keep your creative catalog organized.")
st.subheader("Your Portal for Vocal Magic + AI Music Creation")

st.markdown("""
Welcome to **SonicShare**, where vocalists and AI creators collaborate to shape the sound of tomorrow.  
Upload your voice. Tag your vibe. Empower your creativity.

🚧 This is an early-stage prototype. Stay tuned for updates!
""")

# Upload Section
st.header("🎵 Upload a Vocal Sample")

uploaded_file = st.file_uploader("Upload your vocal run, riff, or harmony sample:", type=["wav", "mp3", "aiff"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    st.success("✅ Vocal uploaded successfully!")

    # Tagging
    st.subheader("🧠 Tag This Vibe")
    vibe_tags = st.multiselect(
        "Select the tags that describe this vocal sample:",
        ["Falsetto", "Harmony", "Ad-lib", "Run", "Vibrato", "Whisper", "Shout", "Soulful", "Gospel", "Neo-Soul", "R&B", "Ambient", "Layered", "Loop-ready", "Dry", "Wet", "Reverb", "Raw Emotion"]
    )

    # Prompt Generator
    st.subheader("🎧 Generate a Sonic Prompt")
    if vibe_tags:
        joined_tags = ", ".join(vibe_tags)
        prompt_output = f"A {joined_tags.lower()} vocal sample, perfect for genre-bending compositions, AI-enhanced music, or soulful loops."
        st.text_area("📝 AI-Ready Prompt", value=prompt_output, height=100)

    # Custom Notes
    st.subheader("🗒️ Add Custom Notes")
    custom_notes = st.text_area("Describe this vocal sample in your own words (optional):", height=100)

    # Save to Archive
    if vibe_tags:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        file_info = {
            "filename": uploaded_file.name,
            "tags": ", ".join(vibe_tags),
            "prompt": prompt_output,
            "custom_notes": custom_notes,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        df = pd.DataFrame([file_info])

        if os.path.exists("logs/data.csv"):
            df.to_csv("logs/data.csv", mode='a', header=False, index=False)
        else:
            df.to_csv("logs/data.csv", index=False)

st.success("✅ Info saved to archive!")

# Archive Viewer
st.header("📚 Upload Archive")

data_path = "logs/data.csv"

if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    st.dataframe(df[["filename", "tags", "prompt", "custom_notes", "timestamp"]])
else:
    st.info("📭 No uploads found yet. Upload something soulful to get started!")
st.subheader("⬇️ Download Archive")

if os.path.exists(data_path):
    with open(data_path, "rb") as f:
        st.download_button(
            label="📥 Download Archive as CSV",
            data=f,
            file_name="sonicshare_archive.csv",
            mime="text/csv"
        )
else:
    st.info("🕊️ Archive not ready for download yet. Upload some magic first.")

