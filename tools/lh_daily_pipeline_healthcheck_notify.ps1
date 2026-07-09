<#
Runs daily pipeline healthcheck and sends a Telegram report when possible.
This wrapper is intended for Windows Task Scheduler.
#>
$ErrorActionPreference = 'Continue'
$Workspace = 'C:\Users\HoaD-CVDT\.openclaw\workspace'
$Health = Join-Path $Workspace 'tools\lh_daily_pipeline_healthcheck.ps1'
$LogDir = Join-Path $Workspace 'logs\daily_pipeline_healthcheck'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$RunLog = Join-Path $LogDir 'scheduled_notify.log'

"[$(Get-Date -Format s)] START healthcheck notify" | Tee-Object -FilePath $RunLog -Append
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Health *>> $RunLog
$ExitCode = $LASTEXITCODE

$LatestMd = Join-Path $LogDir 'latest.md'
$LatestJson = Join-Path $LogDir 'latest.json'
$Summary = if(Test-Path $LatestMd){ Get-Content $LatestMd -Raw -Encoding UTF8 } else { 'Healthcheck did not produce latest.md' }

# Keep Telegram message concise.
$Text = $Summary
if ($Text.Length -gt 3500) { $Text = $Text.Substring(0,3500) + "`n...`nFull report: $LatestMd" }

# Preferred route: OpenClaw messaging if CLI supports it. Fallback: write-only log.
try {
  $openclaw = Get-Command openclaw -ErrorAction SilentlyContinue
  if ($openclaw) {
    # Do not hard fail if this OpenClaw build has no send subcommand.
    $msg = "📋 Daily macro/stock pipeline checklist`n`n$Text"
    $tmp = Join-Path $LogDir 'last_message.txt'
    $msg | Set-Content $tmp -Encoding UTF8
    # Intentionally conservative: no invented CLI send command here.
    "[$(Get-Date -Format s)] Report prepared at $tmp. OpenClaw session/heartbeat can relay it." | Tee-Object -FilePath $RunLog -Append
  }
} catch {
  "[$(Get-Date -Format s)] Notify fallback: $($_.Exception.Message)" | Tee-Object -FilePath $RunLog -Append
}

"[$(Get-Date -Format s)] DONE healthcheck notify exit=$ExitCode" | Tee-Object -FilePath $RunLog -Append
exit $ExitCode
