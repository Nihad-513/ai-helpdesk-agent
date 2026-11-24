"""All model calls live here, so swapping providers later means editing only this file.

Setup:
    pip install google-genai python-dotenv

.env file (and add .env to .gitignore):
    GEMINI_API_KEY=<your key from Google AI Studio>
    GEMINI_MODEL=gemini-3.8-flash            # main model
    GEMINI_FALLBACK_MODELS=name1,name2       # optional; tried in order if the main one is busy
"""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACKS = [
    name.strip()
    for name in os.environ.get("GEMINI_FALLBACK_MODELS", "").split(",")
    if name.strip()
]


def _is_transient(exc: Exception) -> bool:
    text = str(exc)
    return any(code in text for code in ("503", "429", "UNAVAILABLE"))


def chat(
    messages: list[dict],
    system: str,
    temperature: float = 0.3,
    retries: int = 3,
) -> str:
    """Send a conversation to the model and return its reply text.

    messages: [{"role": "user" | "assistant", "content": "..."}, ...]
    system:   the system prompt (the agent's rules)

    Temporary errors (503 overloaded, 429 rate limit) are retried with a growing
    pause, then the next fallback model is tried. Other errors are raised at once.
    """
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in messages
    ]
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
    )

    last_error: Exception | None = None
    for model in [MODEL, *FALLBACKS]:
        for attempt in range(retries):
            try:
                response = _client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                return response.text or ""
            except Exception as exc:
                if not _is_transient(exc):
                    raise
                last_error = exc
                time.sleep(2 ** attempt)

    assert last_error is not None
    raise last_error