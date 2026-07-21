from pathlib import Path
import re, json, hashlib, csv
from datetime import datetime
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
bdir=base/'teams_batches'
files=sorted(bdir.glob('batch_*.txt'))
PROJECT_RE=re.compile(r'(dự án|DA\b|BĐS|FS\b|ha\b|m2|m²|tỷ|giá|quy hoạch|pháp lý|LNTT|IRR|NPV|Maps|maps\.app|google\.com|khu đất|quỹ đất|cao tầng|resort|khách sạn|khu công nghiệp)',re.I)
DATE_HEADING_RE=re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$',re.M)
TS_RE=re.compile(r'(?P<sender>[^\n]{2,80})\n(?P<ts>\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)')
TS_SHORT_RE=re.compile(r'(?P<sender>[^\n]{2,80})\n(?P<ts>\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}\s+[AP]M)')
MONTHS={m:i for i,m in enumerate('January February March April May June July August September October November December'.split(),1)}

def norm(s): return re.sub(r'\s+',' ',s or '').strip()
def parse_ts(raw, current_year=None):
    if not raw: return ('','')
    for fmt in ['%m/%d/%Y %I:%M %p','%d/%m/%Y %I:%M %p']:
        try:
            dt=datetime.strptime(raw,fmt)
            return (dt.date().isoformat(), raw)
        except ValueError: pass
    if current_year and re.match(r'\d{1,2}/\d{1,2}\s+', raw):
        for fmt in ['%m/%d/%Y %I:%M %p','%d/%m/%Y %I:%M %p']:
            try:
                dt=datetime.strptime(raw.replace(' ',f'/{current_year} ',1),fmt)
                return (dt.date().isoformat(), raw)
            except ValueError: pass
    return ('', raw)

def first_date_heading(text):
    m=DATE_HEADING_RE.search(text)
    if not m: return ('','')
    _, mon, day, year=m.groups(); mi=MONTHS.get(mon)
    if not mi: return ('',m.group(0))
    return (f'{int(year):04d}-{mi:02d}-{int(day):02d}',m.group(0))

def extract_meta(text):
    # prefer full timestamp; infer report date from first timestamp. Keep raw.
    m=TS_RE.search(text)
    if m:
        d,raw=parse_ts(m.group('ts'))
        return {'sender':norm(m.group('sender')).replace(' | ',' '),'report_date':d,'report_datetime_raw':raw}
    hd, hd_raw=first_date_heading(text)
    m=TS_SHORT_RE.search(text)
    if m and hd:
        year=hd[:4]
        d,raw=parse_ts(m.group('ts'), current_year=year)
        return {'sender':norm(m.group('sender')).replace(' | ',' '),'report_date':d or hd,'report_datetime_raw':raw}
    return {'sender':'','report_date':hd,'report_datetime_raw':hd_raw}

seen=set(); chunks=[]
for f in files:
    txt=f.read_text(encoding='utf-8',errors='ignore')
    if len(norm(txt))<500: continue
    # Split at weekday headings and likely message starts. broad context retained.
    parts=re.split(r'(?=\n(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), |\n[^\n]{2,80}\n\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M|\n(?:P\.ĐT|Phòng|Báo cáo|Dạ|Admin 01|Hanh T|Khoa L|Dung N|Huy M|Tai L|Thao L|Tèo|Sinh Nguyen|Trieu Nguyen)\b)', txt)
    for p in parts:
        p=p.strip()
        if len(p)<140 or not PROJECT_RE.search(p): continue
        key=hashlib.sha1(norm(p[:2500]).encode('utf-8','ignore')).hexdigest()
        if key in seen: continue
        seen.add(key)
        meta=extract_meta(p)
        chunks.append({'source_file':f.name,**meta,'text':p})
# near dup by normalized prefix + date
out=[]; starts=set()
for c in chunks:
    st=(c.get('report_date',''), norm(c['text'][:700]).lower())
    if st in starts: continue
    starts.add(st); out.append(c)
(base/'teams_candidate_chunks_with_dates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Candidate BĐS chunks with report dates from Teams scroll\n']
for i,c in enumerate(out,1):
    md.append(f'\n## Chunk {i} — {c["source_file"]} — {c.get("report_date","")} — {c.get("report_datetime_raw","")} — {c.get("sender","")}\n\n```text\n{c["text"][:7000]}\n```\n')
(base/'teams_candidate_chunks_with_dates.md').write_text('\n'.join(md),encoding='utf-8')
# compact review table
rows=[]
for i,c in enumerate(out,1):
    text=norm(c['text'])
    name_hint=''
    pats=[r'dự án\s+([^,.\n:;]{3,90})', r'DA\s+([^,.\n:;]{3,90})', r'khu đất\s+([^,.\n:;]{3,90})', r'Báo cáo[^\n]{0,50}?\s+dự án\s+([^,.\n:;]{3,90})']
    for pat in pats:
        m=re.search(pat,text,re.I)
        if m: name_hint=norm(m.group(1)); break
    rows.append({'chunk_id':i,'source_file':c['source_file'],'report_date':c.get('report_date',''),'report_datetime_raw':c.get('report_datetime_raw',''),'sender':c.get('sender',''),'name_hint':name_hint,'excerpt':text[:800]})
with open(base/'teams_project_review_with_dates.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()) if rows else ['chunk_id']); w.writeheader(); w.writerows(rows)
print(json.dumps({'files':len([f for f in files if len(norm(f.read_text(encoding="utf-8",errors="ignore")))>=500]),'chunks':len(out),'review_csv':str(base/'teams_project_review_with_dates.csv')},ensure_ascii=False))
