param(
  [string]$AiBase = $env:MODEL3_FORCE_BASE_URL,
  [string]$MarketBase = $env:MARKET_DATA_GATEWAY_URL,
  [string]$LogFile = (Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..')).Path 'logs\lh_tunnel_healthcheck.log')
)

$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null
function Log($m) { "$(Get-Date -Format s) $m" | Tee-Object -FilePath $LogFile -Append }
function Test-Url($url, [int]$TimeoutSec = 20) {
  try {
    $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec $TimeoutSec
    return @{ ok = ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500); status = $r.StatusCode; body = ($r.Content | Select-Object -First 1) }
  } catch {
    $status = 0
    try { $status = [int]$_.Exception.Response.StatusCode } catch {}
    # For protected AI endpoints, 401/403 means the tunnel route is alive and auth is required.
    if ($status -in @(401,403)) { return @{ ok = $true; status = $status; authRequired = $true; error = $_.Exception.Message } }
    return @{ ok = $false; status = $status; error = $_.Exception.Message }
  }
}

if (-not $AiBase) { $AiBase = 'https://3t8l9f.tail6c0e00.ts.net/v1' }
$AiBase = $AiBase.TrimEnd('/')
$aiProbe = if ($AiBase.EndsWith('/v1')) { "$AiBase/models" } else { "$AiBase/v1/models" }
Log "AI tunnel probe: $aiProbe"
$ai = Test-Url $aiProbe 20
if (-not $ai.ok) {
  Log "AI tunnel FAIL: $($ai.error) status=$($ai.status). Restarting Tailscale service if possible."
  try { Restart-Service Tailscale -ErrorAction SilentlyContinue; Start-Sleep -Seconds 8 } catch { Log "Restart Tailscale failed: $($_.Exception.Message)" }
  $ai2 = Test-Url $aiProbe 20
  Log "AI tunnel retest: ok=$($ai2.ok) status=$($ai2.status) error=$($ai2.error)"
} else { Log "AI tunnel OK status=$($ai.status)" }

if ($MarketBase) {
  $MarketBase = $MarketBase.TrimEnd('/')
  $marketProbe = "$MarketBase/market-data/SSI?refresh=false"
  Log "Market tunnel probe: $marketProbe"
  $mk = Test-Url $marketProbe 30
  if (-not $mk.ok) {
    Log "Market tunnel FAIL: $($mk.error) status=$($mk.status). Do NOT reuse AI/9Router tunnel as market gateway."
  } else { Log "Market tunnel OK status=$($mk.status)" }
} else {
  Log 'MARKET_DATA_GATEWAY_URL blank: OK; Render/local should use bundled provider fallback.'
}

# Record current funnel status for diagnostics.
try { $fs = (& tailscale funnel status 2>&1) -join "`n"; Log "tailscale funnel status:`n$fs" } catch { Log "tailscale funnel status failed: $($_.Exception.Message)" }
exit 0
