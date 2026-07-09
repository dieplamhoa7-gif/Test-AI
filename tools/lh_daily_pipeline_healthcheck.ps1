<#
Daily health check for Hòa's macro / stock update pipelines.

What it does:
- Checks scheduled tasks related to macro / stock after-close pipelines.
- Checks entrypoint files and child scripts used by the after-close orchestrator.
- Checks recent output data freshness for key caches.
- Tries safe self-heal only for path/wrapper issues where a clear candidate exists.
- Writes JSON + Markdown reports under logs/daily_pipeline_healthcheck/.

Safe-fix boundary:
- OK: create missing parent folders, refresh broken scheduled task action when exact current file exists.
- Not OK: rewrite business logic, change formulas, delete data, or deploy externally without explicit separate instruction.
#>

$ErrorActionPreference = 'Continue'
$Workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$ReportDir = Join-Path $Workspace 'logs\daily_pipeline_healthcheck'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Now = Get-Date
$Stamp = $Now.ToString('yyyy-MM-dd_HHmmss')
$JsonPath = Join-Path $ReportDir "healthcheck_$Stamp.json"
$MdPath = Join-Path $ReportDir "healthcheck_$Stamp.md"
$LatestJson = Join-Path $ReportDir 'latest.json'
$LatestMd = Join-Path $ReportDir 'latest.md'

function New-Status($name, $kind) {
  [ordered]@{
    name = $name
    kind = $kind
    ok = $true
    severity = 'ok'
    message = ''
    details = [ordered]@{}
    fixes = @()
  }
}

function Set-Fail([hashtable]$item, [string]$severity, [string]$message) {
  $item.ok = $false
  $item.severity = $severity
  $item.message = $message
}

function Test-RecentFile($path, [int]$maxHours) {
  if (!(Test-Path $path)) { return @{ exists=$false; fresh=$false; ageHours=$null; lastWrite=$null } }
  $it = Get-Item $path
  $age = ((Get-Date) - $it.LastWriteTime).TotalHours
  return @{ exists=$true; fresh=($age -le $maxHours); ageHours=[math]::Round($age,2); lastWrite=$it.LastWriteTime.ToString('s') }
}

# Known scheduled tasks / entrypoints.
$TaskSpecs = @(
  @{ Name='LH Macro Web Daily Vietstock Update'; Expected='C:\Users\HoaD-CVDT\.openclaw\workspace\macro_web\tools\macro_web_daily_update.ps1'; Type='macro'; MaxResultOk=@(0) },
  @{ Name='LHInvestment Daily Macro Update'; Expected='C:\Users\HoaD-CVDT\.openclaw\workspace\FA\run_daily_macro_update.py'; Type='macro'; MaxResultOk=@(0) },
  @{ Name='LH_Daily_VN_Macro_Collect'; Expected='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\collect_daily_vn_macro.py'; Type='macro'; MaxResultOk=@(0) },
  @{ Name='LH Investment After Close Indicators'; Expected='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_scheduled.ps1'; Type='after_close'; MaxResultOk=@(0) },
  @{ Name='LHInvestment After Close Outputs'; Expected='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_output_lh.bat'; Type='after_close'; MaxResultOk=@(0) }
)

$AfterCloseFiles = @(
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_scheduled.ps1',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_output_lh.bat',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_output_lh.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_rs_levels_vn100_safe.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_v3_full_indicator_cache_v2.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_weekly_indicators_vn100_cache.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_monthly_indicators_vn100_cache.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\refresh_vn100_history_for_core12.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_lh_canonical_indicators_daily.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_strategy_results_from_indicator_cache.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\build_firebase_cache_site.py',
  'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\update_popup_ichimoku_all_symbols.py'
)

