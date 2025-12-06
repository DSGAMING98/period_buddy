from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional
import os
import hashlib
import hmac
from datetime import datetime, timedelta

import streamlit as st

# Where credentials live (local JSON, offline only)
USERS_FILE = Path("data") / "users.json"

# Security knobs
LOCK_MAX_ATTEMPTS = 5           # how many wrong tries before lock
LOCK_DURATION_SECONDS = 15 * 60  # 15 minutes
PBKDF2_ITERATIONS = 130_000
SALT_BYTES = 16


# ---------- LOW-LEVEL HELPERS ----------

def _ensure_user_file() -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text("{}", encoding="utf-8")


def _load_user_db() -> Dict[str, Any]:
    _ensure_user_file()
    try:
        raw = USERS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw or "{}")
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _save_user_db(data: Dict[str, Any]) -> None:
    _ensure_user_file()
    USERS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _hash_password(password: str) -> tuple[str, str]:
    """
    PBKDF2-HMAC-SHA256 with random salt.
    Returns (salt_hex, hash_hex).
    """
    if not isinstance(password, str):
        password = str(password)

    salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return salt.hex(), dk.hex()


def _verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """
    Check password using constant-time compare.
    """
    try:
        salt = bytes.fromhex(salt_hex)
        stored = bytes.fromhex(hash_hex)
    except Exception:
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(candidate, stored)


def _parse_locked_until(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # stored as ISO string
        return datetime.fromisoformat(value)
    except Exception:
        return None


# PUBLIC API USED BY PAGES

def init_auth_state() -> None:
    """
    Make sure Streamlit session has the auth keys set.
    """
    if "auth_logged_in" not in st.session_state:
        st.session_state["auth_logged_in"] = False
    if "auth_username" not in st.session_state:
        st.session_state["auth_username"] = None
    if "auth_locked" not in st.session_state:
        st.session_state["auth_locked"] = False


def is_logged_in() -> bool:
    return bool(st.session_state.get("auth_logged_in", False))


def get_current_profile_name() -> Optional[str]:
    return st.session_state.get("auth_username")


def register_profile(username: str, password: str) -> bool:
    """
    Create a new user with salted+hashed password.
    Returns False if username exists or input is invalid.
    """
    username = (username or "").strip()
    if not username or not password:
        return False

    db = _load_user_db()
    if username in db:
        # user already exists
        return False

    salt_hex, hash_hex = _hash_password(password)
    db[username] = {
        "salt": salt_hex,
        "password_hash": hash_hex,
        "failed_attempts": 0,
        "locked_until": None,
    }
    _save_user_db(db)
    return True


def login(username: str, password: str) -> bool:
    """
    Validate credentials, update lockout, and set session state.
    True = logged in, False = fail.
    """
    username = (username or "").strip()
    if not username or not password:
        return False

    db = _load_user_db()
    record = db.get(username)

    # Unknown user – behave like normal failure, no hints
    if not record:
        return False

    now = datetime.now()
    locked_until = _parse_locked_until(record.get("locked_until"))

    # Still locked?
    if locked_until and now < locked_until:
        st.session_state["auth_locked"] = True
        return False

    # Check password
    if _verify_password(password, record.get("salt", ""), record.get("password_hash", "")):
        # success
        record["failed_attempts"] = 0
        record["locked_until"] = None
        _save_user_db(db)

        st.session_state["auth_logged_in"] = True
        st.session_state["auth_username"] = username
        st.session_state["auth_locked"] = False
        return True

    # Wrong password → bump attempts
    attempts = int(record.get("failed_attempts", 0)) + 1
    record["failed_attempts"] = attempts

    if attempts >= LOCK_MAX_ATTEMPTS:
        record["locked_until"] = (now + timedelta(seconds=LOCK_DURATION_SECONDS)).isoformat()
        st.session_state["auth_locked"] = True

    _save_user_db(db)
    return False


def logout() -> None:
    """
    Clear login state from this Streamlit session.
    """
    st.session_state["auth_logged_in"] = False
    st.session_state["auth_username"] = None
    st.session_state["auth_locked"] = False


def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Change password only if old_password matches.
    """
    username = (username or "").strip()
    if not username or not old_password or not new_password:
        return False

    db = _load_user_db()
    record = db.get(username)
    if not record:
        return False

    if not _verify_password(old_password, record.get("salt", ""), record.get("password_hash", "")):
        return False

    salt_hex, hash_hex = _hash_password(new_password)
    record["salt"] = salt_hex
    record["password_hash"] = hash_hex
    record["failed_attempts"] = 0
    record["locked_until"] = None
    _save_user_db(db)
    return True


def delete_profile(username: str, password: str) -> bool:
    """
    Delete user from auth DB if password is correct.
    Also wipes that user's local data dir at data/users/<username> (best-effort).
    """
    username = (username or "").strip()
    if not username or not password:
        return False

    db = _load_user_db()
    record = db.get(username)
    if not record:
        return False

    if not _verify_password(password, record.get("salt", ""), record.get("password_hash", "")):
        return False

    # 1) Remove from auth db
    db.pop(username, None)
    _save_user_db(db)

    # 2) Logout if it's the current session user
    if st.session_state.get("auth_username") == username:
        st.session_state["auth_logged_in"] = False
        st.session_state["auth_username"] = None
        st.session_state["auth_locked"] = False

    # 3) Best-effort wipe of their data directory
    user_dir = Path("data") / "users" / username
    if user_dir.exists() and user_dir.is_dir():
        try:
            import shutil
            shutil.rmtree(user_dir, ignore_errors=True)
        except Exception:
            # if this fails, we just leave the files; no crash
            pass

    return True
