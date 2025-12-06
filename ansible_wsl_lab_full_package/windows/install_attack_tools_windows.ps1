# Script para instalar ferramentas de ataque no Windows via winget
# Deve ser corrido em PowerShell como Administrador

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltinRole] "Administrator"))
{
    Write-Warning "Por favor corre este script em PowerShell como Administrador."
    break
}

Write-Host "Instalar Nmap..." -ForegroundColor Yellow
winget install -e --id Insecure.Nmap --accept-package-agreements --accept-source-agreements

Write-Host "Instalar Wireshark..." -ForegroundColor Yellow
winget install -e --id WiresharkFoundation.Wireshark --accept-package-agreements --accept-source-agreements

Write-Host "Instalar FileZilla..." -ForegroundColor Yellow
winget install -e --id FileZilla.FileZilla --accept-package-agreements --accept-source-agreements

Write-Host "Instalar Git..." -ForegroundColor Yellow
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements

Write-Host "Instalar PuTTY..." -ForegroundColor Yellow
winget install -e --id PuTTY.PuTTY --accept-package-agreements --accept-source-agreements

Write-Host "Instalação concluída. Podes agora carregar o IP do laboratório com o script labinfo.ps1." -ForegroundColor Green
