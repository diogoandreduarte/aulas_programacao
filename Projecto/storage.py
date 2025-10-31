import json, time, os
from typing import Dict, Any, Optional

USERS_DB = "users.json"
STATE_DB = "state.json"  # falhas consecutivas por utilizador, timestamps, etc.

def _load(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    users = _load(USERS_DB)
    return users.get(username)

def upsert_user(username: str, salt_b64: str, pwd_hash_b64: str) -> None:
    users = _load(USERS_DB)
    users[username] = {"salt": salt_b64, "hash": pwd_hash_b64, "created_at": int(time.time())}
    _save(USERS_DB, users)

def get_state() -> Dict[str, Any]:
    return _load(STATE_DB)

def save_state(state: Dict[str, Any]) -> None:
    _save(STATE_DB, state)