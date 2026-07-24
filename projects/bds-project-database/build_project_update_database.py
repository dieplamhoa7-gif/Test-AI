import json,re,unicodedata,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
SRC=BASE/'strict_by_message_projects.json'
OUT=BASE/'project_update_database.json'
WEB=BASE/'web'

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s or '') if unicodedata.category(c)!='Mn')
def clean(s): return re.sub(r'\s+',' ',str(s or '').strip())
def norm_name(name):
    s=strip_accents(clean(name)).lower()
    s=re.sub(r'\b(du an|da|khu dat|kdc|kdt|can ho|chung cu|bao cao|phuong an|pa|tai|co quy mo|voi quy mo)\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s)
    toks=[t for t in s.split() if len(t)>1 and t not in {'anh','sep','admin','phong','dau','tu','gui','cap','nhat','hieu','qua','tai','chinh'}]
    return ' '.join(toks[:10])
def area_key(r):
    txt=strip_accents(' '.join([r.get('name',''),r.get('popup',{}).get('location',''),r.get('popup',{}).get('source_excerpt','')[:500]])).lower()
    hits=[]
    for pat in [r'phuong\s+[a-z0-9 ]{2,25}',r'xa\s+[a-z0-9 ]{2,25}',r'quan\s+[a-z0-9 ]{1,15}',r'huyen\s+[a-z0-9 ]{2,25}',r'thu duc|binh duong|dong nai|da nang|phu quoc|nha trang|ha long|binh chanh|nha be']:
        hits += re.findall(pat,txt)
    return '|'.join(dict.fromkeys(clean(x) for x in hits[:4]))
def dist(a,b):
    try:
        if not a[0] or not b[0]: return None
        return math.hypot((a[0]-b[0])*111,(a[1]-b[1])*111)
    except: return None
def fin_items(r):
    try: return json.loads(r.get('popup',{}).get('financial_line_items') or '[]')
    except: return []
def merge_key(r):
    n=norm_name(r.get('name',''))
    a=area_key(r)
    # Weak/generic extracted names must never broadly merge; keep by message id.
    # These are often report openings or sentence fragments, not project identities.
    generic_exact={'xung quanh','dau gia','nha o xa hoi','co ban dat','dat hieu qua','nhu sau','khach san','gop la','tham gia gia them ve chuyen mo','co trao oi ve viec'}
    generic_prefix=('nhu sau','phuong an','pa ','hieu qua','khong dat','co ban dat','se duoc','dat ty le','tham gia','co loi the','gom cao tang','h2 02 voi cac gia')
    if len(n)<8 or n in generic_exact or any(n.startswith(x) for x in generic_prefix):
        return 'single:'+r['id']
    return n+'::'+a

data=json.loads(SRC.read_text(encoding='utf-8'))
# First pass group by strict key; if coordinates far apart inside group, split by coord bucket/message.
groups={}
for r in data:
    groups.setdefault(merge_key(r),[]).append(r)
projects=[]
for key,rows in groups.items():
    sub=[]
    for r in rows:
        coord=(r.get('lat'),r.get('lng')) if r.get('priority')!='review' else (None,None)
        placed=False
        for bucket in sub:
            d=dist(coord,bucket['coord'])
            if d is None or d<=1.5: # same/unknown coord; allow same name+area updates
                bucket['rows'].append(r)
                if bucket['coord'][0] is None and coord[0] is not None: bucket['coord']=coord
                placed=True; break
        if not placed: sub.append({'coord':coord,'rows':[r]})
    for bucket in sub:
        rows=sorted(bucket['rows'],key=lambda x:(x.get('date') or '9999',x.get('datetime_raw') or '',x.get('id')))
        first=rows[0]; latest=rows[-1]
        all_fin=[]; seen=set()
        for rr in rows:
            for it in fin_items(rr):
                k=(it.get('label',''),it.get('value',''))
                if k not in seen:
                    all_fin.append({'label':it.get('label',''),'value':it.get('value',''),'source_id':rr['id'],'date':rr.get('date','')}); seen.add(k)
        updates=[{'id':rr['id'],'date':rr.get('date',''),'datetime_raw':rr.get('datetime_raw',''),'source_file':rr.get('popup',{}).get('source_files',''),'sender':rr.get('sender',''),'excerpt':rr.get('popup',{}).get('source_excerpt','')} for rr in rows]
        pid='PRJ-'+str(len(projects)+1).zfill(4)
        coord=bucket['coord']
        popup=dict(latest.get('popup',{}))
        popup['financial_line_items']=json.dumps(all_fin,ensure_ascii=False)
        popup['financial_unclassified_items']='[]'
        popup['updates']=updates
        popup['update_count']=len(updates)
        popup['first_report_date']=first.get('date','')
        popup['latest_report_date']=latest.get('date','')
        popup['merge_key']=key
        projects.append({'id':pid,'name':latest.get('name') or first.get('name'),'lat':coord[0] or latest.get('lat') or 10.7769,'lng':coord[1] or latest.get('lng') or 106.7009,'date':latest.get('date',''),'datetime_raw':latest.get('datetime_raw',''),'sender':latest.get('sender',''),'type':'project-update','status':'merged-updates' if len(rows)>1 else 'single-message','priority':'review' if coord[0] is None else 'normal','score':min(95,50+len(rows)*5+len(all_fin)),'map_url':latest.get('map_url',''),'excerpt':latest.get('excerpt',''),'popup':popup})
OUT.write_text(json.dumps(projects,ensure_ascii=False,indent=2),encoding='utf-8')
(WEB/'project_update_database.js').write_text('window.PROJECT_UPDATE_DATABASE = '+json.dumps(projects,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('source_messages',len(data))
print('project_records',len(projects))
print('merged_records',sum(1 for p in projects if p['popup']['update_count']>1))
print('financial_project_records',sum(1 for p in projects if json.loads(p['popup']['financial_line_items'])))
print('max_updates',max((p['popup']['update_count'] for p in projects), default=0))
