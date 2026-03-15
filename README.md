# Groq Voice Chat

A Streamlit web app for voice-first AI chat: speak or type, get Groq-powered replies with optional text-to-speech. The assistant can use tools (e.g. time, weather) when needed.

**Pipeline:** Voice in → Whisper STT → Groq LLM (with tool calling) → Orpheus TTS → Voice out

## Overview

This project is a single-page Streamlit app that uses the Groq API for:

- **Speech-to-text (STT):** Whisper Large v3 (Turbo or full) to transcribe your recordings
- **Chat:** Groq models (Llama 3.3 70B, Llama 3.1 8B, DeepSeek R1 70B, Llama 4 Scout) with optional **function calling** (e.g. current time, weather by city)
- **Text-to-speech (TTS):** Orpheus (canopylabs) with selectable voices for assistant replies

You can use the in-browser mic to speak or type in the chat input; conversation history, token stats, and a clear-conversation control are in the sidebar.

## Features

- 🎤 **Voice input** — Record with the built-in audio widget; Whisper transcribes to text
- 💬 **Text input** — Type messages as a fallback
- 🤖 **Multiple chat models** — Llama 3.3 70B, Llama 3.1 8B (fast), DeepSeek R1 70B, Llama 4 Scout
- 🔧 **Tool use** — Agent can call tools (e.g. `get_time`, `get_weather`) and stream a reply that uses the results
- ⚡ **Streaming responses** — LLM output streams in real time
- 🔊 **TTS playback** — Assistant replies can be spoken with Orpheus (6 voices)
- ⚙️ **Sidebar settings** — System prompt, chat model, history length, STT model, TTS voice
- 📊 **Session stats** — Turn count, approximate tokens; clear conversation button

## Prerequisites

- Python 3.12+
- A [Groq API key](https://console.groq.com)

## Installation

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd streamlit_chatbot
   ```

2. Create a virtual environment and install dependencies (e.g. with uv):

   ```bash
   uv venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   uv sync
   ```

   Or with pip:

   ```bash
   pip install -e .
   ```

3. Add your Groq API key to a `.env` file in the project root:

   ```
   GROQ_API_KEY=your-api-key-here
   ```

   The app loads this via `python-dotenv`.

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open the URL shown in the terminal (usually http://localhost:8501). Use the mic to record or type in the chat box; adjust models and settings in the sidebar.

## Configuration

- **Environment:** `GROQ_API_KEY` in `.env` (required).
- **Defaults:** `config.py` defines default chat/STT/TTS models and `MAX_HISTORY`.
- **In-app:** All other options are in the Streamlit sidebar:
  - Chat model, system prompt, history length
  - STT model (Whisper Large v3 Turbo / Large v3)
  - TTS voice (Autumn, Diana, Hannah, Austin, Daniel, Troy)

## Project structure

```
streamlit_chatbot/
├── README.md
├── app.py           # Streamlit app (STT, LLM agent, TTS, UI)
├── audio.py         # Whisper transcribe; TTS helpers (speak, clean_text)
├── config.py        # Default models and MAX_HISTORY
├── llm_agent.py     # Groq chat + tool calling (get_time, get_weather)
├── tools.py         # Tool implementations (time, weather via wttr.in)
├── tts_stream.py    # Streaming Orpheus TTS
├── utils.py         # Session helpers (init_session, trim_history)
├── webrtc_audio.py  # Optional WebRTC mic processor (av, streamlit-webrtc)
├── style.css        # Optional extra styles
├── pyproject.toml
├── uv.lock
└── .env             # GROQ_API_KEY (not committed)
```

## Technologies

- **Streamlit** — Web UI, session state, chat input, audio input
- **Groq API** — Chat completions with tool calling, Whisper STT, Orpheus TTS
- **python-dotenv** — Load `GROQ_API_KEY` from `.env`
- **requests** — Used by `get_weather` (wttr.in)
- **av / streamlit-webrtc** — Optional WebRTC audio pipeline (see `webrtc_audio.py`)

## Troubleshooting

- **GROQ_API_KEY not found:** Ensure `.env` exists in the project root and contains `GROQ_API_KEY=...`.
- **STT/TTS errors:** Check Groq status and your API key; ensure microphone is allowed in the browser for voice input.
- **TTS quota:** If you see "TTS quota reached", Orpheus daily limit may be exceeded; text replies still work.
- **Slow responses:** Check network; Groq typically responds quickly.

## License

MIT (or your chosen license). See LICENSE for details.
