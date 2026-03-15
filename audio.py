import re
from groq import Groq, RateLimitError
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_text(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    return re.sub(r"\s+", " ", text)


def speak(text, model, voice):
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=clean_text(text),
            response_format="wav",
        )
        return response.read()
    except RateLimitError:
        return None
    except Exception:
        return None


def transcribe(audio_bytes, model):

    return client.audio.transcriptions.create(
        model=model,
        file=("audio.wav", audio_bytes),
        response_format="text",
    )