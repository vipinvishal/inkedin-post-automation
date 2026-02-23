#!/usr/bin/env python3
"""
One-time LinkedIn OAuth: get access/refresh token. Shows and saves in the browser.
With Sign In with LinkedIn + LINKEDIN_SCOPE_OPENID=1, also extracts person URN from id_token.
Run from project root: python scripts/linkedin_oauth.py
"""
import base64
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = ssl.create_default_context()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

REDIRECT_URI = os.environ.get("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
# After adding "Sign In with LinkedIn" in app Products, set LINKEDIN_SCOPE_OPENID=1 in .env and re-run to get a token that can identify you for posting.
_use_openid = os.environ.get("LINKEDIN_SCOPE_OPENID", "").strip().lower() in ("1", "true", "yes")
SCOPE = "openid profile w_member_social" if _use_openid else "w_member_social"
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Set by main(), used by handler
oauth_client_id = None
oauth_client_secret = None
oauth_redirect_uri = None
# Set by handler after callback
oauth_done = False
oauth_refresh_token = None
oauth_access_token = None
oauth_person_urn = None
oauth_error = None
TOKEN_FILE = os.path.join(ROOT, "linkedin_refresh_token.txt")


def _sub_from_id_token(id_token: str) -> str | None:
    """Decode JWT id_token payload and return 'sub' claim (person id)."""
    try:
        parts = id_token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("sub")
    except Exception:
        return None


def exchange_code_for_token(code: str, redirect_uri: str, client_id: str, client_secret: str):
    """Exchange auth code for tokens. Returns (refresh_token or None, access_token or None, error_message or None, full_tokens_dict or None)."""
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=_SSL_CONTEXT) as resp:
            tokens = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return None, None, f"Token exchange failed: HTTP {e.code} – {body}", None
    except Exception as e:
        return None, None, f"Token exchange error: {e}", None
    refresh = tokens.get("refresh_token")
    access = tokens.get("access_token")
    if refresh:
        return refresh, None, None, tokens
    if access:
        return None, access, None, tokens
    return None, None, f"No refresh_token or access_token in response: {tokens}", None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global oauth_done, oauth_refresh_token, oauth_access_token, oauth_person_urn, oauth_error
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in ("/callback", "/"):
            self.send_response(404)
            self.end_headers()
            return

        qs = urllib.parse.parse_qs(parsed.query)
        code = (qs.get("code") or [None])[0]
        err = (qs.get("error") or [None])[0]
        err_desc = (qs.get("error_description") or [None])[0] or ""

        if err:
            oauth_done = True
            oauth_error = err_desc or err
            html = (
                f"<html><body style='font-family:sans-serif;padding:2rem;max-width:600px'>"
                f"<h2 style='color:#c00'>LinkedIn error</h2><p>{oauth_error}</p>"
                f"<p>Fix the issue (e.g. add Share on LinkedIn in app Products) and run the script again.</p></body></html>"
            )
            self._send_html(html)
            return

        if not code:
            self._send_html(
                "<html><body style='font-family:sans-serif;padding:2rem'><h2>No code</h2>"
                "<p>LinkedIn did not send a code. Try again and click Allow.</p></body></html>"
            )
            return

        refresh, access, err_msg, tokens = exchange_code_for_token(
            code, oauth_redirect_uri, oauth_client_id, oauth_client_secret
        )
        oauth_done = True
        if err_msg:
            oauth_error = err_msg
            html = (
                "<html><body style='font-family:sans-serif;padding:2rem;max-width:600px'>"
                "<h2 style='color:#c00'>Token exchange failed</h2>"
                f"<pre style='background:#f5f5f5;padding:1rem;overflow:auto'>{oauth_error}</pre>"
                "<p>Check your app credentials and redirect URL in .env and LinkedIn Developer Portal.</p></body></html>"
            )
            self._send_html(html)
            return

        if refresh:
            oauth_refresh_token = refresh
            env_line = "LINKEDIN_REFRESH_TOKEN=" + refresh
            env_var = "LINKEDIN_REFRESH_TOKEN"
        else:
            oauth_access_token = access
            env_line = "LINKEDIN_ACCESS_TOKEN=" + access
            env_var = "LINKEDIN_ACCESS_TOKEN (valid ~60 days; re-run OAuth when it expires)"

        # If we have id_token (openid scope), extract person URN so posting works without /v2/me or userinfo
        person_urn = None
        id_token = (tokens or {}).get("id_token")
        if id_token:
            sub = _sub_from_id_token(id_token)
            if sub:
                person_urn = sub if str(sub).startswith("urn:li:") else f"urn:li:person:{sub}"
                oauth_person_urn = person_urn

        lines_for_env = [env_line]
        if person_urn:
            lines_for_env.append("LINKEDIN_PERSON_URN=" + person_urn)
        try:
            with open(TOKEN_FILE, "w") as f:
                f.write("\n".join(lines_for_env) + "\n")
        except Exception as e:
            file_note = f"Could not write file: {e}"
        else:
            file_note = f"Saved to: <code>{os.path.basename(TOKEN_FILE)}</code> in your project folder."

        html = (
            "<html><body style='font-family:sans-serif;padding:2rem;max-width:640px'>"
            "<h2 style='color:#0a0'>Success</h2>"
            "<p><b>Add these lines to your <code>.env</code> file:</b></p>"
            f"<pre style='background:#e8f5e9;padding:1rem;word-break:break-all;border:1px solid #4caf50'>{chr(10).join(lines_for_env)}</pre>"
            f"<p>{file_note}</p>"
            "<p>You can close this tab. Then run: <code>python scripts/check_integration.py</code> to verify.</p></body></html>"
        )
        self._send_html(html)

    def _send_html(self, html: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, *args):
        pass


