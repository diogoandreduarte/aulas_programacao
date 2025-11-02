# login_seguro_tk_comentado.py
# Exemplo educativo de um login seguro usando Tkinter.
# Comentários e explicações em Português (PT-PT).
# Implementa: PBKDF2-HMAC-SHA256, salt único, comparação em tempo constante,
# lockout com backoff exponencial e criação segura de utilizadores via CLI.

import json
import os
import sys
import time
import base64
import secrets
import hashlib
import hmac
from getpass import getpass
import tkinter as tk
from tkinter import messagebox

# Ficheiro onde são guardados os utilizadores (salt, hash, iterations).
USERS_FILE = "users_secure.json"

# Parâmetros de PBKDF2 para demonstração (ajustar em produção).
DEFAULT_ITERATIONS = 200_000  # número de iterações - aumenta o custo para atacante
DKLEN = 32  # comprimento do derived key (256 bits)

# Política de lockout / rate limiting (exemplo pedagógico).
MAX_ATTEMPTS = 5          # tentativas consecutivas antes de bloquear
BASE_LOCK_SECONDS = 30    # tempo base de bloqueio (duplica em cada novo bloqueio)

# Estrutura em memória para contagem de falhas (não persistida nesta versão).
_failed_attempts = {}  # username -> {"count": int, "lock_until": timestamp, "lock_count": int}


