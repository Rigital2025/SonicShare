import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime
import os
from transformers import pipeline

# --- PAGE SETUP ---
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

# --- CLASSIFIER LOADER ---
@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_classifier()

# --- GENRE OPTIONS ---
st.markdown("### 🎧 Choose genres to classify against (or use default):")
default_genres = [
    "Neo-Soul", "R&B", "Afrobeats", "Hip Hop", "Gospel",
    "Jazz", "Ambient", "Experimental", "Lo-fi", "House"
]
selected_genres = st.multiselect("Select genres to compare:", default_genres, default=default_genres[:5])

# --- USER INPUT ---
user_input = st.text_input("Describe the sound, mood, or instrumentation of your track:")

if st.button("Classify Genre"):
    if user_input:
        result = classifier(user_input, candidate_labels=selected_genres)

        st.success("🎯 Top Predicted Genres:")

        # --- Altair Chart (✨ Indigo Bar Style) ---
        import altair as alt
        genre_scores = {label: score for label, score in zip(result["labels"], result["scores"])}
        genre_df = pd.DataFrame.from_dict(genre_scores, orient='index', columns=['Confidence'])
        genre_df = genre_df.sort_values(by="Confidence", ascending=True)

        chart = (
            alt.Chart(genre_df.reset_index().rename(columns={"index": "Genre"}))
            .mark_bar(color="#4B0082")  # Indigo vibes 🎼
            .encode(
                x=alt.X("Confidence:Q", title="Confidence Score", scale=alt.Scale(domain=[0, 1])),
                y=alt.Y("Genre:N", sort='-x'),
                tooltip=["Genre", "Confidence"]
            )
            .properties(
                width=600,
                height=300,
                title="🎯 Genre Prediction Confidence"
            )
        )

        st.altair_chart(chart, use_container_width=True)

        # --- Top Match Display ---
        top_label = result["labels"][0]
        top_score = result["scores"][0] * 100
        st.markdown(f"**Top Match:** `{top_label}` with **{top_score:.2f}%** confidence")

    else:
        st.warning("Please enter a description before classifying.")

# --- UPLOAD SECTION ---
st.header("🎵 Upload a Vocal Sample")
uploaded_file = st.file_uploader("Upload your vocal run, riff, or harmony sample:", type=["wav", "mp3", "aiff"])

log_path = "logs/data.csv"
expected_columns = ["filename", "tags", "prompt", "custom_notes", "license", "timestamp"]

if uploaded_file:
    st.audio(uploaded_file, format='audio/wav')
    st.success("✅ Vocal uploaded successfully!")

    # --- VIBE TAGGING ---
    st.subheader("🧠 Tag This Vibe")
    vibe_tags = st.multiselect(
        "Select the tags that describe this vocal sample:",
        ["Falsetto", "Harmony", "Ad-lib", "Run", "Vibrato", "Whisper", "Shout", "Soulful", "Gospel", "Neo-Soul",
         "R&B", "Ambient", "Layered", "Loop-ready", "Dry", "Wet", "Reverb", "Raw Emotion"]
    )

    # --- PROMPT GENERATOR ---
    st.subheader("🎧 Generate a Sonic Prompt")
    if vibe_tags:
        joined_tags = ", ".join(vibe_tags)
        prompt_output = f"A {joined_tags.lower()} vocal sample, perfect for genre-bending compositions, AI-enhanced music, or soulful loops."
        st.text_area("📝 AI-Ready Prompt", value=prompt_output, height=100)

    # --- CUSTOM NOTES ---
    st.subheader("🗒️ Add Custom Notes")
    custom_notes = st.text_area("Describe this vocal sample in your own words (optional):", height=100)

    # --- LICENSING ---
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

    # --- ARCHIVE WRITER ---
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

if st.button("🧽 Auto-Clean CSV"):
    try:
        df = pd.read_csv(log_path, on_bad_lines='skip')
        expected_cols = ["filename", "tags", "prompt", "custom_notes", "license", "source_url"]
        existing_cols = [col for col in expected_cols if col in df.columns]
        cleaned_df = df[existing_cols]
        cleaned_df.to_csv(log_path, index=False)
        st.success("🧼 CSV cleaned and updated successfully!")
    except FileNotFoundError:
        st.error("⚠️ Cannot clean — 'logs/data.csv' not found.")
    except Exception as e:
        st.error(f"🚨 Cleaning failed: {e}")

# --- AI TAG SUGGESTIONS ---
st.header("🧠 AI Tag Suggestions (Hugging Face)")

tag_input = st.text_area("🎤 Describe your audio (tone, style, feeling):", "")
tag_labels = ["Neo-Soul", "Gospel", "R&B", "Jazz", "Ambient", "Hip-Hop", "Experimental"]

if st.button("✨ Suggest Tags"):
    if tag_input.strip():
        with st.spinner("Analyzing with Hugging Face..."):
            result = classifier(tag_input, tag_labels)
            top_tags = result["labels"][:3]
            st.success("✅ Suggested Tags:")
            st.write(", ".join(top_tags))
    else:
        st.warning("⚠️ Please provide a description before running AI suggestions.")

# --- CSV DISPLAY ---
try:
    df = pd.read_csv(log_path)
    st.success("📥 CSV loaded successfully!")
except pd.errors.ParserError:
    st.error("⚠️ Problem with CSV format. Some rows were skipped.")
    try:
        df = pd.read_csv(log_path, on_bad_lines='skip')
        st.warning("⚠️ Loaded with skipped bad lines. Please review the data.")
    except Exception:
        st.error("❌ Couldn't load the CSV at all. Please check the file manually.")
        st.stop()
except FileNotFoundError:
    st.error(f"🚫 CSV file not found at '{log_path}'.")
    st.stop()
except Exception as e:
    st.error(f"🔥 Unexpected error: {e}")
    st.stop()

if not df.empty:
    if all(col in df.columns for col in expected_columns):
        st.dataframe(df[expected_columns])
    else:
        st.warning("⚠️ Archive loaded, but missing expected columns.")
        st.dataframe(df)

    # Download Option
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
