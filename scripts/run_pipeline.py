#!/usr/bin/env python3
"""
Phase 1 pipeline: research → content → print draft.
Run from project root: python scripts/run_pipeline.py
"""
import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from config.settings import get_gmail_address
from src.research import run_research
from src.content import generate_post
from src.image_gen import generate_image
from src.storage import create_draft
from src.email_sender import send_draft_email
from src.gemini_fallback import with_key_fallback


def main() -> None:
    print("Running research...")
    notes = with_key_fallback(run_research)
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
