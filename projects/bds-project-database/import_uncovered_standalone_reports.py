import json,re,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
MAN=BASE/'manual_10parts'
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
covered=set()
for g in db['groups']:
    for r in g.get('reports') or []:
        for c in (r.get('source_chunks') or [])+(r.get('adjacent_context_chunks') or []): covered.add(str(c))
fin_re=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|\b\d+[,.]?\d*\s*tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất|đền bù|hệ số|HSSD|dân số|mật độ|diện tích)',re.I)
report_re=re.compile(r'(?:K\.?ĐT|P\.?ĐT|Phòng ĐT|Phòng đầu tư|P\. Đầu tư|Em gửi anh|KĐT)\s+(?:xin\s+)?(?:gửi|báo cáo|cập nhật)?[^\n]{0,120}?\b(?:về|dự án)\s+(.{4,160}?)(?:\s+như sau|\s*[:\-]|\n|\.|$)',re.I)
stop_re=re.compile(r'^(các|việc|so sánh|đánh giá|cập nhật|hiệu quả|độ nhạy|bảng|thị trường)\b',re.I)

def compact(s): return re.sub(r'\s+',' ',s or '').strip()
def infer_name(txt):
    t=compact(txt)
    m=report_re.search(t[:900])
    if not m: return ''
    name=m.group(1).strip(' .:-–—')
    name=re.sub(r'^(dự án|DA|khu đất|lô đất)\s+', lambda x:x.group(0), name, flags=re.I)
    # cut common trailing clauses
    name=re.split(r'\s+(?:theo|sau khi|với|tại thời điểm|được tính|đánh giá|của phòng|từ P\.|nguồn|mặt tiền|tọa lạc)\b', name, maxsplit=1, flags=re.I)[0].strip(' ,.-')
    if len(name)<5 or len(name)>110 or stop_re.search(name): return ''
    return name

def part_for_chunk(i): return (i-1)//100+1
added=[]; skipped=[]
by_part={}
for i,ch in enumerate(raw,1):
    if str(i) in covered: continue
    txt=ch.get('text') or ''
    head=compact(txt[:1200])
    if not fin_re.search(head): continue
    if not re.search(r'(báo cáo|gửi anh|cập nhật).*?(dự án|khu đất|lô đất)|dự án .* như sau', head, re.I): continue
    name=infer_name(txt)
    if not name:
        skipped.append(i); continue
    # skip obvious market/news/general notes
    if re.search(r'(thị trường|so sánh thị trường|bản tin|news|tiktok|cafebiz|tuoitre|vnexpress)', name, re.I):
        skipped.append(i); continue
    part=part_for_chunk(i)
    by_part.setdefault(part,[]).append((i,ch,name))

for part,rows in by_part.items():
    fp=MAN/f'part_{part:02d}_manual_records.json'
    if not fp.exists(): continue
    data=json.loads(fp.read_text(encoding='utf-8'))
    existing_ids={r.get('id') for r in data.get('records',[])}
    existing_chunks={str(c) for r in data.get('records',[]) for c in r.get('source_chunks',[])}
    auto_n=1
    while f'M{part:02d}-AUTO{auto_n:03d}' in existing_ids: auto_n+=1
    for i,ch,name in rows:
        if str(i) in existing_chunks: continue
        rid=f'M{part:02d}-AUTO{auto_n:03d}'; auto_n+=1
        txt=compact(ch.get('text') or '')
        rec={
            'id':rid,'source_chunks':[str(i)],'decision':'auto_import_uncovered_standalone_report',
            'project_name':name,'report_date':ch.get('report_date',''),'source_file':ch.get('source_file',f'batch_{i:03d}.txt'),
            'sender':ch.get('sender',''),'location':'','map_url':'','scale':'','legal_planning':'','business_notes':'Auto-imported from uncovered standalone report audit; verify manually.',
            'financial_items':[],'excerpt':txt[:900]
        }
        data.setdefault('records',[]).append(rec); added.append({'part':part,'chunk':i,'id':rid,'project_name':name})
    fp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
report=BASE/'reports'/'manual_uncovered_standalone_import.md'
md=['# Auto-import uncovered standalone reports','',f'- Added records: {len(added)}',f'- Skipped candidates without safe project name: {len(skipped)}','','## Added','']
for a in added:
    md.append(f"- Part {a['part']} · {a['id']} · chunk {a['chunk']} · {a['project_name']}")
report.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'added':len(added),'skipped':len(skipped),'report':str(report)},ensure_ascii=False,indent=2))
