from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def area_m2(s):
    m=re.search(r'([\d\.]+)\s*m²',s or '')
    if not m: return None
    try: return float(m.group(1).replace('.',''))
    except: return None
rows=[]
for r in masters:
    issues=[]
    name=clean(r.get('project_name'))
    if len(name)<6 or re.search(r'^(cao tầng$|như sau|này|nguồn|được tính|không đạt|phải nộp|phân lô)',name,re.I): issues.append('bad_name')
    if not r.get('latest_report_date') and not r.get('first_report_date'): issues.append('missing_report_date')
    if not (r.get('latitude') and r.get('longitude')): issues.append('missing_coordinates')
    a=area_m2(r.get('land_area_main') or r.get('land_area'))
    if a is not None and (a<100 or a>5_000_000): issues.append('land_area_outlier')
    if not (r.get('land_area_main') or r.get('land_area')): issues.append('missing_land_area')
    if len(clean(r.get('other_area_mentions')))>120: issues.append('many_other_area_mentions')
    if len(clean(r.get('financial_raw_mentions')))>600 and not (r.get('asking_land_price') or r.get('selling_price') or r.get('irr_clean')): issues.append('financial_not_classified')
    if not (r.get('legal_summary') or r.get('legal_status') or r.get('approval_status') or r.get('lur_status') or r.get('gpm_status')): issues.append('missing_legal')
    if not (r.get('planning_summary') or r.get('far_clean') or r.get('max_floors_clean') or r.get('population_clean') or r.get('planning_doc_status')): issues.append('missing_planning')
    if issues:
        rows.append({'master_id':r.get('master_id'),'project_name':name,'issues':'; '.join(issues),'latest_report_date':r.get('latest_report_date'),'coords':r.get('coordinates'),'land_area_main':r.get('land_area_main') or r.get('land_area'),'sample_excerpt':clean(r.get('source_excerpt'))[:700]})
with open(base/'clean_master_anomaly_report.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()) if rows else ['master_id']); w.writeheader(); w.writerows(rows)
md=['# Clean Master Anomaly Report\n',f'- Total master records: {len(masters)}',f'- Records with issues: {len(rows)}','']
from collections import Counter
cnt=Counter(i for row in rows for i in row['issues'].split('; '))
for k,v in cnt.most_common(): md.append(f'- {k}: {v}')
md.append('\n## Top issue samples\n')
for row in rows[:80]:
    md.append(f"### {row['master_id']} — {row['project_name']}\n- Issues: {row['issues']}\n- Date: {row['latest_report_date']}\n- Coords: {row['coords']}\n- Land area: {row['land_area_main']}\n- Excerpt: {row['sample_excerpt']}\n")
(base/'clean_master_anomaly_report.md').write_text('\n'.join(md),encoding='utf-8')
print({'issues':len(rows),'out':str(base/'clean_master_anomaly_report.csv')})
