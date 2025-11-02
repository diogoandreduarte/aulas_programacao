
# Projeto Analizador de LogPasta

Estrutura:
```
analizador_logs/
  io_utils.py   # leitura/escrita e deteção de formato
  parser.py     # normalização de campos
  analytics.py  # contagens e percentagens
  report.py     # sumário em consola + export CSV/JSON
  main.py       # ponto de entrada
logs_exemplo.csv
```

## Como correr
```bash
python -m analizador_logs.main logs_exemplo.csv --out out/
```
Irá detetar o formato, calcular tentativas por IP/utilizador, percentagens e gerar:
- `out/relatorio_falhas.csv`
- `out/relatorio_completo.json`
