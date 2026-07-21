$ErrorActionPreference='Continue'
$ts=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
Write-Output 'CONFIG'
$cfgText=(Invoke-WebRequest -UseBasicParsing -TimeoutSec 20 ("https://lhrealestate.web.app/api-config.json?ts=$ts")).Content
Write-Output $cfgText
$cfg=$cfgText|ConvertFrom-Json
Write-Output 'HEALTH'
try{(Invoke-WebRequest -UseBasicParsing -TimeoutSec 20 ($cfg.qhApiBase+'/health')).Content}catch{Write-Output ('ERR '+$_.Exception.Message)}
Write-Output 'LOOKUP'
$payload=@{lat=10.764170937189563; lon=106.59137392951396; includeGuland=$false; includeQhViet=$false}|ConvertTo-Json
try{
  $sw=[Diagnostics.Stopwatch]::StartNew()
  $r=Invoke-WebRequest -UseBasicParsing -TimeoutSec 80 -Method POST -Uri ($cfg.qhApiBase+'/planning/lookup') -ContentType 'application/json' -Body $payload
  $sw.Stop()
  $j=$r.Content|ConvertFrom-Json
  Write-Output ('ms='+$sw.ElapsedMilliseconds+' ok='+$j.ok+' plan='+$j.planning.planning_project.TenDoAn)
}catch{Write-Output ('ERR '+$_.Exception.Message)}
Write-Output 'HTML'
$html=(Invoke-WebRequest -UseBasicParsing -TimeoutSec 20 ("https://lhrealestate.web.app/quyhoach.html?ts=$ts")).Content
Write-Output ('uiPatch='+$html.Contains('guland-ui-only-final'))
Write-Output ('qhviet='+$html.Contains('qhviet'))
Write-Output ('includeTrue='+$html.Contains('includeQhViet:true'))
Write-Output ('fallback='+$html.Contains('API_FALLBACKS_QH'))
