"""Run a Gemini call with multiple API keys; on 429 quota, try the next key."""
from typing import Callable, TypeVar

from config.settings import get_gemini_api_keys

T = TypeVar("T")


def _is_429(e: Exception) -> bool:
    msg = str(e)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower()


def with_key_fallback(fn: Callable[..., T], *args, **kwargs) -> T:
    """
    Call fn(*args, api_key=key, **kwargs) with each key in order.
    If one returns 429, try the next key. Raises last error if all keys fail.
    """
    keys = get_gemini_api_keys()
    if not keys:
        raise ValueError("No Gemini API keys configured (GEMINI_API_KEY or GEMINI_API_KEY_2).")
    last_e = None
    for key in keys:
        try:
            return fn(*args, api_key=key, **kwargs)
        except Exception as e:
            last_e = e
            if not _is_429(e):
                raise
            if key is keys[-1]:
                raise
    if last_e:
        raise last_e
    raise RuntimeError("No Gemini keys available.")
