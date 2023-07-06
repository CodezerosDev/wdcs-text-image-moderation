import cv2
import os
import logging

import pydload
import numpy as np
import onnxruntime

from image_model import load_images


# logging.basicConfig(level=logging.DEBUG)

from skimage import metrics as skimage_metrics


def is_similar_frame(f1, f2, resize_to=(64, 64), thresh=0.5, return_score=False):
    thresh = float(os.getenv("FRAME_SIMILARITY_THRESH", thresh))

    if f1 is None or f2 is None:
        return False

    if isinstance(f1, str) and os.path.exists(f1):
        try:
            f1 = cv2.imread(f1)
        except Exception as ex:
            logging.exception(ex, exc_info=True)
            return False

    if isinstance(f2, str) and os.path.exists(f2):
        try:
            f2 = cv2.imread(f2)
        except Exception as ex:
            logging.exception(ex, exc_info=True)
            return False

    if resize_to:
        f1 = cv2.resize(f1, resize_to)
        f2 = cv2.resize(f2, resize_to)

    if len(f1.shape) == 3:
        f1 = f1[:, :, 0]

    if len(f2.shape) == 3:
        f2 = f2[:, :, 0]

    score = skimage_metrics.structural_similarity(f1, f2, multichannel=False)

    if return_score:
        return score

    if score >= thresh:
        return True

    return False


def get_interest_frames_from_video(
    video_path,
    frame_similarity_threshold=0.5,
    similarity_context_n_frames=3,
    skip_n_frames=0.5,
    output_frames_to_dir=None,
):
    skip_n_frames = float(os.getenv("SKIP_N_FRAMES", skip_n_frames))

    important_frames = []
    fps = 0
    video_length = 0

    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        if skip_n_frames < 1:
            skip_n_frames = int(skip_n_frames * fps)
            logging.info(f"skip_n_frames: {skip_n_frames}")

        video_length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        for frame_i in range(length + 1):
            read_flag, current_frame = video.read()

            if not read_flag:
                break

            if skip_n_frames > 0:
                if frame_i % skip_n_frames != 0:
                    continue

            frame_i += 1

            found_similar = False
            for context_frame_i, context_frame in reversed(
                important_frames[-1 * similarity_context_n_frames :]
            ):
                if is_similar_frame(
                    context_frame, current_frame, thresh=frame_similarity_threshold
                ):
                    logging.debug(f"{frame_i} is similar to {context_frame_i}")
                    found_similar = True
                    break

            if not found_similar:
                logging.debug(f"{frame_i} is added to important frames")
                important_frames.append((frame_i, current_frame))
                if output_frames_to_dir:
                    if not os.path.exists(output_frames_to_dir):
                        os.mkdir(output_frames_to_dir)

                    output_frames_to_dir = output_frames_to_dir.rstrip("/")
                    cv2.imwrite(
                        f"{output_frames_to_dir}/{str(frame_i).zfill(10)}.png",
                        current_frame,
                    )

        logging.info(
            f"{len(important_frames)} important frames will be processed from {video_path} of length {length}"
        )

    except Exception as ex:
        logging.exception(ex, exc_info=True)

    return (
        [i[0] for i in important_frames],
        [i[1] for i in important_frames],
        fps,
        video_length,
    )

