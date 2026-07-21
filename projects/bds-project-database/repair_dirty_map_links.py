from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def repair(u):
    u=u.strip()
    u=u.replace('**','').replace('…','').replace('...','')
    u=u.rstrip('-,.;)')
    # Common truncated goo.gl/maps token is still worth storing, but cannot expand if incomplete.
    return u
changed=0
for r in masters:
    links=[x.strip() for x in re.split(r';\s*',r.get('map_urls','') or '') if x.strip()]
    fixed=[]
    for u in links:
        v=repair(u)
        if v and v not in fixed: fixed.append(v)
    if fixed and '; '.join(fixed)!=r.get('map_urls',''):
        r['map_urls']='; '.join(fixed); changed+=1
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'repaired_records':changed})
