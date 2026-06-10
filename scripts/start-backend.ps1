# Start FastAPI backend for local frontend dev (port 8000)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location "$root\backend"

if (-not (Test-Path "$root\.env")) {
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host "Created .env from .env.example — edit TMDB_API_KEY / OPENAI_API_KEY if needed."
}

# Load .env into process (simple KEY=VALUE parser)
Get-Content "$root\.env" | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
    }
}

$port = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8000 }
$healthUrl = "http://127.0.0.1:$port/health"
$backendHealthy = $false

try {
    $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -eq 200 -and $resp.Content -match '"status"\s*:\s*"ok"') {
        $backendHealthy = $true
    }
} catch {
    $backendHealthy = $false
}

if ($backendHealthy) {
    Write-Host "Backend already running at $healthUrl"
    exit 0
}

# Port in use but unhealthy — force restart
$pids = @()
foreach ($line in (netstat -ano | Select-String ":$port\s")) {
    $parts = ($line -split '\s+') | Where-Object { $_ -ne '' }
    if ($parts.Length -ge 5) {
        $pids += [int]$parts[-1]
    }
}
$pids = $pids | Sort-Object -Unique | Where-Object { $_ -gt 0 }
if ($pids.Count) {
    Write-Host "Port $port in use but backend unhealthy — stopping listeners..."
    foreach ($procId in $pids) {
        try {
            $proc = Get-Process -Id $procId -ErrorAction Stop
            if ($proc.ProcessName -match 'python|uvicorn') {
                Write-Host "Stopping PID $procId ($($proc.ProcessName))..."
                Stop-Process -Id $procId -Force -ErrorAction Stop
            } else {
                Write-Host "Skipping PID $procId ($($proc.ProcessName)) — not a Python backend."
            }
        } catch {
            Write-Host "Could not stop PID $procId (may already have exited)."
        }
    }
    Start-Sleep -Seconds 1
}

Write-Host "Starting backend at http://127.0.0.1:$port (DATABASE_URL=$env:DATABASE_URL)"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port $port
