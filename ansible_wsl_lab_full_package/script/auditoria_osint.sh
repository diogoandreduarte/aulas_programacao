#!/usr/bin/env bash

# auditoria_osint.sh
# Uso: ./auditoria_osint.sh dominio.com

# Cores básicas (se o terminal suportar)
if [ -t 1 ]; then
  BOLD="\e[1m"
  NORM="\e[0m"
  GREEN="\e[32m"
  YELLOW="\e[33m"
  RED="\e[31m"
  BLUE="\e[34m"
else
  BOLD=""
  NORM=""
  GREEN=""
  YELLOW=""
  RED=""
  BLUE=""
fi

# -----------------------------
# Validação de argumentos
# -----------------------------
DOMAIN="$1"

if [ -z "$DOMAIN" ]; then
  echo -e "${RED}Uso:${NORM} $0 dominio.com"
  exit 1
fi

# -----------------------------
# Timestamp e ficheiro de log
# -----------------------------
TIMESTAMP="$(date +'%Y-%m-%d_%H-%M-%S')"
LOG_FILE="osint_report_${DOMAIN}_${TIMESTAMP}.log"

# Redirecionar tudo (stdout + stderr) para o log e para o ecrã
exec > >(tee -a "$LOG_FILE") 2>&1

echo
echo -e "${BOLD}Iniciando auditoria OSINT para:${NORM} ${BLUE}${DOMAIN}${NORM}"
echo "Relatório será guardado em: ${LOG_FILE}"
echo

# -----------------------------
# Verificação de dependências
# -----------------------------
echo "======================================"
echo " 0. Verificação de dependências"
echo "======================================"
echo

MISSING_DEPS=()

check_dep() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    MISSING_DEPS+=("$cmd")
  fi
}

check_dep "whois"
check_dep "dig"
check_dep "curl"
check_dep "jq"

if [ "${#MISSING_DEPS[@]}" -gt 0 ]; then
  echo -e "${YELLOW}⚠ As seguintes dependências estão em falta:${NORM}"
  for d in "${MISSING_DEPS[@]}"; do
    echo "   - $d"
  done
  echo
  echo "   Em sistemas Debian/Ubuntu, podes instalar com:"
  echo "   sudo apt update && sudo apt install whois dnsutils curl jq -y"
  echo
  echo -e "${RED}Atenção:${NORM} o script continua, mas algumas secções podem falhar."
else
  echo -e "${GREEN}✅ Todas as dependências principais estão disponíveis.${NORM}"
fi

echo

# -----------------------------
# 1. WHOIS
# -----------------------------
echo "======================================"
echo " 1. WHOIS"
echo "======================================"
echo

if command -v whois >/dev/null 2>&1; then
  whois "$DOMAIN"
else
  echo -e "${YELLOW}⚠ whois não instalado. Secção WHOIS ignorada.${NORM}"
fi

echo

# -----------------------------
# 2. DNS ENUM (A, MX, NS, TXT)
# -----------------------------
echo "======================================"
echo " 2. DNS ENUM (A, MX, NS, TXT)"
echo "======================================"
echo

if command -v dig >/dev/null 2>&1; then
  echo "▶ Registo A:"
  A_RECORDS=$(dig +short A "$DOMAIN" || true)
  if [ -n "$A_RECORDS" ]; then
    echo "$A_RECORDS"
  else
    echo "  (sem registos A ou não resolvido)"
  fi

  echo
  echo "▶ Registos MX:"
  MX_RECORDS=$(dig +short MX "$DOMAIN" || true)
  if [ -n "$MX_RECORDS" ]; then
    echo "$MX_RECORDS"
  else
    echo "  (sem registos MX)"
  fi

  echo
  echo "▶ Servidores NS:"
  NS_RECORDS=$(dig +short NS "$DOMAIN" || true)
  if [ -n "$NS_RECORDS" ]; then
    echo "$NS_RECORDS"
  else
    echo "  (sem registos NS)"
  fi

  echo
  echo "▶ Registos TXT:"
  TXT_RECORDS=$(dig +short TXT "$DOMAIN" || true)
  if [ -n "$TXT_RECORDS" ]; then
    echo "$TXT_RECORDS"
  else
    echo "  (sem registos TXT)"
  fi
else
  echo -e "${YELLOW}⚠ dig (dnsutils) não instalado. Secção DNS ignorada.${NORM}"
fi

echo

