from pathlib import Path
import csv,json,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
web=base/'web'; web.mkdir(exist_ok=True)
res=json.load(open(base/'map_link_resolution_all.json',encoding='utf-8')) if (base/'map_link_resolution_all.json').exists() else []
ml={x['url']:(x.get('lat'),x.get('lng')) for x in res if x.get('lat') and x.get('lng')}
BAD=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|cao tầng$|nhà ở$|\(nguồn|có lợi thế)',re.I)
ALIASES={
    'Trần Đức 1 (2':'Trần Đức 1 2.8ha Thuận Giao',
    '(nguồn anh Hùng)':'Lô mặt tiền Quốc Lộ 13 Hiệp Bình Phước',
    'nhà ở':'Lô đất Phú Thọ Hòa Tân Phú',
    'có lợi thế vị trí khi cách ga Metro Bình Thái khoảng 700m':'Urban Green / Bình Thái Thủ Đức',
    'Diamond Garden ở đường Đào Trí':'Diamond Garden Đào Trí Phú Thuận',
    'Khách sạn 5 sao tại đường 12 Hùng Vương':'Khách sạn 5 sao 12 Hùng Vương Đà Lạt',
}
def clean_name(n):
    n=(n or '').strip()
    return ALIASES.get(n,n)
def add(rows,seen,row):
    name=clean_name(row.get('name'))
    if not name or len(name)<5: return
    row['name']=name
    key=(name.lower(),round(float(row['lat']),6),round(float(row['lng']),6))
    if key in seen: return
    seen.add(key); rows.append(row)
rows=[]; seen=set()
# candidates first: contains latest date/excerpt from Teams mentions
for i,r in enumerate(csv.DictReader(open(base/'project_master_candidates_from_mentions.csv',encoding='utf-8-sig',newline='')),1):
    name=clean_name(r.get('project_name_candidate'))
    if not name or (BAD.search(name) and name not in ALIASES.values()):
        # allow alias source keys
        orig=(r.get('project_name_candidate') or '').strip()
        if orig not in ALIASES: continue
        name=ALIASES[orig]
    maps=[m.strip() for m in (r.get('map_urls') or '').split(';') if m.strip()]
    lat=lng=''
    for m in maps:
        if m in ml: lat,lng=ml[m]; break
    if not(lat and lng): continue
    add(rows,seen,{'id':r.get('existing_project_id') or f'CAND-{i:04d}','name':name,'lat':float(lat),'lng':float(lng),'date':r.get('latest_report_date') or r.get('first_report_date'),'type':'candidate' if not r.get('existing_project_id') else 'curated/candidate','status':'review' if not r.get('existing_project_id') else 'curated','priority':'high' if r.get('existing_project_id') else 'medium','address':'','province':'','district':'','area':r.get('land_area_mentions'),'far':'','population':'','price':r.get('price_mentions'),'sell_price':'','irr':'','risks':'Auto candidate từ Teams mentions; cần review/gom trùng' if not r.get('existing_project_id') else 'Đã match dòng draft cũ','excerpt':r.get('sample_excerpt'),'map_url':maps[0] if maps else ''})
# curated draft supplement
for r in csv.DictReader(open(base/'projects_from_teams_draft.csv',encoding='utf-8-sig',newline='')):
    name=clean_name(r.get('project_name'))
    lat=(r.get('latitude') or '').strip(); lng=(r.get('longitude') or '').strip()
    if (not lat or not lng) and r.get('map_url') in ml: lat,lng=ml[r['map_url']]
    if not(name and lat and lng): continue
    add(rows,seen,{'id':r.get('project_id'),'name':name,'lat':float(lat),'lng':float(lng),'date':r.get('report_date') or r.get('created_at'),'type':r.get('project_type'),'status':r.get('status'),'priority':r.get('priority') or 'high','address':r.get('address'),'province':r.get('province_city'),'district':r.get('district'),'area':r.get('land_area_m2'),'far':r.get('far'),'population':r.get('population'),'price':r.get('asking_land_price_total') or r.get('asking_land_price_per_m2'),'sell_price':r.get('expected_product_selling_price_per_m2'),'irr':r.get('irr_pct'),'risks':r.get('key_risks'),'excerpt':r.get('source_excerpt'),'map_url':r.get('map_url')})
(web/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'mapped_projects':len(rows),'out':str(web/'projects_data.js')})
