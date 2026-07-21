"""Build a conservative, traceable clean project database from curated Teams records.
Records that are messages, attachments, report subjects, or narrative snippets are held in review,
not published as projects. All data fields preserve raw evidence and source lineage.
"""
from pathlib import Path
import json,csv,re,unicodedata,collections
B=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=json.load(open(B/'project_master_curated_deduped.json',encoding='utf-8'))
def clean(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def norm(x):return ''.join(c for c in unicodedata.normalize('NFD',clean(x).lower()) if unicodedata.category(c)!='Mn').replace('đ','d')
def yes(r,*ks):return any(clean(r.get(k)) for k in ks)
# Reject only unambiguous non-project subjects. Ambiguous records are retained as opportunities, never silently deleted.
chat_start=re.compile(r'^(?:theo|gửi|chi tiết|file|📄|image|translate|begin quote|ok\b|ủa\b|cảm ơn|này đâu|vào list|ở thái|bên thái)\b',re.I)
narrative_start=re.compile(r'^(?:có|được|bán|tiếp giáp|cần|tuy|mình|trong kế hoạch|phân lô|chỉnh trang|điều chỉnh chỉ tiêu|theo sổ)\b',re.I)
message_subject=re.compile(r'\b(?:cập nhật|phương án|đề xuất|bổ sung|fs\b|lurf|chi phí liên quan|báo cáo khảo sát|đánh giá pháp lý)\b',re.I)
project_signals=re.compile(r'\b(?:dự án|kđt|kdc|kcn|khu đô thị|khu dân cư|chung cư|resort|hotel|tower|garden|city|urban|beach|villa|living|homes?|plaza|riverside|gateway|diamond|holiday|hermes|felicia|green hill|phú quang|đông trung)\b',re.I)
cleaned=[];review=[]
for r in rows:
    name=clean(r.get('project_name')); ex=clean(r.get('source_excerpt'))
    reasons=[]
    if not name or len(name)>95: reasons.append('name_missing_or_sentence')
    if chat_start.search(name): reasons.append('chat_or_attachment_subject')
    if narrative_start.search(name): reasons.append('narrative_sentence_name')
    if message_subject.search(name): reasons.append('report_or_scenario_subject')
    explicit=bool(project_signals.search(name)) or bool(re.search(r'(?:dự án|project)\s+'+re.escape(name[:35]),ex,re.I))
    # Named standalone sites/address projects are retained if they have strong factual fields.
    factual=sum(yes(r,k) for k in ['land_area_main','planning_summary','legal_summary','asking_land_price','selling_price','irr_clean','attachments'])
    if not explicit and factual<3: reasons.append('insufficient_project_evidence')
    rec=dict(r)
    rec['record_classification']='project_or_deal' if not reasons else 'review_not_published'
    rec['cleaning_status']='published_candidate' if not reasons else 'held_for_review'
    rec['cleaning_notes']='; '.join(reasons)
    rec['source_lineage']=clean('; '.join([r.get('curated_id',''),r.get('source_files',''),r.get('merged_from_ids','')]))
    # Form fields needed by database/UI
    rec['report_date']=r.get('latest_report_date') or r.get('first_report_date') or ''
    rec['has_map']='yes' if yes(r,'latitude','longitude') and r.get('coordinate_quality') not in ['suspicious_shared_by_many_projects','needs_coordinate_review'] else 'no'
    rec['has_area']='yes' if yes(r,'land_area_main') else 'no'
    rec['has_planning']='yes' if yes(r,'planning_summary','planning_doc_status','far_clean') else 'no'
    rec['has_legal']='yes' if yes(r,'legal_summary','legal_status','approval_status') else 'no'
    rec['has_financial']='yes' if yes(r,'asking_land_price','selling_price','total_investment_clean','revenue_clean','profit_clean','irr_clean','npv_clean') else 'no'
    (cleaned if not reasons else review).append(rec)
# exact-name dedupe: preserve richest project, hold duplicate as merged-review source
by=collections.defaultdict(list)
for r in cleaned:by[norm(r['project_name'])].append(r)
final=[]
for _,g in by.items():
    g.sort(key=lambda r:(int(r.get('mention_count') or 0),sum(r[x]=='yes' for x in ['has_map','has_area','has_planning','has_legal','has_financial']),len(clean(r.get('source_excerpt')))),reverse=True)
    final.append(g[0])
    for extra in g[1:]:
        extra['record_classification']='duplicate_project_review';extra['cleaning_status']='held_for_review';extra['cleaning_notes']='duplicate exact name with '+g[0].get('curated_id','');review.append(extra)
final.sort(key=lambda r:(r['has_map']!='yes',r['project_name'].lower()))
fields=list(final[0]) if final else list(rows[0])
for fn,data in [('clean_projects_database.json',final),('clean_projects_review_archive.json',review)]: (B/fn).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
for fn,data in [('clean_projects_database.csv',final),('clean_projects_review_archive.csv',review)]:
    with open(B/fn,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(data)
summary={'input_curated':len(rows),'published_projects':len(final),'review_archive':len(review),'with_reliable_map':sum(x['has_map']=='yes' for x in final),'without_map':sum(x['has_map']!='yes' for x in final)}
(B/'clean_database_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(summary)
