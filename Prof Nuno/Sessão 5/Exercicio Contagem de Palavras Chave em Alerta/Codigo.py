from cryptography.fernet import Fernet
import datetime
import os


# Obter pasta destino
pasta_base = os.path.dirname(os.path.abspath(__file__))

# Gerar uma chave de encriptação
chave = Fernet.generate_key()
fernet = Fernet(chave)

# Gerar timestamp
data_hora = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Guardar a chave num ficheiro
nome_ficheiro_chave = os.path.join(pasta_base, f"chave_encriptacao_{data_hora}.txt")
with open(nome_ficheiro_chave, "w", encoding="utf-8") as f_chave:
    f_chave.write("Chave de encriptação gerada:\n")
    f_chave.write(chave.decode())

# Mostrar cabeçalho
print("Introduza frases de alerta. Escreva 'sair' para terminar.\n")

# Inicializar lista de alertas e contador
alertas = []
contador_falha101 = 0

# Recolher frases
while True:
    frase = input("Alerta:")
    if frase.lower() == 'sair':
        break
    alertas.append(frase)
    if 'falha 101' in frase.lower():
        contador_falha101 += 1

# Encriptar cada alerta
alertas_encriptados = [fernet.encrypt(alerta.encode()).decode() for alerta in alertas]

# Guardar alertas encriptados num ficheiro
nome_ficheiro_alertas = os.path.join(pasta_base, f"alertas_encriptados_{data_hora}.txt")
with open(nome_ficheiro_alertas, "w", encoding="utf-8") as f_alertas:
    f_alertas.write(f"Registo de alertas encriptados - {data_hora}\n\n")
    for alerta in alertas_encriptados:
        f_alertas.write(f"{alerta}\n")

# Mostrar estatísticas
print(f"Total de alertas introduzidos: {len(alertas)}")
print(f"Alertas com a expressão 'Falha 101': {contador_falha101}")
print(f"Registo encriptado guardado em: {nome_ficheiro_alertas}")
print(f"Chave de encriptação guardada em: {nome_ficheiro_chave}")
