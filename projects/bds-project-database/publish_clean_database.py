from pathlib import Path
import json,csv
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
allrows=json.load(open(B/'clean_projects_database.json',encoding='utf-8'))
bad={r['curated_id'] for r in csv.DictReader(open(B/'clean_publish_name_gate.csv',encoding='utf-8-sig'))}
rows=[r for r in allrows if r.get('curated_id') not in bad]
for r in rows:
 r['record_id']=r.get('curated_id') or r.get('master_id');r['report_date']=r.get('latest_report_date') or r.get('first_report_date') or ''
rows.sort(key=lambda r:(r.get('has_map')!='yes',-int(r.get('score_total') or 0),r.get('project_name','')))
mapped=[]
for r in rows:
 if r.get('has_map')!='yes':continue
 try:lat,lng=float(r['latitude']),float(r['longitude'])
 except:continue
 score=int(r.get('score_total') or r.get('data_completeness_score') or 0)
 mapped.append({'id':r['record_id'],'name':r['project_name'],'lat':lat,'lng':lng,'date':r['report_date'],'datetime_raw':'','sender':r.get('senders',''),'type':r.get('project_type') or 'Dự án/deal','status':'clean-project','priority':'high' if score>=70 else 'medium' if score>=45 else 'low','score':score,'popup':r,'area':r.get('land_area_main',''),'price':r.get('asking_land_price',''),'far':r.get('far_clean',''),'population':r.get('population_clean',''),'irr':r.get('irr_clean',''),'npv':r.get('npv_clean',''),'excerpt':r.get('source_excerpt',''),'map_url':r.get('map_urls','').split(';')[0].strip(),'source_file':r.get('source_files',''),'source_chat':'Bee || Phân Tích Đầu Tư'})
for fn,data in [('published_clean_projects.json',rows),('published_clean_projects.csv',rows)]:
 if fn.endswith('.json'):(B/fn).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 else:
  with open(B/fn,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction='ignore');w.writeheader();w.writerows(data)
(B/'web'/'full_project_database.js').write_text('window.FULL_PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(B/'web'/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(mapped,ensure_ascii=False,indent=2)+';\nwindow.DASHBOARD_MODE = "clean_projects_database";\n',encoding='utf-8')
print({'published_projects':len(rows),'mapped':len(mapped),'without_map':len(rows)-len(mapped)})
