import re,json
from pathlib import Path
BASE=Path(__file__).resolve().parent
md=(BASE/'reports/manual_10parts_image_finance_audit.md').read_text(encoding='utf-8',errors='ignore')
blocks=re.split(r'\n### Chunk ', md.split('## Priority review',1)[1].split('## All linked',1)[0])
items=[]
for b in blocks:
    b=b.strip()
    if not b: continue
    first,*rest=b.splitlines()
    m=re.match(r'(\d+) · ([^·]*) · (.*)', first)
    if not m: continue
    chunk=int(m.group(1)); text='\n'.join(rest)
    proj=re.search(r'- Projects: (.*)', text)
    items.append({'chunk':chunk,'header':first,'project':proj.group(1).strip() if proj else '', 'block':'### Chunk '+b})
# balanced chunks
jobs=[[] for _ in range(4)]
for i,it in enumerate(items): jobs[i%4].append(it)
out=BASE/'subagent_jobs'; out.mkdir(exist_ok=True)
for idx,job in enumerate(jobs,1):
    lines=[f'# OCR/extraction review job {idx}', '', 'Review these priority chunks. For each chunk/project:', '- read raw text from teams_candidate_chunks_with_dates.json by chunk number (1-based)', '- inspect linked reports in web/manual_records_merged_reports.js', '- extract missing financial/planning/legal facts that are clearly in text', '- if only image/attachment marker exists and no local file, mark as attachment_missing', '- write JSON result to subagent_jobs/job_%02d_results.json' % idx, '', '## Assigned chunks', '']
    for it in job:
        lines.append(it['block']); lines.append('')
    (out/f'job_{idx:02d}.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'priority':len(items),'jobs':[len(j) for j in jobs]},ensure_ascii=False))
