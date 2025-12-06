# Laboratório de Segurança – Ansible + Ubuntu/WSL + Windows

Este repositório contém um conjunto de playbooks Ansible e scripts para construir
um laboratório completo de segurança de redes e sistemas:

- FTP seguro (vsftpd)
- SSH com chaves e hardening
- Fail2Ban (sshd, vsftpd, nginx)
- NGINX + Juice Shop (vulnerável para testes)
- HTTPS + TLS Hardening (NGINX e Apache)
- Proxy reverso + Netdata (monitorização)
- DNS local simulado via /etc/hosts
- Testes automáticos de segurança
- Scripts Windows para instalar ferramentas de ataque e carregar o IP do laboratório

## Estrutura

- `inventory` – inventário local para Ansible
- `lab_detect_ip.yml` – detecta o IP do Ubuntu e cria `/opt/labinfo/labinfo.ps1`
- `lab_security_stack.yml` – instala FTP, SSH, Juice Shop, UFW, Fail2Ban, ferramentas de ataque
- `lab_https.yml` – ativa HTTPS + TLS hardening em NGINX
- `lab_https_apache.yml` – ativa HTTPS + TLS hardening em Apache (8080/8443)
- `lab_proxy_monitor.yml` – proxy reverso extra + Fail2Ban nginx-http-auth + Netdata
- `lab_dns_local.yml` – simulação de DNS local via /etc/hosts
- `lab_security_tests.yml` – corre testes automáticos e mostra resultados
- `windows/install_attack_tools_windows.ps1` – instala Nmap, Wireshark, FileZilla, Git, PuTTY
- `windows/load_lab_ip.ps1` – lê o IP do Ubuntu (via WSL) e exporta `$LAB_IP` no Windows

## Ordem recomendada de execução (no Ubuntu/WSL)

```bash
ansible-playbook -i inventory lab_detect_ip.yml
ansible-playbook -i inventory lab_security_stack.yml
ansible-playbook -i inventory lab_https.yml
ansible-playbook -i inventory lab_https_apache.yml    # opcional
ansible-playbook -i inventory lab_proxy_monitor.yml
ansible-playbook -i inventory lab_dns_local.yml
ansible-playbook -i inventory lab_security_tests.yml
```

## No Windows

1. Abrir PowerShell como Administrador
2. Correr:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\install_attack_tools_windows.ps1
```

3. Carregar o IP do laboratório (com o WSL Ubuntu ligado):

```powershell
.\load_lab_ip.ps1
```

4. Usar `$LAB_IP` nos testes:

```powershell
nmap -sV $LAB_IP
curl http://$LAB_IP
curl -k https://$LAB_IP
ssh aluno@$LAB_IP
ftp $LAB_IP
```
