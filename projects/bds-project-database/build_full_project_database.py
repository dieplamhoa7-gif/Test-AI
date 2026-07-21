from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
fields=[
 'master_id','project_name','mention_count','first_report_date','latest_report_date','source_files','senders',
 'latitude','longitude','coordinates','coordinate_quality','coordinate_anomaly_note','map_urls','location','province_city','district_area',
 'land_area_main','land_area_main_raw','other_area_mentions','project_type','land_type',
 'planning_doc_status','planning_summary','max_floors_clean','far_clean','density_clean','population_clean',
 'legal_summary','legal_status','gpm_status','lur_status','approval_status',
 'asking_land_price','selling_price','land_cost','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean','payback_clean','financial_raw_mentions',
 'risks','next_actions','attachments','data_completeness_score','source_excerpt'
]
rows=[]
for r in masters:
    row={f:clean(r.get(f,'')) for f in fields}
    row['has_coordinates']='yes' if row['latitude'] and row['longitude'] else 'no'
    row['report_date']=row['latest_report_date'] or row['first_report_date']
    # simple completeness flags for UI/filtering
    row['has_area']='yes' if row['land_area_main'] else 'no'
    row['has_financial']='yes' if any(row.get(f) for f in ['asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean']) else 'no'
    row['has_planning']='yes' if any(row.get(f) for f in ['planning_doc_status','planning_summary','max_floors_clean','far_clean','population_clean']) else 'no'
    row['has_legal']='yes' if any(row.get(f) for f in ['legal_summary','legal_status','gpm_status','lur_status','approval_status']) else 'no'
    rows.append(row)
# Stable useful order
rows.sort(key=lambda r:(r['has_coordinates']!='yes', -(int(r.get('data_completeness_score') or 0)), r['project_name']))
out_fields=['master_id','project_name','report_date','has_coordinates','has_area','has_financial','has_planning','has_legal']+fields[2:]
with open(base/'full_project_database.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=out_fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
(base/'full_project_database.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
# JS for dashboard full table
(base/'web'/'full_project_database.js').write_text('window.FULL_PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print({'full_projects':len(rows),'with_coords':sum(1 for r in rows if r['has_coordinates']=='yes'),'out':str(base/'full_project_database.csv')})
