param(
  [string]$Root = "C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS"
)
$ErrorActionPreference = 'Continue'
Set-Location $Root
$LogDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogPath = Join-Path $LogDir 'lh_bds_unified_watchdog.log'

function Log([string]$Message) {
  $line = "[$(Get-Date -Format o)] $Message"
  Add-Content -Path $LogPath -Value $line -Encoding UTF8
  Write-Host $line
}

function Test-UrlOk([string]$Url, [int]$TimeoutSec = 5) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $TimeoutSec
    return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
  } catch { return $false }
}

function Get-ListeningPid([int]$Port) {
  $lines = netstat -ano | Select-String ":$Port\s+.*LISTENING"
  $pids = @()
  foreach ($line in $lines) {
    $parts = ($line.ToString() -split '\s+') | Where-Object { $_ }
    if ($parts.Count -ge 5) { $pids += [int]$parts[-1] }
  }
  return $pids | Select-Object -Unique
}

function Stop-ProcessIds([int[]]$Pids, [string]$Reason) {
  foreach ($pid in ($Pids | Select-Object -Unique)) {
    if (-not $pid -or $pid -eq $PID) { continue }
    try {
      $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
      if ($p) { Log "Stopping PID=$pid $($p.ProcessName): $Reason"; Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
    } catch {}
  }
}

function Ensure-RdApi() {
  $listeners = @(Get-ListeningPid 8787)
  if ($listeners.Count -gt 1) {
    $keep = ($listeners | Sort-Object | Select-Object -First 1)
    Stop-ProcessIds -Pids ($listeners | Where-Object { $_ -ne $keep }) -Reason "duplicate listener on 8787; keeping PID=$keep"
    Start-Sleep -Seconds 2
  }
  if (Test-UrlOk 'http://127.0.0.1:8787/health' 4) { Log 'R&D API healthy on 8787.'; return }
  Stop-ProcessIds -Pids (Get-ListeningPid 8787) -Reason '8787 unhealthy before R&D restart'
  $out = Join-Path $LogDir 'rd_api_server.out.log'
  $err = Join-Path $LogDir 'rd_api_server.err.log'
  Log 'Starting R&D API bds_engine.rd_api_server:app on 127.0.0.1:8787.'
  Start-Process -FilePath 'python' -ArgumentList @('-m','uvicorn','bds_engine.rd_api_server:app','--host','127.0.0.1','--port','8787') -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err
  for ($i=0; $i -lt 24; $i++) { Start-Sleep -Seconds 5; if (Test-UrlOk 'http://127.0.0.1:8787/health' 5) { Log 'R&D API healthy after start.'; return } }
  Log 'WARNING: R&D API still unhealthy after 120s.'
}

function Ensure-PlanningProxy() {
  $listeners = @(Get-ListeningPid 8788)
  if ($listeners.Count -gt 1) {
    $keep = ($listeners | Sort-Object | Select-Object -First 1)
    Stop-ProcessIds -Pids ($listeners | Where-Object { $_ -ne $keep }) -Reason "duplicate listener on 8788; keeping PID=$keep"
    Start-Sleep -Seconds 2
  }
  if (Test-UrlOk 'http://127.0.0.1:8788/health' 4) { Log 'Guland/GIS planning proxy healthy on 8788.'; return }
  Stop-ProcessIds -Pids (Get-ListeningPid 8788) -Reason '8788 unhealthy before planning proxy restart'
  $backend = Join-Path $Root '_misc_not_luat_bds\backend'
  $out = Join-Path $LogDir 'planning_proxy_8788.out.log'
  $err = Join-Path $LogDir 'planning_proxy_8788.err.log'
  Log 'Starting Guland/GIS planning proxy on 0.0.0.0:8788.'
  Start-Process -FilePath 'node' -ArgumentList 'nvtc_9router_proxy.js' -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -Environment @{ NVTC_PROXY_PORT = '8788' }
  for ($i=0; $i -lt 12; $i++) { Start-Sleep -Seconds 5; if (Test-UrlOk 'http://127.0.0.1:8788/health' 5) { Log 'Guland/GIS planning proxy healthy after start.'; return } }
  Log 'WARNING: planning proxy still unhealthy after 60s.'
}

function Ensure-PublisherSingleton() {
  $pubs = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -like '*tools\lh_tunnel_publish.js*' })
  if ($pubs.Count -gt 1) {
    $keep = ($pubs | Sort-Object ProcessId | Select-Object -First 1).ProcessId
    $kill = $pubs | Where-Object { $_.ProcessId -ne $keep } | ForEach-Object { $_.ProcessId }
    Stop-ProcessIds -Pids $kill -Reason "duplicate lh_tunnel_publish.js; keeping PID=$keep"
  }
  $pubs = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'node.exe' -and $_.CommandLine -like '*tools\lh_tunnel_publish.js*' })
  if ($pubs.Count -ge 1) { Log "Tunnel publisher running PID(s): $($pubs.ProcessId -join ', ')."; return }
  $out = Join-Path $LogDir 'lh_tunnel_publish.out.log'
  $err = Join-Path $LogDir 'lh_tunnel_publish.err.log'
  Log 'Starting tunnel publisher for rd=8787 and qh=8788.'
  Start-Process -FilePath 'node' -ArgumentList @('tools\lh_tunnel_publish.js') -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -Environment @{
    RD_PORT='8787'; QH_PORT='8788'; DEPLOY_DIR='public_final_2026_07_11'; FIREBASE_SITE='lhrealestate'; FIREBASE_PROJECT='hoa-investment'; FIREBASE_CONFIG='firebase.json'; HEALTH_INTERVAL_MS='30000'; HEALTH_FAIL_LIMIT='3'
  }
}

function Remove-DuplicateQuickTunnels() {
  # Remove stale manual/service publishers from old startup entries; this unified watchdog owns the single publisher.
  $oldService = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*lh_tunnel_publish_service.ps1*' })
  if ($oldService.Count) { Stop-ProcessIds -Pids ($oldService | ForEach-Object { $_.ProcessId }) -Reason 'old lh_tunnel_publish_service.ps1 superseded by unified watchdog' }

  foreach ($port in 8787,8788) {
    $cfs = @(Get-CimInstance Win32_Process -Filter "name = 'cloudflared.exe'" | Where-Object { $_.CommandLine -match "tunnel\s+--url\s+http://(127\.0\.0\.1|localhost):$port" })
    if ($cfs.Count -gt 1) {
      $keep = ($cfs | Sort-Object ProcessId | Select-Object -First 1).ProcessId
      $kill = $cfs | Where-Object { $_.ProcessId -ne $keep } | ForEach-Object { $_.ProcessId }
      Stop-ProcessIds -Pids $kill -Reason "duplicate cloudflared tunnel for port $port; keeping PID=$keep"
    }
  }
}

Log 'Unified LH BDS watchdog started.'
while ($true) {
  Ensure-RdApi
  Ensure-PlanningProxy
  Ensure-PublisherSingleton
  Remove-DuplicateQuickTunnels
  Start-Sleep -Seconds 60
}