# -------------------------
# Gestão do ficheiro de utilizadores
# -------------------------
def _load_users() -> dict:
    """Carrega o ficheiro de utilizadores (ou devolve um dict vazio)."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, PermissionError) as e:
        print(f"[ERRO] Não foi possível ler {USERS_FILE}: {e}")
        return {}


def _save_users(users: dict) -> None:
    """Guarda o dicionário de utilizadores de forma atómica (escreve para .tmp e move)."""
    temp = USERS_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(temp, USERS_FILE)


# -------------------------
# Função de hashing (PBKDF2)
# -------------------------
def _hash_password(password: str, salt: bytes, iterations: int = DEFAULT_ITERATIONS) -> bytes:
    """
    Deriva um hash a partir da password usando PBKDF2-HMAC-SHA256.
    - password: string fornecida pelo utilizador
    - salt: bytes únicos por utilizador (secrets.token_bytes)
    - iterations: número de iterações do KDF
    Retorna bytes do derived key.
    """
    pwd_bytes = password.encode("utf-8")
    try:
        dk = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt, iterations, dklen=DKLEN)
        return dk
    finally:
        # Tentar sobrescrever o buffer com zeros para reduzir tempo de vida da password em memória.
        pwd_bytes = b"\x00" * len(pwd_bytes)


def create_user_cli():
    """Cria um utilizador via CLI (usa getpass para não expor password no histórico)."""
    users = _load_users()
    username = input("Novo utilizador (username): ").strip()
    if not username:
        print("Username inválido.")
        return
    if username in users:
        print("Utilizador já existe.")
        return

    pwd = getpass("Password: ")
    pwd2 = getpass("Confirmar password: ")
    if pwd != pwd2:
        print("Passwords não coincidem.")
        return
    if len(pwd) < 8:
        print("Password demasiado curta (mínimo 8).")
        return

    salt = secrets.token_bytes(16)  # 128-bit salt
    iterations = DEFAULT_ITERATIONS
    dk = _hash_password(pwd, salt, iterations)

    # Guardar salt e hash em base64 para persistência em JSON.
    users[username] = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "hash": base64.b64encode(dk).decode("utf-8"),
        "iterations": iterations
    }
    _save_users(users)

    # Limpar variáveis sensíveis
    pwd = None
    pwd2 = None
    dk = None
    salt = None

    print(f"[OK] Utilizador '{username}' criado com sucesso.")


# -------------------------
# Lockout / contagem de falhas
# -------------------------
def _is_locked(username: str) -> (bool, int):
    """Verifica se o utilizador está bloqueado; devolve (locked, seconds_remaining)."""
    info = _failed_attempts.get(username)
    if not info:
        return False, 0
    lock_until = info.get("lock_until", 0)
    now = time.time()
    if now < lock_until:
        return True, int(lock_until - now)
    return False, 0


def _register_failed_attempt(username: str):
    """Regista uma tentativa falhada e aplica lockout se necessário (backoff exponencial)."""
    info = _failed_attempts.setdefault(username, {"count": 0, "lock_until": 0, "lock_count": 0})
    info["count"] += 1
    if info["count"] >= MAX_ATTEMPTS:
        info["lock_count"] = info.get("lock_count", 0) + 1
        lock_time = BASE_LOCK_SECONDS * (2 ** (info["lock_count"] - 1))
        info["lock_until"] = time.time() + lock_time
        info["count"] = 0  # reset attempts after lock
    _failed_attempts[username] = info


def _register_success(username: str):
    """Limpa contadores após login bem-sucedido."""
    if username in _failed_attempts:
        del _failed_attempts[username]


# -------------------------
# Verificação segura de credenciais
# -------------------------
def verify_credentials(username: str, password: str) -> bool:
    """
    Verifica credenciais de forma segura:
    - carrega dados do ficheiro
    - aplica dummy hash se utilizador não existir (evitar enumeração por tempo)
    - calcula hash e compara com hmac.compare_digest (tempo constante)
    - regista falhas/sucesso para lockout
    """
    users = _load_users()

    # Verificar lockout pré-existente
    locked, remaining = _is_locked(username)
    if locked:
        return False

    record = users.get(username)
    if record is None:
        # Fazer um hash dummy para igualar tempo de resposta (mitigar enumeração por temporização)
        dummy_salt = secrets.token_bytes(16)
        _ = _hash_password("dummy_password", dummy_salt, DEFAULT_ITERATIONS)
        return False

    try:
        salt = base64.b64decode(record["salt"])
        expected_hash = base64.b64decode(record["hash"])
        iterations = int(record.get("iterations", DEFAULT_ITERATIONS))
    except Exception:
        # Dados inválidos/corrompidos no ficheiro
        return False

    # Calcular hash da password fornecida
    candidate = _hash_password(password, salt, iterations)

    # Comparação em tempo-constante para mitigar ataques de timing
    ok = hmac.compare_digest(candidate, expected_hash)

    # Limpar variável sensível
    candidate = None

    if ok:
        _register_success(username)
        return True
    else:
        _register_failed_attempt(username)
        return False


# -------------------------
# Interface gráfica (Tkinter)
# -------------------------
def launch_gui():
    """Cria e inicia a UI de login com Tkinter."""
    root = tk.Tk()
    root.title("Login Seguro (exemplo pedagógico)")
    root.geometry("380x210")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=12, pady=12)
    frame.pack(expand=True, fill=tk.BOTH)

    lbl = tk.Label(frame, text="Login (seguro) - Introduz credenciais", font=("Segoe UI", 11))
    lbl.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    tk.Label(frame, text="Utilizador:").grid(row=1, column=0, sticky="w")
    entry_user = tk.Entry(frame, width=30)
    entry_user.grid(row=1, column=1, pady=4)
    entry_user.focus_set()

    tk.Label(frame, text="Palavra-passe:").grid(row=2, column=0, sticky="w")
    entry_pwd = tk.Entry(frame, width=30, show="*")
    entry_pwd.grid(row=2, column=1, pady=4)

    status_var = tk.StringVar()
    status_var.set("Pronto.")
    lbl_status = tk.Label(root, textvariable=status_var, fg="blue")
    lbl_status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(0, 8))

    def on_login(event=None):
        """Handler do botão de login na GUI."""
        user = entry_user.get().strip()
        pwd = entry_pwd.get()
        if not user or not pwd:
            messagebox.showwarning("Aviso", "Preencha utilizador e palavra-passe.")
            return

        locked, seconds = _is_locked(user)
        if locked:
            messagebox.showerror("Bloqueado", f"Conta temporariamente bloqueada. Tente novamente dentro de {seconds}s.")
            return

        # Verificação segura
        ok = verify_credentials(user, pwd)

        # Limpar o campo da password na UI para reduzir exposição em memória
        entry_pwd.delete(0, tk.END)
        pwd = None

        if ok:
            status_var.set(f"Login bem-sucedido. Bem-vindo/a, {user}.")
            messagebox.showinfo("Sucesso", f"Login bem-sucedido. Bem-vindo/a, {user}.")
        else:
            locked2, sec2 = _is_locked(user)
            if locked2:
                messagebox.showerror("Bloqueado", f"Conta bloqueada por muitas tentativas. Tente novamente em {sec2}s.")
                status_var.set("Conta bloqueada.")
            else:
                messagebox.showerror("Erro", "Credenciais inválidas.")
                status_var.set("Credenciais inválidas.")

    btn_login = tk.Button(frame, text="Login", width=12, command=on_login)
    btn_login.grid(row=3, column=0, pady=8)

    btn_quit = tk.Button(frame, text="Sair", width=12, command=root.destroy)
    btn_quit.grid(row=3, column=1, pady=8, sticky="e")

    root.bind("<Return>", on_login)

    footer = tk.Label(root, text="Exemplo seguro educativo — conceitos: hashing, salt, lockout.", font=("Segoe UI", 8), fg="green")
    footer.pack(side=tk.BOTTOM, pady=(0, 6))

    root.mainloop()


# -------------------------
# CLI / Entrypoint
# -------------------------
def print_help():
    print("Uso:")
    print("  python secure_login_tk.py            -> abre GUI de login")
    print("  python secure_login_tk.py --create-user -> criar utilizador via terminal (getpass)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-user":
        create_user_cli()
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)
    else:
        launch_gui()