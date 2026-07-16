param(
  [string]$Root = "C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS",
  [int]$Port = 8788
)
$ErrorActionPreference = 'Continue'
$backend = Join-Path $Root '_misc_not_luat_bds\backend'
$logDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$existing = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*nvtc_9router_proxy.js*' -and $_.CommandLine -like "*NVTC_PROXY_PORT=$Port*" }
if ($existing) { Write-Host "Planning proxy already running on $Port"; exit 0 }
$env:NVTC_PROXY_PORT = [string]$Port
Start-Process -FilePath node -ArgumentList 'nvtc_9router_proxy.js' -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDir 'planning_proxy_8788.out.log') -RedirectStandardError (Join-Path $logDir 'planning_proxy_8788.err.log')
Start-Sleep -Seconds 2
try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 "http://127.0.0.1:$Port/health").Content } catch { Write-Host "Planning proxy health failed: $($_.Exception.Message)" }
