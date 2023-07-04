import os
import openai
import whisper
import librosa
import numpy as np
from googletrans import Translator
from moviepy.editor import VideoFileClip

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

### Extract Text from Audio ###
def transcribe_audio(audio_file):
    print("Transcribing the Audio")
    audio, sr = librosa.load(audio_file)
    audio = audio / np.max(np.abs(audio))
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    text, lang = result["text"], result["language"]
    return text, lang

### Translate extracted text to English ###
def translate_text(text, target_language="en"):
    print("Translating the Text")
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    translated_text = translation.text
    return translated_text

openai.api_key = "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"

### Check Moderation on Translated Text ###
def check_moderation(text, model_name="text-moderation-latest"):
    print("Checking Moderation of the Text")
    response = openai.Moderation.create(
        input = text,
        model = model_name,
    )
    moderation_class = response["results"][0]
    return moderation_class

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
    audio_text, audio_lang = transcribe_audio(audio_path)
    translated_text = translate_text(audio_text)
    moderation_score = check_moderation(translated_text)
    flag = flag_result(moderation_score)
    return flag


if __name__ == "__main__":

    video_file = "Videos/Spanish.mp4"

    flag = check_audio_moderation(video_file)
    print(flag)