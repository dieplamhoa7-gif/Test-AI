from pathlib import Path
import json,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
web=base/'web'; web.mkdir(exist_ok=True)
records=json.load(open(base/'project_popup_records_full.json',encoding='utf-8'))
rows=[]; seen=set()
for r in records:
    if not (r.get('latitude') and r.get('longitude')): continue
    try: lat=round(float(r['latitude']),6); lng=round(float(r['longitude']),6)
    except Exception: continue
    # keep separate records if content differs, but collapse exact same name+coord+date
    key=(lat,lng,(r.get('project_name') or '').lower()[:80],r.get('report_date',''))
    if key in seen: continue
    seen.add(key)
    score=int(r.get('data_completeness_score') or 0)
    rows.append({
        'id':r.get('record_id'), 'name':r.get('project_name'), 'lat':float(r['latitude']), 'lng':float(r['longitude']),
        'date':r.get('report_date'), 'datetime_raw':r.get('report_datetime_raw'), 'sender':r.get('sender'),
        'type':r.get('project_type') or 'raw mention', 'status':'raw/review', 'priority':'high' if score>=70 else 'medium' if score>=45 else 'low',
        'score':score, 'popup':r,
        'area':r.get('land_area'), 'price':r.get('asking_price') or r.get('price_mentions'), 'far':r.get('far'), 'population':r.get('population'),
        'irr':r.get('irr'), 'npv':r.get('npv'), 'excerpt':r.get('source_excerpt'), 'map_url':(r.get('map_urls') or '').split(';')[0].strip(),
        'source_file':r.get('source_file'), 'source_chat':r.get('source_chat')
    })
rows.sort(key=lambda x:(-x['score'],x['name']))
(web/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'mapped_popup_records':len(rows),'out':str(web/'projects_data.js')})
