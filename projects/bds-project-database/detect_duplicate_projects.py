from pathlib import Path
import json,csv,re,math,unicodedata
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn')
    s=re.sub(r'[^a-z0-9]+',' ',s.lower())
    for w in ['du an','khu dat','lo dat','cao tang','chung cu','khach san','noxh']:
        s=re.sub(r'\b'+w+r'\b',' ',s)
    return clean(s)
def tokens(s): return set(t for t in norm(s).split() if len(t)>=3)
def jacc(a,b):
    a=tokens(a); b=tokens(b)
    if not a or not b: return 0
    return len(a&b)/len(a|b)
def hav(lat1,lng1,lat2,lng2):
    R=6371000
    p1=math.radians(float(lat1)); p2=math.radians(float(lat2)); dp=math.radians(float(lat2)-float(lat1)); dl=math.radians(float(lng2)-float(lng1))
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.atan2(math.sqrt(a),math.sqrt(1-a))
def map_tokens(r): return set(re.findall(r'https?://[^;\s]+',r.get('map_urls','') or ''))
rows=[]
for i,a in enumerate(masters):
    for b in masters[i+1:]:
        reasons=[]; score=0
        ns=jacc(a.get('project_name',''),b.get('project_name',''))
        if ns>=0.72: score+=45; reasons.append(f'name_sim={ns:.2f}')
        ma=map_tokens(a); mb=map_tokens(b)
        if ma and mb and ma&mb: score+=80; reasons.append('same_map_link')
        if a.get('latitude') and b.get('latitude') and a.get('longitude') and b.get('longitude'):
            try:
                d=hav(a['latitude'],a['longitude'],b['latitude'],b['longitude'])
                if d<=35: score+=60; reasons.append(f'same_coord_{d:.0f}m')
                elif d<=150 and ns>=0.35: score+=35; reasons.append(f'near_coord_{d:.0f}m')
            except Exception: pass
        # same source + similar name
        if a.get('source_files') and b.get('source_files') and set(a['source_files'].split('; ')) & set(b['source_files'].split('; ')) and ns>=0.45:
            score+=25; reasons.append('same_source_similar_name')
        if score>=60:
            rows.append({'a_id':a.get('master_id'),'a_name':a.get('project_name'),'b_id':b.get('master_id'),'b_name':b.get('project_name'),'score':score,'reasons':'; '.join(reasons),'a_date':a.get('latest_report_date') or a.get('first_report_date'),'b_date':b.get('latest_report_date') or b.get('first_report_date'),'a_coords':a.get('coordinates'),'b_coords':b.get('coordinates'),'a_map':a.get('map_urls','')[:220],'b_map':b.get('map_urls','')[:220]})
rows.sort(key=lambda r:-int(r['score']))
with open(base/'duplicate_project_candidates.csv','w',encoding='utf-8-sig',newline='') as fp:
    fs=list(rows[0].keys()) if rows else ['a_id']; w=csv.DictWriter(fp,fieldnames=fs); w.writeheader(); w.writerows(rows)
md=['# Duplicate Project Candidates\n',f'- Candidate pairs: {len(rows)}','']
for r in rows[:120]:
    md.append(f"## {r['a_id']} ↔ {r['b_id']} — score {r['score']}\n- A: {r['a_name']}\n- B: {r['b_name']}\n- Reasons: {r['reasons']}\n- Coords: {r['a_coords']} | {r['b_coords']}\n- Dates: {r['a_date']} | {r['b_date']}\n")
(base/'duplicate_project_candidates.md').write_text('\n'.join(md),encoding='utf-8')
print({'duplicate_pairs':len(rows),'high_confidence':sum(1 for r in rows if int(r['score'])>=100),'out':str(base/'duplicate_project_candidates.csv')})
