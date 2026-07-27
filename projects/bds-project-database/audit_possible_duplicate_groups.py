import json,re,unicodedata,sys,difflib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    s=re.sub(r'\b(du an|khu dat|khu|lo dat|lo|dat|tai|phuong|quan|tp|tphcm|thu duc|hcm|ha|m2|duong|mat tien|cap nhat|bao cao|project)\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(w for w in s.split() if len(w)>1 and not w.isdigit())
def tokens(s): return set(norm(s).split())
rows=db['groups']
pairs=[]
for i,a in enumerate(rows):
    ta=tokens(a['project_name']); na=norm(a['project_name'])
    if not ta: continue
    for b in rows[i+1:]:
        tb=tokens(b['project_name']); nb=norm(b['project_name'])
        if not tb: continue
        jac=len(ta&tb)/max(1,len(ta|tb)); seq=difflib.SequenceMatcher(None,na,nb).ratio()
        subset=len(ta&tb)>=2 and (ta<=tb or tb<=ta)
        if jac>=0.55 or seq>=0.72 or subset:
            pairs.append({'a_id':a['master_id'],'a':a['project_name'],'a_reports':a['report_count'],'a_fin':len(a.get('financial_items') or []),'b_id':b['master_id'],'b':b['project_name'],'b_reports':b['report_count'],'b_fin':len(b.get('financial_items') or []),'jaccard':round(jac,2),'seq':round(seq,2),'common':' '.join(sorted(ta&tb))})
# filter known broad false positives where common only generic
pairs=[p for p in pairs if len(p['common'].split())>=2]
out=BASE/'reports'/'possible_duplicate_groups_audit.md'
md=['# Possible duplicate group audit','',f'- Groups scanned: {len(rows)}',f'- Candidate pairs: {len(pairs)}','','## Candidates','']
for p in sorted(pairs,key=lambda x:(-x['jaccard'],-x['seq'],x['a'])):
    md.append(f"### {p['a_id']} ↔ {p['b_id']}")
    md.append(f"- A: {p['a']} · reports {p['a_reports']} · fin {p['a_fin']}")
    md.append(f"- B: {p['b']} · reports {p['b_reports']} · fin {p['b_fin']}")
    md.append(f"- score: jaccard {p['jaccard']} · seq {p['seq']} · common `{p['common']}`")
    md.append('')
out.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'groups':len(rows),'pairs':len(pairs),'report':str(out)},ensure_ascii=False))
