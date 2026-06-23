import json
from pathlib import Path

from worker_api.config import get


def load_secret_value(raw_value: str) -> str:
    """Load a secret from inline content or a filesystem path."""
    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("{") or "BEGIN" in value:
        return value
    path = Path(value)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return value


def load_json_secret(raw_value: str) -> dict:
    content = load_secret_value(raw_value)
    if not content:
        return {}
    return json.loads(content)


def is_push_configured(platform: str) -> bool:
    if platform in ("android", "ios"):
        return bool(get("GOOGLE_APPLICATION_CREDENTIALS").strip())
    return False
