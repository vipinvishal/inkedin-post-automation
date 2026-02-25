#!/usr/bin/env python3
"""
Phase 2: Poll Gmail for Approve/Re-write replies and act on them.
Run from project root: python scripts/run_approval_check.py
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from config.settings import get_gmail_address
from src.email_receiver import fetch_pending_actions
from src.storage import get_draft, set_draft_status, create_draft
from src.email_sender import send_draft_email
from src.content import generate_post
from src.gemini_fallback import with_key_fallback
from src.linkedin import post_to_linkedin

RETRY_WAIT_SECONDS = 20  # wait before retry on 429 quota


def main() -> None:
    print("Checking inbox for Approve/Re-write replies...")
    actions = fetch_pending_actions(limit=30)
    if not actions:
        print("No APPROVE/REWRITE replies found.")
        return

    skipped = 0
    unknown_ids: set[str] = set()
    for action, draft_id in actions:
        draft = get_draft(draft_id)
        if not draft:
            unknown_ids.add(draft_id)
            continue

        status = draft.get("status", "pending")

        if action == "approve":
            if status != "pending":
                skipped += 1
                continue
            set_draft_status(draft_id, "approved")
            try:
                post_id = post_to_linkedin(draft["text"])
                print(f"  Approved draft {draft_id} → posted to LinkedIn: {post_id}")
            except ValueError as e:
                print(f"  Approved draft {draft_id}. (LinkedIn not configured: {e})")
            except Exception as e:
                print(f"  Approved draft {draft_id} but LinkedIn post failed: {e}")

        elif action == "rewrite":
            if status != "pending":
                skipped += 1
                continue
            set_draft_status(draft_id, "rewritten")
            print(f"  Re-write requested for draft {draft_id}; generating new draft...")
            try:
                new_post = with_key_fallback(generate_post, rewrite_of=draft["text"])
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                    print(f"  All keys hit quota; waiting {RETRY_WAIT_SECONDS}s then retrying once...")
                    time.sleep(RETRY_WAIT_SECONDS)
                    try:
                        new_post = with_key_fallback(generate_post, rewrite_of=draft["text"])
                    except Exception as e2:
                        print(f"  Re-write failed after retry: {e2}")
                        set_draft_status(draft_id, "pending")
                        continue
                else:
                    print(f"  Re-write failed: {e}")
                    set_draft_status(draft_id, "pending")
                    continue
            try:
                new_id = create_draft(new_post)
                send_draft_email(new_post, new_id)
                print(f"  New draft {new_id} sent to {get_gmail_address()}. Reply APPROVE-{new_id} or REWRITE-{new_id}.")
            except Exception as e:
                print(f"  Re-write failed (send): {e}")
                set_draft_status(draft_id, "pending")

    if skipped:
        print(f"  (Skipped {skipped} reply/replies already handled.)")
    if unknown_ids:
        print(f"  (Skipped {len(unknown_ids)} reply/replies with unknown draft ids — likely from older emails.)")


if __name__ == "__main__":
    main()
