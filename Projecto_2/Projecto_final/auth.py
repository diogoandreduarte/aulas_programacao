
from __future__ import annotations
import os, hashlib, hmac, secrets
from datetime import timedelta
from typing import Optional, Tuple
from storage import get_users, put_users, now
from logger import log_event

PBKDF2_ITERATIONS = 200_000

def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return dk.hex()

def create_user(username: str, password: str) -> None:
    users = get_users()
    if username in users:
        raise ValueError("Utilizador já existe.")
    salt = secrets.token_bytes(16)
    users[username] = {
        "salt": salt.hex(),
        "hash": _hash_password(password, salt),
        "failed_attempts": 0,
        "lockout_until": None,
        "last_failed": None,
    }
    put_users(users)

def _check_lockout(user_rec) -> Optional[str]:
    lu = user_rec.get("lockout_until")
    if not lu:
        return None
    try:
        lu_dt = None
        if isinstance(lu, str):
            from datetime import datetime
            lu_dt = datetime.fromisoformat(lu)
        if lu_dt and now() < lu_dt:
            return lu_dt.isoformat()
    except Exception:
        return None
    return None

def authenticate(username: str, password: str, ip: str) -> Tuple[bool, str]:
    users = get_users()
    user_rec = users.get(username)
    if not user_rec:
        # Não revelar se o user existe; regista falha genérica
        log_event(username, ip, "FAIL")
        return False, "Credenciais inválidas."
    # Lockout?
    lo = _check_lockout(user_rec)
    if lo:
        log_event(username, ip, "LOCKED")
        return False, f"Conta temporariamente bloqueada até {lo}."
    # Verify
    salt = bytes.fromhex(user_rec["salt"])
    expected = user_rec["hash"]
    given = _hash_password(password, salt)
    ok = hmac.compare_digest(given, expected)
    if ok:
        user_rec["failed_attempts"] = 0
        user_rec["last_failed"] = None
        user_rec["lockout_until"] = None
        put_users(users)
        log_event(username, ip, "SUCCESS")
        return True, "Autenticação bem-sucedida."
    else:
        # update attempts + exponential backoff
        user_rec["failed_attempts"] = int(user_rec.get("failed_attempts", 0)) + 1
        user_rec["last_failed"] = now().isoformat()
        attempts = user_rec["failed_attempts"]
        if attempts >= 3:
            # backoff exponencial: 2^(attempts-3) minutos (1,2,4,8,...)
            minutes = 2 ** (attempts - 3)
            from datetime import timedelta
            user_rec["lockout_until"] = (now() + timedelta(minutes=minutes)).isoformat()
        put_users(users)
        log_event(username, ip, "FAIL")
        return False, "Credenciais inválidas."
