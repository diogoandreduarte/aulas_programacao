# Projeto Final — UC00606  
## Plataforma de Autenticação Resiliente e Analisador de Logs  

###  Descrição Geral
Este projeto integra **dois componentes principais**:
1. **Autenticação Segura** — com hashing PBKDF2-HMAC-SHA256, salt único por utilizador e bloqueio (lockout) progressivo.  
2. **Analisador de Logs** — deteta ataques de força bruta e DDoS, gerando bloqueios automáticos de IPs.

O resultado é um **protótipo funcional e resiliente**, capaz de:
- Registar todas as tentativas de login (sucesso ou falha);
- Analisar logs e identificar padrões maliciosos;
- Bloquear automaticamente IPs suspeitos (temporária ou permanentemente).

---

### Estrutura do Projeto

```
projeto_final_uc00606/
├── analyzer.py           # Analisador de logs e regras de bloqueio
├── auth.py               # Autenticação segura (hashing + lockout)
├── logger.py             # Registo de tentativas em CSV
├── storage.py            # Gestão de users, logs e blacklist
├── ui.py                 # Versão CLI (getpass)
├── ui_tk.py              # Interface gráfica Tkinter
├── main.py               # Ponto de entrada principal (CLI + GUI)
├── generate_logs.py      # Gerador de logs de teste (200+ linhas)
├── users.json            # Base de dados de utilizadores
├── logs_exemplo.csv      # Ficheiro de logs
├── blacklist.json        # IPs bloqueados
└── README.md             # Este ficheiro
```

---

### ️ Requisitos
- **Python 3.10+**
- Nenhuma biblioteca externa necessária (usa apenas módulos padrão).

---

###  Como Executar

####  1. Interface Gráfica (Tkinter)
```bash
python main.py
```
Aparece uma janela com:
- Campos de **Username**, **Password** e **IP**  
- Botões:
  - **Login** — autentica e regista tentativa  
  - **Criar Utilizador** — adiciona novo utilizador com password confirmada  

 O sistema regista automaticamente cada tentativa e verifica se o IP está bloqueado.

---

#### 2. Linha de Comando (CLI)

**Criar utilizador**   # opcional tambem cria no UI
```bash
python main.py create-user --username alice
# (será pedida password)
```

**Efetuar login**    # opcional tambem cria no UI
```bash
python main.py login --username alice --ip 192.168.1.10
```

**Executar análise de logs e aplicar bloqueios**
```bash
python main.py analyze
```

**Gerar logs de exemplo (200+ registos)**   # opcional só para criar os logs iniciais 
```bash
python generate_logs.py
```

---

### Lógica de Segurança

**Hashing e armazenamento:**
- PBKDF2-HMAC-SHA256 com 200.000 iterações e salt único por utilizador.  
- Os hashes e salts são guardados em `users.json`.

**Lockout progressivo:**
- A partir de 3 falhas consecutivas:
  - 3 falhas → bloqueio 1 minuto  
  - 4 falhas → 2 minutos  
  - 5 falhas → 4 minutos  
  - 6 falhas → 8 minutos, etc.  

**Registo de logs:**
Cada tentativa (sucesso, falha, bloqueio) é guardada em `logs_exemplo.csv`:
```
timestamp,username,ip,result
2025-11-02 12:45:03,alice,192.168.1.10,FAIL
```

**Heurísticas de bloqueio automático (analyzer.py):**
| Tipo de Ataque | Condição | Ação |
|-----------------|-----------|-------|
| Força Bruta Curto Prazo | ≥ 10 falhas do mesmo IP em 5 min | Bloqueio 1h |
| Força Bruta Longo Prazo | ≥ 30 falhas do mesmo IP em 24h | Bloqueio permanente |
| Ataque Distribuído | ≥ 5 utilizadores diferentes atacados pelo mesmo IP em 10 min | Bloqueio 1h |

Os IPs são guardados em `blacklist.json`:
```json
{
  "203.0.113.5": { "type": "temp", "until": "2025-11-02T14:45:03+00:00" },
  "198.51.100.23": { "type": "perm" }
}
```

---

### Exemplo de Saída da Análise
```
--- Estatísticas ---
Total tentativas: 250
Sucessos: 180 | Falhas: 70
TOP IPs com falhas:
  - 203.0.113.5: 12
  - 198.51.100.23: 32
TOP utilizadores mais atacados:
  - alice: 15
  - bob: 13
--- Bloqueios aplicados ---
203.0.113.5 {'type': 'temp', 'until': '2025-11-02T14:45:03+00:00'}
198.51.100.23 {'type': 'perm'}
```

---

### Validação de Bibliotecas
instalação: pip install safety
Ferramenta: `safety check`  
Bibliotecas utilizadas:
- `hashlib`, `hmac`, `json`, `csv`, `tkinter`, `datetime`, `argparse`  
🔒 Nenhuma vulnerabilidade crítica conhecida (verificado em NVD e CVE).

---

### 🧭 Fluxograma (Mermaid)

```mermaid
flowchart TD
  A[Início] --> B{IP na blacklist?}
  B -- Sim --> X[Negar acesso e registar tentativa]
  B -- Não --> C[Pedir credenciais]
  C --> D[Verificar lockout do utilizador]
  D -- Bloqueado --> X
  D -- Livre --> E[Hash PBKDF2 e comparação segura]
  E -- OK --> F[Login SUCCESS | reset contadores]
  E -- FAIL --> G[Incrementa falhas | aplica backoff]
  F --> H[Registar no CSV]
  G --> H
  H --> I[Analisador lê CSV]
  I --> J[Detetar padrões maliciosos]
  J --> K[Atualizar blacklist.json]
  K --> L[Fim]
```