def main():
    global oauth_client_id, oauth_client_secret, oauth_redirect_uri
    client_id = os.environ.get("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        print("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")
        sys.exit(1)
    oauth_client_id = client_id
    oauth_client_secret = client_secret

    port = None
    for p in (8080, 8081, 8082):
        try:
            HTTPServer.allow_reuse_address = True
            server = HTTPServer(("", p), Handler)
            port = p
            break
        except OSError as e:
            if e.errno != 48 and "in use" not in str(e).lower():
                raise
            if p == 8082:
                print("Ports 8080–8082 are in use. Run: lsof -t -i:8080 | xargs kill")
                sys.exit(1)
    server.socket.settimeout(300)
    oauth_redirect_uri = f"http://localhost:{port}/callback"
    if port != 8080:
        print(f"Using port {port}. In LinkedIn app add redirect URL: {oauth_redirect_uri}\n")

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": oauth_redirect_uri,
        "state": "linkedin_post_automation",
        "scope": SCOPE,
    }
    auth_link = AUTH_URL + "?" + urllib.parse.urlencode(auth_params)

    print("\n  1. Open this URL in your browser:\n")
    print("     " + auth_link)
    print("\n  2. Sign in and click Allow.")
    print("  3. The next page will show your token – copy it into .env\n")
    if not _use_openid:
        print("  (If check_integration fails with 'Could not get person id', add 'Sign In with LinkedIn' in app Products and set LINKEDIN_SCOPE_OPENID=1 in .env, then re-run this script.)\n")
    print("  Waiting for you to complete the steps in the browser...\n")

    try:
        server.handle_request()
    except Exception as e:
        print("Server error:", e)
    server.server_close()

    if not oauth_done:
        print("No redirect received. Keep this terminal open when you click Allow on LinkedIn.")
        sys.exit(1)
    if oauth_error:
        print("Error:", oauth_error)
        sys.exit(1)
    if oauth_refresh_token or oauth_access_token:
        print("Token received and shown in the browser.")
        if oauth_person_urn:
            print("Also add LINKEDIN_PERSON_URN to .env (see browser or", TOKEN_FILE + ").")
        else:
            print("Copy from the browser page into .env, or from:", TOKEN_FILE)
        sys.exit(0)
    print("Unexpected state.")
    sys.exit(1)


if __name__ == "__main__":
    main()
