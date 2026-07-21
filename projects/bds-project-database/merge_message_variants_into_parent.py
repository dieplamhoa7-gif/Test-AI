from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=base/'project_master_curated_deduped.json'
rows=json.loads(p.read_text(encoding='utf-8'))
# Explicit parent aliases: these are report/message subjects, not separate projects.
merge_rules={
 'Phú Quang':['Phú Quang – Phương án bổ sung tiền sử dụng đất (LURF) và chi phí liên quan đến phần đất công trong dự án','Phú Quang cập nhật']
}
def clean(v):return re.sub(r'\s+',' ',str(v or '')).strip()
def join(vals):
 out=[]
 for v in vals:
  for x in re.split(r';\s*',clean(v)):
   if x and x not in out:out.append(x)
 return '; '.join(out)
byname={clean(r.get('project_name')):r for r in rows}
removed=set(); log=[]
for parent_name,aliases in merge_rules.items():
 parent=byname.get(parent_name)
 if not parent:continue
 children=[byname[a] for a in aliases if a in byname]
 for c in children:
  removed.add(c['curated_id'])
  parent['mention_count']=int(parent.get('mention_count') or 0)+int(c.get('mention_count') or 0)
  dates=[x for x in [parent.get('first_report_date'),c.get('first_report_date')] if x]
  if dates:parent['first_report_date']=min(dates)
  dates=[x for x in [parent.get('latest_report_date'),c.get('latest_report_date')] if x]
  if dates:parent['latest_report_date']=max(dates)
  for f in ['source_files','senders','map_urls','planning_summary','legal_summary','legal_status','gpm_status','lur_status','approval_status','asking_land_price','selling_price','land_cost','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean','payback_clean','financial_raw_mentions','risks','next_actions','attachments','source_excerpt','merged_from_ids']:
   parent[f]=join([parent.get(f,''),c.get(f,'')])
  log.append({'parent':parent_name,'merged_message_subject':c.get('project_name'),'merged_id':c.get('curated_id')})
rows=[r for r in rows if r.get('curated_id') not in removed]
# Keep IDs stable; mark classification.
for r in rows:
 r['entity_type']='project_or_deal'
 r['entity_classification_note']=''
 if r.get('project_name') in merge_rules:r['entity_classification_note']='Đã gom các tin cập nhật/phương án vào dự án cha'
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
fields=list(rows[0])
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
with open(base/'message_subject_merge_log.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=['parent','merged_message_subject','merged_id'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(log)
print({'before':len(rows)+len(removed),'after':len(rows),'merged':log})
