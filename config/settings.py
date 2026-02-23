"""Load settings from environment. Call load_dotenv() before importing in app entrypoint."""
import os
from pathlib import Path

# Project root (parent of config/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default topic focus (overridden by env)
DEFAULT_TOPIC_FOCUS = (
    "AI, Agent AI, Gen AI – releases, comparisons, advancements"
)


def get_gemini_api_key() -> str:
    keys = get_gemini_api_keys()
    if not keys:
        raise ValueError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key(s)."
        )
    return keys[0]


def get_gemini_api_keys() -> list[str]:
    """
    Return all configured Gemini API keys (primary first, then backup).
    When one key hits 429 quota, the pipeline will try the next key.
    """
    keys = []
    k1 = os.environ.get("GEMINI_API_KEY", "").strip()
    if k1:
        keys.append(k1)
    k2 = os.environ.get("GEMINI_API_KEY_2", "").strip()
    if k2 and k2 not in keys:
        keys.append(k2)
    return keys


def get_topic_focus() -> str:
    return os.environ.get("TOPIC_FOCUS", "").strip() or DEFAULT_TOPIC_FOCUS


def get_gmail_address() -> str:
    addr = os.environ.get("GMAIL_ADDRESS", "").strip()
    if not addr:
        raise ValueError("GMAIL_ADDRESS is not set in .env")
    return addr


def get_gmail_app_password() -> str:
    pwd = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if not pwd:
        raise ValueError("GMAIL_APP_PASSWORD is not set in .env")
    return pwd


def get_linkedin_client_id() -> str:
    v = os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
    if not v:
        raise ValueError("LINKEDIN_CLIENT_ID is not set in .env")
    return v


def get_linkedin_client_secret() -> str:
    v = os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    if not v:
        raise ValueError("LINKEDIN_CLIENT_SECRET is not set in .env")
    return v


def get_linkedin_refresh_token() -> str | None:
    """Return refresh token if set. None if only access token is used."""
    return os.environ.get("LINKEDIN_REFRESH_TOKEN", "").strip() or None


def get_linkedin_access_token() -> str | None:
    """Return stored access token if set (used when LinkedIn does not return refresh_token)."""
    return os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip() or None


def get_linkedin_person_urn() -> str | None:
    """Return stored person URN if set (from OAuth id_token or manual). Avoids /v2/me and userinfo calls."""
    return os.environ.get("LINKEDIN_PERSON_URN", "").strip() or None
