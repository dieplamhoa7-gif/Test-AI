$ErrorActionPreference = 'Continue'
$root = 'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS'
$self = $PID
Get-CimInstance Win32_Process | Where-Object {
  $_.ProcessId -ne $self -and (
    ($_.Name -eq 'powershell.exe' -and $_.CommandLine -like '*lh_bds_unified_watchdog.ps1*') -or
    ($_.Name -eq 'node.exe' -and $_.CommandLine -like '*tools\lh_tunnel_publish.js*') -or
    ($_.Name -eq 'cloudflared.exe' -and $_.CommandLine -match '127\.0\.0\.1:8787|127\.0\.0\.1:8788')
  )
} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\tools\lh_bds_unified_watchdog.ps1"' -WorkingDirectory $root -WindowStyle Hidden
