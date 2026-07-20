$ErrorActionPreference = 'Stop'
$TaskName = 'LHINVT Continuous News Refresh'
$Root = 'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend'
$Python = 'C:\Users\HoaD-CVDT\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$Script = Join-Path $Root 'run_news_continuous_lh.py'
$Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$Script`"" -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -Once -At '07:30'
$Trigger.Repetition = New-ScheduledTaskTrigger -Once -At '07:30' -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Hours 23 -Minutes 30) | Select-Object -ExpandProperty Repetition
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description 'Refresh LHINVT news cache every 30 minutes; script skips outside weekday 07:30-18:30, verifies freshness and LH final lock, then deploys lhinvt.' -Force | Out-Null
Get-ScheduledTask -TaskName $TaskName | Format-List TaskName,State
Get-ScheduledTaskInfo -TaskName $TaskName | Format-List LastRunTime,LastTaskResult,NextRunTime
