import streamlit as st
from llm_agent import run_agent
from tts_stream import speak_stream
from audio import transcribe
from config import *

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Voice Agent",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stDeployButton"] { visibility: hidden; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 160px !important;
    max-width: 760px !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    padding: 0.55rem 0 !important;
    border-bottom: none !important;
}

/* ── Audio player ── */
audio {
    width: 100% !important;
    height: 32px !important;
    margin-top: 4px !important;
    border-radius: 8px !important;
    opacity: 0.85;
}

/* ══════════════════════════════════════════
   BOTTOM INPUT BAR  —  mic + text side by side
   ══════════════════════════════════════════ */
[data-testid="stBottom"] {
    background: #0e1117;
    padding: 12px 0 20px 0 !important;
    border-top: none !important;
    max-width: 760px;
    margin: 0 auto;
}

[data-testid="stBottom"] > div:first-child {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    background: #1e1e2e !important;
    border-radius: 16px !important;
    border: 1px solid #2e2e40 !important;
    padding: 4px 8px 4px 4px !important;
}

/* Chat input: no own border, fill space */
[data-testid="stBottom"] [data-testid="stChatInput"] {
    flex: 1 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stBottom"] [data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    color: #ececec !important;
    font-size: 1rem !important;
    padding: 10px 12px !important;
    resize: none !important;
}
[data-testid="stBottom"] [data-testid="stChatInput"] textarea::placeholder {
    color: #555 !important;
}
[data-testid="stBottom"] [data-testid="stChatInput"] button {
    border-radius: 50% !important;
    width: 36px !important; height: 36px !important;
    min-width: 36px !important;
    background: #4f46e5 !important;
    border: none !important;
}

/* Audio input: compact mic circle */
[data-testid="stBottom"] [data-testid="stAudioInput"] {
    flex: 0 0 auto !important;
    width: 44px !important;
    min-width: 44px !important;
}
[data-testid="stBottom"] [data-testid="stAudioInput"] label,
[data-testid="stBottom"] [data-testid="stAudioInput"] canvas,
[data-testid="stBottom"] [data-testid="stAudioInput"] [data-testid="stAudioInputTimer"] {
    display: none !important;
}
[data-testid="stBottom"] [data-testid="stAudioInput"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: unset !important;
}
[data-testid="stBottom"] [data-testid="stAudioInput"] button {
    width: 36px !important; height: 36px !important;
    border-radius: 50% !important;
    background: #1e1e2e !important;
    border: 1px solid #3a3a4a !important;
    color: #aaa !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stBottom"] [data-testid="stAudioInput"] button:hover {
    background: #2a2a3e !important;
    border-color: #6b6baa !important;
}
/* Recording pulse */
[data-testid="stBottom"] [data-testid="stAudioInput"] button[title*="Stop"],
[data-testid="stBottom"] [data-testid="stAudioInput"] button[aria-label*="Stop"] {
    background: #7f1d1d !important;
    border-color: #ef4444 !important;
    animation: rec-pulse 1.2s ease-in-out infinite !important;
}
@keyframes rec-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,.5); }
    50%       { box-shadow: 0 0 0 7px rgba(239,68,68,0); }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "messages": [],
    "total_tokens": 0,
    "last_audio_hash": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
CHAT_MODELS = {
    "Llama 3.3 70B":        "llama-3.3-70b-versatile",
    "Llama 3.1 8B (Fast)":  "llama-3.1-8b-instant",
    "DeepSeek R1 70B":      "deepseek-r1-distill-llama-70b",
    "Llama 4 Scout":        "meta-llama/llama-4-scout-17b-16e-instruct",
}
STT_MODELS = {
    "Whisper Large v3 Turbo": "whisper-large-v3-turbo",
    "Whisper Large v3":       "whisper-large-v3",
}
TTS_VOICES = {
    "Autumn (Female)": "autumn",
    "Diana (Female)":  "diana",
    "Hannah (Female)": "hannah",
    "Austin (Male)":   "austin",
    "Daniel (Male)":   "daniel",
    "Troy (Male)":     "troy",
}

with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("Chat Model")
    chat_model = CHAT_MODELS[st.selectbox("Model", list(CHAT_MODELS.keys()), label_visibility="collapsed")]

    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "Prompt",
        value="You are a helpful, concise voice assistant. Keep responses short and clear.",
        height=90,
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("🎙️ Speech-to-Text")
    stt_model = STT_MODELS[st.selectbox("STT", list(STT_MODELS.keys()), label_visibility="collapsed")]

    st.subheader("🔊 Voice")
    tts_voice = TTS_VOICES[st.selectbox("Voice", list(TTS_VOICES.keys()), label_visibility="collapsed")]

    st.divider()
    turns = len(st.session_state.messages) // 2
    st.caption(f"Turns: {turns}  |  ~Tokens: {st.session_state.total_tokens:,}")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_tokens = 0
        st.session_state.last_audio_hash = None
        st.rerun()

# ── Title ──────────────────────────────────────────────────────────────────────
st.title("🎙️ AI Voice Agent")

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/wav")

# ── Input bar ─────────────────────────────────────────────────────────────────
# Both widgets land in Streamlit's fixed stBottom bar; CSS flexes them into one row.
text_input  = st.chat_input("Type a message or use the mic…")
audio_input = st.audio_input("mic", label_visibility="collapsed")


def process(user_text: str):
    """Run LLM + TTS for a given user message and update state."""
    with st.chat_message("user"):
        st.markdown(user_text)

    history = st.session_state.messages[-(MAX_HISTORY * 2):]
    payload = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_text}
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        reply = ""
        for token in run_agent(payload, chat_model):
            reply += token
            placeholder.markdown(reply + "▌")
        placeholder.markdown(reply)
        st.session_state.total_tokens += len(reply.split()) * 4 // 3

        with st.spinner("Generating audio…"):
            audio_chunks = [c for c in speak_stream([reply], TTS_MODEL, tts_voice) if c]
        audio_bytes = audio_chunks[0] if audio_chunks else None
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav", autoplay=True)
        else:
            st.caption("🔇 TTS quota reached — text response above.")

    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "audio": audio_bytes,
    })


# ── Handle voice input ─────────────────────────────────────────────────────────
if audio_input is not None:
    audio_bytes = audio_input.read()
    audio_hash  = hash(audio_bytes)
    if audio_hash != st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        with st.spinner("Transcribing…"):
            user_text = transcribe(audio_bytes, stt_model)
        if user_text:
            process(user_text)
        else:
            st.warning("Could not transcribe. Please try again.")

# ── Handle text input ─────────────────────────────────────────────────────────
if text_input:
    process(text_input)
