import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
chunk_to_reports={}
for g in db['groups']:
    for r in g.get('reports',[]):
        for c in r.get('source_chunks') or []:
            chunk_to_reports.setdefault(str(c),[]).append((g,r))
fin_re=re.compile(r'\b(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá đất|giá đấu|max|tỷ|tr/m2|triệu|chi phí|vốn|lãi vay|hiệu quả|khả thi)\b',re.I)
image_re=re.compile(r'\bimage\b|hình ảnh|hinh anh|ảnh|anh dinh kem|đính kèm|dinh kem',re.I)
rows=[]
for i,ch in enumerate(raw,1):
    txt=ch.get('text') or ''
    has_img=bool(image_re.search(txt)); has_fin=bool(fin_re.search(txt)); reps=chunk_to_reports.get(str(i),[])
    fin_items=sum(len(r.get('financial_items') or []) for _,r in reps)
    if (has_img or has_fin) and reps:
        rows.append({'chunk':i,'date':ch.get('report_date',''),'sender':ch.get('sender',''),'has_image_marker':has_img,'has_fin_text':has_fin,'linked_reports':len(reps),'financial_items':fin_items,'projects':' | '.join(dict.fromkeys(g['project_name'] for g,_ in reps))[:240],'snippet':re.sub(r'\s+',' ',txt[:360])})
# priority: has image/fin but few extracted items
priority=[r for r in rows if (r['has_image_marker'] or r['has_fin_text']) and r['financial_items']<3]
out=BASE/'reports'/'manual_10parts_image_finance_audit.md'
out.parent.mkdir(exist_ok=True)
md=['# Audit 10 part - image/financial extraction','',f'- Raw chunks scanned: {len(raw)}',f'- Linked chunks with image/finance markers: {len(rows)}',f'- Priority review (marker nhưng <3 chỉ tiêu tài chính): {len(priority)}','','## Priority review','']
for r in priority[:120]:
    md.append(f"### Chunk {r['chunk']} · {r['date']} · {r['sender']}")
    md.append(f"- Image marker: {r['has_image_marker']} · Fin text: {r['has_fin_text']} · extracted financial items: {r['financial_items']} · linked reports: {r['linked_reports']}")
    md.append(f"- Projects: {r['projects']}")
    md.append(f"- Snippet: {r['snippet']}")
    md.append('')
md += ['## All linked image/finance chunks (CSV-ish)','', '| chunk | image | fin_text | fin_items | projects |', '|---:|:---:|:---:|---:|---|']
for r in rows:
    md.append(f"| {r['chunk']} | {r['has_image_marker']} | {r['has_fin_text']} | {r['financial_items']} | {r['projects'].replace('|','/')} |")
out.write_text('\n'.join(md),encoding='utf-8')
print(out)
print('rows',len(rows),'priority',len(priority))
