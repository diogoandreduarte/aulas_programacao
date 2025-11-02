# login_inseguro_tk_comentado.py
# Exemplo pedagógico de um login simples usando Tkinter.
# ATENÇÃO (Didático): Este exemplo é intencionalmente INSEGURO.
# Objetivo: Demonstrar uma interface gráfica de login e, ao mesmo tempo,
# discutir más práticas de segurança que NUNCA devem ser usadas em produção.
#
# Problemas principais deste exemplo:
# - Palavras-passe guardadas em claro no código (credenciais hardcoded);
# - Verificação direta de password em texto claro (sem hashing/salting);
# - Sem proteção contra tentativas repetidas (brute force / rate limiting);
# - Sem registo/auditoria de eventos de segurança;
# - Sem separação de responsabilidades (não há backend, nem camadas de segurança);
# - Dados sensíveis presentes em memória sem qualquer proteção.
#
# Nota: Este ficheiro é para fins pedagógicos. Para um exemplo seguro,
# ver a versão que usa PBKDF2/Argon2/Bcrypt.

import tkinter as tk
from tkinter import messagebox

# --- Credenciais "hardcoded" (INSEGURAS) ---
# Guardar credenciais no código é uma prática incorreta porque:
#  1) Qualquer pessoa com acesso ao ficheiro fonte (ou ao binário) pode ler as passwords;
#  2) O controlo de versões (Git) também expõe as credenciais ao histórico;
#  3) Não há possibilidade de rotação/alteração centralizada de password.
# Em contexto real, deve usar-se hashing com salt (ex.: PBKDF2/Argon2/Bcrypt) e
# armazenamento protegido fora do código.
CREDENTIALS = {
    "admin": "admin123",
    "utilizador": "senha123",
    "guest": "guest"
}

def verificar_credenciais(username: str, password: str) -> bool:
    """
    Verifica se o par (username, password) existe nas CREDENTIALS.
    Retorna True se corresponder, False caso contrário.

    ALERTA DE SEGURANÇA:
    - Aqui comparamos password em TEXTO CLARO.
    - Não há hashing, nem salting, nem KDF (Key Derivation Function).
    - Isto torna o sistema vulnerável a compromissos de código/ficheiro.
    """
    # Normalização mínima: removemos espaços acidentais.
    u = username.strip()
    p = password.strip()
    # Verificação direta (INSEGURA): compara-se a password fornecida com a string em claro.
    # Em produção, seria necessário comparar o hash derivado da password do utilizador
    # com o hash armazenado (com salt + iterações).
    return CREDENTIALS.get(u) == p

def on_login():
    """
    Callback executado quando o utilizador pressiona 'Login'.
    Lê os campos e faz uma verificação simples.

    Risco: Não existe qualquer limitação de tentativas.
    Um atacante pode tentar milhares de passwords (brute force) sem bloqueio.
    """
    # Obter o que o utilizador escreveu nos campos (estas strings ficam em memória enquanto a função corre).
    user = entry_user.get()
    pwd = entry_pwd.get()

    # Validação mínima dos campos (apenas UI).
    if not user or not pwd:
        messagebox.showwarning("Aviso", "Por favor preencha utilizador e palavra-passe.")
        return

    # Verificação insegura (texto claro).
    if verificar_credenciais(user, pwd):
        messagebox.showinfo("Sucesso", f"Bem-vindo/a, {user}!")
        # Em caso real, aqui abriríamos a janela principal e inicializaríamos sessão de forma segura.
        # Por simplicidade, apenas limpamos os campos.
        entry_user.delete(0, tk.END)
        entry_pwd.delete(0, tk.END)
    else:
        # Mensagem genérica. (Ponto positivo: não revela se o utilizador existe.)
        messagebox.showerror("Erro", "Credenciais inválidas.")

def on_quit():
    """Fecha a aplicação com confirmação."""
    if messagebox.askyesno("Sair", "Tem a certeza que pretende sair?"):
        root.destroy()

# --- Construção da interface (UI Tkinter) ---
# Cria a janela principal da aplicação.
root = tk.Tk()
root.title("Login (exemplo inseguro)")
# Define o tamanho da janela (largura x altura).
root.geometry("350x180")
# Impede redimensionamento (para o exemplo ficar consistente).
root.resizable(False, False)

# Frame principal com algum espaçamento interno (padding).
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(expand=True, fill=tk.BOTH)

# Rótulo e campo de entrada para o utilizador.
lbl_user = tk.Label(frame, text="Utilizador:")
lbl_user.grid(row=0, column=0, sticky="w", pady=(0, 6))
entry_user = tk.Entry(frame, width=30)
entry_user.grid(row=0, column=1, pady=(0, 6))
entry_user.focus_set()  # Coloca o cursor neste campo ao iniciar a app.

# Rótulo e campo de entrada para a password.
# A opção show="*" apenas mascara visualmente, NÃO protege a password em memória.
lbl_pwd = tk.Label(frame, text="Palavra-passe:")
lbl_pwd.grid(row=1, column=0, sticky="w", pady=(0, 6))
entry_pwd = tk.Entry(frame, width=30, show="*")
entry_pwd.grid(row=1, column=1, pady=(0, 6))

# Botão de Login: chama a função on_login quando clicado.
btn_login = tk.Button(frame, text="Login", width=10, command=on_login)
btn_login.grid(row=2, column=0, pady=(10, 0))

# Botão de Sair: chama a função on_quit.
btn_quit = tk.Button(frame, text="Sair", width=10, command=on_quit)
btn_quit.grid(row=2, column=1, pady=(10, 0), sticky="e")

# Atalho: pressionar a tecla Enter ativa o login.
root.bind("<Return>", lambda event: on_login())

# Rodapé com um aviso explícito de que este é um exemplo pedagógico e inseguro.
lbl_warn = tk.Label(
    root,
    text="Exemplo pedagógico — NÃO usar em ambiente de produção.",
    fg="red",
    font=("Arial", 8)
)
lbl_warn.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 6))

# Arranque do loop principal do Tkinter (mantém a janela ativa).
if __name__ == "__main__":
    root.mainloop()