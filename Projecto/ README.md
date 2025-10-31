projeto_final_uc00606/
├─ README.md
├─ requirements.txt
├─ auth.py                # PBKDF2, verificação
├─ storage.py             # “base de dados” simples em JSON para utilizadores e lockouts
├─ login_cli.py           # CLI: criar utilizadores, efetuar login, integra logging/blacklist
├─ analytics.py           # lê CSV, aplica heurísticas, gera/atualiza blacklist.json
├─ flowchart.mmd          # fluxograma Mermaid
├─ logs_exemplo.csv       # gerado automaticamente (ou via simulador)
├─ blacklist.json         # gerado automaticamente
└─ generate_logs.py       # simulador para produzir ≥200 linhas de teste

Nota: podes apagar os logs_exemplo.csv, logs_exemplo.csv, state.json e users.json para testares do zero.


# Plataforma de Autenticação Resiliente + Analisador de Logs

## 1) Setup

- python3 -m venv venv
- source venv/bin/activate  # (Windows: venv-audit\Scripts\Activate.ps1)
- `pip install -r requirements.txt`

## 2) Criar utilizadores
```bash
python login_cli.py create-user
```



## 3) Fazer login (com logging e lockout/backoff)
```bash
python login_cli.py login
```

4) Gerar dados de teste (≥200 linhas)
```bash
python generate_logs.py
```

5) Executar Analytics (atualiza blacklist.json e imprime estatísticas)
 ```bash
python analytics.py
```


6) Auditoria de dependências (NVD/MITRE + ferramentas locais)
	•	Consultar: NVD (https://nvd.nist.gov) e MITRE CVE (https://cve.mitre.org)


Verificar pacotes instalados
```bash
pip list
```
Auditar vulnerabilidades
```bash
pip-audit
```
Auditar com base alternativa
```bash
safety check
```