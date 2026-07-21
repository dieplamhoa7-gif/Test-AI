from pathlib import Path
import json
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'strict_projects_map.json',encoding='utf-8'))
out=[]
for r in rows:
 try:lat,lng=float(r['latitude']),float(r['longitude'])
 except:continue
 score=int(r.get('score_total') or r.get('data_completeness_score') or 0)
 out.append({'id':r.get('curated_id') or r.get('master_id'),'name':r.get('project_name'),'lat':lat,'lng':lng,'date':r.get('latest_report_date') or r.get('first_report_date'),'datetime_raw':'','sender':r.get('senders',''),'type':r.get('project_type') or 'Dự án/deal','status':'verified-map','priority':'high' if score>=70 else 'medium','score':score,'popup':r,'area':r.get('land_area_main',''),'price':r.get('asking_land_price',''),'far':r.get('far_clean',''),'population':r.get('population_clean',''),'irr':r.get('irr_clean',''),'npv':r.get('npv_clean',''),'excerpt':r.get('source_excerpt',''),'map_url':(r.get('map_urls','').split(';')[0].strip()),'source_file':r.get('source_files',''),'source_chat':'Bee || Phân Tích Đầu Tư'})
(base/'web'/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(out,ensure_ascii=False,indent=2)+';\nwindow.DASHBOARD_MODE = "strict_verified_projects";\n',encoding='utf-8')
(base/'web'/'strict_projects_review_archive.js').write_text('window.STRICT_REVIEW_COUNT = '+str(len(json.load(open(base/'strict_projects_review_archive.json',encoding='utf-8'))))+';\n',encoding='utf-8')
print({'published':len(out),'mode':'strict_verified_projects'})
