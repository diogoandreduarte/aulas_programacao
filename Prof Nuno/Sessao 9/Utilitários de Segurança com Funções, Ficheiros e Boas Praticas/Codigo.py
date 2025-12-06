import hashlib

def hash_password(pwd: str) -> str:
    """
    Calcula o hash SHA-256 da password fornecida.
    Recebe como parâmetro a password.
    Devolve o hash SHA-256 da password. 
    """
    return hashlib.sha256(pwd.encode()).hexdigest()

def check_password(pwd: str, pwd_hash: str) -> bool:
    """
    Verifica se a password corresponde ao hash fornecido.
    Recebe password e hash esperado.
    Devolve True se o hash da password coincidir, senão False.
    """
    return hash_password(pwd) == pwd_hash

def mask_ip(ip: str) -> str:
    """
    Mascara IP válido.
    Recebe IP no formato a.b.c.d.
    Devolve IP mascarado ou "IP inválido".
    """
    partes = ip.split(".")
    if len(partes) == 4 and all(p.isdigit() for p in partes):
        return f"{partes[0]}.***.***.{partes[3]}"
    return "IP inválido"

def is_corporate_email(email: str, dominio: str = "empresa.pt") -> bool:
    """
    Verifica se o email pertence ao domínio corporativo.
    Recebe email a verificar e o dominio corporativo.
    Devolve True se o email termina com @dominio, senão False.
    """
    return email.lower().endswith(f"@{dominio.lower()}")

def main():
    """
    Função principal que recebe dados do utilizador e mostra os resultados.
    """
    pwd = input("Insira a sua password: ")
    email = input("Insira o seu email: ")
    ip = input("Insira o seu IP: ")

    pwd_hash = hash_password(pwd)
    corporativo = is_corporate_email(email)
    ip_mascarado = mask_ip(ip)

    print("\n--- Resultados ---")
    print(f"Hash da password: {pwd_hash}")
    print(f"Email corporativo: {'Sim' if corporativo else 'Não'}")
    print(f"IP mascarado: {ip_mascarado}")

if __name__ == "__main__":
    main()

