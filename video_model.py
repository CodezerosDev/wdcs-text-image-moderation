import time

from verbal_moderation import check_audio_moderation
from visual_moderation import check_visual_moderation


# from old_visual_moderation import check_visual_moderation


def video_moderate(video_filepath):
    video_score = {}
    audio_score = check_audio_moderation(video_filepath)
    if audio_score == False:
        return "Please upload video with duration less than 45 seconds."
    elif audio_score == "No audio":
        visual_unsafe_ratio = check_visual_moderation(video_filepath)
        video_score = {"audio-available": "false", "video-unsafe": visual_unsafe_ratio}
        return video_score
    else:
        visual_unsafe_ratio = check_visual_moderation(video_filepath)
        video_score = {"audio-available": "true",
                        "audio-sexual": audio_score["category_scores"]["sexual"], 
                        "audio-hate": audio_score["category_scores"]["hate"], 
                        "audio-harassment": audio_score["category_scores"]["harassment"], 
                        "audio-self-harm": audio_score["category_scores"]["self-harm"], 
                        "audio-sexual/minors": audio_score["category_scores"]["sexual/minors"], 
                        "audio-hate/threatening": audio_score["category_scores"]["hate/threatening"], 
                        "audio-violence/graphic": audio_score["category_scores"]["violence/graphic"], 
                        "audio-self-harm/intent": audio_score["category_scores"]["self-harm/intent"], 
                        "audio-self-harm/instructions": audio_score["category_scores"]["self-harm/instructions"], 
                        "audio-harassment/threatening": audio_score["category_scores"]["harassment/threatening"], 
                        "audio-violence": audio_score["category_scores"]["violence"], 
                        "video-unsafe": visual_unsafe_ratio}
        return video_score
        
        


if __name__ == "__main__":
    video_filepath = input("Enter a Video file: ")
    start_time = time.time()
    video_flag = video_moderate(video_filepath)
    print(video_flag)
    end_time = time.time()
    print("Time taken to execute code: ", end_time - start_time)
