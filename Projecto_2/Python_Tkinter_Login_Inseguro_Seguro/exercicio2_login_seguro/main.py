import sys
from getpass import getpass


def run_cli_create_user():
    from auth import create_user

    username = input("Novo utilizador: ").strip()
    if not username:
        print("Nome de utilizador vazio.")
        sys.exit(1)

    pw1 = getpass("Nova password: ")
    pw2 = getpass("Confirmar password: ")

    if pw1 != pw2:
        print("As passwords não coincidem.")
        sys.exit(1)

    if len(pw1) < 8:
        print("Password demasiado curta (mínimo 8 caracteres).")
        sys.exit(1)

    create_user(username, pw1)
    print(f"Utilizador '{username}' criado com sucesso.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--create-user":
        run_cli_create_user()
        return

    from ui import build_ui

    app = build_ui()
    app.mainloop()


if __name__ == "__main__":
    main()