$KeyOutputs = @(
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\rs_levels_vn100_cache.json'; MaxHours=36 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\v3_full_indicator_cache_v2.json'; MaxHours=36 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\weekly_indicators_vn100_cache.json'; MaxHours=48 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\monthly_indicators_vn100_cache.json'; MaxHours=48 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\lh_canonical_indicators_daily.json'; MaxHours=36 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\data\strategy_results_cache.json'; MaxHours=36 },
  @{ Path='C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\firebase_public\data\market-data.json'; MaxHours=36 }
)

$Items = @()
$Fixes = @()

foreach ($spec in $TaskSpecs) {
  $item = New-Status $spec.Name 'scheduled_task'
  $task = Get-ScheduledTask -TaskName $spec.Name -ErrorAction SilentlyContinue
  if (!$task) {
    Set-Fail $item 'critical' 'Scheduled task missing'
    $item.details.expected = $spec.Expected
  } else {
    $info = Get-ScheduledTaskInfo -TaskName $spec.Name -TaskPath $task.TaskPath -ErrorAction SilentlyContinue
    $action = $task.Actions | Select-Object -First 1
    $item.details.state = [string]$task.State
    $item.details.execute = [string]$action.Execute
    $item.details.arguments = [string]$action.Arguments
    $item.details.workingDirectory = [string]$action.WorkingDirectory
    $item.details.lastRunTime = if($info){$info.LastRunTime.ToString('s')}else{$null}
    $item.details.lastTaskResult = if($info){$info.LastTaskResult}else{$null}
    $item.details.nextRunTime = if($info -and $info.NextRunTime){$info.NextRunTime.ToString('s')}else{$null}
    $item.details.entrypointExists = Test-Path $spec.Expected
    if ($task.State -eq 'Disabled') { Set-Fail $item 'critical' 'Scheduled task is disabled' }
    elseif (!(Test-Path $spec.Expected)) { Set-Fail $item 'critical' 'Entrypoint configured in scheduler is missing' }
    elseif ($info -and ($spec.MaxResultOk -notcontains [int]$info.LastTaskResult)) {
      Set-Fail $item 'warning' "Last run returned non-zero result $($info.LastTaskResult)"
    }
  }
  $Items += [pscustomobject]$item
}

foreach ($p in $AfterCloseFiles) {
  $item = New-Status (Split-Path $p -Leaf) 'after_close_code_file'
  $item.details.path = $p
  if (!(Test-Path $p)) { Set-Fail $item 'critical' 'Required after-close code file missing' }
  else {
    $it = Get-Item $p
    $item.details.lastWriteTime = $it.LastWriteTime.ToString('s')
    $item.details.length = $it.Length
  }
  $Items += [pscustomobject]$item
}

foreach ($o in $KeyOutputs) {
  $item = New-Status (Split-Path $o.Path -Leaf) 'output_freshness'
  $item.details.path = $o.Path
  $fresh = Test-RecentFile $o.Path $o.MaxHours
  $item.details.exists = $fresh.exists
  $item.details.fresh = $fresh.fresh
  $item.details.ageHours = $fresh.ageHours
  $item.details.lastWrite = $fresh.lastWrite
  $item.details.maxHours = $o.MaxHours
  if (!$fresh.exists) { Set-Fail $item 'critical' 'Expected output file missing' }
  elseif (!$fresh.fresh) { Set-Fail $item 'warning' "Output is stale (> $($o.MaxHours)h)" }
  $Items += [pscustomobject]$item
}

