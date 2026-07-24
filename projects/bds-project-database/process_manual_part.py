import json,re,unicodedata,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
part=int(sys.argv[1]) if len(sys.argv)>1 else 1
IN=BASE/'manual_10parts'/f'part_{part:02d}.json'
OUT=BASE/'manual_10parts'/f'part_{part:02d}_records.json'

def clean(s): return re.sub(r'\s+',' ',str(s or '').strip())
def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',str(s or '')) if unicodedata.category(c)!='Mn')
def is_project(row):
    name=clean(row.get('name_hint'))
    ex=clean(row.get('excerpt'))
    if not name or len(name)<5: return False
    bad=[r'^NHƯ SAU$',r'^NHU SAU$',r'^\(FS\)$',r'^có ',r'^co ',r'^không ',r'^khong ',r'^sẽ ',r'^se ',r'^đạt ',r'^dat ',r'^tham gia',r'^hiện tại',r'^hien tai',r'^gồm ',r'^gom ']
    if any(re.search(p,name,flags=re.I) for p in bad): return False
    txt=name+' '+ex[:300]
    return bool(re.search(r'dự án|DA\b|KDC|KĐT|khu đất|chung cư|cao tầng|resort|khách sạn|phân lô|\d+\s*(ha|m2|m²)|đường|quận|phường|xã|TPHCM|Bình Dương|Đồng Nai',txt,flags=re.I))
def norm_name(s):
    s=strip(clean(s)).lower(); s=re.sub(r'[^a-z0-9]+',' ',s)
    stop={'du','an','da','khu','dat','bao','cao','sep','admin','phong','dau','tu','nhu','sau','ve','viec','cap','nhat','co','quy','mo','voi'}
    return ' '.join(t for t in s.split() if len(t)>1 and t not in stop)[:80]
def area(s):
    t=strip(s).lower(); hits=[]
    for pat in [r'phuong\s+[a-z0-9 ]{2,20}',r'xa\s+[a-z0-9 ]{2,20}',r'quan\s+[a-z0-9 ]{1,12}',r'huyen\s+[a-z0-9 ]{2,20}',r'thu duc|binh duong|dong nai|da nang|phu quoc|nha trang|ha long|quan 9|quan 2']:
        hits+=re.findall(pat,t)
    return '|'.join(dict.fromkeys(clean(x) for x in hits[:3]))
def key(row): return norm_name(row['name_hint'])+'::'+area(row['excerpt'][:800])
def map_url(ex):
    m=re.search(r'https?://(?:maps\.app\.goo\.gl|goo\.gl/maps|www\.google\.com/maps)[^\s,;\)\]]+', ex)
    return m.group(0) if m else ''
def fin(ex):
    rules=[('Giá chào/chuyển nhượng',r'(?:giá chào(?: bán)?|giá chuyển nhượng|tổng giá trị M&A)[^.;\n]{0,100}?(?:\d[\d.,]*\s*(?:tỷ|tr/m2|tr/m²|triệu/m2))'),('Giá bán',r'(?:giá bán|giá căn hộ|giá bán căn hộ|giá bán Shop TM)[^.;\n]{0,100}?(?:\d[\d.,]*(?:\s*-\s*\d[\d.,]*)?\s*(?:tr/m2|tr/m²|triệu/m2|tỷ))'),('Tổng mức đầu tư',r'(?:tổng mức đầu tư|TMĐT)[^.;\n]{0,90}?(?:\d[\d.,]*\s*tỷ)'),('Doanh thu',r'doanh thu[^.;\n]{0,90}?(?:\d[\d.,]*\s*tỷ)'),('LNTT',r'(?:LNTT|lợi nhuận trước thuế)[^.;\n]{0,90}?(?:\d[\d.,]*\s*(?:tỷ|%))'),('IRR',r'IRR[^.;\n]{0,50}?(?:\d[\d.,]*\s*%)')]
    out=[]; seen=set()
    for lab,pat in rules:
        for m in re.finditer(pat,ex,flags=re.I):
            v=clean(m.group(0))[:180]
            if (lab,v) not in seen: out.append({'label':lab,'value':v}); seen.add((lab,v))
    return out
rows=json.loads(IN.read_text(encoding='utf-8'))
projects={}; review=[]
for row in rows:
    if not is_project(row): review.append(row); continue
    k=key(row)
    projects.setdefault(k,[]).append(row)
records=[]
for k,grp in projects.items():
    grp=sorted(grp,key=lambda r:(r.get('report_date') or '9999',r.get('report_datetime_raw') or '',int(r['chunk_id'])))
    latest=grp[-1]
    allfin=[]; seen=set()
    updates=[]
    for r in grp:
        ex=clean(r['excerpt']); updates.append({'chunk_id':r['chunk_id'],'date':r.get('report_date',''),'datetime':r.get('report_datetime_raw',''),'source_file':r.get('source_file',''),'sender':r.get('sender',''),'excerpt':ex})
        for it in fin(ex):
            kk=(it['label'],it['value'])
            if kk not in seen: allfin.append({**it,'chunk_id':r['chunk_id'],'date':r.get('report_date','')}); seen.add(kk)
    records.append({'id':f'P{part:02d}-{len(records)+1:04d}','part':part,'name':clean(latest['name_hint']),'first_date':grp[0].get('report_date',''),'latest_date':latest.get('report_date',''),'source_files':'; '.join(dict.fromkeys(r.get('source_file','') for r in grp)),'map_url':map_url(latest.get('excerpt','')),'location_hint':area(latest.get('excerpt','')),'update_count':len(grp),'financial_items':allfin,'updates':updates,'status':'merged_update' if len(grp)>1 else 'single'})
OUT.write_text(json.dumps({'part':part,'records':records,'review':review},ensure_ascii=False,indent=2),encoding='utf-8')
print('part',part,'rows',len(rows),'records',len(records),'review',len(review),'merged',sum(1 for r in records if r['update_count']>1),'financial',sum(1 for r in records if r['financial_items']))
