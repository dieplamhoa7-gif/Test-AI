from pathlib import Path
import json,csv
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
allrows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))
queue={r['curated_id']:r for r in csv.DictReader(open(base/'project_recovery_queue.csv',encoding='utf-8-sig'))}
rows=[r for r in allrows if queue.get(r.get('curated_id'),{}).get('status')=='recover_project']
full=[];mapped=[]
for r in rows:
 rr=dict(r);q=queue[r['curated_id']]
 rr['record_id']=r.get('curated_id') or r.get('master_id');rr['report_date']=r.get('latest_report_date') or r.get('first_report_date')
 rr['has_coordinates']=q['has_map'];rr['has_area']='yes' if r.get('land_area_main') else 'no';rr['has_planning']='yes' if r.get('planning_summary') else 'no';rr['has_legal']='yes' if r.get('legal_summary') else 'no';rr['has_financial']='yes' if any(r.get(x) for x in ['asking_land_price','selling_price','irr_clean','npv_clean','profit_clean']) else 'no'
 full.append(rr)
 if q['has_map']=='yes':
  try:lat,lng=float(r['latitude']),float(r['longitude'])
  except:continue
  score=int(r.get('score_total') or r.get('data_completeness_score') or 0)
  mapped.append({'id':rr['record_id'],'name':r['project_name'],'lat':lat,'lng':lng,'date':rr['report_date'],'datetime_raw':'','sender':r.get('senders',''),'type':r.get('project_type') or 'Dự án/deal','status':'recovered-project','priority':'high' if score>=70 else 'medium' if score>=45 else 'low','score':score,'popup':rr,'area':r.get('land_area_main',''),'price':r.get('asking_land_price',''),'far':r.get('far_clean',''),'population':r.get('population_clean',''),'irr':r.get('irr_clean',''),'npv':r.get('npv_clean',''),'excerpt':r.get('source_excerpt',''),'map_url':r.get('map_urls','').split(';')[0].strip(),'source_file':r.get('source_files',''),'source_chat':'Bee || Phân Tích Đầu Tư'})
full.sort(key=lambda r:(r['has_coordinates']!='yes',-int(r.get('score_total') or 0),r.get('project_name','')));mapped.sort(key=lambda r:(-r['score'],r['name']))
(base/'recovered_projects_database.json').write_text(json.dumps(full,ensure_ascii=False,indent=2),encoding='utf-8')
with open(base/'recovered_projects_database.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(full[0]),extrasaction='ignore');w.writeheader();w.writerows(full)
(base/'web'/'full_project_database.js').write_text('window.FULL_PROJECTS = '+json.dumps(full,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(base/'web'/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(mapped,ensure_ascii=False,indent=2)+';\nwindow.DASHBOARD_MODE = "recovered_projects";\n',encoding='utf-8')
print({'full_projects':len(full),'mapped':len(mapped),'without_map':len(full)-len(mapped)})
