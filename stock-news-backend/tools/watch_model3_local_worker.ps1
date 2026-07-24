$ErrorActionPreference = 'Stop'
$Root = 'C:\Users\HoaD-CVDT\.openclaw\workspace\render_backend_work\stock-news-backend'
$Worker = Join-Path $Root 'tools\model3_local_worker.py'
$Py = 'C:\Users\HoaD-CVDT\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$LogDir = Join-Path $Root 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir 'model3_local_worker_watchdog.log'
$Running = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*model3_local_worker.py*' -and $_.ProcessId -ne $PID }
if ($Running) {
  Add-Content -Path $Log -Encoding UTF8 -Value "$(Get-Date -Format s) worker already running: $($Running[0].ProcessId)"
  exit 0
}
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:MODEL3_RENDER_BASE = 'https://lh-realestate-browser-backend.onrender.com'
$env:MARKET_DATA_GATEWAY_URL = 'http://100.89.47.25:20129/marketdata'
$token = [Environment]::GetEnvironmentVariable('MODEL3_WORKER_TOKEN','User')
if (-not $token) { throw 'MODEL3_WORKER_TOKEN missing in User environment' }
$env:MODEL3_WORKER_TOKEN = $token
$Out = Join-Path $LogDir 'model3_local_worker.out.log'
$Err = Join-Path $LogDir 'model3_local_worker.err.log'
Start-Process -FilePath $Py -ArgumentList @('-X','utf8',$Worker) -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardOutput $Out -RedirectStandardError $Err
Add-Content -Path $Log -Encoding UTF8 -Value "$(Get-Date -Format s) started worker"
