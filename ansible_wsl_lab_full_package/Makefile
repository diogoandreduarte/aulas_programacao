# ---------------------------
# Makefile – Automação para WSL/Ubuntu
# Corre todos os playbooks e gera logs
# ---------------------------

ANSIBLE_PLAYBOOK=ansible-playbook
INVENTORY=inventory
LOGDIR=logs

# Criar diretório de logs se não existir
$(shell mkdir -p $(LOGDIR))

# ---------------------------
# Targets individuais
# ---------------------------

detect-ip:
	@echo "=== [1/4] Detectar IP do WSL e exportar para Windows ==="
	$(ANSIBLE_PLAYBOOK) -i $(INVENTORY) lab_detect_ip.yml | tee $(LOGDIR)/01_detect_ip.log

stack:
	@echo "=== [2/4] Instalar e configurar o LAB de segurança ==="
	$(ANSIBLE_PLAYBOOK) -i $(INVENTORY) lab_security_stack.yml | tee $(LOGDIR)/02_security_stack.log

https:
	@echo "=== [3/4] Ativar HTTPS + TLS Hardening ==="
	$(ANSIBLE_PLAYBOOK) -i $(INVENTORY) lab_https.yml | tee $(LOGDIR)/03_https.log

tests:
	@echo "=== [4/4] Executar testes automáticos de segurança ==="
	$(ANSIBLE_PLAYBOOK) -i $(INVENTORY) lab_security_tests.yml | tee $(LOGDIR)/04_tests.log

# ---------------------------
# Run ALL
# ---------------------------

all: detect-ip stack https tests
	@echo "=== Tudo concluído! Logs completos em $(LOGDIR)/ ==="
	@cat $(LOGDIR)/*.log > $(LOGDIR)/FULL_REPORT.log
	@echo "=== Relatório final gerado em $(LOGDIR)/FULL_REPORT.log ==="

# ---------------------------
# Clean logs
# ---------------------------

clean-logs:
	rm -f $(LOGDIR)/*.log
	@echo "Logs limpos!"
