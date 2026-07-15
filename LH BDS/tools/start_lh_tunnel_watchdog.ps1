$ErrorActionPreference = 'Continue'

$Root = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $Root 'tools'
$StartupLog = Join-Path $LogDir 'lh_tunnel_watchdog_startup.log'
$BackendOut = Join-Path $Root 'rd_api_server.out.log'
$BackendErr = Join-Path $Root 'rd_api_server.err.log'
$PublisherOut = Join-Path $LogDir 'lh_tunnel_publish.out.log'
$PublisherErr = Join-Path $LogDir 'lh_tunnel_publish.err.log'

function Log($Message) {
  $line = "[$(Get-Date -Format o)] $Message"
  Add-Content -Path $StartupLog -Value $line -Encoding UTF8
  Write-Host $line
}

function Test-UrlOk($Url, $TimeoutSec = 5) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec $TimeoutSec
    return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
  } catch {
    return $false
  }
}

Log "LH Real Estate tunnel watchdog startup. Root=$Root"
Set-Location $Root

# 1) Ensure local R&D backend is alive on 127.0.0.1:8787.
if (Test-UrlOk 'http://127.0.0.1:8787/health' 5) {
  Log 'Backend already healthy on 8787.'
} else {
  Log 'Backend not healthy; starting uvicorn bds_engine.rd_api_server:app on 8787.'
  Start-Process -FilePath 'python' `
    -ArgumentList @('-m','uvicorn','bds_engine.rd_api_server:app','--host','127.0.0.1','--port','8787') `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $BackendOut `
    -RedirectStandardError $BackendErr `
    -WindowStyle Hidden

  $ok = $false
  for ($i = 0; $i -lt 24; $i++) {
    Start-Sleep -Seconds 5
    if (Test-UrlOk 'http://127.0.0.1:8787/health' 5) { $ok = $true; break }
  }
  if ($ok) { Log 'Backend health OK after start.' } else { Log 'WARNING: Backend still not healthy after 120s; publisher will still start and retry.' }
}

# 2) Ensure tunnel publisher is running. It respawns cloudflared and deploys api-config.json when tunnel changes.
$existingPublisher = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*lh_tunnel_publish.js*' }
if ($existingPublisher) {
  Log "Publisher already running: PID(s) $($existingPublisher.ProcessId -join ', ')."
} else {
  Log 'Starting lh_tunnel_publish.js.'
  $env:RD_PORT = '8787'
  $env:QH_PORT = ''
  $env:DEPLOY_DIR = 'public_final_2026_07_11'
  $env:FIREBASE_SITE = 'lhrealestate'
  $env:FIREBASE_PROJECT = 'hoa-investment'
  $env:FIREBASE_CONFIG = 'firebase.json'
  Start-Process -FilePath 'node' `
    -ArgumentList @('tools\lh_tunnel_publish.js') `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $PublisherOut `
    -RedirectStandardError $PublisherErr `
    -WindowStyle Hidden
  Log 'Publisher start requested.'
}

Log 'Watchdog startup done.'
