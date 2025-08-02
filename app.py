import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
import os

# Page setup
st.set_page_config(page_title="SonicShare", page_icon="🎙️")

# Logo
image = Image.open("sonicshare_logo.png")
st.image(image, use_column_width=True)

# Title & Intro
st.title("🎙️ SonicShare")
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

    # Licensing Option
    st.subheader("📜 Choose Licensing Option")
    license_option = st.radio(
        "How would you like this vocal sample to be shared or used?",
        (
            "Contact me before use (default)",
            "Free to use with credit",
            "Creative Commons (non-commercial)",
            "Commercial use allowed"
        )
    )

    # Save to Archive
    if vibe_tags:
        if not os.path.exists("logs"):
            os.makedirs("logs")

        file_info = {
            "filename": uploaded_file.name,
            "tags": ", ".join(vibe_tags),
            "prompt": prompt_output,
            "custom_notes": custom_notes,
            "license": license_option,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        df = pd.DataFrame([file_info])

log_path = "logs/data.csv"
write_header = not os.path.exists(log_path)

df.to_csv(log_path, mode='a', header=write_header, index=False)

st.success("✅ Info saved to archive!")

# Archive Viewer
st.header("📚 Upload Archive")
data_path = "logs/data.csv"

# 🧠 Baby Step: Robust CSV loader
try:
    df = pd.read_csv(data_path)
    st.success("📥 CSV loaded successfully!")

except pd.errors.ParserError as e:
    st.error("⚠️ Uh-oh! Something’s wrong with the CSV format. Some rows couldn't be read.")
    
    # Optional fallback: try loading with 'on_bad_lines=skip' if you're okay with skipping them
    try:
        df = pd.read_csv(data_path, on_bad_lines='skip')
        st.warning("⚠️ Loaded with skipped bad lines. Please review the data.")
    except Exception as fallback_error:
        st.error("❌ Couldn't load the CSV at all. Please check the file manually.")
        st.stop()

except FileNotFoundError:
    st.error("🚫 CSV file not found. Make sure it's saved at 'logs/data.csv'.")
    st.stop()

except Exception as general_error:
    st.error(f"🔥 Unexpected error: {general_error}")
    st.stop()

# Display the archive (only if data is loaded successfully)
expected_columns = ["filename", "tags", "prompt", "custom_notes", "license", "timestamp"]

if all(col in df.columns for col in expected_columns):
    st.dataframe(df[expected_columns])

    st.subheader("⬇️ Download Archive")
    with open(data_path, "rb") as f:
        st.download_button(
            label="📥 Download Archive as CSV",
            data=f,
            file_name="sonicshare_archive.csv",
            mime="text/csv"
        )
else:
    st.warning("⚠️ Archive loaded, but missing expected columns. You may need to clean or recreate the file.")
    st.dataframe(df)


