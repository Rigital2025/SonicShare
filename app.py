# SonicShare v2 - Clean Start 🧼🎙️

import streamlit as st
import pandas as pd
import altair as alt
import os
from datetime import datetime
from PIL import Image
from transformers import pipeline

# --- PAGE SETUP ---
st.set_page_config(page_title="SonicShare", page_icon="🎙️")
st.title("🎙️ SonicShare")
st.subheader("Your Portal for Vocal Magic + AI Music Creation")
st.markdown("""
Welcome to **SonicShare**, where vocalists and AI creators collaborate to shape the sound of tomorrow.
Upload your voice. Tag your vibe. Empower your creativity.

🚧 Early-stage prototype.
""")

# --- LOAD CLASSIFIER ---
@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_classifier()

# --- GENRE CLASSIFIER ---
st.markdown("## 🎶 Genre Classifier")
default_genres = ["Neo-Soul", "R&B", "Afrobeats", "Hip Hop", "Gospel", "Jazz", "Ambient", "Experimental", "Lo-fi", "House"]
selected_genres = st.multiselect("Select genres to compare:", default_genres, default=default_genres[:5])
description = st.text_input("Describe the sound, mood, or instrumentation of your track:")

if st.button("Classify Genre"):
    if description:
        with st.spinner("Analyzing with Hugging Face model..."):
            result = classifier(description, candidate_labels=selected_genres)
            genre_df = pd.DataFrame({"Genre": result["labels"], "Confidence": result["scores"]})

            # Altair chart
            chart = (
                alt.Chart(genre_df)
                .mark_bar(color="#4B0082")
                .encode(
                    x=alt.X("Confidence:Q", scale=alt.Scale(domain=[0, 1]), title="Confidence Score"),
                    y=alt.Y("Genre:N", sort='-x'),
                    tooltip=["Genre", "Confidence"]
                )
                .properties(width=600, height=300, title="🎯 Genre Prediction Confidence")
            )
            st.altair_chart(chart, use_container_width=True)

            # Top Match
            top_label = result["labels"][0]
            top_score = result["scores"][0] * 100
            st.markdown(f"**Top Match:** `{top_label}` with **{top_score:.2f}%** confidence")
    else:
        st.warning("Please enter a description before classifying.")

# --- VOCAL UPLOAD ---
st.header("🎵 Upload a Vocal Sample")
log_path = "logs/data.csv"
expected_columns = ["filename", "tags", "prompt", "custom_notes", "license", "timestamp"]

uploaded_file = st.file_uploader("Upload your vocal run, riff, or harmony sample:", type=["wav", "mp3", "aiff"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/wav')
    st.success("✅ Vocal uploaded successfully!")

    vibe_tags = st.multiselect("🧠 Tag This Vibe", ["Falsetto", "Harmony", "Ad-lib", "Run", "Vibrato", "Whisper", "Shout", "Soulful", "Gospel", "Neo-Soul", "R&B", "Ambient", "Layered", "Loop-ready", "Dry", "Wet", "Reverb", "Raw Emotion"])

    if vibe_tags:
        prompt_output = f"A {', '.join(vibe_tags).lower()} vocal sample, perfect for genre-bending compositions, AI-enhanced music, or soulful loops."
        st.text_area("📝 AI-Ready Prompt", value=prompt_output, height=100)

    custom_notes = st.text_area("🗒️ Custom Notes", height=100)

    license_option = st.radio("📜 License Option", ("Contact me before use (default)", "Free to use with credit", "Creative Commons (non-commercial)", "Commercial use allowed"))

    # ARCHIVE WRITER
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

# --- ARCHIVE VIEWER ---
st.header("📚 Upload Archive")

if st.button("🧹 Reset Archive (Delete All Data)"):
    try:
        os.remove(log_path)
        st.success("🗑️ Archive deleted! Start fresh by uploading new vocals.")
    except FileNotFoundError:
        st.warning("⚠️ Archive file was already missing.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

# --- CSV LOAD AND DISPLAY ---
try:
    df = pd.read_csv(log_path)
    st.success("📥 CSV loaded successfully!")

    if not df.empty:
        st.dataframe(df[expected_columns] if all(col in df.columns for col in expected_columns) else df)
        with open(log_path, "rb") as f:
            st.download_button("📥 Download Archive as CSV", data=f, file_name="sonicshare_archive.csv", mime="text/csv")
    else:
        st.info("📭 No uploads yet. Upload something soulful to get started!")

except FileNotFoundError:
    st.warning("No archive found yet. Upload a vocal sample to create one.")
except Exception as e:
    st.error(f"🚨 Error reading archive: {e}")

