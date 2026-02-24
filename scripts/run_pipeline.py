#!/usr/bin/env python3
"""
Phase 1 pipeline: research → content → print draft.
Run from project root: python scripts/run_pipeline.py
"""
import sys
from pathlib import Path
from datetime import date

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from config.settings import get_gmail_address
from src.research import run_research, RESEARCH_ANGLES
from src.content import generate_post
from src.image_gen import generate_image
from src.storage import create_draft
from src.email_sender import send_draft_email
from src.gemini_fallback import with_key_fallback

DATA_DIR = ROOT / "data"
LAST_THEME_FILE = DATA_DIR / "last_research_theme.txt"


def _read_last_theme() -> str | None:
    if not LAST_THEME_FILE.exists():
        return None
    text = LAST_THEME_FILE.read_text(encoding="utf-8").strip()
    return text or None


def _save_theme(notes: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    theme = (
        (notes.get("headlines") or [""])[0]
        or notes.get("date_context", "")
        or "AI/Gen AI updates"
    )
    LAST_THEME_FILE.write_text(theme[:500], encoding="utf-8")


def main() -> None:
    research_angle = RESEARCH_ANGLES[date.today().weekday() % len(RESEARCH_ANGLES)]
    avoid_theme = _read_last_theme()
    print("Running research...")
    notes = with_key_fallback(
        run_research,
        research_angle=research_angle,
        avoid_theme=avoid_theme,
    )
    _save_theme(notes)
    print("Generating post...")
    post = with_key_fallback(generate_post, research_notes=notes)
    image_path = generate_image(post_text=post)
    print("\n" + "=" * 60 + "\n")
    print(post)
    print("\n" + "=" * 60)
    if image_path:
        print(f"\nImage saved: {image_path}")
    else:
        print("\n(No image. Set ENABLE_IMAGE_GENERATION=1 in .env to try; paid quota may be required.)")

    draft_id = create_draft(post)
    print(f"\nSending draft to {get_gmail_address()}...")
    send_draft_email(post, draft_id)
    print(f"Draft sent. Reply with APPROVE-{draft_id} or REWRITE-{draft_id}.")


if __name__ == "__main__":
    main()
