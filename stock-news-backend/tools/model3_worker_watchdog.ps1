param(
  [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
  [string]$RenderBase = $env:MODEL3_RENDER_BASE,
  [string]$WorkerToken = $env:MODEL3_WORKER_TOKEN,
  [int]$GatewayPort = 20128,
  [string]$GatewayHost = '100.89.47.25'
)

$ErrorActionPreference = 'Continue'
if (-not $RenderBase) { $RenderBase = 'https://lh-realestate-browser-backend.onrender.com' }
$LogDir = Join-Path $RepoDir 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir 'model3_worker_watchdog.log'
function Log($m) { "$(Get-Date -Format s) $m" | Tee-Object -FilePath $LogFile -Append }

if (-not $WorkerToken) {
  Log 'MODEL3_WORKER_TOKEN missing; set machine/user env first.'
  exit 2
}

# Ensure Tailscale is up if installed. This does not re-authenticate; it only starts service/client.
try {
  $svc = Get-Service -Name Tailscale -ErrorAction SilentlyContinue
  if ($svc -and $svc.Status -ne 'Running') {
    Log 'Starting Tailscale service...'
    Start-Service Tailscale
    Start-Sleep -Seconds 5
  }
  $tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
  if ($tailscale) {
    $status = & tailscale status 2>&1
    if ($LASTEXITCODE -ne 0) {
      Log "tailscale status failed: $status"
    }
  }
} catch { Log "Tailscale check failed: $($_.Exception.Message)" }

# Gateway smoke check. If local gateway is managed elsewhere, watchdog only reports; it does not invent start commands.
try {
  $tcp = Test-NetConnection $GatewayHost -Port $GatewayPort -WarningAction SilentlyContinue
  if (-not $tcp.TcpTestSucceeded) {
    Log "Gateway TCP not reachable: ${GatewayHost}:${GatewayPort}. Worker will still run; jobs may fail fast."
  } else {
    Log "Gateway TCP OK: ${GatewayHost}:${GatewayPort}"
  }
} catch { Log "Gateway TCP check failed: $($_.Exception.Message)" }

# Avoid duplicate worker processes.
$needle = 'tools\model3_local_worker.py'
$existing = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*$needle*" -and $_.ProcessId -ne $PID }
if ($existing) {
  Log "Worker already running pid(s): $($existing.ProcessId -join ',')"
  exit 0
}

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { Log 'Python not found'; exit 3 }

$env:MODEL3_RENDER_BASE = $RenderBase
$env:MODEL3_WORKER_TOKEN = $WorkerToken
$env:PIPELINE_MODEL3_OUT_DIR = Join-Path $RepoDir 'outputs\model3'
$worker = Join-Path $RepoDir 'tools\model3_local_worker.py'
$out = Join-Path $LogDir 'model3_local_worker.out.log'
$err = Join-Path $LogDir 'model3_local_worker.err.log'
Log "Starting Model3 worker: $python $worker"
Start-Process -FilePath $python -ArgumentList @($worker) -WorkingDirectory $RepoDir -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err
Start-Sleep -Seconds 3
$started = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*$needle*" }
if ($started) { Log "Worker started pid(s): $($started.ProcessId -join ',')"; exit 0 }
Log 'Worker did not appear after start.'
exit 4
