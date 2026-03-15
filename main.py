import streamlit as st
from groq import Groq
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

# ── Model catalogs ─────────────────────────────────────────────────────────────

CHAT_MODELS = {
    "Llama 3.1 8B (Fast)":          "llama-3.1-8b-instant",
    "Llama 3.3 70B (Smart)":        "llama-3.3-70b-versatile",
    "DeepSeek R1 70B (Reasoning)":  "deepseek-r1-distill-llama-70b",
    "Llama 4 Scout (Multilingual)": "meta-llama/llama-4-scout-17b-16e-instruct",
    "Kimi K2 (Multilingual)":       "moonshotai/kimi-k2-instruct",
}

STT_MODELS = {
    "Whisper Large v3 Turbo": "whisper-large-v3-turbo",
    "Whisper Large v3":       "whisper-large-v3",
}

TTS_MODEL  = "canopylabs/orpheus-v1-english"
TTS_VOICES = {
    "Autumn (Female)": "autumn",
    "Diana (Female)":  "diana",
    "Hannah (Female)": "hannah",
    "Austin (Male)":   "austin",
    "Daniel (Male)":   "daniel",
    "Troy (Male)":     "troy",
}

MAX_HISTORY_TURNS = 10
TTS_CHUNK_SIZE    = 190

# ── Groq client ────────────────────────────────────────────────────────────────

@st.cache_resource
def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found in .env")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Groq Voice Chat",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {
        padding: 1rem 2rem 5rem 2rem !important;
        max-width: 100% !important;
    }
    [data-testid="stBottom"] {
        position: fixed;
        bottom: 0;
        background: #0e1117;
        padding: 0.75rem 2rem;
        width: calc(100% - 245px);
        left: 245px;
        z-index: 999;
        border-top: 1px solid #2a2a2a;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "messages":        [],
    "total_tokens":    0,
    "response_times":  [],
    "last_audio_hash": None,   # sha of audio bytes — stable across reruns
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────

def chunk_text(text: str, max_len: int = TTS_CHUNK_SIZE) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    while len(text) > max_len:
        window = text[:max_len]
        cut = max(window.rfind(". "), window.rfind("! "), window.rfind("? "))
        cut = (cut + 1) if cut != -1 else window.rfind(" ")
        if cut <= 0:
            cut = max_len
        chunks.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        chunks.append(text)
    return chunks

def speak(text: str, voice: str) -> list[bytes]:
    blobs = []
    for chunk in chunk_text(text):
        if not chunk:
            continue
        try:
            blobs.append(
                client.audio.speech.create(
                    model=TTS_MODEL,
                    voice=voice,
                    input=chunk,
                    response_format="wav",
                ).read()
            )
        except Exception as e:
            st.error(f"TTS error: {e}")
    return blobs

def transcribe(audio_bytes: bytes, stt_model: str) -> str:
    try:
        return client.audio.transcriptions.create(
            model=stt_model,
            file=("recording.wav", audio_bytes),
            language="en",
            response_format="text",
        )
    except Exception as e:
        st.error(f"STT error: {e}")
        return ""

def run_llm(payload, model_id, temperature, max_tokens, placeholder) -> str:
    full_reply = ""
    t0 = time.perf_counter()
    try:
        stream = client.chat.completions.create(
            model=model_id,
            messages=payload,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_reply += delta
            placeholder.markdown(full_reply + "▌")
        placeholder.markdown(full_reply)
        st.session_state.response_times.append(time.perf_counter() - t0)
        st.session_state.total_tokens += len(full_reply.split()) * 4 // 3
    except Exception as e:
        full_reply = f"⚠️ Error: {e}"
        placeholder.error(full_reply)
    return full_reply

def process_input(user_text: str, voice: str, model_id: str,
                  temperature: float, max_tokens: int,
                  max_turns: int, system_prompt: str):
    # User bubble
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # LLM
    history = st.session_state.messages[-(max_turns * 2):]
    payload = [{"role": "system", "content": system_prompt}] + history

    with st.chat_message("assistant"):
        placeholder = st.empty()
        reply = run_llm(payload, model_id, temperature, max_tokens, placeholder)
        if reply and not reply.startswith("⚠️"):
            with st.spinner("Generating audio..."):
                blobs = speak(reply, voice)
            for i, blob in enumerate(blobs):
                st.audio(blob, format="audio/wav", autoplay=(i == 0))

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("Chat Model")
    model_label = st.selectbox("Model", list(CHAT_MODELS.keys()))
    model_id    = CHAT_MODELS[model_label]

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful, concise assistant. Keep responses short and clear.",
        height=90,
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens  = st.slider("Max Tokens", 256, 2048, 512, 128)
    max_turns   = st.slider("History Turns", 2, 20, MAX_HISTORY_TURNS, 2)

    st.divider()
    st.subheader("🎙️ STT Model")
    stt_model_id = STT_MODELS[st.selectbox("STT Model", list(STT_MODELS.keys()))]

    st.subheader("🔊 TTS Voice")
    tts_voice = TTS_VOICES[st.selectbox("Voice", list(TTS_VOICES.keys()))]

    st.divider()
    avg_rt = (
        f"{sum(st.session_state.response_times) / len(st.session_state.response_times):.2f}s"
        if st.session_state.response_times else "—"
    )
    st.caption(
        f"Turns: {len(st.session_state.messages) // 2}  |  "
        f"~Tokens: {st.session_state.total_tokens:,}  |  "
        f"Avg RT: {avg_rt}"
    )
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages        = []
        st.session_state.total_tokens    = 0
        st.session_state.response_times  = []
        st.session_state.last_audio_hash = None
        st.rerun()

# ── Main ───────────────────────────────────────────────────────────────────────
st.title("🎙️ Groq Voice Chat")

# ── Mic widget — sits above chat, outside bottom bar ──────────────────────────
audio_input = st.audio_input("🎙️ Record a voice message", label_visibility="visible")

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Text input — goes into Streamlit's fixed bottom bar ───────────────────────
user_input = st.chat_input("Type a message...")

# ── Handle voice input ─────────────────────────────────────────────────────────
# Use a hash of the audio bytes as a stable dedup key (id() changes on rerun)
if audio_input is not None:
    audio_bytes = audio_input.read()
    audio_hash  = hash(audio_bytes)
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        with st.spinner("Transcribing..."):
            transcript = transcribe(audio_bytes, stt_model_id)
        if transcript:
            process_input(transcript, tts_voice, model_id,
                          temperature, max_tokens, max_turns, system_prompt)
        else:
            st.warning("Could not transcribe. Please try again.")

# ── Handle text input ──────────────────────────────────────────────────────────
if user_input:
    process_input(user_input, tts_voice, model_id,
                  temperature, max_tokens, max_turns, system_prompt)