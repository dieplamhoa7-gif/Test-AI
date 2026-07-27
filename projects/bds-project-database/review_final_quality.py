import json,re,sys,collections
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
items=[]
for g in db['groups']:
    for it in g.get('financial_items') or []:
        items.append((g,it))
accepted=[(g,it) for g,it in items if it.get('review_status')=='parallel_review_accepted']
weak=[]
for g,it in accepted:
    v=(it.get('value') or '').strip()
    if len(v)<15 or re.search(r'^(message by|translate|edited|image by|by )',v,re.I) or re.search(r'\.pdf$|\.mp4$|\.xlsx$',v,re.I):
        weak.append((g,it,'bad_marker_or_file'))
    elif not re.search(r'\d',v):
        weak.append((g,it,'no_number'))
# duplicate values within same group
dups=[]
for g in db['groups']:
    c=collections.Counter((it.get('label','').strip().lower(),it.get('value','').strip().lower()) for it in g.get('financial_items') or [])
    for k,n in c.items():
        if n>1: dups.append((g['project_name'],n,k[0],k[1][:120]))
summary={
 'groups':len(db['groups']),
 'reports':sum(len(g.get('reports') or []) for g in db['groups']),
 'financial_groups':sum(1 for g in db['groups'] if g.get('financial_items')),
 'financial_items':len(items),
 'parallel_accepted_items':len(accepted),
 'weak_parallel_items':len(weak),
 'duplicate_group_items':len(dups),
 'totals':db.get('totals')
}
out=BASE/'reports'/'manual_final_quality_review.md'
md=['# Manual database final quality review','', '## Summary','']
for k,v in summary.items(): md.append(f'- {k}: {v}')
md += ['','## Weak accepted items','']
for g,it,reason in weak[:80]: md.append(f"- {reason} · {g['project_name']} · {it.get('label')}: {it.get('value')}")
md += ['','## Duplicate group items','']
for p,n,l,v in dups[:80]: md.append(f'- {p} · x{n} · {l}: {v}')
out.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if weak: print('WEAK_FOUND',len(weak))
