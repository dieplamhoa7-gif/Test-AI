from pathlib import Path
import json,csv,re
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=B/'project_master_curated_deduped.json'; rows=json.load(open(p,encoding='utf-8'));by={r.get('curated_id'):r for r in rows}
# Directly named in raw report opening. These are project/deal/site records, not chat subjects.
rename={
'BDS-CURATED-0010':'Khu đất 1,7 ha đường Hoàng Quốc Việt, Hạ Long',
'BDS-CURATED-0040':'Dự án 2,3 ha Bình Điền, Bình Chánh',
'BDS-CURATED-0089':'KDC Tam Phước 4,9 ha, Biên Hòa',
'BDS-CURATED-0096':'Dự án Victory Hoàn Cầu, Bình Chuẩn, Thuận An',
'BDS-CURATED-0105':'KCN Nghĩa Sơn, Nghĩa Hưng, Nam Định',
'BDS-CURATED-0046':'Khu đất 2.769 m² Hoàng Sa, Đà Nẵng',
'BDS-CURATED-0120':'12 lô đất Sun Group – KĐT ven sông Hòa Xuân, Đà Nẵng',
'BDS-CURATED-0155':'KCN Liễu Sơn – Thái Hòa 1, Vĩnh Phúc',
'BDS-CURATED-0154':'Dự án 1,2 ha đường Thuận An Hòa, An Phú',
'BDS-CURATED-0200':'Cảng tổng hợp và container Cái Mép Hạ',
'BDS-CURATED-0217':'Dự án phân lô Long Phước (ViệtNhân1234 / Blue Diamond Riverside)',
'BDS-CURATED-0338':'Phú Gia Khiêm – phương án giá vốn 900 tỷ',
'BDS-CURATED-0345':'Phú Gia Khiêm – cập nhật 02 phương án',
'BDS-CURATED-0350':'Phú Quang – cập nhật FS NOTM thay thế NOXH',
'BDS-CURATED-0103':'Hội An Riverside Resort & Spa – cập nhật FS Concept Lamanon',
'BDS-CURATED-0069':'Dự án 2,3 ha Bình Điền, Bình Chánh – cập nhật pháp lý/FS',
'BDS-CURATED-0146':'Holiday Beach Đà Nẵng – phương án vận hành tạm thời'
}
# These named update reports must merge into the existing parent rather than become a second project.
merge={
 'BDS-CURATED-0338':'Phú Gia Khiêm','BDS-CURATED-0345':'Phú Gia Khiêm','BDS-CURATED-0350':'Phú Quang','BDS-CURATED-0103':'Hội An Riverside Resort & Spa','BDS-CURATED-0069':'Dự án 2,3 ha Bình Điền, Bình Chánh','BDS-CURATED-0146':'Holiday Beach'
}
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def join(vals):
 out=[]
 for v in vals:
  for x in re.split(r';\s*',c(v)):
   if x and x not in out:out.append(x)
 return '; '.join(out)
# rename direct items first
log=[]
for i,name in rename.items():
 r=by.get(i)
 if r:
  old=r.get('project_name');r['project_name']=name;r['project_name_raw']=old;r['parent_name_source']='verified_raw_report_opening_batch';log.append({'action':'rename','id':i,'old':old,'new_or_parent':name})
# Rebuild names, merge update children into explicit parent.
byname={c(r.get('project_name')):r for r in rows}; removed=set()
for childid,parentname in merge.items():
 child=by.get(childid);parent=byname.get(parentname)
 if not child or not parent or child is parent:continue
 for f in ['source_files','senders','map_urls','attachments','source_excerpt','planning_summary','legal_summary','financial_raw_mentions','risks','next_actions','merged_from_ids']:
  parent[f]=join([parent.get(f,''),child.get(f,''),childid if f=='merged_from_ids' else ''])
 parent['mention_count']=int(parent.get('mention_count') or 0)+int(child.get('mention_count') or 0)
 for fld,fn in [('first_report_date',min),('latest_report_date',max)]:
  ds=[x for x in [parent.get(fld),child.get(fld)] if x]
  if ds:parent[fld]=fn(ds)
 removed.add(childid);log.append({'action':'merge_update_into_parent','id':childid,'old':child.get('project_name'),'new_or_parent':parentname})
rows=[r for r in rows if r.get('curated_id') not in removed]
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(B/'report_opening_batch_cleanup_log.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['action','id','old','new_or_parent']);w.writeheader();w.writerows(log)
print({'renamed':sum(x['action']=='rename' for x in log),'merged':sum(x['action'].startswith('merge') for x in log),'remaining':len(rows)})
