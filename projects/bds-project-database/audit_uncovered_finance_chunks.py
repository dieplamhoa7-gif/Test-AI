import json,re,sys,unicodedata
from pathlib import Path
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
raw=json.loads((BASE/'teams_candidate_chunks_with_dates.json').read_text(encoding='utf-8'))
db=json.loads((BASE/'web/manual_records_merged_reports.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
fin_re=re.compile(r'(IRR|NPV|LNTT|LNST|TMĐT|TMDT|doanh thu|giá bán|giá chào|giá đất|giá đấu|max|\b\d+[,.]?\d*\s*tỷ|tr/m2|triệu/m2|chi phí|vốn|lãi vay|hiệu quả|khả thi|tổng mức đầu tư|tiền sử dụng đất|đền bù|hệ số|HSSD|dân số|mật độ|diện tích thương phẩm)',re.I)
weak_only=re.compile(r'(nghĩa vụ tài chính|nghìn tỷ|quan trọng là giá đấu thầu|sẽ tính|tính fs thử)$',re.I)
intro_re=re.compile(r'(K\.?ĐT|P\.?ĐT|Phòng ĐT|báo cáo|dự án|quỹ đất|khu đất|resort|khách sạn|KCN|CCN|chung cư|cao tầng)',re.I)

def compact(s): return re.sub(r'\s+',' ',s or '').strip()
def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(w for w in s.split() if len(w)>2)
def dt_key(ch):
    rawdt=(ch.get('report_datetime_raw') or ch.get('report_date') or '').strip()
    for fmt in ('%m/%d/%Y %I:%M %p','%m/%d/%y %I:%M %p','%m/%d %I:%M %p','%Y-%m-%d'):
        try:
            dt=datetime.strptime(rawdt,fmt)
            if fmt.startswith('%m/%d ') and dt.year==1900: dt=dt.replace(year=2026)
            return dt
        except Exception: pass
    return None
covered=set(); report_refs=[]
for g in db['groups']:
    for r in g.get('reports') or []:
        ids=[str(x) for x in (r.get('source_chunks') or [])]+[str(x) for x in (r.get('adjacent_context_chunks') or [])]
        for c in ids:
            covered.add(c); report_refs.append((int(c),g['project_name'],r['record_id'],r.get('report_no'),dt_key(raw[int(c)-1]) if c.isdigit() and 1<=int(c)<=len(raw) else None))
project_terms=[]
for g in db['groups']:
    toks=set(norm(g['project_name']).split())-set('du an khu dat bao cao cap nhat phuong quan thanh pho tinh huyen cong ty can ho chung cu khach san'.split())
    if toks: project_terms.append((g['project_name'],toks))
rows=[]
for idx,ch in enumerate(raw,1):
    if str(idx) in covered: continue
    txt=compact(ch.get('text') or '')
    if len(txt)<30 or not fin_re.search(txt): continue
    if weak_only.search(txt.lower()): continue
    has_num=bool(re.search(r'\d',txt))
    if not has_num: continue
    # classify standalone report vs orphan reply
    head=txt[:280]
    is_report=bool(intro_re.search(head) and re.search(r'(như sau|về dự án|về khu đất|báo cáo anh|báo cáo sếp|gửi anh)',head,re.I))
    rtoks=set(norm(txt[:700]).split())
    name_hits=[name for name,toks in project_terms if len(toks & rtoks)>=2][:6]
    # nearest covered report in time/index
    nearest=[]
    d0=dt_key(ch)
    for ci,pj,rid,rno,dt in report_refs:
        score=abs(ci-idx)
        if score<=8:
            if d0 and dt: mins=abs((d0-dt).total_seconds())/60
            else: mins=None
            nearest.append((score,mins,pj,rid,rno,ci))
    nearest=sorted(nearest,key=lambda x:(x[0], x[1] if x[1] is not None else 9999))[:5]
    rows.append({'chunk':idx,'date':ch.get('report_datetime_raw') or ch.get('report_date'),'sender':ch.get('sender'),'is_report':is_report,'project_hits':name_hits,'nearest':nearest,'snippet':txt[:650]})
out=BASE/'reports'/'manual_uncovered_finance_chunks.md'
md=['# Uncovered finance/planning chunks audit','',f'- Raw chunks scanned: {len(raw)}',f'- Covered by source/adjacent context: {len(covered)}',f'- Uncovered finance/planning candidates: {len(rows)}','','## Candidates','']
for x in rows[:300]:
    md.append(f"### chunk {x['chunk']} · {x['date']} · {x['sender']}")
    md.append(f"- standalone_report_like: {x['is_report']}")
    md.append(f"- project_hits: {', '.join(x['project_hits']) if x['project_hits'] else '-'}")
    if x['nearest']:
        md.append('- nearest covered: '+ '; '.join(f"±{a} idx/{'' if b is None else round(b,1)}m → {pj} {rid} BC{rno} chunk{ci}" for a,b,pj,rid,rno,ci in x['nearest']))
    md.append(f"- snippet: {x['snippet']}")
    md.append('')
out.write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'raw_chunks':len(raw),'covered':len(covered),'uncovered_candidates':len(rows),'report':str(out)},ensure_ascii=False,indent=2))
