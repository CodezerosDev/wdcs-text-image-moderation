import os
from moviepy.editor import VideoFileClip
from audio_model import audio_moderate


### Extract Audio from Video ### 
def video_to_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    try:
        audio = video.audio
        audio.write_audiofile(audio_path)
        print("Successfully extracted Audio from Video")
    except:
        print("Video has no Audio")
    
def create_audio_path(video_path):
    filename = os.path.basename(os.path.splitext(video_path)[0])
    if not os.path.exists("Audios"):
        os.mkdir("Audios")
    audio_path = f"Audios/{filename}.wav"
    return audio_path


def flag_result(moderation_class):
    if moderation_class["flagged"] == False:
        print("Verbal Safe")
        return "Safe"
    else:
        print("Verbal Unsafe")
        return "Unsafe"


def check_audio_moderation(video_path):
    audio_path = create_audio_path(video_path)
    video_to_audio(video_path, audio_path)
    moderation_score = audio_moderate(audio_path)
    flag = flag_result(moderation_score)
    return flag


if __name__ == "__main__":

    video_file = "Videos/Spanish.mp4"

    flag = check_audio_moderation(video_file)
    print(flag)