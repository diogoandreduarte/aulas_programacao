import tkinter as tk
from tkinter import messagebox
from auth import authenticate


def build_ui():
    root = tk.Tk()
    root.title("Login (exemplo inseguro)")
    root.geometry("360x180")
    root.resizable(False, False)

    # Frame principal
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    # Campos
    tk.Label(frame, text="Utilizador:").grid(row=0, column=0, sticky="e", pady=5)
    ent_user = tk.Entry(frame, width=30)
    ent_user.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Palavra-passe:").grid(row=1, column=0, sticky="e", pady=5)
    ent_pass = tk.Entry(frame, width=30)
    ent_pass.grid(row=1, column=1, pady=5)

    # Botões
    def do_login():
        ok, msg = authenticate(ent_user.get(), ent_pass.get())
        if ok:
            messagebox.showinfo("Login", msg)
        else:
            messagebox.showerror("Erro", msg)

    btn_frame = tk.Frame(frame, pady=10)
    btn_frame.grid(row=2, column=0, columnspan=2)

    tk.Button(btn_frame, text="Login", width=10, command=do_login).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Sair", width=10, command=root.destroy).pack(side="left", padx=5)

    # Nota pedagógica
    tk.Label(
        frame,
        fg="red",
        text="Exemplo pedagógico — NÃO usar em produção."
    ).grid(row=3, column=0, columnspan=2, pady=(10, 0))

    return root