from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
fields=['curated_id','master_id','merged_from_ids','project_name','mention_count','first_report_date','latest_report_date','source_files','senders','latitude','longitude','coordinates','coordinate_quality','coordinate_anomaly_note','map_urls','location','province_city','district_area','land_area_main','land_area_main_raw','other_area_mentions','project_type','product_structure','land_type','planning_doc_status','planning_summary','max_floors_clean','far_clean','density_clean','population_clean','legal_summary','legal_status','gpm_status','lur_status','approval_status','asking_land_price','selling_price','land_cost','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean','payback_clean','financial_raw_mentions','risks','next_actions','attachments','data_completeness_score','score_total','score_grade','score_location','score_data','score_planning','score_legal','score_financial','score_risk_penalty','score_notes','source_excerpt']
out=[]
for r in rows:
    row={f:clean(r.get(f,'')) for f in fields}
    row['record_id']=row['curated_id'] or row['master_id']
    row['report_date']=row['latest_report_date'] or row['first_report_date']
    row['has_coordinates']='yes' if row['latitude'] and row['longitude'] else 'no'
    row['has_area']='yes' if row['land_area_main'] else 'no'
    row['has_financial']='yes' if any(row.get(f) for f in ['asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean']) else 'no'
    row['has_planning']='yes' if any(row.get(f) for f in ['planning_doc_status','planning_summary','max_floors_clean','far_clean','population_clean']) else 'no'
    row['has_legal']='yes' if any(row.get(f) for f in ['legal_summary','legal_status','gpm_status','lur_status','approval_status']) else 'no'
    out.append(row)
out.sort(key=lambda r:(r['has_coordinates']!='yes',-(int(r.get('score_total') or r.get('data_completeness_score') or 0)),r['project_name']))
out_fields=['record_id','curated_id','master_id','merged_from_ids','project_name','report_date','has_coordinates','has_area','has_financial','has_planning','has_legal']+fields[4:]
with open(base/'full_project_database_curated.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=out_fields,extrasaction='ignore'); w.writeheader(); w.writerows(out)
(base/'full_project_database_curated.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'web'/'full_project_database.js').write_text('window.FULL_PROJECTS = '+json.dumps(out,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
# map subset
mapped=[]
for r in out:
    if not(r['latitude'] and r['longitude']): continue
    try: lat=float(r['latitude']); lng=float(r['longitude'])
    except: continue
    suspicious=r.get('coordinate_quality')=='suspicious_shared_by_many_projects'
    score=int(r.get('score_total') or r.get('data_completeness_score') or 0)
    mapped.append({'id':r['record_id'],'name':r['project_name'],'lat':lat,'lng':lng,'date':r['report_date'],'datetime_raw':'','sender':r['senders'],'type':r['project_type'] or 'curated','status':'coord-review' if suspicious else 'curated/review','priority':'low' if suspicious else ('high' if score>=70 else 'medium' if score>=45 else 'low'),'score':min(score,44) if suspicious else score,'popup':r,'area':r['land_area_main'],'price':r['asking_land_price'] or r['financial_raw_mentions'],'far':r['far_clean'],'population':r['population_clean'],'irr':r['irr_clean'],'npv':r['npv_clean'],'excerpt':r['source_excerpt'],'map_url':(r['map_urls'] or '').split(';')[0].strip(),'source_file':r['source_files'],'source_chat':'Bee || Phân Tích Đầu Tư'})
mapped.sort(key=lambda x:(-x['score'],x['name']))
(base/'web'/'projects_data.js').write_text('window.PROJECTS = '+json.dumps(mapped,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'curated_full':len(out),'mapped':len(mapped),'out':str(base/'full_project_database_curated.csv')})
