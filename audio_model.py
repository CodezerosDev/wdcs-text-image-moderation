import openai
import whisper
import librosa
import numpy as np
from googletrans import Translator

def transcribe_audio(audio_file):
    print("Transcribing the Audio")
    audio, sr = librosa.load(audio_file)  
    audio = audio / np.max(np.abs(audio))
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    return result

def translate_text(text, target_language):
    print("Translating the Text")
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text


def check_moderation(text, model_name="text-moderation-latest"):
    print("Checking Moderation of the Text")
    response = openai.Moderation.create(
        input = text,
        model = model_name
    )
    moderation_class = response["results"][0]
    return moderation_class

def audio_moderate(audio_file):
    transcribed_result = transcribe_audio(audio_file)
    translated_text = translate_text(transcribed_result["text"], "en")
    MODERATION_CLASS = check_moderation(translated_text)
    return MODERATION_CLASS

if __name__ == "__main__":

    audio_file = input("Enter Audio File: ")

    result = audio_moderate(audio_file)
    print(result)


