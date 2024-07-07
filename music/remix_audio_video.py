from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import requests
from pydub import AudioSegment 
import os 
import cv2

def download_audio(url, file_name):
    response = requests.get(url)
    os.makedirs("temp", exist_ok=True)
    with open("temp/" + file_name, "wb") as f:
        f.write(response.content)
    return "temp/" + file_name

def overlay_audio(video_file_name, new_audio_file_name, output_file_name):
    # Load the video file
    video = VideoFileClip(video_file_name)

    # Get the original video resolution
    vid = cv2. VideoCapture(video_file_name)
    height = vid.get (cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get (cv2.CAP_PROP_FRAME_WIDTH)

    print(f"Original resolution: {width}x{height}")

    # Load the new audio file
    new_audio = AudioFileClip(new_audio_file_name)

    # Get the original audio of the video
    original_audio = video. audio

    # Set the original audio volume to 10%
    original_audio = original_audio.volumex (0.01)

    # Trim the new audio to the duration of the video if it's longer
    if new_audio. duration > video. duration:
        new_audio = new_audio. subclip(0, video.duration)

    # Combine the original audio with the new audio
    combined_audio = CompositeAudioClip([original_audio, new_audio])

    # Set the combined audio to the video
    video = video.set_audio (combined_audio)

    # Write the result to a file with the original resolution
    video.write_videofile(
        "newVideos/" + output_file_name, 
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        preset="ultrafast", 
        threads=4, 
        ffmpeg_params=[
            "-vf",
            f"scale={width}:{height}",
            "-crf",
            "18", # Adjusting CRF for quality, lower is higher quality
        ],  
    )

    return output_file_name