
from __future__ import annotations
import getpass

def prompt_credentials() -> tuple[str, str]:
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    return username, password

def prompt_ip() -> str:
    ip = input("IP (ex: 192.168.1.10): ").strip()
    if not ip:
        ip = "127.0.0.1"
    return ip
