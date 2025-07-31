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

st.info("✨ Feature Modules Coming Soon:\n- Vocal Upload\n- Prompt Generator\n- Licensing Tool\n- Playback Preview")
