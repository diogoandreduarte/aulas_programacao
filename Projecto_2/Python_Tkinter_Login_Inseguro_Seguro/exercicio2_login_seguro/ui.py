
import tkinter as tk
from tkinter import messagebox
from auth import authenticate, create_user

def ensure_demo_user():
    # Cria utilizador demo se ainda não existir
    try:
        ok, _ = authenticate("demo", "Password123!")
        if not ok:
            # forçamos criação (se auth falhar por inexistência)
            create_user("demo", "Password123!")
    except Exception:
        create_user("demo", "Password123!")

def build_ui():
    ensure_demo_user()

    root = tk.Tk()
    root.title("Login seguro — Introduz credenciais")
    root.geometry("380x170")
    root.resizable(False, False)

    tk.Label(root, text="Utilizador:").place(x=20, y=25)
    ent_user = tk.Entry(root, width=28)
    ent_user.place(x=130, y=25)

    tk.Label(root, text="Palavra‑passe:").place(x=20, y=60)
    ent_pass = tk.Entry(root, width=28, show="*")
    ent_pass.place(x=130, y=60)

    status = tk.StringVar(value="Pronto.")
    lbl_status = tk.Label(root, textvariable=status, fg="green")
    lbl_status.place(x=20, y=135)

    def do_login():
        u, p = ent_user.get().strip(), ent_pass.get()
        ok, msg = authenticate(u, p)
        if ok:
            messagebox.showinfo("Login", msg)
            status.set("Autenticado.")
        else:
            messagebox.showwarning("Aviso", msg)
            status.set("Tenta novamente.")

    tk.Button(root, text="Login", width=10, command=do_login).place(x=130, y=95)
    tk.Button(root, text="Sair", width=10, command=root.destroy).place(x=230, y=95)

    tk.Label(root, fg="green", text="Exemplo seguro educativo — hashing, salt, lockout.").place(x=20, y=120)

    return root
