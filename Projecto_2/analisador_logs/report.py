
from __future__ import annotations
from typing import Dict, Any
from io_utils import write_csv, write_json

def console_summary(stats: Dict[str, Any]) -> str:
    lines = [
        "Resumo:",
        f"  Total de linhas: {stats['total']}",
        f"  Sucessos: {stats['success']} ({stats['perc_success']}%)",
        f"  Falhas:   {stats['fail']} ({stats['perc_fail']}%)",
        "  IPs suspeitos (>=3 falhas): " + ", ".join(stats['suspicious_ips']) if stats['suspicious_ips'] else "  IPs suspeitos: (nenhum)",
        "",
        "Top falhas por IP:",
    ]
    top_ip = sorted(stats['fail_by_ip'].items(), key=lambda x: x[1], reverse=True)[:10]
    for ip, c in top_ip:
        lines.append(f"  - {ip}: {c}")
    lines.append("")
    lines.append("Top falhas por utilizador:")
    top_user = sorted(stats['fail_by_user'].items(), key=lambda x: x[1], reverse=True)[:10]
    for u, c in top_user:
        lines.append(f"  - {u}: {c}")
    return "\n".join(lines)

def export_reports(stats: Dict[str, Any], out_dir: str) -> Dict[str, str]:
    from pathlib import Path
    out = {}
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)

    rows_ip = [{"ip": ip, "falhas": c} for ip, c in sorted(stats['fail_by_ip'].items(), key=lambda x: x[1], reverse=True)]
    path_ip = base / "relatorio_falhas.csv"
    write_csv(path_ip, rows_ip, fieldnames=["ip","falhas"])
    out['csv_falhas_por_ip'] = str(path_ip)

    path_json = base / "relatorio_completo.json"
    write_json(path_json, stats)
    out['json_completo'] = str(path_json)
    return out
