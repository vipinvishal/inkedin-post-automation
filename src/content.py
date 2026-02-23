"""Content generation: research + style guide + samples → one LinkedIn post (text)."""
import json
from pathlib import Path

from google import genai

from config.prompts import (
    CONTENT_SYSTEM_PREFIX,
    CONTENT_USER_TEMPLATE,
    REWRITE_SYSTEM,
    REWRITE_USER_TEMPLATE,
)
from config.settings import get_gemini_api_key, PROJECT_ROOT


def _load_text(path: Path) -> str:
    p = PROJECT_ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"Missing file: {p}")
    return p.read_text(encoding="utf-8").strip()


def _load_samples() -> str:
    return _load_text(Path("samples/sample_posts.txt"))


def _load_style_guide() -> str:
    return _load_text(Path("config/STYLE_GUIDE.md"))


def generate_post(
    research_notes: dict | None = None,
    rewrite_of: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Generate one LinkedIn post. If rewrite_of is set, re-writes that text (research_notes optional).
    Otherwise uses research_notes. Returns plain post text.
    Pass api_key to use a specific key (e.g. for fallback when another key hits 429).
    """
    key = api_key or get_gemini_api_key()
    client = genai.Client(api_key=key)
    style_guide = _load_style_guide()
    sample_posts = _load_samples()

    if rewrite_of:
        user_prompt = REWRITE_USER_TEMPLATE.format(
            previous_post=rewrite_of,
            style_guide=style_guide,
            sample_posts=sample_posts,
        )
        full_prompt = f"{REWRITE_SYSTEM}\n\n---\n\n{user_prompt}"
    else:
        if not research_notes:
            raise ValueError("research_notes required when not re-writing")
        research_json = json.dumps(research_notes, indent=2)
        user_prompt = CONTENT_USER_TEMPLATE.format(
            research_json=research_json,
            style_guide=style_guide,
            sample_posts=sample_posts,
        )
        full_prompt = f"{CONTENT_SYSTEM_PREFIX}\n\n---\n\n{user_prompt}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    text = getattr(response, "text", None) or ""
    if not text:
        raise RuntimeError("Gemini returned empty response for content.")

    return text.strip()
