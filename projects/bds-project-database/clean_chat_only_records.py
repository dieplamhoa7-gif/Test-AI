from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=base/'project_master_curated_deduped.json'; rows=json.loads(p.read_text(encoding='utf-8'))
byid={r.get('curated_id'):r for r in rows}
# Verified parent merges: chat/file/link messages are source material, not project entities.
verified_merges={
 'BDS-CURATED-0260':('BDS-CURATED-0037','Green Hill tại Quy Nhơn','Tin nhắn gửi PDF và link hồ sơ Green Hill')
}
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def join(vals):
 out=[]
 for v in vals:
  for x in re.split(r';\s*',c(v)):
   if x and x not in out:out.append(x)
 return '; '.join(out)
removed=set();log=[]
for child_id,(parent_id,parent_name,reason) in verified_merges.items():
 child,parent=byid.get(child_id),byid.get(parent_id)
 if not child or not parent:continue
 removed.add(child_id)
 parent['mention_count']=int(parent.get('mention_count') or 0)+int(child.get('mention_count') or 0)
 for f in ['source_files','senders','map_urls','attachments','source_excerpt','merged_from_ids']:
  parent[f]=join([parent.get(f,''),child.get(f,''),child_id if f=='merged_from_ids' else ''])
 ds=[x for x in [parent.get('first_report_date'),child.get('first_report_date')] if x]
 if ds:parent['first_report_date']=min(ds)
 ds=[x for x in [parent.get('latest_report_date'),child.get('latest_report_date')] if x]
 if ds:parent['latest_report_date']=max(ds)
 log.append({'action':'merge_chat_into_parent','record_id':child_id,'record_name':child.get('project_name'),'parent_id':parent_id,'parent_name':parent_name,'reason':reason})
rows=[r for r in rows if r.get('curated_id') not in removed]
# Conservative candidate queue only; do not auto-delete unless parent is verified.
chat_name_re=re.compile(r'^(theo link bên dưới|chi tiết.*link|gửi.*(?:file|link)|ok|okay|ủa|cảm ơn|thanks|đã nhận|image|translate|edited|có file|file đính kèm)$',re.I)
chat_excerpt_re=re.compile(r'^(?:\[[^]]*\]\s*)?(?:.{0,80}\s)?(?:chi tiết hồ sơ.*link bên dưới|theo link bên dưới|ủa |ok\b|thanks\b)',re.I)
candidates=[]
for r in rows:
 name=c(r.get('project_name')); ex=c(r.get('source_excerpt'))
 score=0; reasons=[]
 if chat_name_re.search(name):score+=5;reasons.append('chat-like name')
 if len(name)<18 and re.search(r'\b(link|file|gửi|theo|ủa|ok)\b',name,re.I):score+=3;reasons.append('short chat phrase')
 if chat_excerpt_re.search(ex):score+=2;reasons.append('chat-like excerpt')
 if not any(c(r.get(k)) for k in ['land_area_main','planning_summary','legal_summary','asking_land_price','selling_price','irr_clean']):score+=2;reasons.append('no project facts')
 if score>=4:candidates.append({'curated_id':r.get('curated_id'),'project_name':name,'score':score,'reasons':'; '.join(reasons),'source_excerpt':ex[:1000]})
# save
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
fields=list(rows[0]);
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
for fn,data,fs in [('chat_only_cleanup_log.csv',log,['action','record_id','record_name','parent_id','parent_name','reason']),('chat_only_review_queue.csv',candidates,['curated_id','project_name','score','reasons','source_excerpt'])]:
 with open(base/fn,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fs,extrasaction='ignore');w.writeheader();w.writerows(data)
print({'before':len(rows)+len(removed),'after':len(rows),'merged_removed':len(removed),'review_candidates':len(candidates)})
