import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
# load DB json from source artifact
json_path=BASE/'manual_10parts'/'manual_records_merged_reports.json'
db=json.loads(json_path.read_text(encoding='utf-8'))
results=[]
for fp in sorted((BASE/'subagent_jobs').glob('job_*_results.json')):
    results += json.loads(fp.read_text(encoding='utf-8'))
# strict keep: financial or planning numeric facts, avoid headings/file names/generic narrative
keep_re=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|tổng giá trị|chi phí|tiền sử dụng đất|lãi vay|diện tích|mật độ|MĐXD|HSSDĐ|hệ số|dân số|căn|tầng|m2|ha|tr/m2|tỷ)',re.I)
drop_re=re.compile(r'^(\d+[\./]?\s*)?(vị trí|hạ tầng|thông tin|quy hoạch|pháp lý|nguồn|message|translate|edited|by |image|link|https?://)|\.pdf$|\.mp4$|\.xlsx$',re.I)
weak_re=re.compile(r'^(\d+[\./]?\s*)?(hạ tầng giao thông|hạ tầng trọng điểm|tham gia đấu giá|mô tả sơ bộ|k\.đt gửi|p\.đt báo cáo|báo cáo|nguồn từ)',re.I)
merged=0; held=[]; added=[]
# map chunk -> report objects
chunk_reports={}
for g in db['groups']:
    for r in g.get('reports',[]):
        for c in r.get('source_chunks') or []:
            chunk_reports.setdefault(str(c),[]).append((g,r))
        # ensure group financial_items includes report items later rebuilt below
for res in results:
    if res.get('status')!='extracted': continue
    ch=str(res['chunk'])
    targets=chunk_reports.get(ch,[])
    if not targets:
        held.append({**res,'hold_reason':'no linked report'}); continue
    for item in res.get('extracted_items') or []:
        val=(item.get('value') or '').strip()
        if len(val)<15 or not keep_re.search(val) or drop_re.search(val) or weak_re.search(val):
            held.append({'chunk':ch,'project':res.get('project'),'item':item,'hold_reason':'weak_or_generic'}); continue
        # avoid duplicate in target report
        for g,r in targets:
            exists='\n'.join((x.get('label','')+' '+x.get('value','')) for x in (r.get('financial_items') or [])).lower()
            if val.lower() in exists: continue
            new={'label':item.get('label') or 'Bổ sung rà song song','value':val,'source_chunk':ch,'review_status':'parallel_review_accepted'}
            r.setdefault('financial_items',[]).append(new)
            added.append({'master_id':g['master_id'],'project':g['project_name'],'record_id':r.get('record_id'),'item':new})
            merged+=1
# rebuild group financial_items from reports
for g in db['groups']:
    financial=[]
    for idx,r in enumerate(g.get('reports',[]),1):
        for x in r.get('financial_items') or []:
            y=dict(x); y.setdefault('record_id',r.get('record_id')); y.setdefault('report_no',r.get('report_no',idx)); y.setdefault('project_name',r.get('project_name_original') or g['project_name']); y.setdefault('part',r.get('part'))
            financial.append(y)
    g['financial_items']=financial
# update totals
db['totals']['financial_groups']=sum(1 for g in db['groups'] if g.get('financial_items'))
db['totals']['financial_items']=sum(len(g.get('financial_items') or []) for g in db['groups'])
json_path.write_text(json.dumps(db,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'web'/'manual_records_merged_reports.js').write_text('window.MANUAL_MERGED_REPORTS_DB = '+json.dumps(db,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
report=BASE/'reports'/'manual_parallel_merge_review.md'
md=['# Parallel candidate merge review','',f'- Accepted items merged: {len(added)}',f'- Held/rejected candidates: {len(held)}',f"- Financial groups after merge: {db['totals']['financial_groups']}",f"- Financial items after merge: {db['totals']['financial_items']}",'','## Accepted','']
for a in added:
    md.append(f"### {a['project']} · {a['record_id']}")
    md.append(f"- **{a['item']['label']}**: {a['item']['value']} (chunk {a['item']['source_chunk']})")
    md.append('')
md += ['## Held / not merged','']
for h in held[:300]:
    it=h.get('item') or {}
    md.append(f"- Chunk {h.get('chunk')} · {h.get('project')} · {h.get('hold_reason')} · {it.get('value','')}")
report.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'accepted':len(added),'held':len(held),'financial_items':db['totals']['financial_items'],'financial_groups':db['totals']['financial_groups']},ensure_ascii=False))
