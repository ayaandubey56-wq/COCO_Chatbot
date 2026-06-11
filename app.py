"""Streamlit conversational interface for Coco, the luxury travel consultant."""

from importlib import import_module
from pathlib import Path
import time
from typing import Any

import streamlit as st


MODEL_NAME = "gemini-2.5-flash"
SYSTEM_PROMPT_FILE = Path(__file__).with_name("system-prompt.md")
HISTORY_LIMIT = 10
MAX_RETRIES = 4
BASE_BACKOFF_SECONDS = 1.0


def get_api_key() -> str:
    """Read the Gemini API key from Streamlit secrets."""

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("Missing GEMINI_API_KEY in .streamlit/secrets.toml")
        st.stop()

    api_key = str(api_key).strip()
    if not api_key:
        st.error("GEMINI_API_KEY in .streamlit/secrets.toml is empty")
        st.stop()

    return api_key


def load_gemini_sdk() -> tuple[Any, Any] | tuple[None, None]:
    """Load the Gemini SDK only when the dependency is installed."""

    try:
        genai_module = import_module("google.genai")
        types_module = import_module("google.genai.types")
    except ImportError:
        return None, None

    return genai_module, types_module


@st.cache_data(show_spinner=False)
def load_system_prompt(prompt_path: str) -> str:
    """Load Coco's system prompt from disk."""

    return Path(prompt_path).read_text(encoding="utf-8")


def ensure_session_state() -> None:
    """Initialize Streamlit session state for chat history."""

    if "messages" not in st.session_state:
        st.session_state.messages = []


def build_context_prompt(latest_user_input: str) -> str:
    """Build a compact transcript so each request is independent and reliable."""

    history_lines = []
    for message in st.session_state.messages[-HISTORY_LIMIT:]:
        role = "User" if message["role"] == "user" else "Assistant"
        history_lines.append(f"{role}: {message['content']}")

    history_lines.append(f"User: {latest_user_input}")
    return "\n".join(history_lines)


def is_transient_api_error(error: Exception) -> bool:
    """Detect API errors that are usually safe to retry."""

    text = str(error).lower()
    retry_markers = (
        "503",
        "unavailable",
        "429",
        "resource_exhausted",
        "timeout",
        "temporar",
        "overloaded",
    )
    return any(marker in text for marker in retry_markers)


def generate_reply(user_input: str) -> str:
    """Generate a response with retries for transient provider failures."""

    genai_module, types_module = load_gemini_sdk()
    if genai_module is None or types_module is None:
        st.error(
            "Missing dependency: install google-genai in the active environment "
            "with pip install -r requirements.txt, then restart Streamlit."
        )
        st.stop()

    system_prompt = load_system_prompt(str(SYSTEM_PROMPT_FILE))
    config = types_module.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.3,
    )
    api_key = get_api_key()

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            client = genai_module.Client(api_key=api_key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=build_context_prompt(user_input),
                config=config,
            )
            return getattr(response, "text", None) or ""
        except Exception as error:
            last_error = error
            if not is_transient_api_error(error) or attempt == MAX_RETRIES - 1:
                raise
            time.sleep(BASE_BACKOFF_SECONDS * (2**attempt))

    if last_error is not None:
        raise last_error
    return ""


def render_chat_history() -> None:
    """Render all prior chat messages stored in session state."""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    """Build the Coco travel consultancy chat interface."""

    st.set_page_config(page_title="Aura Luxury Travel", page_icon="✦")

    st.title("Aura Luxury Travel")
    st.markdown(
        """
        Welcome to **Coco**, your elite luxury travel consultant at **Aura Travel Group**.
        Share your destination, preferences, and budget, and Coco will curate a
        polished, bespoke itinerary with refined discretion.
        """
    )

    ensure_session_state()
    render_chat_history()

    user_input = st.chat_input("Describe your luxury travel request...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Coco is preparing a tailored response..."):
            try:
                response_text = generate_reply(user_input)
            except Exception:
                response_text = (
                    "I am experiencing temporary high demand from the model service. "
                    "Please retry in a few seconds."
                )
                st.error(
                    "Temporary model overload (503/429). Please try again in a few seconds."
                )
        response_placeholder.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})


if __name__ == "__main__":
    main()