
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent
USERS_FILE = BASE_DIR / "users.json"
BLACKLIST_FILE = BASE_DIR / "blacklist.json"
LOG_FILE = BASE_DIR / "logs_exemplo.csv"

def now() -> datetime:
    return datetime.now(timezone.utc)

def read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: Path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(path)

def get_users() -> Dict[str, Any]:
    return read_json(USERS_FILE, {})

def put_users(users: Dict[str, Any]) -> None:
    write_json(USERS_FILE, users)

def get_blacklist() -> Dict[str, Any]:
    return read_json(BLACKLIST_FILE, {})

def put_blacklist(black: Dict[str, Any]) -> None:
    write_json(BLACKLIST_FILE, black)

def ensure_log_headers() -> None:
    if not LOG_FILE.exists():
        LOG_FILE.write_text("timestamp,username,ip,result\n", encoding="utf-8")

def log_line(line: str) -> None:
    ensure_log_headers()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

def is_ip_blocked(ip: str, now_dt: Optional[datetime] = None) -> Optional[str]:
    black = get_blacklist()
    rec = black.get(ip)
    if not rec:
        return None
    if rec.get("type") == "perm":
        return "permanent"
    if rec.get("type") == "temp":
        until_s = rec.get("until")
        if not until_s:
            return None
        try:
            until_dt = datetime.fromisoformat(until_s)
        except Exception:
            return None
        if now_dt is None:
            now_dt = now()
        if now_dt < until_dt:
            return f"temporary until {until_dt.isoformat()}"
        else:
            # expired -> remove
            del black[ip]
            put_blacklist(black)
            return None
    return None
