$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$logDir = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir 'auto_refresh_news_15m.log'
python auto_refresh_news_15m.py *>> $log
