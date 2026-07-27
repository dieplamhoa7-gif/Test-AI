import json,re,sys,unicodedata
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(w for w in s.split() if len(w)>2)
def toks(s):
    bad=set('du an khu dat bao cao cap nhat phuong quan thanh pho tinh huyen cong ty can ho chung cu khach san'.split())
    return set(w for w in norm(s).split() if w not in bad and not w.isdigit())
project_terms=[(g['project_name'], toks(g['project_name'])) for g in db['groups']]
rows=[]
for g in db['groups']:
    gt=toks(g['project_name'])
    for r in g.get('reports') or []:
        for c in r.get('adjacent_context_chunks') or []:
            txt=raw[int(c)-1].get('text') or ''
            nt=toks(txt[:500])
            other=[]
            for name,pt in project_terms:
                if name==g['project_name']: continue
                if len(pt & nt)>=2 and len(pt & gt)<2:
                    other.append(name)
            if other:
                rows.append({'project':g['project_name'],'record':r['record_id'],'ctx':c,'possible_other':other[:5],'snippet':re.sub(r'\s+',' ',txt[:350])})
out=BASE/'reports'/'manual_adjacent_context_audit.md'
md=['# Adjacent context audit','',f'- context chunks with possible other project hints: {len(rows)}','']
for x in rows[:200]:
    md.append(f"### {x['project']} · {x['record']} · ctx {x['ctx']}")
    md.append(f"- Possible other: {', '.join(x['possible_other'])}")
    md.append(f"- Snippet: {x['snippet']}")
    md.append('')
out.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'possible_mismatch':len(rows),'report':str(out)},ensure_ascii=False))
