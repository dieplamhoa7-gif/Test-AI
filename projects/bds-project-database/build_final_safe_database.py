import json,re,unicodedata,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
SRC=BASE/'strict_by_message_projects.json'
OUT=BASE/'final_safe_project_database.json'
WEB=BASE/'web'

def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',str(s or '')) if unicodedata.category(c)!='Mn')
def clean(s): return re.sub(r'\s+',' ',str(s or '').strip())
def norm(s):
    s=strip(clean(s)).lower(); s=re.sub(r'[^a-z0-9]+',' ',s)
    stop={'du','an','da','khu','dat','bao','cao','sep','admin','phong','dau','tu','nhu','sau','ve','viec','cap','nhat','hieu','qua','tai','chinh','phuong','pa','co','voi','quy','mo'}
    toks=[t for t in s.split() if len(t)>1 and t not in stop]
    return ' '.join(toks[:8])
def explicit_project_name(name, excerpt):
    n=clean(name)
    bad_patterns=[r'^như sau$',r'^nhu sau$',r'^\(fs\)$',r'^khách sạn$',r'^xung quanh$',r'^có ',r'^không ',r'^sẽ ',r'^đạt ',r'^tham gia',r'^hiện tại',r'^gồm ',r'^gộp là',r'^theo phương án',r'^h2-02 với các giả định',r'.*\bnhư sau$',r'.*\bnhu sau$',r'.*\bvề việc điều chỉnh',r'.*\btheo phương án tổ hợp',r'.*\bđánh giá nhanh phương án']
    if not n or len(n)<5: return False
    if any(re.search(p,n,flags=re.I) for p in bad_patterns): return False
    nn=norm(n)
    if len(nn)<4: return False
    # require either project-ish keyword, proper name, area/road identifier, or map in excerpt
    ex=excerpt.lower()
    if re.search(r'\b(dự án|DA|KDC|KĐT|khu đất|chung cư|resort|khách sạn|cao tầng|phân lô)\b', n+' '+excerpt, flags=re.I): return True
    if re.search(r'\d+\s*(ha|m2|m²)|đường|quận|phường|xã|thủ đức|bình dương|đồng nai|đà nẵng', n, flags=re.I): return True
    if 'maps.app.goo.gl' in ex or 'google.com/maps' in ex: return True
    return False
def area_key(r):
    txt=strip(' '.join([r.get('name',''),r.get('popup',{}).get('location',''),r.get('popup',{}).get('source_excerpt','')[:700]])).lower()
    hits=[]
    for pat in [r'phuong\s+[a-z0-9 ]{2,22}',r'xa\s+[a-z0-9 ]{2,22}',r'quan\s+[a-z0-9 ]{1,14}',r'huyen\s+[a-z0-9 ]{2,22}',r'thu duc|binh duong|dong nai|da nang|phu quoc|nha trang|ha long|binh chanh|nha be|quan 9|quan 2']:
        hits += re.findall(pat,txt)
    return '|'.join(dict.fromkeys(clean(x) for x in hits[:3]))
def dist(a,b):
    if not a or not b or a[0] is None or b[0] is None: return None
    return math.hypot((a[0]-b[0])*111,(a[1]-b[1])*111)
def fin(r):
    try: return json.loads(r.get('popup',{}).get('financial_line_items') or '[]')
    except: return []
def key(r): return norm(r['name'])+'::'+area_key(r)

data=json.loads(SRC.read_text(encoding='utf-8'))
accepted=[]; review=[]
for r in data:
    if explicit_project_name(r.get('name',''), r.get('popup',{}).get('source_excerpt','')):
        accepted.append(r)
    else:
        review.append(r)

groups={}
for r in accepted:
    groups.setdefault(key(r),[]).append(r)
projects=[]; merge_review=[]
for k,rows in groups.items():
    # only merge if not generic and coord/source proximity okay
    buckets=[]
    for r in rows:
        coord=None if r.get('priority')=='review' else (r.get('lat'),r.get('lng'))
        placed=False
        for b in buckets:
            d=dist(coord,b['coord'])
            if len(rows)>1 and d is not None and d>1.5: continue
            # if no coord, require area key non-empty for merge
            if (coord is None or b['coord'] is None) and not area_key(r): continue
            b['rows'].append(r); placed=True
            if b['coord'] is None and coord is not None: b['coord']=coord
            break
        if not placed: buckets.append({'coord':coord,'rows':[r]})
    for b in buckets:
        rows=sorted(b['rows'], key=lambda x:(x.get('date') or '9999', x.get('datetime_raw') or '', x['id']))
        first,latest=rows[0],rows[-1]
        allfin=[]; seen=set()
        for rr in rows:
            for it in fin(rr):
                val=clean(it.get('value',''))[:180]; lab=clean(it.get('label',''))
                if lab and val and (lab,val) not in seen:
                    allfin.append({'label':lab,'value':val,'source_id':rr['id'],'date':rr.get('date','')}); seen.add((lab,val))
        ups=[{'id':rr['id'],'date':rr.get('date',''),'datetime_raw':rr.get('datetime_raw',''),'source_file':rr.get('popup',{}).get('source_files',''),'sender':rr.get('sender',''),'excerpt':rr.get('popup',{}).get('source_excerpt','')} for rr in rows]
        popup=dict(latest.get('popup',{})); popup.update({'updates':ups,'update_count':len(ups),'first_report_date':first.get('date',''),'latest_report_date':latest.get('date',''),'merge_key':k,'financial_line_items':json.dumps(allfin,ensure_ascii=False),'financial_unclassified_items':'[]'})
        coord=b['coord'] or (latest.get('lat'),latest.get('lng'))
        projects.append({'id':'SAFE-'+str(len(projects)+1).zfill(4),'name':latest['name'],'lat':coord[0] if coord else 10.7769,'lng':coord[1] if coord else 106.7009,'date':latest.get('date',''),'datetime_raw':latest.get('datetime_raw',''),'sender':latest.get('sender',''),'type':'project','status':'merged-update' if len(rows)>1 else 'single-source','priority':'normal' if b['coord'] else 'review-location','score':min(95,55+len(rows)*5+len(allfin)),'map_url':latest.get('map_url',''),'excerpt':latest.get('excerpt',''),'popup':popup})

OUT.write_text(json.dumps({'projects':projects,'review_messages':review},ensure_ascii=False,indent=2),encoding='utf-8')
(WEB/'final_safe_project_database.js').write_text('window.FINAL_SAFE_PROJECTS = '+json.dumps(projects,ensure_ascii=False,indent=2)+';\nwindow.FINAL_REVIEW_MESSAGES = '+json.dumps(review,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('source_messages',len(data))
print('accepted_project_messages',len(accepted))
print('review_messages',len(review))
print('final_projects',len(projects))
print('merged_projects',sum(1 for p in projects if p['popup']['update_count']>1))
print('financial_projects',sum(1 for p in projects if json.loads(p['popup']['financial_line_items'])))
print('max_updates',max([p['popup']['update_count'] for p in projects] or [0]))
