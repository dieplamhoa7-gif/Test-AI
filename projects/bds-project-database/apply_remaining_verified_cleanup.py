from pathlib import Path
import json,csv,re
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database');p=B/'project_master_curated_deduped.json';rows=json.load(open(p,encoding='utf-8'));by={r.get('curated_id'):r for r in rows}
rename={
'BDS-CURATED-0019':'Dự án 1,2 ha đường Thuận An Hóa, Thuận An',
'BDS-CURATED-0147':'Khu chung cư và văn phòng An Phú',
'BDS-CURATED-0097':'Khu du lịch TMDV Quất Lâm 7 ha và CCN Giao Tiến 50 ha',
'BDS-CURATED-0257':'Khu đất Phú Thọ Hòa, Tân Phú',
'BDS-CURATED-0108':'Dự án Suối Nhum',
'BDS-CURATED-0190':'Khách sạn 25 Trần Phú, Đà Lạt',
'BDS-CURATED-0433':'KDC Đồi An Tôn',
'BDS-CURATED-0195':'The Sang Residence',
'BDS-CURATED-0194':'SwanBay 456 ha',
'BDS-CURATED-0148':'Lô đất mặt tiền Quốc lộ 13, Hiệp Bình Phước',
'BDS-CURATED-0193':'Regalia Gold Nha Trang',
'BDS-CURATED-0388':'Khu đất 02 Tây Thạnh',
'BDS-CURATED-0270':'Khu đất đấu thầu 386 ha Nhơn Trạch',
'BDS-CURATED-0429':'Khu đất đấu thầu 386 ha Nhơn Trạch – cập nhật',
}
# Child -> parent project name
merges={'BDS-CURATED-0167':'the Bale tại Phan Thiết','BDS-CURATED-0281':'the Bale tại Phan Thiết','BDS-CURATED-0304':'the Bale tại Phan Thiết','BDS-CURATED-0433':'KDC An Tôn theo 02 phương án quy hoạch','BDS-CURATED-0280':'Phượng Hoàng','BDS-CURATED-0279':'Phượng Hoàng','BDS-CURATED-0429':'Khu đất đấu thầu 386 ha Nhơn Trạch'}
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def join(a,b):
 out=[]
 for v in [a,b]:
  for x in re.split(r';\s*',c(v)):
   if x and x not in out:out.append(x)
 return '; '.join(out)
log=[]
for i,n in rename.items():
 if i in by:
  old=by[i].get('project_name');by[i]['project_name']=n;by[i]['project_name_raw']=old;by[i]['parent_name_source']='verified_manual_raw_review';log.append({'action':'rename','id':i,'from':old,'to':n})
byname={c(r.get('project_name')):r for r in rows};removed=set()
for cid,pname in merges.items():
 child=by.get(cid);parent=byname.get(pname)
 if not child or not parent or child is parent:continue
 for f in ['source_files','senders','attachments','source_excerpt','planning_summary','legal_summary','financial_raw_mentions','risks','next_actions','merged_from_ids']:
  parent[f]=join(parent.get(f,''),child.get(f,''))
 parent['merged_from_ids']=join(parent.get('merged_from_ids',''),cid);parent['mention_count']=int(parent.get('mention_count') or 0)+int(child.get('mention_count') or 0)
 removed.add(cid);log.append({'action':'merge','id':cid,'from':child.get('project_name'),'to':pname})
rows=[r for r in rows if r.get('curated_id') not in removed];p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(B/'remaining_verified_cleanup_log.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['action','id','from','to']);w.writeheader();w.writerows(log)
print({'renamed':sum(x['action']=='rename' for x in log),'merged':sum(x['action']=='merge' for x in log),'remaining':len(rows)})
