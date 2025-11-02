
from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import Iterable, Dict, Any, Iterator, Tuple, List

def read_lines_auto(path: str | Path) -> Tuple[str, Iterator[Dict[str, Any]]]:
    """Detecta formato automaticamente e devolve (format, iterator de registos normalizados).
    Formatos suportados: CSV, JSON (array), JSONL (.jsonl), pipe-delimited (|).
    Campos esperados: timestamp, ip, user, status.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Ficheiro não encontrado: {p}")
    suffix = p.suffix.lower()
    # Tentativa por extensão
    if suffix in {'.jsonl', '.ndjson'}:
        return 'jsonl', _iter_jsonl(p)
    if suffix == '.json':
        return 'json', _iter_json_array_or_obj(p)
    # Olhar para as primeiras linhas
    with p.open('r', encoding='utf-8', errors='ignore') as f:
        head = ''.join([f.readline() for _ in range(3)])
    if '|' in head and ',' not in head:
        return 'pipe', _iter_delimited(p, delimiter='|')
    # default: csv
    return 'csv', _iter_delimited(p, delimiter=',')

def _normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
    mapping = {
        'ts': 'timestamp',
        'time': 'timestamp',
        'data': 'timestamp',
        'ip_addr': 'ip',
        'username': 'user',
        'utilizador': 'user',
        'status_code': 'status',
        'result': 'status',
        'ok': 'status',
    }
    norm = {}
    for k, v in rec.items():
        k2 = mapping.get(k.strip().lower(), k.strip().lower())
        norm[k2] = v
    for k in ('timestamp','ip','user','status'):
        norm.setdefault(k, None)
    return norm

def _iter_delimited(p: Path, delimiter: str=',') -> Iterator[Dict[str, Any]]:
    with p.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield _normalize(row)

def _iter_json_array_or_obj(p: Path) -> Iterator[Dict[str, Any]]:
    with p.open('r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'logs' in data:
        data = data['logs']
    if not isinstance(data, list):
        data = [data]
    for obj in data:
        if isinstance(obj, dict):
            yield _normalize(obj)

def _iter_jsonl(p: Path) -> Iterator[Dict[str, Any]]:
    with p.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield _normalize(obj)

def write_csv(path: str | Path, rows: Iterable[Dict[str, Any]], fieldnames: List[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def write_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
