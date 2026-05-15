$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$envFile = Join-Path $PSScriptRoot '.env.bds.local'
if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
    $k, $v = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process')
  }
}
$log = Join-Path $PSScriptRoot 'bds_bot.log'
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = 'node'
$scriptPath = Join-Path $PSScriptRoot 'bds_planning_bot.js'
$psi.Arguments = "`"$scriptPath`""
$psi.WorkingDirectory = $PSScriptRoot
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
$psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
$writer = [System.IO.StreamWriter]::new($log, $false, [System.Text.UTF8Encoding]::new($false))
$p.add_OutputDataReceived({ if ($_.Data -ne $null) { $writer.WriteLine($_.Data); $writer.Flush() } })
$p.add_ErrorDataReceived({ if ($_.Data -ne $null) { $writer.WriteLine($_.Data); $writer.Flush() } })
$p.Start() | Out-Null
$p.BeginOutputReadLine()
$p.BeginErrorReadLine()
Set-Content -Path (Join-Path $PSScriptRoot 'bds_bot.pid') -Value $p.Id -Encoding ascii
Write-Host "BDS bot started pid=$($p.Id); log=$log"
# Keep wrapper alive so redirected async handlers keep writing logs.
try { Wait-Process -Id $p.Id } finally { $writer.Dispose() }
