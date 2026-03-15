import av
import io
import wave
import numpy as np
from streamlit_webrtc import AudioProcessorBase


class MicProcessor(AudioProcessorBase):

    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame)
        return frame


def get_audio_bytes(processor: MicProcessor):
    if not processor.frames:
        return None

    frames = processor.frames.copy()
    processor.frames.clear()

    sample_rate = frames[0].sample_rate

    # Resample every frame to mono s16 PCM
    resampler = av.AudioResampler(format="s16", layout="mono", rate=sample_rate)
    pcm_data = b""
    for frame in frames:
        for resampled in resampler.resample(frame):
            pcm_data += bytes(resampled.planes[0])

    # Wrap raw PCM in a proper WAV container so Whisper accepts it
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # s16 = 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    buf.seek(0)
    return buf.read()
