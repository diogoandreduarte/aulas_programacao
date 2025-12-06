# Script para carregar o IP do laboratório (Ubuntu/WSL) exposto em /opt/labinfo/labinfo.ps1
# Garante que tens o WSL Ubuntu ativo e o playbook lab_detect_ip.yml já foi corrido.

$wslPath = "\\wsl$\Ubuntu\opt\labinfo\labinfo.ps1"

if (Test-Path $wslPath) {
    Copy-Item $wslPath -Destination . -Force
    . .\labinfo.ps1
    Write-Host "IP do laboratório carregado em $LAB_IP" -ForegroundColor Green
    Write-Host "Exemplos de testes:" -ForegroundColor Cyan
    Write-Host "  nmap -sV $LAB_IP" -ForegroundColor Cyan
    Write-Host "  curl http://$LAB_IP" -ForegroundColor Cyan
    Write-Host "  curl -k https://$LAB_IP" -ForegroundColor Cyan
    Write-Host "  ssh aluno@$LAB_IP" -ForegroundColor Cyan
    Write-Host "  ftp $LAB_IP" -ForegroundColor Cyan
} else {
    Write-Warning "Não foi encontrado labinfo.ps1 em $wslPath. Garante que o WSL Ubuntu está a correr e o playbook lab_detect_ip.yml foi executado."
}
