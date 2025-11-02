
import os, hmac, hashlib, secrets, base64, time
from typing import Tuple
from storage import get_user, put_user, now

PBKDF2_ITERATIONS = 120_000
LOCK_MAX_ATTEMPTS = 5
LOCK_BASE_SECONDS = 30

def _pbkdf2(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

def create_user(username: str, password: str) -> None:
    salt = secrets.token_bytes(16)
    h = _pbkdf2(password, salt, PBKDF2_ITERATIONS)
    rec = {
        "salt": base64.b64encode(salt).decode(),
        "hash": base64.b64encode(h).decode(),
        "iterations": PBKDF2_ITERATIONS,
        "fail_count": 0,
        "locked_until": 0.0,
    }
    put_user(username, rec)

def _locked(rec: dict) -> bool:
    return now() < rec.get("locked_until", 0.0)

def _register_fail(rec: dict) -> None:
    rec["fail_count"] = rec.get("fail_count", 0) + 1
    if rec["fail_count"] >= LOCK_MAX_ATTEMPTS:
        exp = LOCK_BASE_SECONDS * (2 ** (rec["fail_count"] - LOCK_MAX_ATTEMPTS))
        rec["locked_until"] = now() + exp
    put_user(rec["_username"], rec)

def _register_success(rec: dict) -> None:
    rec["fail_count"] = 0
    rec["locked_until"] = 0.0
    put_user(rec["_username"], rec)

def authenticate(username: str, password: str) -> Tuple[bool, str]:
    rec = get_user(username)
    # Mensagem genérica por omissão
    generic = "Credenciais inválidas."

    if not rec:
        # Tempo artificial para não denunciar inexistência
        _ = _pbkdf2(password, b"0"*16, 50_000)
        return False, generic

    rec["_username"] = username  # para persistir

    if _locked(rec):
        return False, "Conta temporariamente bloqueada. Tenta novamente mais tarde."

    try:
        salt = base64.b64decode(rec["salt"])
        iterations = int(rec["iterations"])
        expected = base64.b64decode(rec["hash"])
    except Exception:
        return False, generic

    candidate = _pbkdf2(password, salt, iterations)
    if hmac.compare_digest(candidate, expected):
        _register_success(rec)
        return True, "Autenticação concluída."
    else:
        _register_fail(rec)
        return False, generic
