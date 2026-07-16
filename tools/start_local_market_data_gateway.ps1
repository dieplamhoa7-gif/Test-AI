$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$logDir = Join-Path $workspace 'logs\local_market_data_gateway'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stdout = Join-Path $logDir 'gateway.out.log'
$stderr = Join-Path $logDir 'gateway.err.log'

# If the gateway is already listening, do nothing.
try {
  $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:20129/health' -UseBasicParsing -TimeoutSec 3
  if ($resp.StatusCode -eq 200) { exit 0 }
} catch {}

$python = 'python'
$args = '-m uvicorn tools.local_market_data_gateway:app --host 0.0.0.0 --port 20129'
Start-Process -FilePath $python -ArgumentList $args -WorkingDirectory $workspace -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Start-Sleep -Seconds 3
try {
  $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:20129/health' -UseBasicParsing -TimeoutSec 5
  if ($resp.StatusCode -eq 200) { exit 0 }
} catch {
  Write-Error "Gateway failed to start: $($_.Exception.Message)"
  exit 1
}
