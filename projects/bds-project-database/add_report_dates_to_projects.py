from pathlib import Path
import csv, json, re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
csvp=base/'projects_from_teams_draft.csv'
chunks=json.load(open(base/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))

def norm(s): return re.sub(r'\s+',' ',s or '').strip().lower()
def tokens(s):
    s=norm(s)
    return [t for t in re.split(r'[^0-9a-zA-ZÀ-ỹ]+',s) if len(t)>=3]
rows=list(csv.DictReader(open(csvp,encoding='utf-8-sig',newline='')))
fieldnames=list(rows[0].keys()) if rows else []
# insert report fields after source_message_link
for fld in ['report_date','report_datetime_raw']:
    if fld not in fieldnames:
        idx=fieldnames.index('source_excerpt') if 'source_excerpt' in fieldnames else len(fieldnames)
        fieldnames.insert(idx,fld)
for r in rows:
    r.pop(None,None)
    if r.get('report_date'): continue
    hay=(r.get('project_name','')+' '+r.get('source_excerpt','')+' '+r.get('address',''))
    rt=tokens(r.get('project_name',''))[:5]
    best=None; bestscore=0
    for c in chunks:
        text=norm(c.get('text',''))
        score=0
        for t in rt:
            if t in text: score+=2
        # source excerpt is often very telling
        ex=norm(r.get('source_excerpt',''))[:80]
        if ex and ex.lower() in text: score+=8
        if r.get('map_url') and r.get('map_url') in c.get('text',''): score+=10
        if score>bestscore:
            bestscore=score; best=c
    if best and bestscore>=4:
        r['report_date']=best.get('report_date','')
        r['report_datetime_raw']=best.get('report_datetime_raw','')
with open(csvp,'w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fieldnames,extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
print({'rows':len(rows),'dated':sum(1 for r in rows if r.get('report_date'))})
