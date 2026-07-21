from pathlib import Path
import json,csv,re
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
review=json.load(open(B/'clean_projects_review_archive.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
# Strong project evidence in raw content regardless of dirty extracted name.
rx=[
 re.compile(r'\b(?:báo cáo|đánh giá|thẩm định|fs|hiệu quả)\s+(?:về\s+)?(?:dự án|DA)\s+([^,:;\n]{3,80})',re.I),
 re.compile(r'\b(?:dự án|project)\s+([A-ZÀ-ỸĐ][^,:;\n]{2,70})',re.I),
 re.compile(r'\b(KĐT|KDC|KCN|NOXH|Chung cư|Resort|Khách sạn|Khu đất|Quỹ đất)\s+([^,:;\n]{2,70})',re.I)
]
out=[]
for r in review:
 ex=c(r.get('source_excerpt')); suggestions=[]
 for pat in rx:
  for m in pat.finditer(ex[:5000]):
   s=c(' '.join(x for x in m.groups() if x))
   s=re.split(r'\s+(?:có|với|quy mô|tại|theo|giá|gồm|được)\b',s,maxsplit=1,flags=re.I)[0].strip(' .-')
   if 3<=len(s)<=80 and s.lower() not in [x.lower() for x in suggestions]:suggestions.append(s)
 if suggestions:
  out.append({'curated_id':r.get('curated_id'),'dirty_name':r.get('project_name'),'suggested_parent_names':'; '.join(suggestions[:5]),'cleaning_notes':r.get('cleaning_notes'),'source_excerpt':ex[:1600]})
with open(B/'false_exclusion_recovery.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=list(out[0]) if out else ['curated_id'];w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(out)
print({'review':len(review),'strong_project_evidence_recoverable':len(out)})
