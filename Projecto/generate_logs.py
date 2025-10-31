import csv, random, time, os
from datetime import datetime, timedelta

LOG_PATH = "logs_exemplo.csv"
HEADERS = ["timestamp", "username", "ip", "result"]

USERS = [f"user{i}" for i in range(1, 21)]
IPS = [f"203.0.113.{i}" for i in range(1, 21)] + [f"198.51.100.{i}" for i in range(1, 21)]
RESULTS = ["success", "fail_bad_pwd", "fail_no_user"]

def main():
    now = datetime.utcnow()
    rows = []
    # 240 eventos nas últimas ~3 horas, com alguns IPs maliciosos
    for i in range(240):
        ts = (now - timedelta(seconds=random.randint(0, 3*3600))).isoformat()
        ip = random.choice(IPS)
        if random.random() < 0.25:
            # enviesar falhas
            result = random.choice(["fail_bad_pwd", "fail_bad_pwd", "fail_no_user"])
        else:
            result = "success"
        user = random.choice(USERS)
        rows.append([ts, user, ip, result])

    # Injetar rajadas de falhas para disparar regras
    burst_ip = "203.0.113.200"
    for i in range(12):  # 12 falhas em <5 min
        ts = (now - timedelta(minutes=4, seconds= i*15)).isoformat()
        rows.append([ts, random.choice(USERS), burst_ip, "fail_bad_pwd"])

    scatter_ip = "198.51.100.250"
    for i in range(6):  # 6 users distintos em <10 min
        ts = (now - timedelta(minutes=9, seconds=i*60)).isoformat()
        rows.append([ts, f"userS{i}", scatter_ip, "fail_no_user"])

    rows.sort(key=lambda r: r[0])

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADERS)
        w.writerows(rows)

    print(f"Gerado {len(rows)} registos em {LOG_PATH}")

if __name__ == "__main__":
    main()