import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
import os
from transformers import pipeline
@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_classifier()
# --- Genre Options ---
st.markdown("### 🎧 Choose genres to classify against (or use default):")

default_genres = [
    "Neo-Soul", "R&B", "Afrobeats", "Hip Hop", "Gospel",
    "Jazz", "Ambient", "Experimental", "Lo-fi", "House"
]

selected_genres = st.multiselect(
    "Select genres to compare:",
    default_genres,
    default=default_genres[:5]
)

# --- User Input ---
user_input = st.text_input("Describe the sound, mood, or instrumentation of your track:")

if st.button("Classify Genre"):
    if user_input:
        result = classifier(user_input, candidate_labels=selected_genres)

        st.success("🎯 Top Predicted Genres:")

        # Show results as bar chart
        genre_scores = {label: score for label, score in zip(result["labels"], result["scores"])}
        genre_df = pd.DataFrame.from_dict(genre_scores, orient='index', columns=['Confidence'])
        genre_df = genre_df.sort_values(by="Confidence", ascending=True)

        st.bar_chart(genre_df)

        # Optional: Show top result
        top_label = result["labels"][0]
        top_score = result["scores"][0] * 100
        st.markdown(f"**Top Match:** `{top_label}` with **{top_score:.2f}%** confidence")
    else:
        st.warning("Please enter a description before classifying.")

# --- Genre Prediction Section ---
st.markdown("## 🎶 Genre Classifier")

# User input
description = st.text_input("Describe the sound, mood, or instrumentation of your track:")

# Candidate genres
candidate_labels = ["Neo-Soul", "Gospel", "R&B", "Jazz", "Ambient", "Hip-Hop", "Experimental"]

# Classify button
if st.button("Classify Genre"):
    if description:
        with st.spinner("Analyzing vibe..."):
            result = classifier(description, candidate_labels)
            top_labels = result["labels"][:3]
            top_scores = result["scores"][:3]
            
            st.success("Top Predicted Genres:")
            for label, score in zip(top_labels, top_scores):
                st.markdown(f"- **{label}** ({score:.2%} confidence)")
    else:
        st.warning("Please enter a description before classifying.")

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
# --- Auto-Clean CSV Tool ---  
# (Your current logic ends around line 117)

# --- AI Tag Suggestion Section ---
st.header("🧠 AI Tag Suggestions (Hugging Face)")

user_input = st.text_area("🎤 Describe your audio (tone, style, feeling):", "")

candidate_labels = ["Neo-Soul", "Gospel", "R&B", "Jazz", "Ambient", "Hip-Hop", "Experimental"]

if st.button("✨ Suggest Tags"):
    if user_input.strip():
        with st.spinner("Analyzing with Hugging Face..."):
            result = classifier(user_input, candidate_labels)
            top_tags = result["labels"][:3]
            st.success("✅ Suggested Tags:")
            st.write(", ".join(top_tags))
    else:
        st.warning("⚠️ Please provide a description before running AI suggestions.")

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

