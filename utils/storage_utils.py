from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

import json

DATA_DIR = Path("data")
USERS_DIR = DATA_DIR / "users"

# Old global files (for migration from earlier version)
GLOBAL_PERIOD_FILE = DATA_DIR / "period_starts.json"
GLOBAL_SYMPTOM_FILE = DATA_DIR / "symptom_logs.json"


def _ensure_base_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_username(username: str) -> str:
    username = (username or "").strip()
    if not username:
        return "default"
    safe_chars = []
    for ch in username:
        if ch.isalnum() or ch in ("_", "-"):
            safe_chars.append(ch)
        else:
            safe_chars.append("_")
    slug = "".join(safe_chars).strip("._")
    return slug or "default"


def _user_dir(username: str) -> Path:
    _ensure_base_dirs()
    slug = _safe_username(username)
    d = USERS_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def _period_file(username: str) -> Path:
    return _user_dir(username) / "period_starts.json"


def _symptom_file(username: str) -> Path:
    return _user_dir(username) / "symptom_logs.json"


#  PERIOD STARTS


def load_period_starts(username: str) -> List[date]:
    """
    Load period start dates for a specific user from JSON file.
    Returns a list of date objects.
    If file doesn't exist, returns [].
    """
    f = _period_file(username)

    # Migration: if user file missing but old global file exists, read that once
    if not f.exists() and GLOBAL_PERIOD_FILE.exists():
        try:
            with open(GLOBAL_PERIOD_FILE, "r", encoding="utf-8") as g:
                data = json.load(g)
        except json.JSONDecodeError:
            data = {}
        raw_list = data.get("period_starts", [])
    else:
        if not f.exists():
            return []
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError:
            return []
        raw_list = data.get("period_starts", [])

    dates: List[date] = []
    for item in raw_list:
        try:
            d = datetime.strptime(item, "%Y-%m-%d").date()
            dates.append(d)
        except Exception:
            continue
    dates.sort()
    return dates


def save_period_starts(period_starts: List[date], username: str) -> None:
    """
    Save period start dates for a specific user as ISO strings into JSON file.
    """
    f = _period_file(username)

    iso_list = [d.isoformat() for d in period_starts]
    payload = {"period_starts": iso_list}

    with open(f, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


# SYMPTOM LOGS


def load_symptom_logs(username: str) -> List[Dict[str, Any]]:
    """
    Load symptom logs for a specific user from JSON file.
    Each log entry looks like:
    {
      "date": date,
      "symptoms": [str, ...],
      "pain": int,
      "flow": str,
      "mood": str,
      "notes": str,
      "analysis": {...}   # optional
    }
    """
    f = _symptom_file(username)

    # Migration: use global file if user-specific doesn't exist
    if not f.exists() and GLOBAL_SYMPTOM_FILE.exists():
        try:
            with open(GLOBAL_SYMPTOM_FILE, "r", encoding="utf-8") as g:
                raw_list = json.load(g)
        except json.JSONDecodeError:
            raw_list = []
    else:
        if not f.exists():
            return []
        try:
            with open(f, "r", encoding="utf-8") as fh:
                raw_list = json.load(fh)
        except json.JSONDecodeError:
            return []

    if not isinstance(raw_list, list):
        return []

    logs: List[Dict[str, Any]] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        entry = item.copy()

        raw_date = entry.get("date")
        if isinstance(raw_date, str):
            try:
                entry["date"] = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except Exception:
                continue
        else:
            continue

        logs.append(entry)

    logs.sort(key=lambda x: x["date"])
    return logs


def save_symptom_logs(logs: List[Dict[str, Any]], username: str) -> None:
    """
    Save symptom logs for a specific user to JSON.
    - Converts date objects to ISO strings.
    """
    f = _symptom_file(username)

    serializable: List[Dict[str, Any]] = []
    for entry in logs:
        item = entry.copy()

        d = item.get("date")
        if isinstance(d, date):
            item["date"] = d.isoformat()
        elif isinstance(d, str):
            # Assume it's already ISO
            pass
        else:
            # Invalid date, skip
            continue

        serializable.append(item)

    with open(f, "w", encoding="utf-8") as fh:
        json.dump(serializable, fh, ensure_ascii=False, indent=2)
