$ErrorActionPreference = 'Stop'
$workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$watcher = Join-Path $workspace 'tools\watch_local_market_data_gateway.ps1'
$startup = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path $startup 'LH Local Market Data Gateway Watchdog.lnk'
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $watcher + '"'
$shortcut.WorkingDirectory = $workspace
$shortcut.WindowStyle = 7
$shortcut.Description = 'Keeps LH local market data gateway on port 20129 running for Render/Model3 bots.'
$shortcut.Save()
Write-Host "Installed startup shortcut: $shortcutPath"
