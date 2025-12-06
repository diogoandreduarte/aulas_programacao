from cryptography.fernet import Fernet
import os

# === 1. Obter a base path (pasta do script) ===
pasta_base = os.path.dirname(os.path.abspath(__file__))

# === 2. Pedir ao utilizador os nomes dos ficheiros ===
nome_ficheiro_chave = input("Introduza o nome do ficheiro da chave (ex: chave_encriptacao_*.txt): ").strip()
nome_ficheiro_alertas = input("Introduza o nome do ficheiro dos alertas (ex: alertas_encriptados_*.txt): ").strip()

# === 3. Construir paths completos ===
ficheiro_chave = os.path.join(pasta_base, nome_ficheiro_chave)
ficheiro_alertas = os.path.join(pasta_base, nome_ficheiro_alertas)

# === 4. Validar se os ficheiros existem ===
if not os.path.isfile(ficheiro_chave):
    print(f"Ficheiro da chave não encontrado: {ficheiro_chave}")
    exit(1)

if not os.path.isfile(ficheiro_alertas):
    print(f"Ficheiro de alertas não encontrado: {ficheiro_alertas}")
    exit(1)

# === 5. Ler a chave ===
with open(ficheiro_chave, "r", encoding="utf-8") as f:
    linhas = f.readlines()
    if len(linhas) < 2:
        print("Ficheiro de chave mal formatado (esperado pelo menos 2 linhas).")
        exit(1)
    chave = linhas[1].strip()

# Inicializar Fernet
fernet = Fernet(chave.encode())

# === 6. Ler os alertas encriptados ===
with open(ficheiro_alertas, "r", encoding="utf-8") as f:
    linhas = f.readlines()
    alertas_encriptados = [
        linha.strip() for linha in linhas
        if linha.strip() and not linha.startswith("Registo")
    ]

# === 7. Desencriptar os alertas ===
alertas_desencriptados = []
for alerta in alertas_encriptados:
    try:
        alerta_desencriptado = fernet.decrypt(alerta.encode()).decode()
        alertas_desencriptados.append(alerta_desencriptado)
    except Exception as e:
        print(f"Erro ao desencriptar um alerta: {e}")

# === 8. Mostrar os alertas desencriptados ===
print("\n=== Alertas Desencriptados ===")
if alertas_desencriptados:
    for alerta in alertas_desencriptados:
        print(f"- {alerta}")
else:
    print("Nenhum alerta válido foi desencriptado.")
