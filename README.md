# Coco - Luxury Travel Chatbot

A sophisticated Streamlit-powered chatbot built to serve as an elite luxury travel consultant at Aura Travel Group, powered by Google's Gemini AI.

## Features

✨ **Intelligent Conversation** - Uses Google's Gemini 2.5 Flash model with custom system instructions to provide expert luxury travel advice

🔄 **Resilient API Handling** - Implements automatic retry logic with exponential backoff to gracefully handle transient API errors (503, 429, timeouts)

🔐 **Secure Configuration** - API keys stored in Streamlit secrets, never committed to version control

💬 **Context-Aware Responses** - Maintains conversation history (last 10 messages) for coherent multi-turn dialogue

🚀 **Production-Ready** - Clean error handling, proper logging, and user-friendly error messages

## Getting Started

### Prerequisites

- Python 3.13+
- Google Gemini API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayaandubey56-wq/COCO_Chatbot.git
   cd coco_chatbot
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API credentials:**
   - Get your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create `.streamlit/secrets.toml`:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     ```
   - **Never commit this file** (it's in `.gitignore`)

### Running the Application

```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
coco_chatbot/
├── app.py                      # Main Streamlit application
├── system-prompt.md            # System instructions for Coco personality
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── secrets.toml           # API keys (local only, never committed)
└── .venv/                     # Virtual environment (not in git)
```

## Configuration

### System Prompt
Edit `system-prompt.md` to customize Coco's personality, tone, and expertise.

### App Settings (in `app.py`)
- `MODEL_NAME`: Change the Gemini model (default: `gemini-2.5-flash`)
- `HISTORY_LIMIT`: Adjust context window size (default: 10 messages)
- `MAX_RETRIES`: Number of retry attempts for API failures (default: 4)
- `BASE_BACKOFF_SECONDS`: Initial backoff time (default: 1 second)

## How It Works

1. **Initialization**: Loads system prompt and API key from secure storage
2. **User Input**: Captures chat messages from Streamlit UI
3. **Context Building**: Assembles last 10 messages to maintain conversation continuity
4. **API Call**: Sends request to Gemini with smart retry logic
5. **Response**: Displays AI-generated response in chat interface
6. **Resilience**: Automatically retries transient failures with exponential backoff

### Retry Strategy
- Detects transient errors: 503 (UNAVAILABLE), 429 (QUOTA), timeouts, resource exhaustion
- Retries 4 times with delays: 1s → 2s → 4s → 8s
- Shows user-friendly message after final failure

## Dependencies

- **streamlit**: Web UI framework for Python
- **google-genai**: Official Google Gemini SDK

## Troubleshooting

### ImportError: cannot import name 'genai' from 'google'
- Make sure you're running from the virtual environment: `.\.venv\Scripts\python.exe -m streamlit run app.py`
- Reinstall dependencies: `pip install -r requirements.txt`

### RuntimeError: "Cannot send a request, as the client has been closed"
- This is handled automatically. The app creates a fresh API client for each request.

### 503 UNAVAILABLE from Gemini API
- The app automatically retries. If it persists, the Gemini service may be experiencing issues.

### API Key Not Found
- Verify `.streamlit/secrets.toml` exists and contains `GEMINI_API_KEY = "your-key"`
- Check that the file is in the `.streamlit/` directory (not in the main folder)

## Development Notes

- All work uses the local virtual environment at `.\.venv`
- Never hardcode API keys in source code
- The `secrets.toml` file is gitignored for security
- Each deployment must populate its own API key

## Author

**Ayaan Dubey**

## License

MIT License - See project for details

## Support

For issues with the Gemini API, visit [Google AI Studio Documentation](https://ai.google.dev)
