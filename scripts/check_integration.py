#!/usr/bin/env python3
"""
Run this to verify the full integration: Gmail, LinkedIn, and end-to-end flow.
Usage: python scripts/check_integration.py [--post]
  --post  Also post a test to LinkedIn (otherwise only verify token + /me).
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

def main():
    do_post = "--post" in sys.argv
    errors = []
    ok = []

    # 1. Gmail
    gmail = os.environ.get("GMAIL_ADDRESS", "").strip()
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
    if gmail and gmail_pass:
        ok.append("Gmail: configured")
    else:
        errors.append("Gmail: set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")

    # 2. LinkedIn app
    li_id = os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
    li_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    li_token = os.environ.get("LINKEDIN_REFRESH_TOKEN", "").strip()
    if li_id and li_secret:
        ok.append("LinkedIn app: client id and secret set")
    else:
        errors.append("LinkedIn: set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")
    li_access = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
    if li_token:
        ok.append("LinkedIn: refresh token set")
    elif li_access:
        ok.append("LinkedIn: access token set (valid ~60 days)")
    else:
        errors.append("LinkedIn: set LINKEDIN_REFRESH_TOKEN or LINKEDIN_ACCESS_TOKEN (run python scripts/linkedin_oauth.py)")

    # 3. Gemini (for pipeline)
    gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if gemini:
        ok.append("Gemini: API key set")
    else:
        errors.append("Gemini: set GEMINI_API_KEY in .env")

    print("Integration check\n" + "=" * 50)
    for s in ok:
        print("  OK:", s)
    for s in errors:
        print("  MISSING:", s)
    if errors:
        print("\nFix the missing items above, then run this script again.")
        sys.exit(1)

    # 4. LinkedIn API (token + /me, optional post)
    print("\nChecking LinkedIn API...")
    try:
        from src.linkedin import get_access_token, get_person_urn, post_to_linkedin
    except ImportError as e:
        print("  Import error:", e)
        sys.exit(1)
    try:
        token = get_access_token()
        urn = get_person_urn(token)
        print("  OK: token and /me –", urn)
    except Exception as e:
        print("  FAIL:", e)
        sys.exit(1)
    if do_post:
        try:
            post_id = post_to_linkedin("Test post from integration check – safe to delete.")
            print("  OK: test post created –", post_id)
        except Exception as e:
            print("  FAIL (post):", e)
            sys.exit(1)
    else:
        print("  (Skip test post. Run with --post to post a test.)")

    print("\n" + "=" * 50)
    print("Integration OK. Full flow:")
    print("  1. python scripts/run_pipeline.py          → research, draft, email")
    print("  2. Reply to the email with APPROVE-<id>   → e.g. APPROVE-abc123")
    print("  3. python scripts/run_approval_check.py   → posts that draft to LinkedIn")
    print("=" * 50)

if __name__ == "__main__":
    main()
