param(
  [string]$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
  [string]$RenderBase = 'https://lh-realestate-browser-backend.onrender.com',
  [Parameter(Mandatory=$true)][string]$WorkerToken,
  [string]$TaskName = 'LH Model3 Local Worker Watchdog'
)

$ErrorActionPreference = 'Stop'
$watchdog = Join-Path $RepoDir 'tools\model3_worker_watchdog.ps1'
if (-not (Test-Path $watchdog)) { throw "Missing watchdog: $watchdog" }

# Persist env for the current user so task survives reboot/login.
[Environment]::SetEnvironmentVariable('MODEL3_RENDER_BASE', $RenderBase, 'User')
[Environment]::SetEnvironmentVariable('MODEL3_WORKER_TOKEN', $WorkerToken, 'User')

$ps = (Get-Command powershell.exe).Source
$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$watchdog`" -RepoDir `"$RepoDir`" -RenderBase `"$RenderBase`""
$action = New-ScheduledTaskAction -Execute $ps -Argument $arg -WorkingDirectory $RepoDir
$triggerLogin = New-ScheduledTaskTrigger -AtLogOn
$triggerRepeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($triggerLogin,$triggerRepeat) -Settings $settings -Description 'Keeps LHINVT Model3 local worker alive and checks Tailscale/gateway.' -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "Installed and started task: $TaskName"
Write-Host "RepoDir: $RepoDir"
Write-Host "RenderBase: $RenderBase"
