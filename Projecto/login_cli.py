import csv, json, time, argparse, getpass, os, ipaddress
from datetime import datetime, timedelta
from typing import Tuple
from auth import gen_salt, hash_password, verify_password
from storage import get_user, upsert_user, get_state, save_state

LOG_PATH = "logs_exemplo.csv"
BLACKLIST_PATH = "blacklist.json"

# Heurística de lockout local: backoff exponencial com base em falhas consecutivas
# Ex.: 1 falha -> 5s; 2 -> 10s; 3 -> 20s; ... (cap em 15 min)
BASE_BACKOFF = 5
MAX_BACKOFF = 15 * 60

CSV_HEADERS = ["timestamp", "username", "ip", "result"]

def ensure_csv():
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADERS)

def load_blacklist():
    if not os.path.exists(BLACKLIST_PATH):
        return {}
    with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def is_ip_blocked(ip: str) -> Tuple[bool, str]:
    bl = load_blacklist()
    now = time.time()
    if ip in bl:
        entry = bl[ip]
        if entry["type"] == "permanent":
            return True, "permanent"
        elif entry["type"] == "temporary" and now < entry.get("until", 0):
            return True, "temporary"
    return False, ""

def record_attempt(username: str, ip: str, result: str):
    ensure_csv()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.utcnow().isoformat(), username, ip, result])

def valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def create_user():
    username = input("Novo utilizador: ").strip()
    pwd = getpass.getpass("Password: ").strip()
    salt = gen_salt()
    pwd_hash = hash_password(pwd, salt)
    upsert_user(username, salt, pwd_hash)
    print(f"Utilizador '{username}' criado.")

def login():
    username = input("Username: ").strip()
    ip = input("IP origem (ex.: 10.0.0.1): ").strip()
    if not valid_ip(ip):
        print("IP inválido.")
        return

    blocked, btype = is_ip_blocked(ip)
    if blocked:
        print(f"Acesso rejeitado: IP em blacklist ({btype}).")
        record_attempt(username, ip, f"blocked_{btype}")
        return

    user = get_user(username)
    state = get_state()
    ustate = state.setdefault(username, {"fails": 0, "next_allowed": 0})

    now = time.time()
    if now < ustate["next_allowed"]:
        wait = int(ustate["next_allowed"] - now)
        print(f"Conta temporariamente bloqueada (backoff). Tenta novamente em {wait}s.")
        record_attempt(username, ip, "local_lockout")
        return

    if not user:
        # user inexistente também conta como falha
        record_attempt(username, ip, "fail_no_user")
        ustate["fails"] += 1
        backoff = min(MAX_BACKOFF, BASE_BACKOFF * (2 ** (ustate["fails"] - 1)))
        ustate["next_allowed"] = now + backoff
        save_state(state)
        print("Credenciais inválidas.")
        return

    pwd = getpass.getpass("Password: ").strip()
    if verify_password(pwd, user["salt"], user["hash"]):
        print("Login bem-sucedido.")
        record_attempt(username, ip, "success")
        ustate["fails"] = 0
        ustate["next_allowed"] = 0
        save_state(state)
    else:
        record_attempt(username, ip, "fail_bad_pwd")
        ustate["fails"] += 1
        backoff = min(MAX_BACKOFF, BASE_BACKOFF * (2 ** (ustate["fails"] - 1)))
        ustate["next_allowed"] = now + backoff
        save_state(state)
        print("Credenciais inválidas.")

def main():
    p = argparse.ArgumentParser(description="Login seguro + logging + lockout/backoff + blacklist")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("create-user")
    sub.add_parser("login")

    args = p.parse_args()
    if args.cmd == "create-user":
        create_user()
    elif args.cmd == "login":
        login()
    else:
        p.print_help()

if __name__ == "__main__":
    main()