class Classifier:
    """
    Class for loading model and running predictions.
    For example on how to use take a look the if __name__ == '__main__' part.
    """

    nsfw_model = None

    def __init__(self):
        """
        model = Classifier()
        """
        url = "https://github.com/notAI-tech/NudeNet/releases/download/v0/classifier_model.onnx"
        home = os.path.expanduser("~")
        model_folder = os.path.join(home, ".NudeNet/")
        if not os.path.exists(model_folder):
            os.mkdir(model_folder)

        model_path = os.path.join(model_folder, os.path.basename(url))

        if not os.path.exists(model_path):
            print("Downloading the checkpoint to", model_path)
            pydload.dload(url, save_to_path=model_path, max_time=None)

        self.nsfw_model = onnxruntime.InferenceSession(model_path)

    def classify_video(
        self,
        video_path,
        batch_size=4,
        image_size=(256, 256),
        categories=["unsafe", "safe"],
    ):
        frame_indices = None
        frame_indices, frames, fps, video_length = get_interest_frames_from_video(
            video_path
        )
        logging.debug(
            f"VIDEO_PATH: {video_path}, FPS: {fps}, Important frame indices: {frame_indices}, Video length: {video_length}"
        )

        frames, frame_names = load_images(frames, image_size, image_names=frame_indices)

        if not frame_names:
            return {}

        preds = []
        model_preds = []
        while len(frames):
            _model_preds = self.nsfw_model.run(
                [self.nsfw_model.get_outputs()[0].name],
                {self.nsfw_model.get_inputs()[0].name: frames[:batch_size]},
            )[0]
            model_preds.append(_model_preds)
            preds += np.argsort(_model_preds, axis=1).tolist()
            frames = frames[batch_size:]

        probs = []
        for i, single_preds in enumerate(preds):
            single_probs = []
            for j, pred in enumerate(single_preds):
                single_probs.append(
                    model_preds[int(i / batch_size)][int(i % batch_size)][pred]
                )
                preds[i][j] = categories[pred]

            probs.append(single_probs)

        return_preds = {
            "metadata": {
                "fps": fps,
                "video_length": video_length,
                "video_path": video_path,
            },
            "preds": {},
        }

        for i, frame_name in enumerate(frame_names):
            return_preds["preds"][frame_name] = {}
            for _ in range(len(preds[i])):
                return_preds["preds"][frame_name][preds[i][_]] = probs[i][_]

        return return_preds

    def classify(
        self,
        image_paths=[],
        batch_size=4,
        image_size=(256, 256),
        categories=["unsafe", "safe"],
    ):
        """
        inputs:
            image_paths: list of image paths or can be a string too (for single image)
            batch_size: batch_size for running predictions
            image_size: size to which the image needs to be resized
            categories: since the model predicts numbers, categories is the list of actual names of categories
        """
        if not isinstance(image_paths, list):
            image_paths = [image_paths]

        loaded_images, loaded_image_paths = load_images(
            image_paths, image_size, image_names=image_paths
        )

        if not loaded_image_paths:
            return {}

        preds = []
        model_preds = []
        while len(loaded_images):
            _model_preds = self.nsfw_model.run(
                [self.nsfw_model.get_outputs()[0].name],
                {self.nsfw_model.get_inputs()[0].name: loaded_images[:batch_size]},
            )[0]
            model_preds.append(_model_preds)
            preds += np.argsort(_model_preds, axis=1).tolist()
            loaded_images = loaded_images[batch_size:]

        probs = []
        for i, single_preds in enumerate(preds):
            single_probs = []
            for j, pred in enumerate(single_preds):
                single_probs.append(
                    model_preds[int(i / batch_size)][int(i % batch_size)][pred]
                )
                preds[i][j] = categories[pred]

            probs.append(single_probs)

        images_preds = {}

        for i, loaded_image_path in enumerate(loaded_image_paths):
            if not isinstance(loaded_image_path, str):
                loaded_image_path = i

            images_preds[loaded_image_path] = {}
            for _ in range(len(preds[i])):
                images_preds[loaded_image_path][preds[i][_]] = float(probs[i][_])

        return images_preds


def check_visual_moderation(video_filepath):
    classifier = Classifier()
    result = classifier.classify_video(video_filepath)
    print(result)
    frame_count = len(result['preds'])  # Total number of frames
    unsafe_count = sum(1 for frame in result['preds'].values() if frame['unsafe'] > 0.5)  # Count of frames with unsafe score > 0.5
    if unsafe_count / frame_count > 0.1:
        video_safety = "Unsafe"
        print("Visual Unsafe")
    else:
        video_safety = "Safe"
        print("Visual Safe") 

    return video_safety

if __name__ == "__main__":

    videofilepath = input("Enter video path:")
    check_visual_moderation(videofilepath)
