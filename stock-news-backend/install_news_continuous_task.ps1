$ErrorActionPreference = 'Stop'
$Root = 'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend'
$Python = 'C:\Users\HoaD-CVDT\AppData\Local\Python\pythoncore-3.14-64\python.exe'

# A daily trigger repeats for 24 hours. Unlike the old one-shot trigger, it is
# renewed every day and therefore never silently expires after its first day.
$RefreshName = 'LHINVT Continuous News Refresh'
$RefreshScript = Join-Path $Root 'run_news_continuous_lh.py'
$RefreshAction = New-ScheduledTaskAction -Execute $Python -Argument "`"$RefreshScript`"" -WorkingDirectory $Root
$RefreshTrigger = New-ScheduledTaskTrigger -Daily -At '07:30'
$RefreshTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At '07:30' -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Hours 11)).Repetition
$RefreshSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -ExecutionTimeLimit (New-TimeSpan -Minutes 25)
Register-ScheduledTask -TaskName $RefreshName -Action $RefreshAction -Trigger $RefreshTrigger -Settings $RefreshSettings -Description 'Refresh and publish LHINVT news every 15 minutes on weekdays 07:30-18:30; daily trigger never expires.' -Force | Out-Null

$WatchdogName = 'LHINVT News Pipeline Watchdog'
$WatchdogScript = Join-Path $Root 'tools\lh_news_pipeline_watchdog.py'
$WatchdogAction = New-ScheduledTaskAction -Execute $Python -Argument "`"$WatchdogScript`"" -WorkingDirectory $Root
$WatchdogTrigger = New-ScheduledTaskTrigger -Daily -At '07:40'
$WatchdogTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At '07:40' -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Hours 11)).Repetition
$WatchdogSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -WakeToRun -MultipleInstances IgnoreNew -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 3) -ExecutionTimeLimit (New-TimeSpan -Minutes 3)
Register-ScheduledTask -TaskName $WatchdogName -Action $WatchdogAction -Trigger $WatchdogTrigger -Settings $WatchdogSettings -Description 'Checks published LHINVT news freshness every 10 minutes and self-recovers a stale pipeline.' -Force | Out-Null

Get-ScheduledTask -TaskName $RefreshName,$WatchdogName | Select-Object TaskName,State
Get-ScheduledTaskInfo -TaskName $RefreshName | Select-Object LastRunTime,LastTaskResult,NextRunTime
Get-ScheduledTaskInfo -TaskName $WatchdogName | Select-Object LastRunTime,LastTaskResult,NextRunTime
