from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def has(r,*fields): return any(clean(r.get(f,'')) for f in fields)
def risk_penalty(r):
    txt=' '.join(clean(r.get(f,'')) for f in ['risks','legal_summary','source_excerpt']).lower()
    p=0
    for term,pts in [('không đạt',12),('rủi ro',8),('chậm',5),('chưa',4),('vướng',5),('cần làm rõ',5),('đấu giá',3),('thu hồi',8),('pháp lý chưa',8)]:
        if term in txt: p+=pts
    if r.get('coordinate_quality')=='suspicious_shared_by_many_projects': p+=15
    return min(p,35)
for r in rows:
    location=0
    if has(r,'latitude','longitude'): location+=20
    if has(r,'map_urls'): location+=8
    if has(r,'location','province_city','district_area'): location+=7
    if r.get('coordinate_quality')=='suspicious_shared_by_many_projects': location=max(0,location-18)
    location=min(location,35)
    data=0
    if has(r,'latest_report_date','first_report_date'): data+=7
    if has(r,'land_area_main'): data+=8
    if int(r.get('mention_count') or 0)>=2: data+=5
    if has(r,'source_excerpt'): data+=5
    data=min(data,25)
    planning=0
    if has(r,'planning_doc_status'): planning+=7
    if has(r,'far_clean'): planning+=6
    if has(r,'max_floors_clean'): planning+=4
    if has(r,'population_clean'): planning+=4
    if has(r,'density_clean'): planning+=2
    planning=min(planning,23)
    legal=0
    if has(r,'legal_summary','legal_status'): legal+=8
    if has(r,'approval_status'): legal+=6
    if has(r,'lur_status'): legal+=5
    if has(r,'gpm_status'): legal+=4
    legal=min(legal,23)
    financial=0
    if has(r,'asking_land_price'): financial+=6
    if has(r,'selling_price'): financial+=5
    if has(r,'total_investment_clean'): financial+=5
    if has(r,'revenue_clean'): financial+=4
    if has(r,'profit_clean'): financial+=4
    if has(r,'irr_clean'): financial+=5
    if has(r,'npv_clean'): financial+=4
    financial=min(financial,28)
    penalty=risk_penalty(r)
    raw=location*0.22 + data*0.15 + planning*0.18 + legal*0.2 + financial*0.2 - penalty*0.15
    total=max(0,min(100,round(raw*4)))  # calibrated to 0-100
    r['score_total']=total
    r['score_location']=location
    r['score_data']=data
    r['score_planning']=planning
    r['score_legal']=legal
    r['score_financial']=financial
    r['score_risk_penalty']=penalty
    if total>=75: grade='A'
    elif total>=60: grade='B'
    elif total>=45: grade='C'
    elif total>=30: grade='D'
    else: grade='E'
    r['score_grade']=grade
    notes=[]
    if not has(r,'latitude','longitude'): notes.append('Thiếu tọa độ')
    if r.get('coordinate_quality')=='suspicious_shared_by_many_projects': notes.append('Tọa độ nghi ngờ')
    if not has(r,'land_area_main'): notes.append('Thiếu diện tích đất')
    if not has(r,'legal_summary','legal_status','approval_status','lur_status'): notes.append('Thiếu pháp lý')
    if not has(r,'planning_doc_status','far_clean','max_floors_clean','population_clean'): notes.append('Thiếu quy hoạch')
    if not has(r,'asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean'): notes.append('Thiếu tài chính')
    r['score_notes']='; '.join(notes)
rows.sort(key=lambda r:(-int(r.get('score_total') or 0),r.get('project_name','')))
fields=list(rows[0].keys()) if rows else []
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
(base/'project_master_curated_deduped.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print({'scored':len(rows),'A':sum(1 for r in rows if r.get('score_grade')=='A'),'B':sum(1 for r in rows if r.get('score_grade')=='B'),'C':sum(1 for r in rows if r.get('score_grade')=='C')})
