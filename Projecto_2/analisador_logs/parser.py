
from __future__ import annotations
from typing import Dict, Any, Iterable, Iterator

def parse_records(records: Iterable[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
    """Converte registos em dicionários uniformes, tentando coerção mínima."""
    for r in records:
        out = {
            'timestamp': r.get('timestamp'),
            'ip': (r.get('ip') or '').strip() if isinstance(r.get('ip'), str) else r.get('ip'),
            'user': (r.get('user') or '').strip() if isinstance(r.get('user'), str) else r.get('user'),
            'status': str(r.get('status')).lower() if r.get('status') is not None else None,
        }
        val = out['status']
        if val in ('ok','success','200','true','s','sucesso'):
            out['status'] = 'success'
        elif val in ('fail','failed','error','false','401','403','500','f','falha'):
            out['status'] = 'fail'
        yield out
