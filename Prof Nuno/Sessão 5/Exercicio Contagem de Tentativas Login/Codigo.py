import time
tentativas = 0

while tentativas < 3:
    nome = input("Introduza o nome de utilizador: ")
    senha = input("Introduza a palavra-passe: ")

    if nome == "admin" and senha == "1234":
        print("Acesso permitido")
        break
    else:
        print("Acesso negado")
        tentativas += 1
        time.sleep(5)

if tentativas == 3:
    print("Conta bloqueada")
    
    

    

    
    


