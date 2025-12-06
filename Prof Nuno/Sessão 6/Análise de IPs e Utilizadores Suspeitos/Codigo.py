# Lista de IPs suspeitos
ips_suspeitos = ["10.0.0.1", "192.168.1.1", "10.1.2.3", "172.16.0.5", "10.10.10.10"]

# Imprimir IPs que começam por "10"
for ip in ips_suspeitos:
    if ip.startswith("10"):
        print(f"IP suspeito: {ip}")

# Dicionário do utilizador
utilizador = {
    "nome": "admin",
    "tentativas": 4,
    "bloqueado": False
}

# Verificar número de tentativas
if utilizador["tentativas"] >= 3:
    utilizador["bloqueado"] = True
print("Dados do utilizador:", utilizador)

# Verificar se a mensagem contém a palavra "falha"
mensagem = "Tentativa de login do utilizador admin falhada"
if "falha" in mensagem.lower():
    print("Falha detetada")