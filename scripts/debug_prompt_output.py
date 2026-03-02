#!/usr/bin/env python3
"""
Debug helper: run research + content once and print the post.

No email is sent and no draft is stored. This is only to inspect
the effect of the current prompts on the generated LinkedIn post.

Run from project root:
  python scripts/debug_prompt_output.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from src.research import run_research  # noqa: E402
from src.content import generate_post  # noqa: E402
from src.gemini_fallback import with_key_fallback  # noqa: E402


def main() -> None:
    print("Running research (debug)...")
    notes = with_key_fallback(run_research)

    print("\n=== Research snapshot ===")
    print("Headlines:", len(notes.get("headlines", [])))
    print("Contrarian angle:", (notes.get("contrarian_angle") or "")[:220])
    print("Second-order impact:", notes.get("second_order_impact", []))
    print("Viral hook angles:", notes.get("viral_hook_angles", []))

    print("\nFull research JSON:")
    print(json.dumps(notes, indent=2, ensure_ascii=False))

    print("\n=== Generated LinkedIn post (no email sent) ===\n")
    post = with_key_fallback(generate_post, research_notes=notes)
    print(post)


if __name__ == "__main__":
    main()

