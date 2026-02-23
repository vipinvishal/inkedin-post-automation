"""Send draft email to Gmail with Approve / Re-write instructions (SMTP)."""
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import get_gmail_address, get_gmail_app_password

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_draft_email(post_text: str, draft_id: str) -> None:
    """
    Send the draft post to GMAIL_ADDRESS with clear Approve/Re-write instructions.
    Recipient replies with APPROVE-<draft_id> or REWRITE-<draft_id>.
    """
    to_addr = get_gmail_address()
    from_addr = to_addr  # send to self for simplicity
    password = get_gmail_app_password()

    subject = f"[LinkedIn Draft] Approval needed – {date.today().isoformat()}"
    body = _build_body(post_text, draft_id)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())


def _build_body(post_text: str, draft_id: str) -> str:
    return f"""This is your LinkedIn post draft. Approve or request a re-write.

————————————————————————————
DRAFT (copy for reference):
————————————————————————————

{post_text}

————————————————————————————
WHAT TO DO (reply to this email):
————————————————————————————

• To APPROVE this draft (post it later when we add LinkedIn):
  Reply with exactly:  APPROVE-{draft_id}

• To request a RE-WRITE:
  Reply with exactly:  REWRITE-{draft_id}

Your reply is read by the automation script. Do not change the format of the keyword.
"""
