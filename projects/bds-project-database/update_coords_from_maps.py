import csv,json
from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
reader=csv.DictReader(open(p/'projects_from_teams_draft.csv',encoding='utf-8-sig'))
fieldnames=reader.fieldnames
rows=list(reader)
maps=json.load(open(p/'map_link_resolution_full.json',encoding='utf-8'))
d={m['url']:(m.get('lat',''),m.get('lng','')) for m in maps}
changed=0
for r in rows:
    url=(r.get('map_url','') or r.get('google_maps_url','') or '').strip()
    if url in d:
        lat,lng=d[url]
        for k in ['latitude','lat']:
            if k in r and lat and not r[k].strip():
                r[k]=lat; changed+=1
        for k in ['longitude','lng']:
            if k in r and lng and not r[k].strip():
                r[k]=lng; changed+=1
for r in rows:
    r.pop(None, None)
with open(p/'projects_from_teams_draft.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='ignore')
    w.writeheader(); w.writerows(rows)
print('changed',changed)
