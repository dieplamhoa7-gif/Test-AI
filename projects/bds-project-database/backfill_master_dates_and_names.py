from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
chunks=json.load(open(base/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def norm(s):
    s=clean(s).lower()
    s=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',s)
    return clean(s)
def infer_name(text):
    bad=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|như sau$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ|một lần|không phải|xác nhận|để hiệu quả|phân lô)',re.I)
    pats=[
        r'(?:P\.ĐT|Phòng ĐT|K\.ĐT|Phòng Đầu tư)[^\n]{0,80}?dự án\s+([^,.\n:;]{4,120})',
        r'dự án\s+([^,.\n:;]{4,120})', r'DA\s+([^,.\n:;]{4,120})',
        r'khu đất\s+([^,.\n:;]{4,120})', r'lô đất\s+([^,.\n:;]{4,120})',
        r'khách sạn\s+([^,.\n:;]{4,120})', r'cao tầng\s+([^,.\n:;]{4,120})',
    ]
    for p in pats:
        m=re.search(p,text or '',re.I)
        if m:
            c=clean(m.group(1)).strip(' -:;,.')
            c=re.sub(r'\s+(như sau|theo.*|với.*)$','',c,flags=re.I).strip(' -:;,.')
            if len(c)>=5 and not bad.search(c): return c[:140]
    return ''
def bad_name(name):
    return bool(re.search(r'^(link|image|vị trí|xung quanh|gộp là|này$|như sau$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ|một lần|không phải|xác nhận|để hiệu quả|phân lô)',clean(name),re.I)) or len(clean(name))<5
# Build searchable chunks by normalized content prefix
chunk_texts=[]
for c in chunks:
    chunk_texts.append({'date':c.get('report_date',''),'raw':c.get('report_datetime_raw',''),'text':c.get('text',''), 'norm':norm(c.get('text',''))})
fixed_dates=0; fixed_names=0
for r in masters:
    ex=clean(r.get('source_excerpt',''))
    if bad_name(r.get('project_name','')):
        nm=infer_name(ex)
        if nm:
            r['project_name_raw2']=r.get('project_name','')
            r['project_name']=nm; fixed_names+=1
    if not (r.get('first_report_date') or r.get('latest_report_date')):
        # direct timestamp in excerpt first
        m=re.search(r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s+[AP]M)',ex)
        if m:
            raw=m.group(1)
            mm,dd,yy=re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})',raw).groups()
            iso=f'{int(yy):04d}-{int(mm):02d}-{int(dd):02d}'
            r['first_report_date']=r['latest_report_date']=iso
            r['report_datetime_raw_backfilled']=raw; fixed_dates+=1; continue
        # match source excerpt against dated chunks
        key=norm(ex[:500])
        best=None; bestscore=0
        name_tokens=[t for t in norm(r.get('project_name','')).split() if len(t)>=4][:6]
        for c in chunk_texts:
            score=0
            if key and key[:160] in c['norm']: score+=20
            for t in name_tokens:
                if t in c['norm']: score+=2
            if score>bestscore:
                bestscore=score; best=c
        if best and bestscore>=8 and best.get('date'):
            r['first_report_date']=r['latest_report_date']=best['date']
            r['report_datetime_raw_backfilled']=best.get('raw','')
            fixed_dates+=1
# refresh ids sorted
masters.sort(key=lambda x:(not bool(x.get('latitude') and x.get('longitude')),-int(x.get('data_completeness_score') or 0),x.get('project_name','')))
for i,r in enumerate(masters,1): r['master_id']=f'BDS-MASTER-{i:04d}'
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'fixed_dates':fixed_dates,'fixed_names':fixed_names,'rows':len(masters)})
