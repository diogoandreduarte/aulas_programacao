
from __future__ import annotations
from datetime import datetime, timezone
from storage import log_line

def log_event(username: str, ip: str, result: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")
    # CSV: timestamp,username,ip,result
    line = f"{ts},{username},{ip},{result}"
    log_line(line)
