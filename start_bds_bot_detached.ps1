$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$envFile = Join-Path $PSScriptRoot '.env.bds.local'
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process')
  }
}

$node = (Get-Command node).Source
$script = Join-Path $PSScriptRoot 'bds_planning_bot.js'
$log = Join-Path $PSScriptRoot 'bds_bot.log'
$pidFile = Join-Path $PSScriptRoot 'bds_bot.pid'

# Stop old BDS bot processes only.
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like '*bds_planning_bot.js*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

# Create/clear log as UTF-8 no BOM.
[System.IO.File]::WriteAllText($log, '', [System.Text.UTF8Encoding]::new($false))

$cmd = "cd /d `"$PSScriptRoot`" && `"$node`" `"$script`" >> `"$log`" 2>&1"
$p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cmd -WindowStyle Hidden -PassThru
Set-Content -Path $pidFile -Value $p.Id -Encoding ascii
Write-Host "BDS bot detached launcher pid=$($p.Id); log=$log"
Start-Sleep -Seconds 2
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*bds_planning_bot.js*' } | Select-Object ProcessId,Name,CommandLine
