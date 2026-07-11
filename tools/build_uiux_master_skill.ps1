$ErrorActionPreference='Stop'
$srcNames=@('21st-frontend-design','avoid-ai-design','banner-design','brand','design','design-system','slides','taste-redesign-skill','ui-styling','ui-ux-pro-max','utf8-frontend-guard')
$outDir='skills/openclaw-ui-ux-frontend-master'
if(Test-Path $outDir){ Remove-Item -Recurse -Force $outDir }
New-Item -ItemType Directory -Force $outDir | Out-Null
$records=@()
$hashes=@{}
foreach($skill in $srcNames){
  if(!(Test-Path "skills/$skill")){ continue }
  $root=(Resolve-Path "skills/$skill").Path
  $files=Get-ChildItem "skills/$skill" -Recurse -File -Force | Where-Object { $_.Extension -notin @('.ttf','.png','.jpg','.jpeg','.webp','.gif','.ico','.pdf') -and $_.FullName -notmatch '\\\.git(\\|$)' -and $_.FullName -notmatch '\\node_modules(\\|$)' } | Sort-Object FullName
  foreach($f in $files){
    $rel=$f.FullName.Substring($root.Length+1)
    $bytes=[IO.File]::ReadAllBytes($f.FullName)
    $sha=[BitConverter]::ToString([Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace('-','').ToLowerInvariant()
    $text=Get-Content $f.FullName -Raw -Encoding UTF8
    if($hashes.ContainsKey($sha)){
      $records += [pscustomobject]@{ skill=$skill; rel=$rel; sha=$sha; duplicateOf=$hashes[$sha]; text=$null }
    } else {
      $key="$skill/$rel"; $hashes[$sha]=$key
      $records += [pscustomobject]@{ skill=$skill; rel=$rel; sha=$sha; duplicateOf=$null; text=$text }
    }
  }
}
$sb=New-Object Text.StringBuilder
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('name: openclaw-ui-ux-frontend-master')
[void]$sb.AppendLine('description: "Unified OpenClaw master skill for design, UX, UI, frontend implementation, branding, slides, banners, visual quality, accessibility, UTF-8 frontend guardrails, and anti-generic-AI design. Aggregates local design/frontend skills with exact duplicate files removed while preserving source mapping and details."')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# OpenClaw UI/UX Frontend Master Skill')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Scope')
[void]$sb.AppendLine('Use this master skill for any task involving UI, UX, frontend, visual design, design systems, landing pages, app interfaces, dashboards, charts, branding, banners, slides, responsive implementation, accessibility, interaction polish, or frontend text/encoding safety.')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Aggregated Skills')
foreach($n in $srcNames){ [void]$sb.AppendLine(('- `{0}`' -f $n)) }
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Deduplication Policy')
[void]$sb.AppendLine('- Exact duplicate source files are omitted from the main body once and listed in `SOURCE_INDEX.md`.')
[void]$sb.AppendLine('- Non-identical files are preserved in full, even if topics overlap, to avoid losing detail.')
[void]$sb.AppendLine('- Binary assets such as fonts/images are not embedded in this single file; keep using their original skill folders for assets.')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Full Consolidated Knowledge')
foreach($r in ($records | Where-Object { -not $_.duplicateOf })){
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('---')
  [void]$sb.AppendLine(('## Source: {0}/{1}' -f $r.skill,$r.rel))
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine($r.text.TrimEnd())
}
$skillPath=Join-Path $outDir 'SKILL.md'
[IO.File]::WriteAllText((Join-Path (Resolve-Path $outDir).Path 'SKILL.md'), $sb.ToString(), [Text.UTF8Encoding]::new($false))
$idx=New-Object Text.StringBuilder
[void]$idx.AppendLine('# Source Index - OpenClaw UI/UX Frontend Master Skill')
[void]$idx.AppendLine('')
[void]$idx.AppendLine('## Included Unique Files')
foreach($r in ($records | Where-Object { -not $_.duplicateOf })){ [void]$idx.AppendLine(('- {0}/{1} - sha256:{2}' -f $r.skill,$r.rel,$r.sha)) }
[void]$idx.AppendLine('')
[void]$idx.AppendLine('## Exact Duplicates Omitted From Body')
foreach($r in ($records | Where-Object { $_.duplicateOf })){ [void]$idx.AppendLine(('- {0}/{1} duplicates `{2}` - sha256:{3}' -f $r.skill,$r.rel,$r.duplicateOf,$r.sha)) }
[IO.File]::WriteAllText((Join-Path (Resolve-Path $outDir).Path 'SOURCE_INDEX.md'), $idx.ToString(), [Text.UTF8Encoding]::new($false))
"Created $skillPath"
"Unique files: $((($records|Where-Object { -not $_.duplicateOf})|Measure-Object).Count)"
"Duplicate files omitted: $((($records|Where-Object { $_.duplicateOf})|Measure-Object).Count)"
"Size: $((Get-Item $skillPath).Length) bytes"
