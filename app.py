import os
from time import time
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request

from audio_model import audio_moderate
from image_model import image_moderate
from text_model import predict_text_mod
from video_model import video_moderate


load_dotenv()
app = Flask(__name__)
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


@app.route("/", methods=["GET", "POST"])
def text_mod():
    if request.method == "POST":
        # try:
        if "text" in request.form:
            input_text = request.form["text"]
            response = predict_text_mod(input_text)
            return render_template("index.html", response=response, type="text")

        elif "image" in request.files:
            input_image = request.files["image"]
            image_path = save_image(input_image)
            response = image_moderate(image_path)
            return render_template("index.html", response=response, type="image")

        elif "video" in request.files:
            input_video = request.files["video"]
            video_path = save_video(input_video)
            st = time()
            response = video_moderate(video_path)
            et = time()
            print("TIMEEEEEEEEEEEEEEEE", et - st)
            return render_template("index.html", response=response, type="video")

        elif "audio" in request.files:
            input_audio = request.files["audio"]
            audio_path = save_audio(input_audio)
            response = audio_moderate(audio_path)
            return render_template("index.html", response=response, type="audio")

    # except:
    #     response = "Request Failed"
    #     return render_template('index.html', response=response, type='image')

    return render_template("index.html")


def save_image(image):
    if not os.path.exists("./Images"):
        os.makedirs("./Images")
    image_path = os.path.join("./Images", image.filename)
    image.save(image_path)
    return image_path


def save_video(video):
    if not os.path.exists("./Videos"):
        os.makedirs("./Videos")
    video_path = os.path.join("./Videos", video.filename)
    video.save(video_path)
    return video_path


def save_audio(audio):
    if not os.path.exists("./Audios"):
        os.makedirs("./Audios")
    audio_path = os.path.join("./Audios", audio.filename)
    audio.save(audio_path)
    return audio_path


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
