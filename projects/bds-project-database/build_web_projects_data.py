from pathlib import Path
import csv,json,re,hashlib
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
web=base/'web'; web.mkdir(exist_ok=True)
res=json.load(open(base/'map_link_resolution_all.json',encoding='utf-8')) if (base/'map_link_resolution_all.json').exists() else []
ml={x['url']:(x.get('lat'),x.get('lng')) for x in res if x.get('lat') and x.get('lng')}
ALIASES={
    'Trần Đức 1 (2':'Trần Đức 1 2.8ha Thuận Giao','(nguồn anh Hùng)':'Lô mặt tiền Quốc Lộ 13 Hiệp Bình Phước','nhà ở':'Lô đất Phú Thọ Hòa Tân Phú','có lợi thế vị trí khi cách ga Metro Bình Thái khoảng 700m':'Urban Green / Bình Thái Thủ Đức','Diamond Garden ở đường Đào Trí':'Diamond Garden Đào Trí Phú Thuận','Khách sạn 5 sao tại đường 12 Hùng Vương':'Khách sạn 5 sao 12 Hùng Vương Đà Lạt',
}
BAD=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|cao tầng$|nhà ở$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ)',re.I)
def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def clean_name(n, excerpt=''):
    n=clean(n); n=ALIASES.get(n,n)
    if (not n or BAD.search(n)):
        # Better fallbacks from excerpt
        pats=[r'dự án\s+([^,.\n:;]{4,90})', r'DA\s+([^,.\n:;]{4,90})', r'khu đất\s+([^,.\n:;]{4,90})', r'lô đất\s+([^,.\n:;]{4,90})']
        for p in pats:
            m=re.search(p,excerpt or '',re.I)
            if m:
                cand=clean(m.group(1)).strip(' -:;,.')
                if cand and not BAD.search(cand): return ALIASES.get(cand,cand)[:100]
    return n[:100]
def score_project(row):
    s=45
    blob=' '.join(str(row.get(k,'') or '') for k in ['area','price','far','population','irr','excerpt','risks']).lower()
    if row.get('priority')=='high': s+=12
    if row.get('status') in ('curated','screening','checking_planning'): s+=8
    for term,pts in [('irr',8),('npv',5),('pháp lý',8),('quy hoạch',7),('giá chào',7),('tổng mức đầu tư',6),('doanh thu',6),('hệ số',4),('dân số',4)]:
        if term in blob: s+=pts
    if row.get('map_url'): s+=5
    if row.get('area'): s+=5
    if row.get('price'): s+=5
    if 'rủi ro' in blob or 'không đạt' in blob: s-=8
    return max(0,min(100,s))
def add(rows,seen,row):
    row['name']=clean_name(row.get('name'), row.get('excerpt',''))
    if not row['name'] or len(row['name'])<4: return
    try: lat=round(float(row['lat']),6); lng=round(float(row['lng']),6)
    except Exception: return
    # key by map coordinate + normalized name prefix. Allows multiple deals at same location only if name differs.
    key=(lat,lng,re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',row['name'].lower()).strip()[:45])
    if key in seen: return
    seen.add(key)
    row['score']=score_project(row)
    rows.append(row)
rows=[]; seen=set()
# 1) mention-level: fullest coverage of map links and source date
for i,m in enumerate(csv.DictReader(open(base/'project_mentions_from_teams_full.csv',encoding='utf-8-sig',newline='')),1):
    maps=[x.strip() for x in re.split(r';\s*',m.get('map_urls','') or '') if x.strip()]
    if not maps: continue
    lat=lng=map_url=''
    for u in maps:
        if u in ml: lat,lng=ml[u]; map_url=u; break
    if not(lat and lng): continue
    name=clean_name(m.get('project_name_hint'),m.get('excerpt'))
    if not name or len(name)<4: name=f"Mention {m.get('mention_id') or i}"
    add(rows,seen,{'id':m.get('mention_id') or f'MENTION-{i:04d}','name':name,'lat':float(lat),'lng':float(lng),'date':m.get('report_date'),'datetime_raw':m.get('report_datetime_raw'),'sender':m.get('sender'),'type':'mention','status':'raw/review','priority':'medium','address':'','province':'','district':'','area':m.get('land_area_mentions'),'far':m.get('far_mentions'),'population':m.get('population_mentions'),'price':m.get('price_mentions'),'sell_price':'','irr':m.get('irr_mentions'),'npv':m.get('npv_mentions'),'risks':'Raw Teams mention — cần master/gom trùng','excerpt':m.get('excerpt'),'map_url':map_url,'source_file':m.get('source_file'),'source_chat':m.get('source_chat')})
# 2) curated master draft supplements
for r in csv.DictReader(open(base/'projects_from_teams_draft.csv',encoding='utf-8-sig',newline='')):
    lat=clean(r.get('latitude')); lng=clean(r.get('longitude')); map_url=r.get('map_url') or ''
    if (not lat or not lng) and map_url in ml: lat,lng=ml[map_url]
    add(rows,seen,{'id':r.get('project_id'),'name':r.get('project_name'),'lat':lat,'lng':lng,'date':r.get('report_date') or r.get('created_at'),'datetime_raw':r.get('report_datetime_raw'),'sender':'','type':r.get('project_type'),'status':r.get('status') or 'curated','priority':r.get('priority') or 'high','address':r.get('address'),'province':r.get('province_city'),'district':r.get('district'),'area':r.get('land_area_m2'),'far':r.get('far'),'population':r.get('population'),'price':r.get('asking_land_price_total') or r.get('asking_land_price_per_m2'),'sell_price':r.get('expected_product_selling_price_per_m2'),'irr':r.get('irr_pct'),'npv':'','risks':r.get('key_risks'),'excerpt':r.get('source_excerpt'),'map_url':map_url,'source_file':'projects_from_teams_draft.csv','source_chat':r.get('source_chat')})
rows.sort(key=lambda r:(-r.get('score',0), r.get('name','')))
(web/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'mapped_records':len(rows),'resolved_links':len(ml),'out':str(web/'projects_data.js')})
