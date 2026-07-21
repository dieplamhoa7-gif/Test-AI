from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def uniq(vals,limit=12):
    out=[]
    for v in vals:
        for p in re.split(r';\s*',clean(v)):
            p=p.strip(' -;,.')
            if p and p not in out: out.append(p)
    return '; '.join(out[:limit])
def first_match(pattern,text,flags=re.I):
    m=re.search(pattern,text or '',flags)
    return clean(m.group(0)) if m else ''
def all_match(pattern,text,flags=re.I,limit=8):
    vals=[]
    for m in re.finditer(pattern,text or '',flags):
        v=clean(m.group(0))
        if v and v not in vals: vals.append(v)
        if len(vals)>=limit: break
    return '; '.join(vals)
def extract_money(text):
    # Returns canonical snippets by business meaning, not every amount.
    patterns={
      'asking_land_price': [r'(?:giá chào|giá mua|giá bán dự án|M&A|chào bán|giá vốn)[^\n.;]{0,120}?\d+[\.,]?\d*\s*(?:tỷ|tr/m2|tr\/m2|triệu/m2|triệu\/m2)', r'\d+[\.,]?\d*\s*tỷ[^\n.;]{0,70}?(?:giá chào|giá mua|M&A)'],
      'selling_price': [r'(?:giá bán|đơn giá bán|giá căn hộ|giá phòng|giá kinh doanh)[^\n.;]{0,130}?\d+[\.,]?\d*\s*(?:tr/m2|tr\/m2|triệu/m2|triệu\/m2|triệu|USD|tỷ)'],
      'land_cost': [r'(?:tiền đất|chi phí đất|giá vốn đất|tiền sử dụng đất|TSDĐ|LUR)[^\n.;]{0,130}?\d+[\.,]?\d*\s*(?:tỷ|tr/m2|triệu/m2)?'],
      'total_investment_clean': [r'(?:tổng mức đầu tư|TMĐT|tổng chi phí|chi phí đầu tư)[^\n.;]{0,140}?\d+[\.,]?\d*\s*tỷ'],
      'revenue_clean': [r'(?:doanh thu|DT)[^\n.;]{0,120}?\d+[\.,]?\d*\s*tỷ'],
      'profit_clean': [r'(?:LNTT|LNST|lợi nhuận|PBT|gross profit)[^\n.;]{0,120}?-?\s*\d+[\.,]?\d*\s*tỷ'],
      'irr_clean': [r'IRR[^\n.;]{0,45}?-?\s*\d+[\.,]?\d*%'],
      'npv_clean': [r'NPV[^\n.;]{0,60}?-?\s*\d+[\.,]?\d*\s*tỷ'],
      'payback_clean': [r'(?:hoàn vốn|payback)[^\n.;]{0,80}?\d+[\.,]?\d*\s*(?:năm|tháng)'],
    }
    out={}
    for k,pats in patterns.items():
        vals=[]
        for pat in pats:
            found=all_match(pat,text,limit=10)
            if found: vals.append(found)
        out[k]=uniq(vals,10)
    return out
def numeric_amounts(text):
    return re.findall(r'-?\d+[\.,]?\d*\s*(?:tỷ|tr/m2|tr\/m2|triệu/m2|%|ha|m2|m²)',text or '',re.I)
for r in masters:
    text=' '.join(clean(r.get(k,'')) for k in ['asking_price','price_mentions','selling_price','land_cost','total_investment','revenue','profit','irr','npv','payback','source_excerpt'])
    fin=extract_money(text)
    for k,v in fin.items(): r[k]=v
    r['financial_raw_mentions']=uniq([r.get('asking_price',''),r.get('price_mentions',''),r.get('selling_price',''),r.get('land_cost',''),r.get('total_investment',''),r.get('revenue',''),r.get('profit',''),r.get('irr',''),r.get('npv','')],40)
    # overwrite broad fields with clean fields where possible for dashboard compatibility
    if r.get('asking_land_price'): r['asking_price']=r['asking_land_price']
    if r.get('selling_price'): r['selling_price']=r['selling_price']
    if r.get('total_investment_clean'): r['total_investment']=r['total_investment_clean']
    if r.get('revenue_clean'): r['revenue']=r['revenue_clean']
    if r.get('profit_clean'): r['profit']=r['profit_clean']
    if r.get('irr_clean'): r['irr']=r['irr_clean']
    if r.get('npv_clean'): r['npv']=r['npv_clean']
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'rows':len(masters),'with_asking':sum(1 for r in masters if r.get('asking_land_price')),'with_selling':sum(1 for r in masters if r.get('selling_price')),'with_irr':sum(1 for r in masters if r.get('irr_clean'))})
