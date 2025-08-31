import streamlit as st
import ffmpeg
import os

st.title("🎵 Video to Audio Extractor")

# Upload video
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    # Save uploaded video temporarily
    input_path = "input_video.mp4"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    # Output audio file
    output_path = "output_audio.mp3"

    try:
        # Extract audio using ffmpeg
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format="mp3", acodec="libmp3lame")
            .run(overwrite_output=True, quiet=True)
        )

        st.success("✅ Audio extracted successfully!")

        # Play audio in the app
        st.audio(output_path)

        # Download button
        with open(output_path, "rb") as f:
            st.download_button("⬇️ Download Audio", f, file_name="extracted_audio.mp3")

    except Exception as e:
        st.error(f"Error: {e}")

    # Clean up
    if os.path.exists(input_path):
        os.remove(input_path)
