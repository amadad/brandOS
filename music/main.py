from file_processing import chat_video_gemini 
from generate_music import generate_music 
from remix_audio_video import overlay_audio, download_audio 
import streamlit as st 
import tempfile

def generate_music_video(video_file_path, prompt):
    # Generate music prompt from video
    prompt = chat_video_gemini(video_file_path, prompt)
    print (prompt)

    music_urls = generate_music(
    prompt ["music_title"], prompt["music_style_tags"], prompt ["music_lyric"]
    )
    print (music_urls)
    
    audio_file = download_audio(music_urls[0], "audio.mp3")
    overlay_audio(video_file_path, audio_file, f"{prompt ['music_title']}.mp4")

    print(f"Music video generated: {prompt ['music_title']}-mp4")

    return f"{prompt['music_title']}.mp4"

uploaded_file = st.file_uploader("Upload video file", accept_multiple_files=False)

if uploaded_file is not None:
    # Read the uploaded file
    bytes_data = uploaded_file.read()

    # Save the file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
        temp_file.write(bytes_data)
        temp_file_path = temp_file.name

    st.video (bytes_data)

    prompt = st.text_input("Prompt")
    if st.button("Generate Music Video"):
        print(temp_file_path, prompt)
        new_video_path = generate_music_video (temp_file_path, prompt)

        with open ("newVideos/" + new_video_path, "rb") as video_file:
            video_bytes = video_file.read()
            
        # Display the video in Streamlit
        st.video (video_bytes)