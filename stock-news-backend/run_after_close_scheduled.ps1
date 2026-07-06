$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$logDir = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir 'after_close_indicators_task.log'
"[$(Get-Date -Format s)] START indicators output-only task" | Tee-Object -FilePath $log -Append
python .\run_after_close_output_lh.py *>> $log
"[$(Get-Date -Format s)] DONE indicators output-only task" | Tee-Object -FilePath $log -Append
