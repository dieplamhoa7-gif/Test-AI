from pathlib import Path
import json
p=Path('FA/data/history/2026-06-05_v2.json')
s=json.loads(p.read_text(encoding='utf-8'))
rows=[]
def walk(prefix,obj):
    if isinstance(obj,dict):
        if any(k in obj for k in ('value','sell','buy','totalNetBn','overnight')):
            rows.append((prefix,obj))
        for k,v in obj.items(): walk(prefix+'.'+k if prefix else k,v)
    elif isinstance(obj,list):
        pass
walk('',s)
nonnull=[]; null=[]
for k,o in rows:
    val=None
    for kk in ('value','sell','buy','totalNetBn','overnight'):
        if kk in o: val=o.get(kk); break
    (nonnull if val is not None else null).append((k,val,o.get('source') or o.get('error')))
out={'file':str(p),'nonnull_count':len(nonnull),'null_count':len(null),'nonnull':nonnull,'null':null,'top_keys':list(s.keys())}
Path('FA/data/unified_macro/fetch_run_2026-06-05_v2_coverage.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'nonnull':len(nonnull),'null':len(null),'keys':list(s.keys())},ensure_ascii=False,indent=2))
