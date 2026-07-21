from pathlib import Path
import json,csv,re,unicodedata,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def norm(x):return ''.join(ch for ch in unicodedata.normalize('NFD',c(x).lower()) if unicodedata.category(ch)!='Mn').replace('đ','d')
# Broad evidence: accept named projects/deals, but reject obvious chat sentence names.
chat=re.compile(r'^(?:có|được|theo|tại|gồm|bán|cần|này|mình|ủa|ok|vào|trong|tuy|phân lô|tiếp giáp|chỉnh trang|ở thái|thông qua)\b|\b(?:link bên dưới|begin quote|📄\s*file)\b',re.I)
project_token=re.compile(r'\b(?:dự án|kđt|kdc|kcn|khu đô thị|khu dân cư|chung cư|resort|hotel|tower|garden|city|urban|beach|villa|living|homes?|plaza|land|riverside|gateway|diamond|holiday|hermes|felicia|felix|phú quang|đông trung|green hill)\b',re.I)
rows_out=[]
for r in rows:
 name=c(r.get('project_name')); ex=c(r.get('source_excerpt'))
 reasons=[]
 if not name or len(name)>95:reasons.append('bad_name_length')
 if chat.search(name):reasons.append('chat_sentence_name')
 evidence=bool(project_token.search(name)) or bool(re.search(r'\b(?:báo cáo|đánh giá|fs|hiệu quả)\s+(?:dự án\s+)?'+re.escape(name[:35]),ex,re.I))
 if not evidence:reasons.append('needs_parent_name_extraction')
 map_ok=bool(c(r.get('latitude')) and c(r.get('longitude'))) and c(r.get('coordinate_quality')) not in ['suspicious_shared_by_many_projects','needs_coordinate_review']
 status='recover_project' if not reasons else 'needs_name_or_parent_review'
 rows_out.append({'curated_id':r.get('curated_id'),'project_name':name,'status':status,'has_map':'yes' if map_ok else 'no','issues':'; '.join(reasons),'mention_count':r.get('mention_count'),'first_report_date':r.get('first_report_date'),'latest_report_date':r.get('latest_report_date'),'source_excerpt':ex[:1400]})
with open(base/'project_recovery_queue.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=list(rows_out[0]);w=csv.DictWriter(f,fieldnames=fs);w.writeheader();w.writerows(rows_out)
print(collections.Counter((r['status'],r['has_map']) for r in rows_out))
