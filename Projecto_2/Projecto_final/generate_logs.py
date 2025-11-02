
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
from storage import LOG_FILE, ensure_log_headers

USERS = ["joao","maria","manuel","david","paulo","paula","rodrigo","joana","rui","daniel"]
IPS_BENIGN = ["10.0.0." + str(i) for i in range(2,30)]
IPS_ATTACKER = ["203.0.113.5","198.51.100.23"]

def main():
    ensure_log_headers()
    start = datetime.now(timezone.utc) - timedelta(hours=26)
    rows = []
    # Normal activity
    for _ in range(150):
        dt = start + timedelta(minutes=random.randint(0, 1500))
        user = random.choice(USERS)
        ip = random.choice(IPS_BENIGN)
        res = "SUCCESS" if random.random() < 0.7 else "FAIL"
        rows.append((dt, user, ip, res))
    # Attack burst (>=10 fails in 5 minutes)
    burst_ip = IPS_ATTACKER[0]
    burst_start = datetime.now(timezone.utc) - timedelta(minutes=30)
    for i in range(12):
        dt = burst_start + timedelta(seconds=i*20)
        user = random.choice(USERS[:3])
        rows.append((dt, user, burst_ip, "FAIL"))
    # Long term attacker (>=30 fails in 24h)
    perm_ip = IPS_ATTACKER[1]
    for i in range(32):
        dt = start + timedelta(minutes=10*i)
        user = random.choice(USERS)
        rows.append((dt, user, perm_ip, "FAIL"))
    rows.sort(key=lambda x: x[0])
    with LOG_FILE.open("a", encoding="utf-8") as f:
        for dt, user, ip, res in rows:
            ts = dt.strftime("%Y-%m-%d %H:%M:%S%z")
            f.write(f"{ts},{user},{ip},{res}\n")
    print(f"Geradas {len(rows)} linhas em {LOG_FILE}")

if __name__ == "__main__":
    main()
