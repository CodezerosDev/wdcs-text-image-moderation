FROM python:3.11

WORKDIR /app

COPY . .

RUN rm -rf /app/Images /app/Videos /app/Audios /app/video_frames
RUN mkdir /app/Images /app/Videos /app/Audios /app/video_frames

RUN apt-get update &&  \
    apt-get install ffmpeg libsm6 libxext6 -y &&  \
    apt-get clean &&  \
    pip3 install --upgrade pip &&  \
    pip3 install --upgrade setuptools &&  \
    pip3 install -r requirements.txt

EXPOSE 7001

ENTRYPOINT [ "python3", "app.py" ]
