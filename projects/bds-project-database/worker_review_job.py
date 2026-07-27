import json,re,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
job_id=int(sys.argv[1])
job_md=(BASE/'subagent_jobs'/f'job_{job_id:02d}.md').read_text(encoding='utf-8',errors='ignore')
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
chunk_to_reports={}
for g in db['groups']:
    for r in g.get('reports',[]):
        for c in r.get('source_chunks') or []:
            chunk_to_reports.setdefault(int(c),[]).append((g,r))
chunks=[int(x) for x in re.findall(r'### Chunk (\d+)', job_md)]
keys=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất|m2|ha|căn|tầng)',re.I)
img=re.compile(r'\bimage\b|hình ảnh|hinh anh|ảnh|attachment|đính kèm|dinh kem|pdf|xlsx|mp4',re.I)
def candidates(txt, existing):
    exist=' '.join(x.get('value','') for x in existing).lower(); out=[]
    for line in [re.sub(r'\s+',' ',x).strip(' -•\t') for x in txt.splitlines()]:
        if len(line)<18 or len(line)>320 or not re.search(r'\d',line): continue
        if not keys.search(line): continue
        if line.lower() in exist: continue
        if re.match(r'^(by |message by|translate|edited|image by)',line,re.I): continue
        lab='Bổ sung từ rà job'
        if re.search(r'IRR|NPV|LNTT|LNST|hiệu quả|khả thi',line,re.I): lab='Hiệu quả bổ sung'
        elif re.search(r'giá|tr/m2|triệu/m2',line,re.I): lab='Giá/đơn giá bổ sung'
        elif re.search(r'chi phí|vốn|lãi|TMĐT|TMDT|tiền sử dụng đất',line,re.I): lab='Chi phí/vốn bổ sung'
        elif re.search(r'ha|m2|căn|tầng',line,re.I): lab='Quy mô/thông số bổ sung'
        out.append({'label':lab,'value':line,'source_chunk':str(chno)})
        if len(out)>=8: break
    return out
res=[]
for chno in chunks:
    txt=(raw[chno-1].get('text') or '') if 0<chno<=len(raw) else ''
    reps=chunk_to_reports.get(chno,[])
    existing=[x for _,r in reps for x in (r.get('financial_items') or [])]
    cand=candidates(txt, existing)
    has_attach=bool(img.search(txt))
    status='extracted' if cand else ('attachment_missing' if has_attach else 'already_ok' if existing else 'not_financial')
    res.append({'chunk':chno,'project':' | '.join(dict.fromkeys(g['project_name'] for g,_ in reps)),'status':status,'extracted_items':cand,'notes':('attachment/pdf/image marker present' if has_attach else '')})
(BASE/'subagent_jobs'/f'job_{job_id:02d}_results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(job_id,len(res),sum(1 for r in res if r['status']=='extracted'))
