param(
  [string]$Root = "C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS"
)
$ErrorActionPreference = 'Continue'
Set-Location $Root
$env:RD_PORT = if ($env:RD_PORT) { $env:RD_PORT } else { '8787' }
$env:QH_PORT = if ($env:QH_PORT) { $env:QH_PORT } else { '8787' }
$env:DEPLOY_DIR = if ($env:DEPLOY_DIR) { $env:DEPLOY_DIR } else { 'public_final_2026_07_11' }
$env:FIREBASE_SITE = if ($env:FIREBASE_SITE) { $env:FIREBASE_SITE } else { 'lhrealestate' }
$env:FIREBASE_PROJECT = if ($env:FIREBASE_PROJECT) { $env:FIREBASE_PROJECT } else { 'hoa-investment' }
$env:HEALTH_INTERVAL_MS = if ($env:HEALTH_INTERVAL_MS) { $env:HEALTH_INTERVAL_MS } else { '30000' }
$env:HEALTH_FAIL_LIMIT = if ($env:HEALTH_FAIL_LIMIT) { $env:HEALTH_FAIL_LIMIT } else { '3' }
$logDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
"[$stamp] starting LH tunnel publisher Root=$Root RD_PORT=$env:RD_PORT QH_PORT=$env:QH_PORT DEPLOY_DIR=$env:DEPLOY_DIR" | Tee-Object -FilePath (Join-Path $logDir 'lh_tunnel_publish_service.log') -Append
node tools\lh_tunnel_publish.js 2>&1 | Tee-Object -FilePath (Join-Path $logDir 'lh_tunnel_publish_service.log') -Append
