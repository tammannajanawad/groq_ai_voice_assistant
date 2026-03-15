# Groq AI Voice Assistant

A Python-based voice assistant powered by Groq's API for fast and efficient AI responses.

## Overview

This project implements a voice-interactive AI assistant that leverages the Groq API to provide rapid AI-powered responses. The assistant can process voice input and deliver intelligent outputs using Groq's optimized inference engine.

## Features

- 🎤 Voice input processing
- 🤖 AI-powered responses via Groq API
- ⚡ Fast inference using Groq's LPU technology
- 🔊 Voice output capabilities
- 💬 Natural language conversation support

## Prerequisites

Before running this project, ensure you have:

- Python 3.8 or higher
- A Groq API key (get one at [Groq Console](https://console.groq.com))
- Required Python dependencies (see Installation section)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tammannajanawad/groq_ai_voice_assistant.git
cd groq_ai_voice_assistant
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Groq API key:
```bash
export GROQ_API_KEY="your-api-key-here"  # On Windows: set GROQ_API_KEY=your-api-key-here
```

## Usage

Run the voice assistant:

```bash
python main.py
```

Or import as a module:
```python
from groq_ai_voice_assistant import VoiceAssistant

assistant = VoiceAssistant()
assistant.start()
```

## Configuration

You can customize the assistant behavior by modifying the configuration file or environment variables:

- `GROQ_API_KEY`: Your Groq API authentication key
- `MODEL`: The Groq model to use (default: mixtral-8x7b-32768)
- `VOICE_INPUT`: Enable/disable voice input (default: true)
- `VOICE_OUTPUT`: Enable/disable voice output (default: true)

## Project Structure

```
groq_ai_voice_assistant/
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── voice_processor.py
├── ai_assistant.py
└── utils.py
```

## Technologies Used

- **Python** - Core language
- **Groq API** - AI inference engine
- **Speech Recognition** - Voice input processing
- **Text-to-Speech** - Voice output

## API Reference

### VoiceAssistant

Main class for interacting with the voice assistant.

**Methods:**
- `start()`: Start the voice assistant
- `process_voice_input(audio)`: Process voice input
- `get_ai_response(prompt)`: Get AI response from Groq
- `play_audio(text)`: Convert text to speech and play

## Troubleshooting

### Issue: API Key Not Found
Ensure your `GROQ_API_KEY` environment variable is properly set.

### Issue: Audio Processing Failed
Check that your microphone and speakers are properly connected and recognized by your system.

### Issue: Slow Responses
This might indicate issues with your internet connection. The Groq API should respond very quickly under normal conditions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
- Open an issue on [GitHub Issues](https://github.com/tammannajanawad/groq_ai_voice_assistant/issues)
- Check existing documentation in the project
- Review Groq API documentation at [docs.groq.com](https://docs.groq.com)

## Acknowledgments

- [Groq](https://groq.com) for providing the powerful LPU inference engine
- Python community for excellent libraries

## Author

**Tammanna Janawad** - [@tammannajanawad](https://github.com/tammannajanawad)

---

**Note:** This is a template README. Please update it with specific details about your implementation, actual project structure, and any additional features as your project develops.