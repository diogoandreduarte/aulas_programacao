
USERS = {
    # username: plaintext password  (INSEGURO!)
    "diogo": "Password123!",
    "duarte": "letmein",
}

def authenticate(username: str, password: str) -> tuple[bool, str]:
    if username not in USERS:
        return False, "Utilizador não existe."
    if USERS[username] != password:
        return False, "Palavra‑passe incorreta para o utilizador fornecido."
    return True, "Login efetuado com sucesso!"
