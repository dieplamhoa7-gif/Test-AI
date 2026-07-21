from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
p=base/'project_master_curated_deduped.json'
rows=json.loads(p.read_text(encoding='utf-8'))
# These are narrative/location-reference patterns, not a valid project/deal title.
reference_patterns=[
 r'\bkhoảng\s*\d+(?:[.,]\d+)?\s*(?:m|km)\b', r'\bcách\s+(?:dự án\s+)?',
 r'^tại\s+\d+', r'^gồm\s+', r'^chung cư\s+(?:cao|tại)', r'^cao tầng\s+\d+',
 r'\bii?\/\s*kết nối giao thông', r'\bquy hoạch phân khu\b.*\bcập nhật',
 r'^phú quang\s+khoảng', r'^khu đất\s+.*\b(?:gần|cách)\s+phú quang'
]
land_patterns=[r'^khu đất\b',r'^lô đất\b',r'^quỹ đất\b',r'\bgom đất\b',r'\bthu gom\b']
for r in rows:
    name=' '.join(str(r.get('project_name','')).split())
    low=name.lower()
    excerpt=str(r.get('source_excerpt','')).lower()
    is_ref=any(re.search(x,low,re.I) for x in reference_patterns)
    # Sentence-like names are invalid even if no explicit phrase.
    if len(name)>95 or (len(name)>55 and re.search(r'\b(?:và|đến|tại|có|thuộc|theo)\b',low)): is_ref=True
    if is_ref:
        kind='reference_or_narrative'; reason='Tên lấy từ câu mô tả vị trí/nội dung, không phải tên dự án'; valid='no'
    elif any(re.search(x,low,re.I) for x in land_patterns):
        kind='land_opportunity'; reason='Khu đất/quỹ đất cơ hội, chưa khẳng định tên dự án'; valid='yes'
    else:
        kind='project_or_deal'; reason='Tên dự án/deal có thể hiển thị'; valid='yes'
    r['entity_type']=kind; r['entity_valid_for_project_map']=valid; r['entity_classification_note']=reason
# output same master + audit
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
fields=list(rows[0])
with open(base/'project_master_curated_deduped.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
audit=[r for r in rows if r['entity_valid_for_project_map']=='no']
with open(base/'entity_classification_review.csv','w',encoding='utf-8-sig',newline='') as f:
 fs=['curated_id','project_name','entity_type','entity_valid_for_project_map','entity_classification_note','source_excerpt'];w=csv.DictWriter(f,fieldnames=fs,extrasaction='ignore');w.writeheader();w.writerows(audit)
print({'total':len(rows),'project_or_deal':sum(r['entity_type']=='project_or_deal' for r in rows),'land_opportunity':sum(r['entity_type']=='land_opportunity' for r in rows),'excluded_reference':len(audit)})
