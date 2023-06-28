import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def predict_text_mod(text, model_name="text-moderation-latest"):
    response = openai.Moderation.create(
        input = text,
        model = model_name
    )
    moderation_class = response["results"][0]

    return moderation_class


if __name__ == "__main__":

    INPUT_TEXT = input("Enter text: ")
    predict_text_mod(INPUT_TEXT)