# Safe self-heal: if the two after-close scheduler wrappers exist but last scheduler result failed due path issues,
# normalize task actions to current absolute paths. This does not run/deploy pipelines.
try {
  $ac1 = 'LH Investment After Close Indicators'
  $p1 = 'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_scheduled.ps1'
  if (Test-Path $p1) {
    $t = Get-ScheduledTask -TaskName $ac1 -ErrorAction SilentlyContinue
    if ($t) {
      $a = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$p1`"" -WorkingDirectory (Split-Path $p1 -Parent)
      $changed = ($t.Actions[0].Arguments -notmatch [regex]::Escape($p1)) -or ([string]$t.Actions[0].WorkingDirectory -ne (Split-Path $p1 -Parent))
      if ($changed) {
        Set-ScheduledTask -TaskName $ac1 -Action $a | Out-Null
        $Fixes += "Normalized scheduled task action for $ac1"
      }
    }
  }
  $ac2 = 'LHInvestment After Close Outputs'
  $p2 = 'C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\run_after_close_output_lh.bat'
  if (Test-Path $p2) {
    $t = Get-ScheduledTask -TaskName $ac2 -ErrorAction SilentlyContinue
    if ($t) {
      $a = New-ScheduledTaskAction -Execute $p2 -WorkingDirectory (Split-Path $p2 -Parent)
      $changed = ([string]$t.Actions[0].Execute -ne $p2) -or ([string]$t.Actions[0].WorkingDirectory -ne (Split-Path $p2 -Parent))
      if ($changed) {
        Set-ScheduledTask -TaskName $ac2 -Action $a | Out-Null
        $Fixes += "Normalized scheduled task action for $ac2"
      }
    }
  }
} catch {
  $Fixes += "Auto-fix attempt failed: $($_.Exception.Message)"
}

$Failed = @($Items | Where-Object { -not $_.ok })
$Critical = @($Failed | Where-Object { $_.severity -eq 'critical' })
$Warning = @($Failed | Where-Object { $_.severity -eq 'warning' })
$Overall = if($Critical.Count -gt 0){'FAIL'} elseif($Warning.Count -gt 0){'WARN'} else {'OK'}

$Report = [ordered]@{
  generatedAt = $Now.ToString('s')
  computer = $env:COMPUTERNAME
  workspace = $Workspace
  overall = $Overall
  counts = [ordered]@{ total=$Items.Count; ok=@($Items|Where-Object ok).Count; warning=$Warning.Count; critical=$Critical.Count; fixes=$Fixes.Count }
  fixes = $Fixes
  items = $Items
}

$Report | ConvertTo-Json -Depth 8 | Set-Content -Path $JsonPath -Encoding UTF8
$Report | ConvertTo-Json -Depth 8 | Set-Content -Path $LatestJson -Encoding UTF8

$lines = @()
$lines += "# LH Daily Pipeline Health Check - $Overall"
$lines += ""
$lines += "- Generated: $($Report.generatedAt)"
$lines += "- Total checks: $($Report.counts.total) | OK: $($Report.counts.ok) | Warning: $($Report.counts.warning) | Critical: $($Report.counts.critical)"
if ($Fixes.Count -gt 0) { $lines += "- Auto-fixes: $($Fixes -join '; ')" }
$lines += ""
$lines += "## Failed / attention"
if ($Failed.Count -eq 0) { $lines += "- None" }
else {
  foreach($f in $Failed) {
    $lines += "- [$($f.severity.ToUpper())] $($f.kind): $($f.name) - $($f.message)"
    if ($f.details.path) { $lines += "  - Path: $($f.details.path)" }
    if ($f.details.lastTaskResult -ne $null) { $lines += "  - LastTaskResult: $($f.details.lastTaskResult); LastRun: $($f.details.lastRunTime); Next: $($f.details.nextRunTime)" }
    if ($f.details.ageHours -ne $null) { $lines += "  - AgeHours: $($f.details.ageHours); LastWrite: $($f.details.lastWrite)" }
  }
}
$lines += ""
$lines += "## Checklist"
foreach($i in $Items) {
  $mark = if($i.ok){'[x]'}else{'[ ]'}
  $lines += "- $mark $($i.kind): $($i.name)"
}
$lines -join "`r`n" | Set-Content -Path $MdPath -Encoding UTF8
$lines -join "`r`n" | Set-Content -Path $LatestMd -Encoding UTF8

Write-Host "Overall: $Overall"
Write-Host "Report: $MdPath"
if ($Failed.Count -gt 0) { Write-Host "Attention: $($Failed.Count) issue(s)." }
exit $(if($Overall -eq 'FAIL'){2}elseif($Overall -eq 'WARN'){1}else{0})
