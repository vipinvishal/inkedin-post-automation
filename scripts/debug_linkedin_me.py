#!/usr/bin/env python3
"""
Debug: see what LinkedIn returns for /v2/me and /v2/userinfo with your token.
Run: python scripts/debug_linkedin_me.py [vanity_name]
  vanity_name = the part after linkedin.com/in/ (e.g. if your URL is linkedin.com/in/john-doe, use john-doe)
  If provided, we try to resolve it to a person URN (may require extra app permissions).
"""
import base64
import json
import os
import ssl
import sys
import urllib.request
import urllib.error
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

try:
    import certifi
    ctx = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ctx = ssl.create_default_context()

def main():
    vanity = sys.argv[1] if len(sys.argv) > 1 else None
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
    if not token:
        print("LINKEDIN_ACCESS_TOKEN not set in .env")
        sys.exit(1)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 1. Try decode access token as JWT
    print("1. Decoding access token as JWT (middle part only)...")
    try:
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            print("   Payload keys:", list(payload.keys()))
            if "sub" in payload:
                sub = payload["sub"]
                print("   sub =", sub)
                urn = sub if str(sub).startswith("urn:li:") else f"urn:li:person:{sub}"
                print("   -> Add to .env: LINKEDIN_PERSON_URN=" + urn)
            else:
                print("   (no 'sub' in token)")
        else:
            print("   (token is not a JWT)")
    except Exception as e:
        print("   Error:", e)
    print()

    # 2. GET /v2/me
    print("2. GET https://api.linkedin.com/v2/me")
    try:
        req = urllib.request.Request("https://api.linkedin.com/v2/me", headers=headers)
        with urllib.request.urlopen(req, context=ctx) as r:
            body = json.loads(r.read().decode())
            print("   Status: 200")
            print("   Body:", json.dumps(body, indent=2))
            if body.get("id"):
                print("   -> Add to .env: LINKEDIN_PERSON_URN=urn:li:person:" + str(body["id"]))
    except urllib.error.HTTPError as e:
        print("   Status:", e.code)
        print("   Body:", e.read().decode() if e.fp else "")
    except Exception as e:
        print("   Error:", e)
    print()

    # 3. GET /v2/userinfo
    print("3. GET https://api.linkedin.com/v2/userinfo")
    try:
        req = urllib.request.Request("https://api.linkedin.com/v2/userinfo", headers=headers)
        with urllib.request.urlopen(req, context=ctx) as r:
            body = json.loads(r.read().decode())
            print("   Status: 200")
            print("   Body:", json.dumps(body, indent=2))
            if body.get("sub"):
                sub = body["sub"]
                urn = sub if str(sub).startswith("urn:li:") else f"urn:li:person:{sub}"
                print("   -> Add to .env: LINKEDIN_PERSON_URN=" + urn)
    except urllib.error.HTTPError as e:
        print("   Status:", e.code)
        print("   Body:", e.read().decode() if e.fp else "")
    except Exception as e:
        print("   Error:", e)

    # 4. Try vanity name (if you passed your profile username)
    if vanity:
        print("4. GET profile by vanity name (linkedin.com/in/" + vanity + ")")
        try:
            url = "https://api.linkedin.com/v2/people?q=vanityName&vanityName=" + urllib.parse.quote(vanity)
            req = urllib.request.Request(url, headers=headers)
            req.add_header("X-Restli-Protocol-Version", "2.0.0")
            with urllib.request.urlopen(req, context=ctx) as r:
                body = json.loads(r.read().decode())
                print("   Status: 200")
                elements = body.get("elements") or []
                if elements and elements[0].get("id"):
                    pid = elements[0]["id"]
                    urn = "urn:li:person:" + pid if not str(pid).startswith("urn:li:") else pid
                    print("   -> Add to .env: LINKEDIN_PERSON_URN=" + urn)
                else:
                    print("   Body:", json.dumps(body, indent=2)[:500])
        except urllib.error.HTTPError as e:
            print("   Status:", e.code, e.read().decode()[:150])
        except Exception as e:
            print("   Error:", e)
        print()

    print("--- If both /me and /userinfo returned 403 ---")
    print("Your token has only Share on LinkedIn (w_member_social). To get LINKEDIN_PERSON_URN:")
    print("  A) Add 'Sign In with LinkedIn' in Developer Portal → your app → Products.")
    print("     Then set LINKEDIN_SCOPE_OPENID=1 in .env and run: python scripts/linkedin_oauth.py")
    print("     The success page will show LINKEDIN_PERSON_URN – add it to .env.")
    print("  B) Or find it manually: log into linkedin.com, F12 → Network, load your profile,")
    print("     search for 'urn:li:person' in any response, copy that value and add to .env:")
    print("     LINKEDIN_PERSON_URN=urn:li:person:XXXXX")

if __name__ == "__main__":
    main()
