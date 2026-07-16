$ErrorActionPreference = 'Continue'
$workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$starter = Join-Path $workspace 'tools\start_local_market_data_gateway.ps1'
$logDir = Join-Path $workspace 'logs\local_market_data_gateway'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$watchLog = Join-Path $logDir 'watchdog.log'
while ($true) {
  $ts = Get-Date -Format o
  try {
    $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:20129/health' -UseBasicParsing -TimeoutSec 5
    if ($resp.StatusCode -eq 200) {
      Add-Content -Path $watchLog -Value "$ts OK"
    } else {
      Add-Content -Path $watchLog -Value "$ts BAD_STATUS $($resp.StatusCode); restarting"
      powershell -NoProfile -ExecutionPolicy Bypass -File $starter | Out-Null
    }
  } catch {
    Add-Content -Path $watchLog -Value "$ts DOWN $($_.Exception.Message); restarting"
    powershell -NoProfile -ExecutionPolicy Bypass -File $starter | Out-Null
  }
  Start-Sleep -Seconds 300
}
