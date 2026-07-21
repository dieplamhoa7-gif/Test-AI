from pathlib import Path
import json
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
web=base/'web'; web.mkdir(exist_ok=True)
records=json.load(open(base/'project_popup_master.json',encoding='utf-8'))
rows=[]
for r in records:
    if not (r.get('latitude') and r.get('longitude')): continue
    try: lat=float(r['latitude']); lng=float(r['longitude'])
    except Exception: continue
    score=int(r.get('data_completeness_score') or 0)
    rows.append({
        'id':r.get('master_id'), 'name':r.get('project_name'), 'lat':lat, 'lng':lng,
        'date':r.get('latest_report_date') or r.get('first_report_date'), 'datetime_raw':'', 'sender':r.get('senders'),
        'type':r.get('project_type') or 'master', 'status':'master/review', 'priority':'high' if score>=70 else 'medium' if score>=45 else 'low',
        'score':score, 'popup':r,
        'area':r.get('land_area'), 'price':r.get('asking_price') or r.get('price_mentions'), 'far':r.get('far'), 'population':r.get('population'),
        'irr':r.get('irr'), 'npv':r.get('npv'), 'excerpt':r.get('source_excerpt'), 'map_url':(r.get('map_urls') or '').split(';')[0].strip(),
        'source_file':r.get('source_files'), 'source_chat':'Bee || Phân Tích Đầu Tư'
    })
rows.sort(key=lambda x:(-x['score'],x['name']))
(web/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'mapped_master_records':len(rows),'out':str(web/'projects_data.js')})
