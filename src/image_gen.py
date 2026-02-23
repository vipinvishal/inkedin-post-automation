"""Optional image generation for LinkedIn post (Gemini). Saves to file for email/LinkedIn."""
import os
from datetime import date
from pathlib import Path

from google import genai
from google.genai import types

from config.settings import get_gemini_api_key, PROJECT_ROOT

# LinkedIn posts often use square or 1:1; optional 16:9 for hero
DEFAULT_ASPECT_RATIO = "1:1"
OUTPUT_DIR = PROJECT_ROOT / "output"
IMAGE_MODEL = "gemini-2.5-flash-image"


def _ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def _image_prompt_from_post(post_text: str, max_words: int = 25) -> str:
    """Derive a short, visual prompt from the first part of the post (hook + one line)."""
    lines = [s.strip() for s in post_text.split("\n") if s.strip() and not s.strip().startswith("#")]
    if not lines:
        return "Professional illustration about AI and technology, modern and minimal."
    combined = " ".join(lines[:3])
    words = combined.split()[:max_words]
    prompt = " ".join(words)
    # Ask for an illustration style suitable for LinkedIn
    return (
        f"Professional, modern illustration for a LinkedIn post about: {prompt}. "
        "Style: clean, minimal, tech/AI theme. No text in the image. Suitable for professional social media."
    )


def generate_image(
    post_text: str,
    reference_date: date | None = None,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
) -> Path | None:
    """
    Generate one image from the post content and save to output/draft_YYYYMMDD.png.
    Returns the file path, or None if generation is disabled or fails.
    """
    if not os.environ.get("ENABLE_IMAGE_GENERATION", "").strip().lower() in ("1", "true", "yes"):
        return None

    reference_date = reference_date or date.today()
    out_dir = _ensure_output_dir()
    prompt = _image_prompt_from_post(post_text)

    client = genai.Client(api_key=get_gemini_api_key())
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio) if aspect_ratio else None,
    )

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=config,
        )
    except Exception as e:
        print(f"[Image gen] Skipped: {e}", flush=True)
        return None

    if not getattr(response, "candidates", None) or not response.candidates:
        return None
    content = response.candidates[0].content
    if not getattr(content, "parts", None):
        return None

    for part in content.parts:
        if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
            data = part.inline_data.data
            mime = getattr(part.inline_data, "mime_type", None) or "image/png"
            ext = "png" if "png" in (mime or "") else "jpg"
            path = out_dir / f"draft_{reference_date.isoformat().replace('-', '')}.{ext}"
            path.write_bytes(data)
            return path

    return None
