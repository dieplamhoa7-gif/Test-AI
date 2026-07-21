from pathlib import Path
import json,csv,re,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
dup_groups=list(csv.DictReader(open(base/'duplicate_project_groups_conservative.csv',encoding='utf-8-sig',newline='')))
by_id={r['master_id']:r for r in masters}

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def uniq_join(vals,limit=1800):
    out=[]
    for v in vals:
        for p in re.split(r';\s*',clean(v)):
            p=p.strip(' -;,.')
            if p and p not in out: out.append(p)
    return '; '.join(out)[:limit]
def choose_name(items):
    names=[clean(r.get('project_name')) for r in items if clean(r.get('project_name')) and not re.search(r'^(này|như|không|có|được|phải|với|theo)',clean(r.get('project_name')),re.I)]
    if not names: return clean(items[0].get('project_name'))
    return sorted(set(names),key=lambda x:(len(x)>90,len(x)))[0]
def choose_coord(items):
    # Prefer non-suspicious coordinate. If multiple non-suspicious coords conflict, keep blank and flag review.
    coords=[]
    for r in items:
        if r.get('latitude') and r.get('longitude') and r.get('coordinate_quality')!='suspicious_shared_by_many_projects':
            key=(r['latitude'],r['longitude'],r.get('coordinates',''),r.get('coordinate_quality',''))
            if key not in coords: coords.append(key)
    if len(coords)==1: return coords[0],''
    if len(coords)>1: return ('','','',''), 'multiple_conflicting_coordinates'
    return ('','','',''), 'no_reliable_coordinate'
# Only merge duplicate groups with same/alias name. Exclude groups where all records are suspicious coords and names not exact enough.
merged_ids=set(); curated=[]; merge_log=[]
for g in dup_groups:
    ids=[x.strip() for x in g.get('ids','').split(';') if x.strip() and x.strip() in by_id]
    items=[by_id[i] for i in ids if i not in merged_ids]
    if len(items)<2: continue
    # Skip if names are too broad/noisy
    if len(g.get('group_key',''))<5: continue
    base_rec=dict(items[0])
    base_rec['master_id']=''
    base_rec['project_name']=choose_name(items)
    base_rec['merged_from_ids']='; '.join(r.get('master_id','') for r in items)
    base_rec['mention_count']=sum(int(r.get('mention_count') or 0) for r in items)
    dates=[d for r in items for d in [r.get('first_report_date'),r.get('latest_report_date')] if d]
    if dates:
        base_rec['first_report_date']=min(dates); base_rec['latest_report_date']=max(dates)
    for f in ['source_files','senders','map_urls','location','province_city','district_area','land_area_main','land_area_main_raw','other_area_mentions','project_type','land_type','planning_doc_status','planning_summary','max_floors_clean','far_clean','density_clean','population_clean','legal_summary','legal_status','gpm_status','lur_status','approval_status','asking_land_price','selling_price','land_cost','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean','payback_clean','financial_raw_mentions','risks','next_actions','attachments']:
        base_rec[f]=uniq_join([r.get(f,'') for r in items])
    snippets=[]
    for r in sorted(items,key=lambda x:x.get('latest_report_date') or x.get('first_report_date') or '',reverse=True)[:5]:
        ex=clean(r.get('source_excerpt'))[:1200]
        if ex: snippets.append(f"[{r.get('latest_report_date') or r.get('first_report_date') or ''} | {r.get('master_id')}] {ex}")
    base_rec['source_excerpt']='\n\n---\n\n'.join(snippets)
    coord,coord_issue=choose_coord(items)
    lat,lng,coordstr,cq=coord
    base_rec['latitude']=lat; base_rec['longitude']=lng; base_rec['coordinates']=coordstr or (f'{lat}, {lng}' if lat and lng else '')
    base_rec['coordinate_quality']=cq or base_rec.get('coordinate_quality','')
    if coord_issue:
        base_rec['coordinate_anomaly_note']=coord_issue + '; merged duplicate group needs coordinate review'
    # recompute rough score
    keys=['project_name','latest_report_date','map_urls','coordinates','land_area_main','planning_summary','legal_summary','asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean','risks']
    base_rec['data_completeness_score']=round(sum(1 for k in keys if clean(base_rec.get(k,'')))/len(keys)*100)
    curated.append(base_rec)
    for r in items: merged_ids.add(r['master_id'])
    merge_log.append({'curated_temp_name':base_rec['project_name'],'merged_from_ids':base_rec['merged_from_ids'],'count':len(items),'coord_issue':coord_issue})
# Add unmerged records
for r in masters:
    if r.get('master_id') not in merged_ids:
        rr=dict(r); rr['merged_from_ids']=''; curated.append(rr)
curated.sort(key=lambda r:(not bool(r.get('latitude') and r.get('longitude')),-int(r.get('data_completeness_score') or 0),r.get('project_name','')))
for i,r in enumerate(curated,1): r['curated_id']=f'BDS-CURATED-{i:04d}'
fields=list(curated[0].keys()) if curated else []
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(curated)
(base/'project_master_curated_deduped.json').write_text(json.dumps(curated,ensure_ascii=False,indent=2),encoding='utf-8')
with open(base/'dedupe_merge_log.csv','w',encoding='utf-8-sig',newline='') as fp:
    fs=list(merge_log[0].keys()) if merge_log else ['curated_temp_name']; w=csv.DictWriter(fp,fieldnames=fs); w.writeheader(); w.writerows(merge_log)
print({'input':len(masters),'curated':len(curated),'merged_groups':len(merge_log),'merged_records':len(merged_ids),'out':str(base/'project_master_curated_deduped.csv')})
