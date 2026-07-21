$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$root = Join-Path $workspace 'LH BDS'
$startup = [Environment]::GetFolderPath('Startup')
$backup = Join-Path $startup ('LH_BDS_old_startup_disabled_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Force -Path $backup | Out-Null

$oldNames = @(
  'LH BDS Tunnel Watchdog.lnk',
  'LH Real Estate Tunnel Watchdog.bat',
  'LHBDS_Bot_Local_Watchdog.bat',
  'LHBDS_Bot_Watchdog.cmd',
  'LHRealEstateTunnelWatchdog.cmd'
)
foreach ($name in $oldNames) {
  $p = Join-Path $startup $name
  if (Test-Path $p) { Move-Item -Force $p (Join-Path $backup $name) }
}

$watcher = Join-Path $root 'tools\lh_bds_unified_watchdog.ps1'
$shortcutPath = Join-Path $startup 'LH BDS Unified Watchdog.lnk'
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $watcher + '"'
$shortcut.WorkingDirectory = $root
$shortcut.WindowStyle = 7
$shortcut.Description = 'Unified self-healing watchdog for LH BDS R&D API, Guland/GIS proxy, and Cloudflare tunnels.'
$shortcut.Save()
Write-Host "Installed: $shortcutPath"
Write-Host "Disabled old startup entries into: $backup"
