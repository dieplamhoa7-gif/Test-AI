import json,re,sys,unicodedata
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
fin_re=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|\b\d+[,.]?\d*\s*tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất)',re.I)
plan_re=re.compile(r'(MĐXD|mật độ|HSSDĐ|hệ số|tầng|dân số|quy hoạch|1/500|1/2000|diện tích|m2|ha|GFA|thương phẩm)',re.I)
legal_re=re.compile(r'(pháp lý|GCN|QSDĐ|chủ trương|quyết định|giao đất|đất ở|CLN|SKC|GPMB|bồi thường|nghĩa vụ tài chính|Nghị quyết 171)',re.I)
attach_re=re.compile(r'(\bimage\b|hình ảnh|hinh anh|ảnh|has attachment|has attachments|đính kèm|dinh kem|\.pdf|\.xlsx|\.png|\.jpg|\.mp4)',re.I)

def raw_text(chunks):
    out=[]
    for c in chunks or []:
        try: i=int(c)-1
        except Exception: continue
        if 0<=i<len(raw): out.append(raw[i].get('text') or '')
    return '\n'.join(out)
issues=[]; stats={'reports':0,'raw_fin':0,'raw_plan':0,'raw_legal':0,'raw_attach':0,'missing_fin':0,'missing_plan':0,'missing_legal':0,'short_excerpt':0,'attach_marker':0}
for g in db['groups']:
    for r in g.get('reports') or []:
        stats['reports']+=1
        txt=raw_text(r.get('source_chunks'))
        full=r.get('full_excerpt') or ''
        has_fin=bool(fin_re.search(txt))
        # Avoid false positives where only legal phrase 'nghĩa vụ tài chính' appears without actual amount/FS metric.
        if has_fin and not re.search(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|\b\d+[,.]?\d*\s*tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất)', txt, re.I):
            has_fin=False
        has_plan=bool(plan_re.search(txt)); has_legal=bool(legal_re.search(txt)); has_attach=bool(attach_re.search(txt))
        stats['raw_fin']+=has_fin; stats['raw_plan']+=has_plan; stats['raw_legal']+=has_legal; stats['raw_attach']+=has_attach
        problem=[]
        if has_fin and not (r.get('financial_items') or []): problem.append('missing_financial_items'); stats['missing_fin']+=1
        if has_plan and len((r.get('scale') or '').strip())<20: problem.append('planning_summary_thin'); stats['missing_plan']+=1
        if has_legal and len((r.get('legal_planning') or '').strip())<20: problem.append('legal_summary_thin'); stats['missing_legal']+=1
        if len(full)<max(200, min(len(txt)*0.5, 800)): problem.append('full_excerpt_short_vs_raw'); stats['short_excerpt']+=1
        if has_attach: stats['attach_marker']+=1
        if problem:
            issues.append({'master_id':g['master_id'],'project':g['project_name'],'record_id':r.get('record_id'),'report_no':r.get('report_no'),'chunks':r.get('source_chunks'),'issues':problem,'fin_items':len(r.get('financial_items') or []),'scale_len':len(r.get('scale') or ''),'legal_len':len(r.get('legal_planning') or ''),'full_excerpt_len':len(full),'raw_len':len(txt),'snippet':re.sub(r'\s+',' ',txt[:450])})
# write report
out=BASE/'reports'/'manual_information_coverage_audit.md'
md=['# Manual database information coverage audit','', '## Stats','']
for k,v in stats.items(): md.append(f'- {k}: {v}')
md += ['', f'- total issues: {len(issues)}', '', '## Issue list', '']
for it in issues[:300]:
    md.append(f"### {it['master_id']} · {it['project']} · BC {it['report_no']} · {it['record_id']}")
    md.append(f"- Issues: {', '.join(it['issues'])}")
    md.append(f"- Chunks: {it['chunks']} · fin_items {it['fin_items']} · scale_len {it['scale_len']} · legal_len {it['legal_len']} · full/raw {it['full_excerpt_len']}/{it['raw_len']}")
    md.append(f"- Snippet: {it['snippet']}")
    md.append('')
out.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'stats':stats,'issues':len(issues),'report':str(out)},ensure_ascii=False,indent=2))
