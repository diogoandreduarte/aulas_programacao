import os, hmac, hashlib, base64
from typing import Tuple

# Parâmetros recomendados (podem ser ajustados no README)
PBKDF2_ITERATIONS = 200_000
DKLEN = 32  # 256 bits

def gen_salt(n: int = 16) -> str:
    return base64.b64encode(os.urandom(n)).decode("utf-8")

def hash_password(password: str, salt_b64: str) -> str:
    salt = base64.b64decode(salt_b64.encode("utf-8"))
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS, dklen=DKLEN)
    return base64.b64encode(dk).decode("utf-8")

def verify_password(password: str, salt_b64: str, pwd_hash_b64: str) -> bool:
    expected = hash_password(password, salt_b64)
    return hmac.compare_digest(expected, pwd_hash_b64)