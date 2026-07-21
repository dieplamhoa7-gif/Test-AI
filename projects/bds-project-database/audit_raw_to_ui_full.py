from pathlib import Path
import json,csv,re,unicodedata,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def norm(x):return ''.join(ch for ch in unicodedata.normalize('NFD',c(x).lower()) if unicodedata.category(ch)!='Mn').replace('đ','d')
issues=[]
def add(r,severity,kind,detail):issues.append({'severity':severity,'kind':kind,'curated_id':r.get('curated_id',''),'project_name':r.get('project_name',''),'detail':detail})
msg_words=r'\b(cập nhật|phương án|đề xuất|báo cáo|đánh giá|fs|lur\w*|nghĩa vụ|chi phí liên quan)\b'
for r in rows:
 n=c(r.get('project_name')); low=norm(n)
 if len(n)>90:add(r,'critical','bad_project_name','Tên dài >90 ký tự, có thể là tiêu đề tin nhắn/câu mô tả')
 if re.search(msg_words,n,re.I):add(r,'high','message_subject_variant','Tên chứa từ khóa tiêu đề báo cáo/phương án, cần gom dự án cha')
 if re.search(r'\b(khoảng|cách|gần)\s*\d+(?:[.,]\d+)?\s*(m|km)\b',n,re.I):add(r,'critical','location_reference_as_name','Tên là câu tham chiếu khoảng cách, không phải dự án')
 if not c(r.get('land_area_main')):add(r,'medium','missing_main_area','Thiếu diện tích chính')
 if not c(r.get('planning_summary')):add(r,'medium','missing_planning','Thiếu quy hoạch')
 if not c(r.get('legal_summary')):add(r,'medium','missing_legal','Thiếu pháp lý')
 if not any(c(r.get(k)) for k in ['asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean']):add(r,'medium','missing_financial','Thiếu dữ liệu tài chính')
 if c(r.get('latitude')) and c(r.get('longitude')):
  try:
   lat=float(r['latitude']);lng=float(r['longitude'])
   if not(7<=lat<=24 and 102<=lng<=110):add(r,'critical','coordinate_outside_vietnam','Tọa độ ngoài biên độ Việt Nam')
  except:add(r,'high','bad_coordinate','Không parse được tọa độ')
 if c(r.get('coordinate_quality'))=='suspicious_shared_by_many_projects':add(r,'high','suspicious_shared_coordinate',c(r.get('coordinate_anomaly_note')))
 # likely mixed scenario; do not auto-assert but flag review
 blob=' '.join(c(r.get(k)) for k in ['planning_summary','other_area_mentions','population_clean','max_floors_clean'])
 areas=len(set(re.findall(r'\b\d+(?:[.,]\d+)?\s*(?:ha|m2|m²)\b',blob,re.I)))
 if areas>=4 and not c(r.get('scenario_data')):add(r,'high','multi_scenario_unstructured',f'Có {areas} quy mô/diện tích khác nhau nhưng chưa có scenario_data')
# duplicate normalized names
by=collections.defaultdict(list)
for r in rows:by[norm(r.get('project_name'))].append(r)
for k,g in by.items():
 if k and len(g)>1:
  for r in g:add(r,'high','duplicate_exact_name','Trùng tên với: '+'; '.join(x.get('curated_id','') for x in g if x is not r))
issues.sort(key=lambda x:({'critical':0,'high':1,'medium':2}.get(x['severity'],3),x['project_name']))
with open(base/'full_raw_to_ui_audit.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['severity','kind','curated_id','project_name','detail']);w.writeheader();w.writerows(issues)
cnt=collections.Counter((x['severity'],x['kind']) for x in issues)
md=['# Full raw → curated → UI audit','',f'- Curated records audited: **{len(rows)}**',f'- Issues: **{len(issues)}**','', '## Summary']
for (sev,k),v in cnt.items():md.append(f'- {sev.upper()} | {k}: **{v}**')
md+=['','## Critical / High review queue','']
for x in [z for z in issues if z['severity'] in ['critical','high']][:200]:md.append(f"- **{x['severity'].upper()}** `{x['curated_id']}` — {x['project_name']}: {x['kind']} — {x['detail']}")
(base/'full_raw_to_ui_audit.md').write_text('\n'.join(md),encoding='utf-8')
print({'records':len(rows),'issues':len(issues),'by_severity':collections.Counter(x['severity'] for x in issues),'out':'full_raw_to_ui_audit.md'})
