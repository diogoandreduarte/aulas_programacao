from __future__ import annotations
import argparse, getpass, sys
from storage import is_ip_blocked, ensure_log_headers
from auth import create_user, authenticate
from ui import prompt_credentials, prompt_ip
from analyzer import read_logs, analyze, detect_and_block, console_summary


def cmd_create_user(args):
    username = args.username or input("Novo utilizador: ").strip()
    password = args.password or getpass.getpass("Password: ")
    try:
        create_user(username, password)
        print(f"Utilizador '{username}' criado.")
    except ValueError as e:
        print(f"Erro: {e}")


def cmd_login(args):
    ensure_log_headers()
    ip = args.ip or prompt_ip()
    blk = is_ip_blocked(ip)
    if blk:
        print(f"Acesso bloqueado para o IP {ip} ({blk}).")
        sys.exit(1)

    username, password = (args.username, args.password) if (args.username and args.password) else prompt_credentials()
    ok, msg = authenticate(username, password, ip)
    print(msg)

    if args.auto_analyze:
        run_analyzer()


def run_analyzer():
    recs = read_logs()
    stats = analyze(recs)
    print("--- Estatísticas ---")
    print(console_summary(stats))
    blocked = detect_and_block(recs)
    if blocked:
        print("--- Bloqueios aplicados ---")
        for ip, rec in blocked.items():
            print(ip, rec)


def cmd_analyze(_args):
    run_analyzer()


def cmd_gui(_args=None):
    from ui_tk import run_gui
    run_gui()


def main():
    parser = argparse.ArgumentParser(
        description="Plataforma de Autenticação Resiliente + Analisador de Logs",
        add_help=True
    )
    sub = parser.add_subparsers(dest="cmd")

    # --- Subcomandos CLI ---
    p1 = sub.add_parser("create-user", help="Criar utilizador (CLI)")
    p1.add_argument("--username")
    p1.add_argument("--password")
    p1.set_defaults(func=cmd_create_user)

    p2 = sub.add_parser("login", help="Efetuar login")
    p2.add_argument("--username")
    p2.add_argument("--password")
    p2.add_argument("--ip")
    p2.add_argument("--auto-analyze", action="store_true",
                    help="Executa a análise e bloqueio após a tentativa de login")
    p2.set_defaults(func=cmd_login)

    p3 = sub.add_parser("analyze", help="Executar o analisador de logs e aplicar bloqueios")
    p3.set_defaults(func=cmd_analyze)

    p4 = sub.add_parser("gui", help="Abrir interface gráfica Tkinter")
    p4.set_defaults(func=cmd_gui)

    # --- Se não houver argumentos, abrir GUI por defeito ---
    if len(sys.argv) == 1:
        cmd_gui(None)
        return

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
