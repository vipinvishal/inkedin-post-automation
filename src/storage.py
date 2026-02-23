"""Draft storage (JSON file) for Phase 2 email flow."""
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from config.settings import PROJECT_ROOT

DATA_DIR = PROJECT_ROOT / "data"
DRAFTS_FILE = DATA_DIR / "drafts.json"


def _ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def _load_drafts() -> list[dict]:
    _ensure_data_dir()
    if not DRAFTS_FILE.exists():
        return []
    try:
        data = json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_drafts(drafts: list[dict]) -> None:
    _ensure_data_dir()
    DRAFTS_FILE.write_text(json.dumps(drafts, indent=2), encoding="utf-8")


def create_draft(post_text: str) -> str:
    """Save a new draft; return its id (short 8-char id for easy reply)."""
    drafts = _load_drafts()
    draft_id = uuid4().hex[:8]
    drafts.append({
        "id": draft_id,
        "text": post_text,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "pending",  # pending | approved | rewritten
    })
    _save_drafts(drafts)
    return draft_id


def get_draft(draft_id: str) -> dict | None:
    """Return draft by id or None."""
    for d in _load_drafts():
        if d.get("id") == draft_id:
            return d
    return None


def set_draft_status(draft_id: str, status: str) -> bool:
    """Set status to approved or rewritten. Returns True if found and updated."""
    drafts = _load_drafts()
    for d in drafts:
        if d.get("id") == draft_id:
            d["status"] = status
            _save_drafts(drafts)
            return True
    return False
