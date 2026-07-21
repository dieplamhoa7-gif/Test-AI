from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
chunks=json.load(open(base/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def norm(s):
    s=clean(s).lower(); s=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',s); return clean(s)
by_file={}
for c in chunks:
    by_file.setdefault(c.get('source_file',''),[]).append(c)
fixed=0
for r in masters:
    if r.get('first_report_date') or r.get('latest_report_date'):
        continue
    files=[]
    for f in re.split(r';\s*',r.get('source_files','') or ''):
        f=clean(f)
        if f: files.append(f)
    name_tokens=[t for t in norm(r.get('project_name','')).split() if len(t)>=4][:8]
    ex_key=norm((r.get('source_excerpt') or '')[:700])
    best=None; bestscore=0
    for f in files:
        for c in by_file.get(f,[]):
            if not c.get('report_date'): continue
            txtn=norm(c.get('text',''))
            score=0
            if ex_key and ex_key[:180] in txtn: score+=30
            for t in name_tokens:
                if t in txtn: score+=3
            # map link is an excellent join key
            for u in re.findall(r'https://maps\.app\.goo\.gl/[A-Za-z0-9]+', r.get('map_urls','') or ''):
                if u in c.get('text',''): score+=20
            if score>bestscore:
                bestscore=score; best=c
    if best and bestscore>=6:
        r['first_report_date']=r['latest_report_date']=best.get('report_date','')
        r['report_datetime_raw_backfilled']=best.get('report_datetime_raw','')
        fixed+=1
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'fixed_dates_from_batches':fixed})
