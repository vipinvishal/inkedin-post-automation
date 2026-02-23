"""Post to LinkedIn via Posts API (OAuth 2.0, refresh token)."""
import base64
import json
import ssl
import urllib.request
import urllib.error
import urllib.parse

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = ssl.create_default_context()

from config.settings import (
    get_linkedin_client_id,
    get_linkedin_client_secret,
    get_linkedin_refresh_token,
    get_linkedin_access_token,
    get_linkedin_person_urn,
)

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
# Use userinfo (openid/profile) to get person id; /v2/me often returns 403 with w_member_social only
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
ME_URL = "https://api.linkedin.com/v2/me"
UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"


def get_access_token() -> str:
    """Return a valid access_token: use stored LINKEDIN_ACCESS_TOKEN if set, else exchange refresh_token."""
    access_token = get_linkedin_access_token()
    if access_token:
        return access_token
    refresh_token = get_linkedin_refresh_token()
    if not refresh_token:
        raise ValueError(
            "Set LINKEDIN_REFRESH_TOKEN or LINKEDIN_ACCESS_TOKEN in .env. "
            "Run scripts/linkedin_oauth.py and add the token from the success page."
        )
    client_id = get_linkedin_client_id()
    client_secret = get_linkedin_client_secret()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, context=_SSL_CONTEXT) as resp:
        out = json.loads(resp.read().decode())
    access_token = out.get("access_token")
    if not access_token:
        raise RuntimeError("LinkedIn token response missing access_token")
    return access_token


def _person_urn_from_jwt(access_token: str) -> str | None:
    """If the access token is a JWT, try to get person id from payload (sub or client_id as fallback)."""
    try:
        parts = access_token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        sub = payload.get("sub")
        if sub:
            return sub if str(sub).startswith("urn:li:") else f"urn:li:person:{sub}"
        return None
    except Exception:
        return None


def get_person_urn(access_token: str) -> str:
    """Get current user's person URN (urn:li:person:{id}). Uses env, then JWT decode, /v2/me, then userinfo."""
    # 0. Use stored URN from .env (set by OAuth when id_token is returned, or manual)
    stored = get_linkedin_person_urn()
    if stored:
        return stored
    # 1. Try decoding access token as JWT (no API call)
    urn = _person_urn_from_jwt(access_token)
    if urn:
        return urn
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    # 2. Try /v2/me (some apps get id with w_member_social)
    try:
        req = urllib.request.Request(ME_URL, headers=headers)
        with urllib.request.urlopen(req, context=_SSL_CONTEXT) as resp:
            me = json.loads(resp.read().decode())
        person_id = me.get("id")
        if person_id:
            return f"urn:li:person:{person_id}"
    except urllib.error.HTTPError:
        pass
    # 3. Try userinfo (requires openid profile; add "Sign In with LinkedIn" in app Products)
    try:
        req = urllib.request.Request(USERINFO_URL, headers=headers)
        with urllib.request.urlopen(req, context=_SSL_CONTEXT) as resp:
            userinfo = json.loads(resp.read().decode())
        sub = userinfo.get("sub")
        if sub:
            return sub if sub.startswith("urn:li:") else f"urn:li:person:{sub}"
    except urllib.error.HTTPError:
        pass
    raise RuntimeError(
        "Could not get person id. In LinkedIn Developer Portal → your app → Products, "
        'add "Sign In with LinkedIn", then re-run linkedin_oauth.py with openid profile scope.'
    )


def post_to_linkedin(post_text: str) -> str:
    """
    Create a text-only share on LinkedIn via Share on LinkedIn (v2/ugcPosts).
    Returns the post id from X-RestLi-Id response header.
    """
    access_token = get_access_token()
    author = get_person_urn(access_token)
    body = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        UGC_POSTS_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=_SSL_CONTEXT) as resp:
            post_id = resp.headers.get("X-RestLi-Id", "").strip() or "unknown"
            return post_id
    except urllib.error.HTTPError as e:
        err_body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"LinkedIn API error {e.code}: {err_body}") from e