# Guardar IPs para a secção de Shodan (se existirem)
RESOLVED_IPS=""
if [ -n "$A_RECORDS" ]; then
  RESOLVED_IPS="$A_RECORDS"
fi

# -----------------------------
# 3. DNSDumpster – Enumeração
# -----------------------------
echo "======================================"
echo " 3. DNSDumpster – Enumeração de subdomínios"
echo "======================================"
echo

echo "⚠ DNSDumpster bloqueia automatização. Ver manualmente:"
echo "   https://dnsdumpster.com"
echo

# Tentativa de abrir automaticamente no browser (útil em WSL/desktop)
if command -v wslview >/dev/null 2>&1; then
  # WSL em Windows
  wslview "https://dnsdumpster.com" >/dev/null 2>&1 &
elif command -v xdg-open >/dev/null 2>&1; then
  # Linux com ambiente gráfico
  xdg-open "https://dnsdumpster.com" >/dev/null 2>&1 &
fi

echo

# -----------------------------
# 4. SHODAN – Serviços públicos
# -----------------------------
echo "======================================"
echo " 4. SHODAN – Serviços públicos encontrados"
echo "======================================"
echo

SHODAN_API_KEY="${SHODAN_API_KEY:-}"

if [ -z "$SHODAN_API_KEY" ]; then
  echo -e "${YELLOW}⚠ Variável de ambiente SHODAN_API_KEY não definida.${NORM}"
  echo "   Define antes de correr o script, por exemplo:"
  echo "   export SHODAN_API_KEY=\"A_TUA_API_KEY_DO_SHODAN_AQUI\""
  echo
else
  if [ -z "$RESOLVED_IPS" ]; then
    echo "Domínio não tem registos A resolvidos. Nada para consultar no Shodan."
    echo
  else
    echo "Domínio resolve para os IPs:"
    echo "$RESOLVED_IPS"
    echo

    if ! command -v curl >/dev/null 2>&1; then
      echo -e "${YELLOW}⚠ curl não instalado. Secção Shodan ignorada.${NORM}"
    elif ! command -v jq >/dev/null 2>&1; then
      echo -e "${YELLOW}⚠ jq não instalado. Instala com: sudo apt install jq -y${NORM}"
    else
      for IP in $RESOLVED_IPS; do
        echo "🔍 A analisar IP no Shodan: $IP"

        SHODAN_URL="https://api.shodan.io/shodan/host/$IP?key=$SHODAN_API_KEY"
        SHODAN_RAW="$(curl -sS "$SHODAN_URL" || true)"

        # Verificar se é JSON válido
        if echo "$SHODAN_RAW" | jq -e . >/dev/null 2>&1; then
          # Guardar resposta JSON também em ficheiro separado (útil para análise posterior)
          SHODAN_JSON_FILE="shodan_${IP}_${TIMESTAMP}.json"
          echo "$SHODAN_RAW" > "$SHODAN_JSON_FILE"
          echo "  JSON bruto guardado em: $SHODAN_JSON_FILE"

          ORG=$(echo "$SHODAN_RAW" | jq -r '.org // "N/A"')
          OS=$(echo "$SHODAN_RAW" | jq -r '.os // "N/A"')
	  PORTS=$(echo "$SHODAN_RAW" | jq -r '
	     if (.ports? // []) | length > 0 then
		     (.ports? // [] | join(", "))
		else
			"N/A"
		end
		')

          echo "  Organização: $ORG"
          echo "  Sistema Operativo: $OS"
          echo "  Portas expostas: $PORTS"
          echo

        else
          echo -e "  ${YELLOW}⚠ Erro ao processar resposta do Shodan (não é JSON válido).${NORM}"
          echo "  Primeiras linhas da resposta:"
          echo "  --------------------------------"
          echo "$SHODAN_RAW" | sed 's/^/  /' | head -n 10
          echo "  --------------------------------"
          echo
        fi
      done
    fi
  fi
fi

# -----------------------------
# 5. SUMÁRIO
# -----------------------------
echo "======================================"
echo " 5. SUMÁRIO"
echo "======================================"
echo

echo "Domínio auditado: $DOMAIN"
echo "Data: $(date)"
echo "Ferramentas: WHOIS, DIG, DNSDumpster (manual), Shodan API"
echo "Arquivo gerado: $LOG_FILE"
echo
echo -e "${GREEN}✅ Auditoria OSINT concluída!${NORM}"
echo -e "📄 Relatório gerado em: ${BOLD}${LOG_FILE}${NORM}"
echo

