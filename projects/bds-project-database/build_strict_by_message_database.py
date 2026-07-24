import csv,json,re,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
SRC=BASE/'teams_project_review_with_dates.csv'
OUT_JSON=BASE/'strict_by_message_projects.json'
WEB=BASE/'web'

def clean(s): return re.sub(r'\s+',' ',(s or '').strip())
def norm_name(s):
    s=clean(s).lower()
    s=re.sub(r'^(dự án|da|khu đất|kdc|kđt|báo cáo|p\.đt|phòng đầu tư)\s+','',s)
    return s[:120]
def extract_coord(text):
    # google maps URL coords are often unavailable; capture explicit lat,lng only
    m=re.search(r'(?<!\d)(1[0-2]\.\d{4,})\s*,\s*(10[5-7]\.\d{4,})(?!\d)', text)
    if m: return float(m.group(1)),float(m.group(2))
    return None,None
def extract_map(text):
    m=re.search(r'https?://(?:maps\.app\.goo\.gl|goo\.gl/maps|www\.google\.com/maps)[^\s,;\)\]]+', text)
    return m.group(0) if m else ''
def area_hint(text):
    pats=[]
    for pat in [r'(?:P\.|phường|xã)\s*[A-Za-zÀ-ỹ0-9 .-]{2,35}',r'(?:Q\.|quận|huyện|TP\.|thành phố|tỉnh)\s*[A-Za-zÀ-ỹ0-9 .-]{2,35}']:
        pats += re.findall(pat,text,flags=re.I)
    return '; '.join(dict.fromkeys(clean(x) for x in pats))[:240]
def label_financial(text):
    rules=[
      ('Giá chào / chuyển nhượng', r'(?:giá chào(?: bán)?|giá chuyển nhượng|giá mua dự án|tổng giá trị M&A)[^.;\n]{0,90}?(?:\d[\d.,]*\s*(?:tỷ|tr\.?đồng|tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Giá bán căn hộ', r'(?:giá bán căn hộ|giá căn hộ)[^.;\n]{0,90}?(?:\d[\d.,]*(?:\s*-\s*\d[\d.,]*)?\s*(?:tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Giá bán shophouse/TM', r'(?:giá bán\s*(?:shop|shophouse|Shop TM)|ShopTM)[^.;\n]{0,90}?(?:\d[\d.,]*(?:\s*-\s*\d[\d.,]*)?\s*(?:tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Chi phí mua đất', r'(?:chi phí mua đất|giá vốn đất|giá mua)[^.;\n]{0,90}?(?:\d[\d.,]*\s*(?:tỷ|tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Tiền sử dụng đất', r'(?:tiền sử dụng đất|TSDĐ)[^.;\n]{0,90}?(?:\d[\d.,]*\s*(?:tỷ|tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Chi phí xây dựng / suất đầu tư', r'(?:chi phí xây dựng|suất vốn|suất đầu tư|all[ -]?in|đơn giá XD)[^.;\n]{0,100}?(?:\d[\d.,]*\s*(?:tỷ|tr/m2|tr/m²|triệu/m2|triệu/m²))'),
      ('Tổng mức đầu tư', r'(?:tổng mức đầu tư|TMĐT)[^.;\n]{0,80}?(?:\d[\d.,]*\s*tỷ)'),
      ('Doanh thu', r'(?:doanh thu)[^.;\n]{0,80}?(?:\d[\d.,]*\s*tỷ)'),
      ('Lợi nhuận trước thuế', r'(?:lợi nhuận trước thuế|LNTT)[^.;\n]{0,80}?(?:\d[\d.,]*\s*(?:tỷ|%))'),
      ('Lợi nhuận sau thuế', r'(?:lợi nhuận sau thuế|LNST)[^.;\n]{0,80}?(?:\d[\d.,]*\s*(?:tỷ|%))'),
      ('IRR', r'IRR[^.;\n]{0,40}?(?:\d[\d.,]*\s*%)'),
      ('NPV', r'NPV[^.;\n]{0,60}?(?:\d[\d.,]*\s*tỷ)'),
    ]
    out=[]; seen=set()
    for lab,pat in rules:
        for m in re.finditer(pat,text,flags=re.I):
            val=clean(m.group(0))
            if len(val)>160: val=val[:157]+'…'
            key=(lab,val.lower())
            if key not in seen:
                out.append({'label':lab,'value':val}); seen.add(key)
    return out

def should_keep(row):
    name=clean(row.get('name_hint'))
    ex=clean(row.get('excerpt'))
    if not name or len(name)<4: return False
    # skip obvious replies/comments without project identity
    bad=['xung quanh','này','đạt tỷ lệ','không đạt hiệu quả','sẽ được','cơ bản đạt']
    if norm_name(name) in bad: return False
    return True
rows=[]
with SRC.open(encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f):
        if not should_keep(r): continue
        ex=clean(r['excerpt']); name=clean(r['name_hint'])
        lat,lng=extract_coord(ex); mp=extract_map(ex)
        rec_id=f"MSG-{int(r['chunk_id']):04d}"
        popup={
          'project_name':name,'source_files':r.get('source_file',''),'report_date':r.get('report_date',''),
          'report_datetime_raw':r.get('report_datetime_raw',''),'senders':r.get('sender',''),
          'location':area_hint(ex),'source_excerpt':ex,'financial_line_items':json.dumps(label_financial(ex),ensure_ascii=False),
          'financial_unclassified_items':'[]'
        }
        rows.append({'id':rec_id,'name':name,'lat':lat or 10.7769,'lng':lng or 106.7009,'date':r.get('report_date',''),
          'datetime_raw':r.get('report_datetime_raw',''),'sender':r.get('sender',''),'type':'message-record','status':'strict-message',
          'priority':'review' if not (lat and lng) else 'normal','score':50,'map_url':mp,'excerpt':ex[:520],'popup':popup})
OUT_JSON.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
# write standalone web data for checking without overwriting current app data
(WEB/'strict_by_message_projects.js').write_text('window.STRICT_BY_MESSAGE_PROJECTS = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('wrote',len(rows),'records to',OUT_JSON)
print('financial records',sum(1 for x in rows if json.loads(x['popup']['financial_line_items'])))
