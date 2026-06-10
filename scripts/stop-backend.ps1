# Stop backend processes listening on port 8000 (Windows)
$port = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8000 }

$pids = @()
foreach ($line in (netstat -ano | Select-String ":$port\s")) {
    $parts = ($line -split '\s+') | Where-Object { $_ -ne '' }
    if ($parts.Length -ge 5) {
        $pids += [int]$parts[-1]
    }
}
$pids = $pids | Sort-Object -Unique | Where-Object { $_ -gt 0 }

if (-not $pids.Count) {
    Write-Host "No process listening on port $port."
    exit 0
}

foreach ($procId in $pids) {
    try {
        $proc = Get-Process -Id $procId -ErrorAction Stop
        Write-Host "Stopping PID $procId ($($proc.ProcessName))..."
        Stop-Process -Id $procId -Force -ErrorAction Stop
    } catch {
        Write-Host "Could not stop PID $procId (may already have exited)."
    }
}

Start-Sleep -Seconds 1
$still = netstat -ano | Select-String ":$port\s+.*LISTENING"
if ($still) {
    Write-Host "Port $port may still be in use. Wait a few seconds or run as Administrator."
} else {
    Write-Host "Port $port is free. Run .\scripts\start-backend.ps1 to start again."
}
