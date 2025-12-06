<#
    run_fail2ban_attack.ps1
    Ataques SSH + FTP + HYDRA contra o lab no Ubuntu/WSL
    - IP do WSL DETETADO automaticamente
    - Gera logs separados para SSH, FTP e HYDRA
    - Designed para acionar Fail2Ban (sshd + vsftpd) e gerar material de análise
#>

# =========================
# 1) DETETAR IP DO WSL
# =========================

Write-Host "A detectar IP do Ubuntu/WSL..." -ForegroundColor Cyan

$ip = (wsl hostname -I).Trim()

if (-not $ip) {
    Write-Host "[ERRO] Não foi possível obter o IP do Ubuntu/WSL com 'wsl hostname -I'!" -ForegroundColor Red
    exit 1
}

Write-Host "IP detectado (WSL): $ip" -ForegroundColor Green

# =========================
# 2) CONFIGURAÇÃO
# =========================

$sshAttempts = 10
$ftpAttempts = 12

$logDir = "$PSScriptRoot\logs"
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$sshLogFile   = "$logDir\ssh_fail2ban_log_$ts.txt"
$ftpLogFile   = "$logDir\ftp_fail2ban_log_$ts.txt"
$hydraLogFile = "$logDir\hydra_ftp_log_$ts.txt"

if (!(Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

# Logs base
"=== LOG TESTE SSH Fail2Ban ===" | Out-File $sshLogFile
"Data: $(Get-Date)" | Out-File $sshLogFile -Append
"IP alvo (WSL): $ip" | Out-File $sshLogFile -Append
"SSH Tentativas: $sshAttempts" | Out-File $sshLogFile -Append
"----------------------------------------`n" | Out-File $sshLogFile -Append

"=== LOG TESTE FTP Fail2Ban ===" | Out-File $ftpLogFile
"Data: $(Get-Date)" | Out-File $ftpLogFile -Append
"IP alvo (WSL): $ip" | Out-File $ftpLogFile -Append
"FTP Tentativas: $ftpAttempts" | Out-File $ftpLogFile -Append
"----------------------------------------`n" | Out-File $ftpLogFile -Append

"=== LOG TESTE HYDRA FTP ===" | Out-File $hydraLogFile
"Data: $(Get-Date)" | Out-File $hydraLogFile -Append
"Alvo (vista de dentro do WSL): 127.0.0.1:21" | Out-File $hydraLogFile -Append
"Wordlist: /opt/wordlists/common.txt" | Out-File $hydraLogFile -Append
"----------------------------------------`n" | Out-File $hydraLogFile -Append

Write-Host "=== TESTE Fail2Ban SSH + FTP + HYDRA ===" -ForegroundColor Cyan
Write-Host "IP WSL detectado: $ip" -ForegroundColor Yellow
Write-Host "SSH tentativas:   $sshAttempts" -ForegroundColor Yellow
Write-Host "FTP tentativas:   $ftpAttempts" -ForegroundColor Yellow
Write-Host "Log SSH:   $sshLogFile" -ForegroundColor Yellow
Write-Host "Log FTP:   $ftpLogFile" -ForegroundColor Yellow
Write-Host "Log HYDRA: $hydraLogFile" -ForegroundColor Yellow
Write-Host ""

# =========================
# 3) ATAQUE SSH – jail sshd
# =========================

Write-Host "=== ATAQUE SSH (jail sshd) ===" -ForegroundColor Magenta

for ($i = 1; $i -le $sshAttempts; $i++) {
    Write-Host "[SSH] Tentativa $i de $sshAttempts..."

    "---- SSH Tentativa $i ----" | Out-File $sshLogFile -Append
    "Hora: $(Get-Date)" | Out-File $sshLogFile -Append

    $result = & ssh `
        -o BatchMode=yes `
        -o PreferredAuthentications=password `
        -o PubkeyAuthentication=no `
        -o StrictHostKeyChecking=no `
        -o UserKnownHostsFile=/dev/null `
        "user_invalido@$ip" `
        exit 2>&1

    $result | Out-File $sshLogFile -Append
    "`n" | Out-File $sshLogFile -Append

    Start-Sleep -Milliseconds 200
}

Write-Host "[OK] Ataques SSH enviados." -ForegroundColor Green
Write-Host ""

# =========================
# 4) ATAQUE FTP – jail vsftpd
# =========================

Write-Host "=== ATAQUE FTP (jail vsftpd) ===" -ForegroundColor Magenta

$ftpCommands = @"
user alunoftp wrongpass
pwd
ls
bye
"@

for ($i = 1; $i -le $ftpAttempts; $i++) {
    Write-Host "[FTP] Tentativa $i de $ftpAttempts..."

    "---- FTP Tentativa $i ----" | Out-File $ftpLogFile -Append
    "Hora: $(Get-Date)" | Out-File $ftpLogFile -Append

    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $ftpCommands

    $result = ftp -n -v -s:$tmp $ip 2>&1
    $result | Out-File $ftpLogFile -Append

    Remove-Item $tmp -Force

    "`n" | Out-File $ftpLogFile -Append

    Start-Sleep -Milliseconds 200
}

Write-Host "[OK] Ataques FTP enviados." -ForegroundColor Green
Write-Host ""

# =========================
# 5) ATAQUE HYDRA – brute force FTP (dentro do WSL)
# =========================

Write-Host "=== ATAQUE HYDRA (FTP brute force no WSL) ===" -ForegroundColor Magenta
Write-Host "A correr: hydra -l alunoftp -P /opt/wordlists/common.txt ftp://127.0.0.1" -ForegroundColor DarkGray

"---- HYDRA RUN ----" | Out-File $hydraLogFile -Append
"Hora: $(Get-Date)" | Out-File $hydraLogFile -Append

# Hydra corre dentro do WSL, contra 127.0.0.1:21
$hydraResult = & wsl hydra `
    -l alunoftp `
    -P /opt/wordlists/common.txt `
    -t 4 `
    -f `
    ftp://127.0.0.1 2>&1

$hydraResult | Out-File $hydraLogFile -Append
"`n" | Out-File $hydraLogFile -Append

Write-Host "[OK] Ataque HYDRA concluído." -ForegroundColor Green

# =========================
# 6) FINALIZAÇÃO
# =========================

Write-Host "`n=== ATAQUES CONCLUÍDOS ===" -ForegroundColor Green
Write-Host "Log SSH:   $sshLogFile"
Write-Host "Log FTP:   $ftpLogFile"
Write-Host "Log HYDRA: $hydraLogFile"

Write-Host "`nNo Ubuntu verifica:" -ForegroundColor Cyan
Write-Host "  sudo fail2ban-client status sshd" -ForegroundColor White
Write-Host "  sudo fail2ban-client status vsftpd" -ForegroundColor White
Write-Host "  sudo tail -f /var/log/auth.log /var/log/vsftpd.log" -ForegroundColor White
Write-Host "`nE no Windows podes abrir os logs na pasta 'logs' para análise com os alunos." -ForegroundColor Cyan
