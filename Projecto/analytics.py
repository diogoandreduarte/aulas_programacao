#!/usr/bin/env python3
import csv
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import argparse
import os

LOG_PATH = "logs_exemplo.csv"
BLACKLIST_PATH = "blacklist.json"

# --- Parâmetros das regras (ajusta se necessário)
SHORT_FAILS = 10              # >=10 falhas
SHORT_WINDOW_MIN = 5          # em 5 minutos
SHORT_BLOCK_SECS = 60 * 60    # bloqueio 1h

LONG_FAILS = 30               # >=30 falhas
LONG_WINDOW_H = 24            # em 24h -> bloqueio permanente

SCATTERED_USERS = 5           # >=5 utilizadores distintos
SCATTERED_WINDOW_MIN = 10     # em 10 minutos
SCATTERED_BLOCK_SECS = 60 * 60  # bloqueio 1h

# --------------------- Utils de I/O ---------------------

def load_logs() -> List[Dict[str, str]]:
    if not os.path.exists(LOG_PATH):
        raise FileNotFoundError(f"Ficheiro de logs não encontrado: {LOG_PATH}")
    rows: List[Dict[str, str]] = []
    with open(LOG_PATH, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def save_blacklist(bl: Dict[str, Dict[str, Any]]) -> None:
    with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(bl, f, indent=2, ensure_ascii=False)

def load_blacklist() -> Dict[str, Dict[str, Any]]:
    try:
        with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Aceita "2025-11-30T14:03:31.519413" ou "2025-11-30T14:03:31.519413Z"
def parse_ts(ts: str) -> float:
    ts = ts.rstrip("Z")
    return datetime.fromisoformat(ts).timestamp()

def iso_utc(ts_seconds: float) -> str:
    return datetime.utcfromtimestamp(ts_seconds).isoformat()

# --------------------- Motor de regras ---------------------

def apply_rules(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
    now = time.time()
    bl = load_blacklist()

    # ip -> [(ts, user, result)]
    by_ip: Dict[str, List[Tuple[float, str, str]]] = defaultdict(list)
    for row in rows:
        ts = parse_ts(row["timestamp"])
        by_ip[row["ip"]].append((ts, row["username"], row["result"]))

    for ip, events in by_ip.items():
        events.sort(key=lambda x: x[0])

        # Lista de timestamps de falhas
        fails_ts = [ts for ts, _, res in events if res.startswith("fail")]

        # --- Regra 1: >=10 falhas em 5 min (bloqueio 1h)
        window_5m = SHORT_WINDOW_MIN * 60
        i = 0
        for j in range(len(fails_ts)):
            while fails_ts[j] - fails_ts[i] > window_5m:
                i += 1
            if (j - i + 1) >= SHORT_FAILS:
                bl[ip] = {
                    "type": "temporary",
                    "reason": f">={SHORT_FAILS} fails/{SHORT_WINDOW_MIN}m",
                    "since": now,
                    "until": now + SHORT_BLOCK_SECS,
                    "since_human": iso_utc(now),
                    "until_human": iso_utc(now + SHORT_BLOCK_SECS),
                }
                break  # já bloqueado por esta regra

        # --- Regra 2: >=30 falhas em 24h (bloqueio permanente)
        window_24h = LONG_WINDOW_H * 3600
        i = 0
        for j in range(len(fails_ts)):
            while fails_ts[j] - fails_ts[i] > window_24h:
                i += 1
            if (j - i + 1) >= LONG_FAILS:
                bl[ip] = {
                    "type": "permanent",
                    "reason": f">={LONG_FAILS} fails/{LONG_WINDOW_H}h",
                    "since": now,
                    "since_human": iso_utc(now),
                }
                break

        # --- Regra 3: >=5 utilizadores distintos em 10 min (bloqueio 1h)
        fails = [(ts, user) for ts, user, res in events if res.startswith("fail")]
        window_10m = SCATTERED_WINDOW_MIN * 60
        i = 0
        for j in range(len(fails)):
            tsj, _ = fails[j]
            while tsj - fails[i][0] > window_10m:
                i += 1
            distinct_users = len(set(u for _, u in fails[i:j+1]))
            if distinct_users >= SCATTERED_USERS:
                # Não sobrepor permanente
                if ip not in bl or bl[ip]["type"] != "permanent":
                    bl[ip] = {
                        "type": "temporary",
                        "reason": f">={SCATTERED_USERS} users/{SCATTERED_WINDOW_MIN}m",
                        "since": now,
                        "until": now + SCATTERED_BLOCK_SECS,
                        "since_human": iso_utc(now),
                        "until_human": iso_utc(now + SCATTERED_BLOCK_SECS),
                    }
                break

    return bl

# --------------------- Estatísticas ---------------------

def stats(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    total = len(rows)
    by_result: Dict[str, int] = defaultdict(int)
    fail_count_by_ip: Dict[str, int] = defaultdict(int)
    attacked_users_by_ip: Dict[str, set] = defaultdict(set)

    for r in rows:
        by_result[r["result"]] += 1
        if r["result"].startswith("fail"):
            fail_count_by_ip[r["ip"]] += 1
            attacked_users_by_ip[r["ip"]].add(r["username"])

    top_ips_by_fails = sorted(fail_count_by_ip.items(), key=lambda x: x[1], reverse=True)[:10]
    ips_by_distinct_users = sorted(
        ((ip, len(users)) for ip, users in attacked_users_by_ip.items()),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return {
        "total_events": total,
        "by_result": dict(by_result),
        "top_ips_by_fails": top_ips_by_fails,
        "ips_by_distinct_users_attacked": ips_by_distinct_users,
    }

# --------------------- CLI / Main ---------------------

def main():
    parser = argparse.ArgumentParser(description="Analytics de tentativas de login e geração de blacklist.")
    parser.add_argument(
        "--show-human",
        action="store_true",
        help="Imprime datas legíveis (UTC) ao apresentar a blacklist atualizada."
    )
    args = parser.parse_args()

    rows = load_logs()
    bl = apply_rules(rows)
    save_blacklist(bl)

    s = stats(rows)
    print("=== Estatísticas ===")
    print(json.dumps(s, indent=2, ensure_ascii=False))

    print("\n=== Blacklist atualizada ===")
    if args.show_human:  # <-- underscore
        printable = {}
        for ip, entry in bl.items():
            e = dict(entry)
            if "since" in e and "since_human" not in e:
                e["since_human"] = iso_utc(e["since"])
            if e.get("until") and "until_human" not in e:
                e["until_human"] = iso_utc(e["until"])
            printable[ip] = e
        print(json.dumps(printable, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(bl, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()