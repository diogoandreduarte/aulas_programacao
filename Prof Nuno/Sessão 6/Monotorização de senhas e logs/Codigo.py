# ler 5 senhas
senhas = []
for i in range(5):
    senha = input(f"Introduza a senha {i+1}: ")
    senhas.append(senha)

# Verificar senhas
registo = {"fortes": 0, "fracas": 0}

for senha in senhas:
    if len(senha) < 8:
        print("Senha fraca")
        registo["fracas"] += 1
    else:
        print("Senha forte")
        registo["fortes"] += 1

# Mensagem final
print(f"Foram registadas {registo['fortes']} senhas fortes e {registo['fracas']} senhas fracas.")

# Verificação da palavra "root"
log = "Tentativa de acesso do utilizador root"
if "root" in log:
    print("A palavra 'root' foi detetada.")
else:
    print("A palavra 'root' não foi detetada.")
