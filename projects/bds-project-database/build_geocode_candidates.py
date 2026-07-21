from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def bad_query(q): return len(q)<8 or re.search(r'^(chưa|không|này|image|link)',q,re.I)
rows=[]
for r in masters:
    if r.get('latitude') and r.get('longitude'): continue
    parts=[]
    for f in ['location','project_name','district_area','province_city']:
        v=clean(r.get(f,''))
        if v and v not in parts: parts.append(v)
    query=', '.join(parts)
    if bad_query(query):
        # fallback from source excerpt first location-like line
        ex=clean(r.get('source_excerpt',''))
        m=re.search(r'(?:Vị trí|Địa chỉ)[:：]?\s*([^\n.;]{10,180})',ex,re.I)
        if m:
            query=clean(m.group(1)+' '+r.get('province_city',''))
    if bad_query(query): continue
    priority=0
    if r.get('location'): priority+=5
    if r.get('province_city'): priority+=3
    if r.get('land_area_main'): priority+=1
    if r.get('latest_report_date') or r.get('first_report_date'): priority+=1
    rows.append({'master_id':r.get('master_id'),'project_name':r.get('project_name'),'query':query,'priority':priority,'latest_report_date':r.get('latest_report_date') or r.get('first_report_date'),'sample_excerpt':clean(r.get('source_excerpt'))[:500]})
rows.sort(key=lambda x:(-x['priority'],x['project_name']))
with open(base/'geocode_candidates.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()) if rows else ['master_id']); w.writeheader(); w.writerows(rows)
print({'geocode_candidates':len(rows),'out':str(base/'geocode_candidates.csv')})
