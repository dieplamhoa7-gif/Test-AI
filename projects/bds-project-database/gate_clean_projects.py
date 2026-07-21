from pathlib import Path
import json,csv,re,collections
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(B/'clean_projects_database.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
bad_start=re.compile(r'^(?:có|được|bán|tiếp giáp|cần|tuy|mình|ở\b|trong kế hoạch|phân lô|chỉnh trang|điều chỉnh|theo sổ|gồm|tại\s+\d+|chung cư trên|vào phòng|dân số|quy hoạch)\b',re.I)
bad_phrase=re.compile(r'\b(?:với tổng diện tích đất|để thực hiện dự án là|theo phương pháp thặng dư|có thể theo \d+ hướng|begin quote|by unknown user)\b',re.I)
issues=[]
for r in rows:
 n=c(r.get('project_name'))
 if bad_start.search(n) or bad_phrase.search(n) or len(n)>75:
  issues.append({'curated_id':r.get('curated_id'),'project_name':n,'issue':'likely_sentence_name','source_excerpt':c(r.get('source_excerpt'))[:1200]})
with open(B/'clean_publish_name_gate.csv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(issues[0]) if issues else ['curated_id']);w.writeheader();w.writerows(issues)
print({'publish_candidates':len(rows),'bad_name_gate':len(issues),'good_name_gate':len(rows)-len(issues)})
