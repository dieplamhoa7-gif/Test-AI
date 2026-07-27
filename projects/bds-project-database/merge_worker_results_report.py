import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
all=[]
for fp in sorted((BASE/'subagent_jobs').glob('job_*_results.json')):
    all += json.loads(fp.read_text(encoding='utf-8'))
summary={}
for r in all: summary[r['status']]=summary.get(r['status'],0)+1
md=['# Parallel job review results','',f'- Total priority chunks reviewed: {len(all)}']+[f'- {k}: {v}' for k,v in sorted(summary.items())]+['','## Extracted candidates','']
for r in all:
    if r['status']!='extracted': continue
    md.append(f"### Chunk {r['chunk']} - {r['project']}")
    for x in r['extracted_items']:
        md.append(f"- **{x['label']}**: {x['value']}")
    if r.get('notes'): md.append(f"- Notes: {r['notes']}")
    md.append('')
md += ['## Attachment missing / no text candidates','']
for r in all:
    if r['status']!='extracted': md.append(f"- Chunk {r['chunk']} · {r['status']} · {r['project']} · {r.get('notes','')}")
(BASE/'reports'/'manual_parallel_job_review.md').write_text('\n'.join(md),encoding='utf-8')
print(summary)
