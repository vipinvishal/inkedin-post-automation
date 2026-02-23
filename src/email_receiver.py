"""Poll Gmail via IMAP and parse Approve / Re-write replies."""
import imaplib
import re
from email import policy
from email.parser import BytesParser

from config.settings import get_gmail_address, get_gmail_app_password

IMAP_HOST = "imap.gmail.com"
APPROVE_PATTERN = re.compile(r"APPROVE-([a-f0-9]{8})", re.I)
REWRITE_PATTERN = re.compile(r"REWRITE-([a-f0-9]{8})", re.I)


def _get_body(msg) -> str:
    """Extract plain-text body from email (plain + HTML fallback for keyword search)."""
    body_plain = ""
    body_html = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type() or ""
            try:
                content = part.get_content() or ""
            except Exception:
                payload = part.get_payload(decode=True)
                content = (payload.decode("utf-8", errors="replace") if isinstance(payload, bytes) else str(payload)) or ""
            if ct == "text/plain":
                body_plain = content
            elif ct == "text/html":
                body_html = content
    else:
        try:
            body_plain = msg.get_content() or ""
        except Exception:
            payload = msg.get_payload(decode=True)
            body_plain = (payload.decode("utf-8", errors="replace") if isinstance(payload, bytes) else str(payload)) or ""
    # Prefer plain; if empty, strip HTML tags for keyword search
    text = (body_plain or "").strip()
    if not text and body_html:
        text = re.sub(r"<[^>]+>", " ", body_html)
    return text


# Match start of quoted/original message so we only parse what the user actually replied with
REPLY_QUOTE_START = re.compile(
    r"(\n\s*On .+wrote:|\n\s*_{10,}|\n-{5,}Original Message-{5,}|\n\s*From:\s*|\n\s*>+\s*|\n\s*On .+,\s+.+wrote:)",
    re.I,
)


def _get_reply_only(body: str) -> str:
    """Keep only the reply text before the quoted original (where APPROVE/REWRITE appear in instructions)."""
    if not body:
        return ""
    m = REPLY_QUOTE_START.search(body)
    if m:
        return body[: m.start()].strip()
    return body.strip()


def _parse_action(text: str) -> tuple[str | None, str | None]:
    """Return ('approve', draft_id) or ('rewrite', draft_id) or (None, None)."""
    combined = (text or "").upper()
    # Check REWRITE first so "REWRITE-xxx" in reply wins over "APPROVE-xxx" in quoted text
    m = REWRITE_PATTERN.search(combined)
    if m:
        return "rewrite", m.group(1).lower()
    m = APPROVE_PATTERN.search(combined)
    if m:
        return "approve", m.group(1).lower()
    return None, None


def fetch_pending_actions(limit: int = 20) -> list[tuple[str, str]]:
    """
    Connect via IMAP, fetch recent emails in INBOX from GMAIL_ADDRESS,
    parse for APPROVE-<id> or REWRITE-<id>. Returns list of (action, draft_id).
    """
    results = []
    addr = get_gmail_address()
    password = get_gmail_app_password()

    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(addr, password)
        mail.select("INBOX")
        _, numbers = mail.search(None, "ALL")
        msg_ids = numbers[0].split()
        # Process newest first
        for uid in reversed(msg_ids[-limit:] if len(msg_ids) > limit else msg_ids):
            _, data = mail.fetch(uid, "(RFC822)")
            if not data or not data[0][1]:
                continue
            msg = BytesParser(policy=policy.default).parsebytes(data[0][1])
            # Only consider emails from the same account (your replies)
            from_header = msg.get("From") or ""
            if addr not in from_header and "vipiniskaizen" not in from_header.lower():
                continue
            body = _get_body(msg)
            # Only parse the reply part, not the quoted original (which contains APPROVE/REWRITE in instructions)
            reply_only = _get_reply_only(body)
            subject = (msg.get("Subject") or "")
            combined = f"{subject}\n{reply_only}"
            action, draft_id = _parse_action(combined)
            if action and draft_id:
                results.append((action, draft_id))
        mail.logout()
    except Exception as e:
        raise RuntimeError(f"IMAP error: {e}") from e

    return results
