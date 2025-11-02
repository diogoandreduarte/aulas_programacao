# main.py
from io_utils import ler_ficheiro, escrever_csv, escrever_json
from parser import detetar_formato, parse_linhas
from analytics import (
    contar_falhas_por_ip,
    top_utilizadores_visados,
    percentagem_sucesso,
    ips_suspeitos
)
from report import resumo_consola

def main():
    """Coordena todo o processo de análise dos logs."""
    caminho = "logs_exemplo.csv"  # Caminho do ficheiro de logs
    linhas = ler_ficheiro(caminho)
    if not linhas:
        return

    formato = detetar_formato(linhas)
    registos = parse_linhas(linhas, formato)

    contagens_ip = contar_falhas_por_ip(registos)
    top_users = top_utilizadores_visados(registos)
    percentagens = percentagem_sucesso(registos)
    suspeitos = ips_suspeitos(contagens_ip, limite=3)

    resumo_consola(contagens_ip, top_users, percentagens, suspeitos)

    # Exportar resultados
    escrever_csv("relatorio_falhas.csv", [{"ip": ip, "falhas": n} for ip, n in contagens_ip.items()])
    escrever_json("relatorio_completo.json", {
        "contagens_ip": contagens_ip,
        "top_users": top_users,
        "percentagens": percentagens,
        "suspeitos": suspeitos
    })

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERRO CRÍTICO] Ocorreu um erro inesperado: {e}")
