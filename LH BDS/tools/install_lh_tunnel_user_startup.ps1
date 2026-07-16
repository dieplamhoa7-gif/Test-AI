$ErrorActionPreference = 'Stop'
$root = 'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS'
$service = Join-Path $root 'tools\lh_tunnel_publish_service.ps1'
$startup = [Environment]::GetFolderPath('Startup')
$linkPath = Join-Path $startup 'LH BDS Tunnel Watchdog.lnk'
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($linkPath)
$shortcut.TargetPath = 'powershell.exe'
$shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $service + '"'
$shortcut.WorkingDirectory = $root
$shortcut.WindowStyle = 7
$shortcut.Description = 'Keeps LH Real Estate R&D/QH Cloudflare tunnels alive and republishes api-config.json'
$shortcut.Save()
Write-Host "Installed startup shortcut: $linkPath"
