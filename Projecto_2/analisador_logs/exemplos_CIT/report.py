# report.py
def resumo_consola(contagens_ip, top_users, percentagens, suspeitos):
    """Imprime o resumo da análise no ecrã."""
    print("\n=== RELATÓRIO DE LOGS ===")
    print("Falhas por IP:", contagens_ip)
    print("Top utilizadores com falhas:", top_users)
    print(f"Percentagens → Sucesso: {percentagens['sucesso']}% | Falha: {percentagens['falha']}%")
    if suspeitos:
        print("IPs suspeitos (falhas ≥ limite):", ", ".join(suspeitos))
    else:
        print("Sem IPs suspeitos.")
