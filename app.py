import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
import os

# --- Page Setup ---
st.set_page_config(page_title="SonicShare", page_icon="🎙️")
image = Image.open("sonicshare_logo.png")
st.image(image, use_column_width=True)

st.title("🎙️ SonicShare")
st.subheader("Your Portal for Vocal Magic + AI Music Creation")
st.markdown("""
Welcome to **SonicShare**, where vocalists and AI creators collaborate to shape the sound of tomorrow.  
Upload your voice. Tag your vibe. Empower your creativity.

🚧 This is an early-stage prototype. Stay tuned for updates!
""")

# --- Constants ---
log_path = "logs/data.csv"
expected_columns = ["filename", "tags", "prompt", "custom_notes", "license", "timestamp"]

# --- Upload Section ---
st.header("🎵 Upload a Vocal Sample")
uploaded_file = st.file_uploader("Upload your vocal run, riff, or harmony sample:", type=["wav", "mp3", "aiff"])

if uploaded_file:
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
        write_header = not os.path.exists(log_path)
        df.to_csv(log_path, mode='a', header=write_header, index=False)
        st.success("✅ Info saved to archive!")

# --- Archive Viewer ---
st.header("📚 Upload Archive")

# 👇 Add this near your Archive Viewer section
if st.button("🧹 Reset Archive (Delete All Data)"):
    try:
        os.remove(log_path)
        st.success("🗑️ Archive deleted! Start fresh by uploading new vocals.")
    except FileNotFoundError:
        st.warning("⚠️ Archive file was already missing.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
# 🧼 Auto-Clean CSV Tool
if st.button("🧽 Auto-Clean CSV"):
    try:
        df = pd.read_csv(log_path, on_bad_lines='skip')
        expected_columns = ["filename", "tags", "prompt", "custom_notes", "license", "source_url"]

        # Only keep expected columns that exist in the current CSV
        existing_columns = [col for col in expected_columns if col in df.columns]
        cleaned_df = df[existing_columns]

        # Overwrite the file
        cleaned_df.to_csv(log_path, index=False)
        st.success("🧼 CSV cleaned and updated successfully!")

    except FileNotFoundError:
        st.error("⚠️ Cannot clean — 'logs/data.csv' not found.")
    except Exception as e:
        st.error(f"🚨 Cleaning failed: {e}")

try:
    df = pd.read_csv(log_path)
    st.success("📥 CSV loaded successfully!")
except pd.errors.ParserError:
    st.error("⚠️ Uh-oh! Something’s wrong with the CSV format. Some rows couldn't be read.")
    try:
        df = pd.read_csv(log_path, on_bad_lines='skip')
        st.warning("⚠️ Loaded with skipped bad lines. Please review the data.")
    except Exception:
        st.error("❌ Couldn't load the CSV at all. Please check the file manually.")
        st.stop()
except FileNotFoundError:
    st.error(f"🚫 CSV file not found. Make sure it's saved at '{log_path}'.")
    st.stop()
except Exception as e:
    st.error(f"🔥 Unexpected error: {e}")
    st.stop()

# --- Display the Archive ---
if not df.empty:
    if all(col in df.columns for col in expected_columns):
        st.dataframe(df[expected_columns])
    else:
        st.warning("⚠️ Archive loaded, but missing expected columns. You may need to clean or recreate the file.")
        st.dataframe(df)

    # Download Button
    st.subheader("⬇️ Download Archive")
    with open(log_path, "rb") as f:
        st.download_button(
            label="📥 Download Archive as CSV",
            data=f,
            file_name="sonicshare_archive.csv",
            mime="text/csv"
        )
else:
    st.info("📭 No uploads found yet. Upload something soulful to get started!")

