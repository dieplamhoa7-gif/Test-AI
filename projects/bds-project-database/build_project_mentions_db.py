from pathlib import Path
import json, csv, re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
chunks=json.load(open(base/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))

def norm(s): return re.sub(r'\s+',' ',s or '').strip()
def find_all(pat,text,flags=re.I): return '; '.join(dict.fromkeys(m.group(0) for m in re.finditer(pat,text,flags)))
def first_num(pattern,text):
    m=re.search(pattern,text,re.I)
    return norm(m.group(1)) if m else ''
def name_hint(text):
    text=norm(text)
    patterns=[
        r'dự án\s+([^,.\n:;]{3,110})',
        r'DA\s+([^,.\n:;]{3,110})',
        r'khu đất\s+([^,.\n:;]{3,110})',
        r'lô đất\s+([^,.\n:;]{3,110})',
        r'Báo cáo[^\n]{0,60}?\s+dự án\s+([^,.\n:;]{3,110})',
    ]
    for p in patterns:
        m=re.search(p,text,re.I)
        if m:
            return norm(m.group(1)).strip(' -')[:120]
    return ''
rows=[]
for i,c in enumerate(chunks,1):
    text=c.get('text','')
    ntext=norm(text)
    maps='; '.join(dict.fromkeys(re.findall(r'https?://(?:maps\.app\.goo\.gl|goo\.gl/maps|www\.google\.com/maps|www\.google\.com/maps\?q=)[^\s,)>]+',text)))
    row={
        'mention_id':f'TEAMS-MENTION-{i:04d}',
        'chunk_id':i,
        'source_file':c.get('source_file',''),
        'source_chat':'Bee || Phân Tích Đầu Tư',
        'report_date':c.get('report_date',''),
        'report_datetime_raw':c.get('report_datetime_raw',''),
        'sender':c.get('sender',''),
        'project_name_hint':name_hint(text),
        'map_urls':maps,
        'land_area_mentions':find_all(r'\b\d+[\.,]?\d*\s*(?:ha|m2|m²)\b',text),
        'price_mentions':find_all(r'\b\d+[\.,]?\d*\s*(?:tỷ|tr/m2|tr\/m2|triệu/m2|triệu\/m2)\b',text),
        'far_mentions':find_all(r'(?:HSSDĐ|HS SDĐ|hệ số(?: sử dụng đất)?)[^\n,.]{0,40}?\d+[\.,]?\d*',text),
        'population_mentions':find_all(r'(?:dân số|dân)[^\n,.]{0,50}?\d+[\.,]?\d*',text),
        'irr_mentions':find_all(r'IRR[^\n,.]{0,30}?\d+[\.,]?\d*%?',text),
        'npv_mentions':find_all(r'NPV[^\n,.]{0,40}?-?\s*\d+[\.,]?\d*\s*tỷ?',text),
        'excerpt':ntext[:1800],
    }
    rows.append(row)
with open(base/'project_mentions_from_teams_full.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print({'mentions':len(rows),'out':str(base/'project_mentions_from_teams_full.csv')})
