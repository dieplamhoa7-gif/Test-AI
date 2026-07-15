$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $Root 'tools\start_lh_tunnel_watchdog.ps1'
$PowerShell = (Get-Command powershell.exe).Source
$Argument = "-NoProfile -ExecutionPolicy Bypass -File `"$Script`""
$Action = New-ScheduledTaskAction -Execute $PowerShell -Argument $Argument -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'LHRealEstateTunnelWatchdog' -Action $Action -Trigger $Trigger -Settings $Settings -Description 'Keeps LH Real Estate local backend + Cloudflare quick tunnel alive and redeploys Firebase URL when tunnel changes.' -Force | Out-Null
Start-ScheduledTask -TaskName 'LHRealEstateTunnelWatchdog'
Write-Host "Installed and started LHRealEstateTunnelWatchdog -> $Script"
