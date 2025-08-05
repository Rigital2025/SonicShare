import streamlit as st
import os
from PIL import Image
from huggingface_hub import InferenceClient
client = InferenceClient(model="gpt2")
genre_client = InferenceClient(model="facebook/bart-large-mnli")

# --- PAGE SETUP ---
st.set_page_config(page_title="SonicShare", page_icon="🎙️")

# --- Safe Logo Load ---
if os.path.exists("sonicshare_logo.png"):
    image = Image.open("sonicshare_logo.png")
    st.image(image, width=200)
else:
    st.warning("Logo image not found.")

# --- TITLE ---
st.title("DJ Chad's AI Kindness Generator")

# --- Prompt Input ---
prompt = st.text_input("Enter a prompt:", "Say something kind to DJ Chad.")

# --- Generate Button ---
if st.button("Generate"):
    with st.spinner("Thinking..."):
        try:
            response = client.text_generation(prompt=prompt, max_new_tokens=30)
            st.write("### Response from Hugging Face:")
            st.write(response)
        except Exception as e:
            st.error(f"🤖 Oops! Something went wrong: {e}")
            
# --- Custom Styling for Header ---
st.markdown("""
    <style>
        .main-title {
            font-size: 3em;
            text-align: center;
            font-weight: bold;
            color: #4B0082; /* Indigo Vibes */
            margin-bottom: 0.2em;
        }
        .subtitle {
            font-size: 1.5em;
            text-align: center;
            color: #5E5E5E;
            margin-bottom: 2em;
        }
        .hero-box {
            background: linear-gradient(90deg, #4B0082 0%, #8A2BE2 100%);
            padding: 1.5em;
            border-radius: 15px;
            color: white;
            margin-bottom: 1.5em;
        }
    </style>

    <div class='hero-box'>
        <div class='main-title'>🎙️ SonicShare</div>
        <div class='subtitle'>Your Portal for Vocal Magic + AI Music Creation</div>
    </div>
""", unsafe_allow_html=True)
# st.title("🎙️ SonicShare")
# st.subheader("Your Portal for Vocal Magic + AI Music Creation")

st.markdown("""
Welcome to **SonicShare**, where vocalists and AI creators collaborate to shape the sound of tomorrow.  
Upload your voice. Tag your vibe. Empower your creativity.

🚧 This is an early-stage prototype. Stay tuned for updates!
""")

# --- GENRE OPTIONS ---
st.markdown("### 🎧 Choose genres to classify against (or use default):")
default_genres = [
    "Neo-Soul", "R&B", "Afrobeats", "Hip Hop", "Gospel",
    "Jazz", "Ambient", "Experimental", "Lo-fi", "House"
]
selected_genres = st.multiselect("Select genres to compare:", default_genres, default=default_genres[:5])

# --- USER INPUT ---
user_input = st.text_input(
    "Describe the sound, mood, or instrumentation of your track:",
    placeholder="Example: A slow, soulful track with jazzy undertones and lo-fi drums"
)

if st.button("Classify Genre"):
    if user_input:
        response = genre_client.zero_shot_classification(
    inputs=user_input,
    candidate_labels=selected_genres,
)

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
# --- Enhanced Archive Viewer with Filter ---
st.header("🔍 Search Your Sonic Archive")

search_term = st.text_input("Search by tag, filename, or notes:")

try:
    assert 'df' in locals(), "DataFrame not loaded yet"
    if not df.empty:
        filtered_df = df[
            df.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)
        ] if search_term else df

        if filtered_df.empty:
            st.warning("No results match your search. Try a different tag or word.")
        else:
            st.dataframe(filtered_df)

            # Optional: Preview the first 3 entries
            st.subheader("🎧 Quick Preview (First 3 Entries)")
            st.write(filtered_df.head(3))
    else:
        st.info("📭 No uploaded vocal samples found yet.")
except NameError:
    st.info("📭 No archive data available yet. Please upload a vocal sample.")

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
# --- Tag Frequency Visualizer ---
st.subheader("📊 Vibe Tag Frequency")

if 'df' in locals() and not df.empty:
    tag_series = df["tags"].dropna().str.split(", ").explode()
    tag_counts = tag_series.value_counts().reset_index()
    tag_counts.columns = ["Tag", "Count"]

    chart = alt.Chart(tag_counts).mark_bar(color="#6A5ACD").encode(
        x=alt.X("Count:Q", title="Frequency"),
        y=alt.Y("Tag:N", sort='-x'),
        tooltip=["Tag", "Count"]
    ).properties(
        width=600,
        height=400,
        title="🎶 Top Vibe Tags in Your Archive"
    )

    st.altair_chart(chart)

else:
    st.info("📭 No uploads yet. Add your sonic gems to see the vibe tag breakdown!")

    # Download Option
    st.subheader("⬇️ Download Archive")
    with open(log_path, "rb") as f:
        st.download_button(
            label="📥 Download Archive as CSV",
            data=f,
            file_name="sonicshare_archive.csv",
            mime="text/csv"
        )

if 'df' in locals() and not df.empty:
    with open(log_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Archive as CSV",
            data=f,
            file_name="sonicshare_archive.csv",
            mime="text/csv"
        )
else:
    st.info("📭 No uploads found yet. Upload something soulful to get started!")
st.markdown("""
    <hr style="margin-top: 3em; margin-bottom: 1em; border: none; border-top: 1px solid #aaa;" />
    <div style="text-align: center; font-size: 0.9em; color: gray;">
        🔮 Crafted with Soul | Powered by Frequency <br>
        <span style="font-size: 0.75em;">© 2025 SonicShare – A Harmonic Healing Initiative</span>
    </div>
""", unsafe_allow_html=True)
