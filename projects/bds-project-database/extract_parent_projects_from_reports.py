from pathlib import Path
import json,csv,re,collections
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
review=json.load(open(B/'clean_projects_review_archive.json',encoding='utf-8'))
def clean(x):return re.sub(r'\s+',' ',str(x or '')).strip(' .:-–—')
def valid(s):
 if not(3<=len(s)<=80):return False
 if re.search(r'^(?:1?\.?\d+\s*(?:ha|m2|m²)|khu đất này|dự án này|như sau|về việc|theo phương án|được|có|tại)\b',s,re.I):return False
 if re.search(r'\b(?:giá|quy hoạch|pháp lý|đất|tổng mức|hiệu quả|chi phí)\s*$',s,re.I):return False
 return True
patterns=[
 # Strongest: explicit report + project name, ending at a factual clause.
 (10,re.compile(r'(?:kđt|p\.đt|phòng đầu tư|đầu tư)\s+(?:gửi|báo cáo)\b.{0,90}?\b(?:về|đánh giá|cập nhật|nghiên cứu|thẩm định)\s+(?:dự án\s+)?([^\n:;]{3,100})',re.I)),
 (9,re.compile(r'\bbáo cáo\b.{0,80}?\b(?:dự án|da)\s+([^\n:;]{3,100})',re.I)),
 (8,re.compile(r'\b(?:đánh giá|hiệu quả|fs)\s+(?:dự án\s+)?([^\n:;]{3,100})',re.I)),
 (7,re.compile(r'\b(?:dự án|project)\s+([A-ZÀ-ỸĐ][^\n:;]{3,100})',re.I)),
]
def trim(s):
 s=clean(s)
 # drop common factual tails, preserving address only when it is part of title.
 s=re.split(r'\s+(?=có\s+(?:quy mô|giá|diện tích)|với\s+(?:quy mô|tổng)|tại thời điểm|,?\s*cụ thể|,?\s*như sau|\.|\(|-\s*(?:pháp lý|quy hoạch|giá))',s,maxsplit=1,flags=re.I)[0]
 return clean(s)
rows=[]
for r in review:
 ex=str(r.get('source_excerpt','')).replace('\r',' ')
 found=[]
 for score,pat in patterns:
  for m in pat.finditer(ex[:7000]):
   s=trim(m.group(1))
   if valid(s) and s.lower() not in [x['name'].lower() for x in found]:found.append({'name':s,'confidence':score,'pattern':pat.pattern[:42]})
 if found:
  found.sort(key=lambda x:(-x['confidence'],len(x['name'])))
  top=found[0]
  rows.append({'curated_id':r.get('curated_id'),'current_dirty_name':r.get('project_name'),'extracted_parent_name':top['name'],'confidence':top['confidence'],'alternatives':' | '.join(x['name'] for x in found[1:4]),'cleaning_notes':r.get('cleaning_notes'),'source_excerpt':clean(ex)[:1600]})
with open(B/'report_parent_extraction_review.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=list(rows[0]) if rows else ['curated_id'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rows)
print({'archive_records':len(review),'extracted_parent_candidates':len(rows),'high_confidence':sum(int(x['confidence'])>=9 for x in rows)})
