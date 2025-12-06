# IP do WSL detetado automaticamente
$wslIp = (wsl hostname -I).Trim().Split(" ")[0]

Write-Host "IP WSL detetado: $wslIp" -ForegroundColor Cyan

$hostsPath = "$env:WINDIR\System32\drivers\etc\hosts"
$backupPath = "$hostsPath.bak"

# Backup do hosts
if (-not (Test-Path $backupPath)) {
    Copy-Item $hostsPath $backupPath
}

$entries = @"
127.0.0.1 meu-site.local
$wslIp ftp.local
$wslIp ssh.local
"@

Add-Content -Path $hostsPath -Value $entries

Write-Host "Entradas DNS locais adicionadas ao hosts do Windows:" -ForegroundColor Green
Write-Host $entries
