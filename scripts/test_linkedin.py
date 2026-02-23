#!/usr/bin/env python3
"""
Quick check: LinkedIn token works and (optional) post a test.
Run from project root: python scripts/test_linkedin.py [--post]
  --post   Actually create a test post (otherwise only verify token + /me).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

def main():
    do_post = "--post" in sys.argv
    try:
        from src.linkedin import get_access_token, get_person_urn, post_to_linkedin
    except ImportError as e:
        print("Import error:", e)
        sys.exit(1)

    if not (os.environ.get("LINKEDIN_REFRESH_TOKEN", "").strip() or os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()):
        print("Set LINKEDIN_REFRESH_TOKEN or LINKEDIN_ACCESS_TOKEN in .env. Run: python scripts/linkedin_oauth.py")
        sys.exit(1)

    print("Getting access token...")
    token = get_access_token()
    print("  OK")

    print("Getting person URN (/v2/me)...")
    urn = get_person_urn(token)
    print("  ", urn)

    if do_post:
        text = "Test post from LinkedIn automation – safe to delete."
        print("Posting test share...")
        post_id = post_to_linkedin(text)
        print("  Created:", post_id)
    else:
        print("Token and /me OK. To post a test run: python scripts/test_linkedin.py --post")

if __name__ == "__main__":
    main()
