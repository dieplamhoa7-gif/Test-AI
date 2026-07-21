from pathlib import Path
import json,csv,re,collections,unicodedata
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(base/'project_master_curated_deduped.json',encoding='utf-8'))
def c(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def norm(x):return ''.join(ch for ch in unicodedata.normalize('NFD',c(x).lower()) if unicodedata.category(ch)!='Mn').replace('đ','d')
# Count exact coordinate reuse across names.
coord_names=collections.defaultdict(set)
for r in rows:
 if c(r.get('latitude')) and c(r.get('longitude')):coord_names[(c(r['latitude']),c(r['longitude']))].add(norm(r.get('project_name')))
chat_name=re.compile(r'\b(theo link|link bên dưới|file đính kèm|📄\s*file|translate|begin quote|ủa|ok tiến hành|vào list|này đâu có|ở thái à|bên thái)\b',re.I)
subject_variant=re.compile(r'\b(cập nhật|phương án|đề xuất|bổ sung|fs\b|lurf|chi phí liên quan|báo cáo khảo sát|đánh giá pháp lý)\b',re.I)
narrative=re.compile(r'\b(khoảng|cách)\s*\d+(?:[.,]\d+)?\s*(?:m|km)\b|\bii?[/ ]\s*kết nối|^(?:tại|gồm|có|bán|tiếp giáp|được|theo|cần|tuy|này|trong kế hoạch|mình|phân lô|chỉnh trang)\b|\b(?:với tổng diện tích|để phát triển dự án|điều chỉnh chỉ tiêu dân số)\b',re.I)
project_evidence=re.compile(r'\b(dự án|khu đô thị|kđt|khu dân cư|kdc|chung cư|resort|tòa nhà|cao ốc|khu nghỉ dưỡng|quỹ đất|khu đất|lô đất|nhà ở xã hội|noxh)\b',re.I)
strict=[];review=[]
for r in rows:
 reasons=[];name=c(r.get('project_name'));ex=c(r.get('source_excerpt'))
 if not name or len(name)>72:reasons.append('invalid_or_long_name')
 if chat_name.search(name):reasons.append('chat_only_name')
 if narrative.search(name):reasons.append('narrative_name')
 # Report/update subject should have been merged into parent; reject standalone.
 if subject_variant.search(name):reasons.append('message_subject_variant')
 if not project_evidence.search(name+' '+ex[:1800]):reasons.append('insufficient_project_evidence')
 lat,lng=c(r.get('latitude')),c(r.get('longitude'))
 if not(lat and lng):reasons.append('missing_coordinates')
 else:
  try:
   a,b=float(lat),float(lng)
   if not(8<=a<=23.5 and 102<=b<=109.8):reasons.append('coordinate_outside_vietnam')
  except:reasons.append('bad_coordinate')
 q=c(r.get('coordinate_quality'))
 if q in ['suspicious_shared_by_many_projects','needs_coordinate_review']:reasons.append('unreliable_coordinate')
 if lat and lng and len(coord_names[(lat,lng)])>=4:reasons.append('coordinate_shared_by_4plus_names')
 score=int(float(r.get('map_link_match_score') or 100)) if c(r.get('map_link_match_score')) else 100
 if c(r.get('coordinate_source'))=='matched_teams_map_link' and score<35:reasons.append('weak_map_match')
 if reasons:
  rr=dict(r);rr['strict_reject_reasons']='; '.join(sorted(set(reasons)));review.append(rr)
 else:
  rr=dict(r);rr['strict_map_status']='verified_candidate';strict.append(rr)
# Collapse exact normalized duplicate names: retain richest record.
by=collections.defaultdict(list)
for r in strict:by[norm(r.get('project_name'))].append(r)
final=[]
for _,g in by.items():
 g.sort(key=lambda r:(int(r.get('mention_count') or 0),int(r.get('score_total') or 0),len(c(r.get('source_excerpt')))),reverse=True)
 final.append(g[0])
 for x in g[1:]:x['strict_reject_reasons']='duplicate_exact_name';review.append(x)
final.sort(key=lambda r:(-int(r.get('score_total') or 0),r.get('project_name','')))
for fn,data in [('strict_projects_map.json',final),('strict_projects_review_archive.json',review)]:
 (base/fn).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for fn,data in [('strict_projects_map.csv',final),('strict_projects_review_archive.csv',review)]:
 fields=list(data[0]) if data else ['project_name'];
 with open(base/fn,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data)
print({'input':len(rows),'strict_projects_with_map':len(final),'excluded_to_review':len(review),'shared_coordinate_groups':sum(1 for v in coord_names.values() if len(v)>=4)})
