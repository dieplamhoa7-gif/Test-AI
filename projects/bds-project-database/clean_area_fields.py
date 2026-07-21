from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
AREA_RE=re.compile(r'(?P<num>\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(?P<unit>ha|m2|m²)\b',re.I)
LAND_CONTEXT=re.compile(r'(diện tích đất|diện tích khu đất|tổng diện tích đất|quy mô|khu đất|lô đất|tổng diện tích dự án|diện tích dự án)',re.I)
NON_LAND_CONTEXT=re.compile(r'(gfa|sàn|thương phẩm|căn|phòng|villa|shophouse|shop|hầm|xây dựng|tim đường|căn hộ|mộ|đường|hành lang)',re.I)

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def parse_num(s):
    s=s.replace(' ','')
    # VN style: 25.045,10 -> 25045.10; 43.702 -> 43702 if 3 trailing digits
    if ',' in s and '.' in s:
        # 13,907.5 = US thousands; 25.045,10 = VN thousands/decimal
        if s.find(',') < s.find('.'):
            s=s.replace(',','')
        else:
            s=s.replace('.','').replace(',','.')
    elif ',' in s:
        # 13,907 usually thousands if exactly 3 digits after comma; otherwise decimal comma
        if re.search(r',\d{3}$',s): s=s.replace(',','')
        else: s=s.replace(',','.')
    elif re.search(r'\.\d{3}$',s):
        s=s.replace('.','')
    try: return float(s)
    except: return None
def to_m2(num,unit): return num*10000 if unit.lower()=='ha' else num
def fmt_m2(v):
    if v is None: return ''
    if v>=10000 and abs(v/10000-round(v/10000,2))<0.01:
        return f"{v:,.0f} m² (~{v/10000:,.2f} ha)".replace(',', '.')
    return f"{v:,.0f} m²".replace(',', '.')
def candidates_from_text(text):
    c=[]
    for m in AREA_RE.finditer(text or ''):
        raw=m.group(0); num=parse_num(m.group('num')); unit=m.group('unit')
        if num is None: continue
        start=max(0,m.start()-90); end=min(len(text),m.end()+90); ctx=text[start:end]
        val=to_m2(num,unit)
        score=0
        if LAND_CONTEXT.search(ctx): score+=8
        if unit.lower()=='ha': score+=4
        if NON_LAND_CONTEXT.search(ctx): score-=5
        if val<80: score-=4
        if val>5000000: score-=4
        c.append({'raw':raw,'m2':val,'ctx':clean(ctx),'score':score})
    return c
def explicit_project_area(text):
    # Highest confidence: title/opening says "dự án X (2.8ha)" or a line says "Diện tích: 2.8 ha".
    patterns=[
        r'dự án[^\n]{0,100}?\((\d{1,3}(?:[.,]\d{1,3})?)\s*(ha|m2|m²)\)',
        r'(?:^|[-•\n])\s*(?:Tổng\s+)?(?:Diện tích|Quy mô)(?:\s+(?:khu đất|dự án|đất))?\s*[:：]\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(ha|m2|m²)',
        r'(?:tổng diện tích dự án|diện tích dự án|diện tích khu đất|diện tích đất thực hiện dự án|tổng diện tích khu đất)[^\n]{0,45}?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(ha|m2|m²)',
        r'(?:quy mô|khu đất dự án)[^\n]{0,40}?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(ha|m2|m²)',
    ]
    for pat in patterns:
        m=re.search(pat,text or '',re.I|re.M)
        if m:
            num=parse_num(m.group(1)); unit=m.group(2)
            if num is not None:
                val=to_m2(num,unit)
                if val>=1000:
                    return {'raw':m.group(1)+' '+unit,'m2':val,'ctx':clean(m.group(0)),'score':99}
    return None

def choose_land_area(r):
    text=' '.join(clean(r.get(k,'')) for k in ['land_area','location','planning_summary','source_excerpt'])
    c=candidates_from_text(text)
    if not c: return ('','','')
    explicit=explicit_project_area(text)
    if explicit:
        best=explicit
    else:
        # Prefer realistic total land/project area. Tiny apartment/room/shop sizes often appear near the word "đất".
        strong=[x for x in c if x['score']>=7 and x['m2']>=1000]
        if strong:
            strong.sort(key=lambda x:(-x['score'], -x['m2']))
            best=strong[0]
        else:
            plausible=[x for x in c if x['m2']>=1000 and x['score']>=0]
            if plausible:
                plausible.sort(key=lambda x:(-x['score'], -x['m2']))
                best=plausible[0]
            else:
                c.sort(key=lambda x:(-x['score'], -x['m2']))
                best=c[0]
    others=[]
    seen={round(best['m2'],2)}
    for x in c[1:]:
        key=round(x['m2'],2)
        if key in seen: continue
        seen.add(key); others.append(x['raw'])
        if len(others)>=10: break
    return (fmt_m2(best['m2']), best['raw'], '; '.join(others))
for r in masters:
    main,raw,others=choose_land_area(r)
    r['land_area_raw_mentions']=r.get('land_area','')
    r['land_area_main']=main
    r['land_area_main_raw']=raw
    r['other_area_mentions']=others
    if main:
        r['land_area']=main
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'rows':len(masters),'with_land_area_main':sum(1 for r in masters if r.get('land_area_main'))})
