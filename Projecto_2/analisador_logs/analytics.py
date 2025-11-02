
from __future__ import annotations
from typing import Dict, Any, Iterable
from collections import Counter

def analyze(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    total = 0
    ok = 0
    by_ip_fail = Counter()
    by_user_fail = Counter()
    suspicious_ips = set()

    for r in records:
        total += 1
        status = r.get('status')
        ip = r.get('ip') or 'unknown'
        user = r.get('user') or 'unknown'
        if status == 'success':
            ok += 1
        else:
            by_ip_fail[ip] += 1
            by_user_fail[user] += 1

    for ip, c in by_ip_fail.items():
        if c >= 3:
            suspicious_ips.add(ip)

    fail = total - ok
    perc_success = (ok / total * 100.0) if total else 0.0
    perc_fail = 100.0 - perc_success if total else 0.0

    return {
        'total': total,
        'success': ok,
        'fail': fail,
        'perc_success': round(perc_success, 2),
        'perc_fail': round(perc_fail, 2),
        'fail_by_ip': dict(by_ip_fail),
        'fail_by_user': dict(by_user_fail),
        'suspicious_ips': sorted(suspicious_ips),
    }
