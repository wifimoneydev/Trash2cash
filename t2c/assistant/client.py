"""OpenAI client setup for the Trash2Cash assistant.

OpenAI is optional everywhere it's used: if no key is configured, or the
`openai` package isn't installed, get_client() returns None and callers
fall back to the local Naive Bayes chatbot. The API key is never
hardcoded or logged.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()  # populates os.environ from a local .env file, if present
except ImportError:
    pass  # python-dotenv is a soft dependency; env vars set another way still work

DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
REQUEST_TIMEOUT_SECONDS = 8


def get_api_key():
    return os.environ.get("OPENAI_API_KEY")


def get_client():
    """Return an OpenAI client, or None if unavailable.

    None is a normal, expected return value (no key configured, or the
    `openai` package isn't installed) — callers must treat it as "use
    the local fallback", not as an error.
    """
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        return None
    return OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)
