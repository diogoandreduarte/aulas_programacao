
import json, time
from pathlib import Path

DB_FILE = Path(__file__).parent / "users_secure.json"

def load_db() -> dict:
    if not DB_FILE.exists():
        return {"users": {}}
    return json.loads(DB_FILE.read_text(encoding="utf-8"))

def save_db(data: dict) -> None:
    DB_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_user(u: str) -> dict | None:
    return load_db()["users"].get(u)

def put_user(u: str, record: dict) -> None:
    db = load_db()
    db["users"][u] = record
    save_db(db)

def now() -> float:
    return time.time()
