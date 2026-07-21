from pathlib import Path
import json,re,csv
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(B/'published_clean_projects.json',encoding='utf-8'))
js=(B/'web'/'field_config.js').read_text(encoding='utf-8')
mapped=set(re.findall(r"\['[^']+',\s*'([^']+)'\]",js))
# Operational/internal fields intentionally not displayed as business facts.
ignore={'record_id','master_id','curated_id','clean_key','project_name_raw','data_completeness_score','score_total','score_grade','score_location','score_data','score_planning','score_legal','score_financial','score_risk_penalty','score_notes','has_map','has_area','has_planning','has_legal','has_financial','cleaning_status','cleaning_notes','record_classification','source_lineage','report_date','latitude','longitude','map_link_match_score','map_link_attached_from_chunk','coordinate_source','coordinate_quality','coordinate_anomaly_note','parent_name_source'}
issues=[]
keys=set().union(*(r.keys() for r in rows))
for k in sorted(keys):
 count=sum(bool(str(r.get(k,'')).strip()) for r in rows)
 if count and k not in mapped and k not in ignore:
  issues.append({'field':k,'nonempty_records':count,'issue':'data_field_not_mapped_to_detail_table'})
# duplicate mappings / group listing
seen={};dups=[]
for m in re.finditer(r"\['([^']+)',\s*'([^']+)'\]",js):
 label,key=m.groups()
 if key in seen:dups.append({'field':key,'label':label,'issue':'field_mapped_more_than_once'})
 seen[key]=label
issues+=dups
with open(B/'web_field_mapping_audit.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=['field','nonempty_records','issue','label'];w=csv.DictWriter(f,fieldnames=fs,extrasaction='ignore');w.writeheader();w.writerows(issues)
print({'published_fields':len(keys),'mapped_fields':len(mapped),'unmapped_nonempty':len([x for x in issues if x['issue'].startswith('data_field')]),'duplicate_mapping':len(dups)})
