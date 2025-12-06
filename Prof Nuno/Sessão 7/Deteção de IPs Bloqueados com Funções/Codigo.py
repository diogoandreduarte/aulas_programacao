def obter_lista_ips():
    print("Introduza 5 endereços IP:")
    lista_ips = []
    for i in range(5):
        ip = input(f"> ").strip()
        lista_ips.append(ip)
    return lista_ips

def verificar_bloqueio(ip, lista_bloqueados):
    return ip in lista_bloqueados

def gerar_relatorio(lista_ips, lista_bloqueados):
    print("\nRelatório:")
    for ip in lista_ips:
        estado = "Bloqueado" if verificar_bloqueio(ip, lista_bloqueados) else "Limpo"
        print(f"{ip} -> {estado}")

def main():
    lista_bloqueados = ["10.0.0.1", "172.16.8.3"]
    lista_ips = obter_lista_ips()
    gerar_relatorio(lista_ips, lista_bloqueados)

if __name__ == "__main__":
    main()
