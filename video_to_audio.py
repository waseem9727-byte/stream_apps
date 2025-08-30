import streamlit as st
from moviepy.editor import VideoFileClip
import os

st.title("🎥 Video to Audio Extractor")

# Upload video
uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_video is not None:
    # Save uploaded video temporarily
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_video.read())

    st.video("temp_video.mp4")

    if st.button("Extract Audio 🎵"):
        # Extract audio using moviepy
        clip = VideoFileClip("temp_video.mp4")
        audio_file = "extracted_audio.mp3"
        clip.audio.write_audiofile(audio_file)

        st.success("✅ Audio extracted successfully!")

        # Provide download button
        with open(audio_file, "rb") as audio:
            st.download_button(
                label="Download Audio File",
                data=audio,
                file_name="audio.mp3",
                mime="audio/mpeg"
            )

        # Clean up
        clip.close()
        os.remove("temp_video.mp4")
