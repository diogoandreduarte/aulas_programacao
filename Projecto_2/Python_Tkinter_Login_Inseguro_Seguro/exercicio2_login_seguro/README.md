
# Exercício 2 — Login **Seguro** (Tkinter)

Conceitos demonstrados:
- Hashing com `PBKDF2-HMAC-SHA256` + salt único por utilizador + `iterations` elevadas.
- Comparação constante (`hmac.compare_digest`).
- Guardar apenas `salt`, `hash` e `iterations` em ficheiro `users_secure.json`.
- Política de tentativas: 5 falhas ⇒ bloqueio temporário (30s, exponencial).
- Mensagens de erro genéricas.
- Separação por módulos (`auth.py`, `ui.py`, `storage.py`).

# Criar utilizador (modo seguro no terminal)
```bash
python main.py --create-user
```
## Executar
```bash
python3 main.py
```
