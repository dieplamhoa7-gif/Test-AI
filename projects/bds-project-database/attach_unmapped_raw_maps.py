from pathlib import Path
import json,csv,re
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=B/'project_master_curated_deduped.json';rows=json.load(open(p,encoding='utf-8'))
audit={x['curated_id']:x for x in csv.DictReader(open(B/'unmapped_projects_audit.csv',encoding='utf-8-sig'))}
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
changed=[]
for r in rows:
 a=audit.get(r.get('curated_id'))
 if not a or a['category']!='has_unresolved_or_unattached_map_link':continue
 links=[x.strip() for x in a['map_urls_found'].split(';') if x.strip()]
 existing=[x.strip() for x in c(r.get('map_urls')).split(';') if x.strip()]
 out=[]
 for x in existing+links:
  if x not in out:out.append(x)
 if out and '; '.join(out)!=c(r.get('map_urls')):
  r['map_urls']='; '.join(out);r['map_link_attached_from_chunk']='raw_name_token_match';r['map_link_match_score']='name_token_overlap>=2';changed.append({'curated_id':r.get('curated_id'),'project_name':r.get('project_name'),'links_added':'; '.join(links)})
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(B/'unmapped_raw_map_attach_log.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(changed[0]) if changed else ['curated_id']);w.writeheader();w.writerows(changed)
print({'attached':len(changed)})
