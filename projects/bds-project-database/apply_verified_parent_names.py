from pathlib import Path
import json,csv
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=B/'project_master_curated_deduped.json';rows=json.load(open(p,encoding='utf-8'))
# Manually verified from report-opening text. Names describe a deal/site when no formal project name exists.
verified={
'BDS-CURATED-0033':'Quỹ đất 2.316 ha phía Nam Nhơn Trạch',
'BDS-CURATED-0030':'Khu đất 2,6 ha mặt tiền Song Hành XLHN, Thủ Đức',
'BDS-CURATED-0112':'Dự án Vương Bảo Long',
'BDS-CURATED-0029':'Khu đất 197 Lê Văn Sỹ',
'BDS-CURATED-0141':'Khu đất 1,6 ha Phan Văn Hớn, Quận 12',
'BDS-CURATED-0107':'Khu đất Ngô Chí Quốc, Bình Chiểu, Thủ Đức',
'BDS-CURATED-0043':'Khu đất mặt tiền Ngô Chí Quốc gần Phú Quang',
'BDS-CURATED-0156':'Khu đất 10.052,1 m² tại 1691/3N',
'BDS-CURATED-0117':'Quỹ đất Tân Hiệp, Long Thành, Đồng Nai',
'BDS-CURATED-0084':'Khách sạn 5 sao 12 Hùng Vương, Đà Lạt',
'BDS-CURATED-0282':'Võ Văn Kiệt – Gộp 2 lô',
'BDS-CURATED-0181':'Khu đất đấu thầu Nhơn Trạch, Đồng Nai'
}
log=[]
for r in rows:
 i=r.get('curated_id')
 if i in verified:
  old=r.get('project_name');r['project_name']=verified[i];r['project_name_raw']=old;r['clean_key']=verified[i].lower();r['parent_name_source']='verified_from_report_opening'
  log.append({'curated_id':i,'old_name':old,'clean_parent_name':verified[i]})
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with open(B/'verified_parent_name_log.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['curated_id','old_name','clean_parent_name']);w.writeheader();w.writerows(log)
print({'verified_renamed':len(log)})
