import time

from verbal_moderation import check_audio_moderation
from visual_moderation import check_visual_moderation


# from old_visual_moderation import check_visual_moderation


def video_moderate(video_filepath):
    audio_flag = check_audio_moderation(video_filepath)
    if audio_flag == False:
        return "Please upload video with duration less than 45 seconds."
    else:
        visual_flag = check_visual_moderation(video_filepath)
        output_messages = {
            ("Safe", "Safe"): "Audio and Visual Safe",
            ("Unsafe", "Unsafe"): "Audio and Visual Unsafe",
            ("Safe", "Unsafe"): "Audio Safe and Visual Unsafe",
            ("Unsafe", "Safe"): "Audio Unsafe and Visual Safe",
            ("No audio", "Safe"): "No Audio in Video and Visual Video Safe",
            ("No audio", "Unsafe"): "No Audio in Video and Visual Video Unsafe",
        }
        return output_messages[(audio_flag, visual_flag)]


if __name__ == "__main__":
    video_filepath = input("Enter a Video file: ")
    start_time = time.time()
    video_flag = video_moderate(video_filepath)
    print(video_flag)
    end_time = time.time()
    print("Time taken to execute code: ", end_time - start_time)
