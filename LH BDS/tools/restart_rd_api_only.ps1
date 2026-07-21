$ErrorActionPreference='Continue'
$self=$PID
Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $self -and $_.CommandLine -like '*bds_engine.rd_api_server:app*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
