from groq import Groq, RateLimitError
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def speak_stream(text_chunks, model, voice):
    for chunk in text_chunks:
        try:
            audio = client.audio.speech.create(
                model=model,
                voice=voice,
                input=chunk,
                response_format="wav",
            ).read()
            yield audio
        except RateLimitError:
            # Daily TTS quota exhausted — signal the caller with None
            yield None
            return
        except Exception:
            yield None
            return
