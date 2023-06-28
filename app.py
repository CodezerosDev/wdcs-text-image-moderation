from dotenv import load_dotenv
load_dotenv()
import os
from flask import Flask, render_template, request
from text_model import predict_text_mod
from image_model import image_moderate

app = Flask(__name__)

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

@app.route('/', methods=['GET','POST'])
def text_mod():
    if request.method == 'POST':

        if 'text' in request.form:
            input_text = request.form['text']
            response = predict_text_mod(input_text)
            return render_template('result.html', response=response, type='text')
        
        elif 'image' in request.files:
            input_image = request.files['image']
            image_path = save_image(input_image)
            response = image_moderate(image_path)
            return render_template('result.html', response=response, type='image')
        
    return render_template('index.html')


def save_image(image):
    image_path = os.path.join('input_images', image.filename)
    image.save(image_path)
    return image_path


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)