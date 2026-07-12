param(
  [string]$RepoDir,
  [string]$RenderBase = 'https://lh-realestate-browser-backend.onrender.com',
  [Parameter(Mandatory=$true)][string]$WorkerToken
)
if (-not $RepoDir) { $RepoDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path }
$ErrorActionPreference = 'Stop'
$watchdog = Join-Path $RepoDir 'tools\model3_worker_watchdog.ps1'
if (-not (Test-Path $watchdog)) { throw "Missing watchdog: $watchdog" }
[Environment]::SetEnvironmentVariable('MODEL3_RENDER_BASE', $RenderBase, 'User')
[Environment]::SetEnvironmentVariable('MODEL3_WORKER_TOKEN', $WorkerToken, 'User')
$startup = [Environment]::GetFolderPath('Startup')
$cmd = Join-Path $startup 'LH_Model3_Worker_Watchdog.cmd'
$cmdText = "@echo off`r`nset MODEL3_RENDER_BASE=$RenderBase`r`nset MODEL3_WORKER_TOKEN=$WorkerToken`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$watchdog`" -RepoDir `"$RepoDir`" -RenderBase `"$RenderBase`"`r`n"
Set-Content -Path $cmd -Value $cmdText -Encoding ASCII
Write-Host "Installed startup watchdog: $cmd"
Start-Process -FilePath $cmd -WindowStyle Hidden
