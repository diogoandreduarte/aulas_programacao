
from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Iterable
from storage import LOG_FILE, get_blacklist, put_blacklist

DTFMT = "%Y-%m-%d %H:%M:%S%z"

def _parse_row(row: List[str]):
    # timestamp,username,ip,result
    ts_s, username, ip, result = row
    # normalize timestamp to aware datetime
    try:
        dt = datetime.strptime(ts_s, DTFMT)
    except ValueError:
        # If missing %z, treat as UTC
        dt = datetime.fromisoformat(ts_s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt, username, ip, result.strip().upper()

def read_logs() -> List[Tuple[datetime, str, str, str]]:
    recs = []
    if not LOG_FILE.exists():
        return recs
    with LOG_FILE.open("r", encoding="utf-8") as f:
        next(f, None)  # skip header
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 4:
                continue
            recs.append(_parse_row(parts[:4]))
    return recs

def analyze(recs) -> Dict[str, any]:
    # Basic stats
    per_ip_fail = defaultdict(int)
    per_user_fail = defaultdict(int)
    total = len(recs)
    fail = 0
    success = 0
    for dt, user, ip, res in recs:
        if res == "FAIL":
            fail += 1
            per_ip_fail[ip] += 1
            per_user_fail[user] += 1
        elif res == "SUCCESS":
            success += 1
    return {
        "total": total,
        "success": success,
        "fail": fail,
        "per_ip_fail": dict(sorted(per_ip_fail.items(), key=lambda x: x[1], reverse=True)),
        "per_user_fail": dict(sorted(per_user_fail.items(), key=lambda x: x[1], reverse=True)),
    }

def detect_and_block(recs) -> Dict[str, dict]:
    # Rules:
    # 1) >= 10 FAIL in 5 minutes -> temp block 1h
    # 2) >= 30 FAIL in 24h -> permanent
    # 3) >= 5 distinct users attacked by same IP in 10 minutes -> temp 1h
    by_ip = defaultdict(list)
    for dt, user, ip, res in recs:
        if res == "FAIL":
            by_ip[ip].append((dt, user))
    to_block = {}
    for ip, events in by_ip.items():
        events.sort(key=lambda x: x[0])
        # Sliding windows
        q5 = deque()
        q24 = deque()
        q10_users = deque()
        users_window = defaultdict(int)
        perm = False
        temp = False
        for dt, user in events:
            # maintain 5 min window
            while q5 and (dt - q5[0]).total_seconds() > 5*60:
                q5.popleft()
            q5.append(dt)
            # maintain 24h window
            while q24 and (dt - q24[0]).total_seconds() > 24*3600:
                q24.popleft()
            q24.append(dt)
            # maintain 10 min window of users
            while q10_users and (dt - q10_users[0][0]).total_seconds() > 10*60:
                old_dt, old_user = q10_users.popleft()
                users_window[old_user] -= 1
                if users_window[old_user] <= 0:
                    del users_window[old_user]
            q10_users.append((dt, user))
            users_window[user] = users_window.get(user, 0) + 1

            # check rules
            if len(q24) >= 30:
                perm = True
            if len(q5) >= 10:
                temp = True
            if len(users_window.keys()) >= 5:
                temp = True
        if perm:
            to_block[ip] = {"type": "perm"}
        elif temp:
            until = (events[-1][0] + timedelta(hours=1)).astimezone(timezone.utc).isoformat()
            to_block[ip] = {"type": "temp", "until": until}

    black = get_blacklist()
    changed = False
    for ip, rec in to_block.items():
        old = black.get(ip)
        if old:
            # Upgrade temp->perm if necessary
            if old.get("type") != rec.get("type"):
                black[ip] = rec
                changed = True
        else:
            black[ip] = rec
            changed = True
    if changed:
        put_blacklist(black)
    return to_block

def console_summary(stats: Dict[str, any]) -> str:
    lines = []
    lines.append(f"Total tentativas: {stats['total']}")
    lines.append(f"Sucessos: {stats['success']} | Falhas: {stats['fail']}")
    lines.append("TOP IPs com falhas:")
    for ip, c in list(stats["per_ip_fail"].items())[:10]:
        lines.append(f"  - {ip}: {c}")
    lines.append("TOP utilizadores mais atacados:")
    for u, c in list(stats["per_user_fail"].items())[:10]:
        lines.append(f"  - {u}: {c}")
    return "\n".join(lines)
