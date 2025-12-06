Write-Host "=== GERAR TRAFEGO E ATAQUES ==="

# 1) Descobrir IP REAL do WSL (lado Linux)
$wslIpRaw = wsl hostname -I
$wslIp = $wslIpRaw.Trim().Split(" ")[0]

Write-Host "IP alvo (WSL): $wslIp"

# 2) Trafego HTTP normal
Write-Host ""
Write-Host "[1] A enviar trafego HTTP normal para http://$wslIp ..."

for ($i = 1; $i -le 5; $i++) {
    Write-Host "  [HTTP] Pedido $i..."
    try {
        Invoke-WebRequest -UseBasicParsing -Uri ("http://{0}" -f $wslIp) -TimeoutSec 3 | Out-Null
    } catch {
        Write-Host "    Falhou: $($_.Exception.Message)"
    }
    Start-Sleep -Milliseconds 300
}

# 3) Ataques SSH
Write-Host ""
Write-Host "[2] A simular 5 tentativas SSH falhadas..."

for ($i = 1; $i -le 5; $i++) {
    Write-Host "  [SSH] Tentativa $i..."
    ssh -o BatchMode=yes -o StrictHostKeyChecking=no invalid@$wslIp exit 2>&1 | Out-Null
}

# 4) Ataques FTP
Write-Host ""
Write-Host "[3] A simular 5 tentativas FTP falhadas..."

for ($i = 1; $i -le 5; $i++) {
    Write-Host "  [FTP] Tentativa $i..."
    ftp -n -v $wslIp 2>&1 | Out-Null
}

# 5) Hydra (se existir)
Write-Host ""
Write-Host "[4] Testar Hydra FTP..."

if (Get-Command hydra -ErrorAction SilentlyContinue) {
    Write-Host "  [HYDRA] A executar ataque..."
    hydra -l invalid -p 123456 ftp://$wslIp -t 4
} else {
    Write-Host "  [HYDRA] Comando hydra nao encontrado no Windows. Passo ignorado."
}

Write-Host ""
Write-Host "=== FIM DO TRAFEGO ==="
Write-Host "No Ubuntu/WSL, corre: sudo ansible-playbook lab_log_correlation.yml"
