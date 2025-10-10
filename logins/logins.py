tentativas = int(input("Introduza o número de tentativas de login já realizadas: "))

limite = 5

if tentativas < limite:
    restantes = limite - tentativas
    print(f"Ainda tem {restantes} tentativa(s) antes do bloqueio.")
else:
    print("Conta bloqueada.")
    