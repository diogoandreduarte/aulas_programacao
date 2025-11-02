
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional, Callable
from auth import authenticate, create_user
from storage import is_ip_blocked

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plataforma de Autenticação — UC00606")
        self.geometry("380x240")
        self.resizable(False, False)

        # Username
        tk.Label(self, text="Username").pack(pady=(20, 0))
        self.username_var = tk.StringVar()
        tk.Entry(self, textvariable=self.username_var).pack()

        # Password
        tk.Label(self, text="Password").pack(pady=(10, 0))
        self.password_var = tk.StringVar()
        tk.Entry(self, textvariable=self.password_var, show="*").pack()

        # IP
        tk.Label(self, text="IP").pack(pady=(10, 0))
        self.ip_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(self, textvariable=self.ip_var).pack()

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Login", width=12, command=self.on_login).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Criar Utilizador", width=12, command=self.on_create_user).grid(row=0, column=1, padx=5)

        # Status
        self.status = tk.StringVar(value="Pronto.")
        tk.Label(self, textvariable=self.status, fg="gray").pack(pady=(5,0))

    def on_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        ip = self.ip_var.get().strip() or "127.0.0.1"

        blocked = is_ip_blocked(ip)
        if blocked:
            messagebox.showwarning("IP bloqueado", f"Acesso bloqueado para o IP {ip} ({blocked}).")
            return

        ok, msg = authenticate(username, password, ip)
        self.status.set(msg)
        if ok:
            messagebox.showinfo("Sucesso", msg)
        else:
            messagebox.showerror("Falha", msg)

    def on_create_user(self):
        username = simpledialog.askstring("Criar utilizador", "Novo username:")
        if not username:
            return
        # Ask for password twice
        pwd1 = simpledialog.askstring("Password", "Password:", show="*")
        if not pwd1:
            return
        pwd2 = simpledialog.askstring("Password", "Confirmar password:", show="*")
        if pwd1 != pwd2:
            messagebox.showerror("Erro", "As passwords não coincidem.")
            return
        try:
            create_user(username.strip(), pwd1)
            messagebox.showinfo("OK", f"Utilizador '{username}' criado.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

def run_gui():
    app = LoginApp()
    app.mainloop()
