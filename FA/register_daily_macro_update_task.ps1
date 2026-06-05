$ErrorActionPreference = 'Stop'

$TaskName = 'LHInvestment Daily Macro Update'
$Workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace\FA'
$Python = (Get-Command py).Source
$Script = Join-Path $Workspace 'run_daily_macro_update.py'

# Run at 08:15 every day. If machine is asleep, run as soon as possible after wake/logon.
$Action = New-ScheduledTaskAction -Execute $Python -Argument "-3 `"$Script`"" -WorkingDirectory $Workspace
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:15
$Settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew `
  -ExecutionTimeLimit (New-TimeSpan -Minutes 45)

# Run under current user only when logged on. This avoids storing password and allows headed Chrome/Playwright scraping.
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description 'Daily LH Investment macro data update: Pinetree, VCB FX, Yahoo global, VN market, SBV, OMO, FiinProX fallback, TradingEconomics browser scrape, WorldBank.'

Register-ScheduledTask -TaskName $TaskName -InputObject $Task -Force | Out-Null
Write-Host "Registered scheduled task: $TaskName"
Write-Host "Runs daily at 08:15 under interactive user: $env:USERNAME"
Write-Host "Script: $Script"
