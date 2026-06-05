from __future__ import annotations
import json, urllib.request, urllib.parse, re
from datetime import datetime
from pathlib import Path

UA='Mozilla/5.0 LHInvestment/macro-source-discovery'
TESTS=[
 ('worldbank_gdp','https://api.worldbank.org/v2/country/VN/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=5'),
 ('worldbank_cpi','https://api.worldbank.org/v2/country/VN/indicator/FP.CPI.TOTL.ZG?format=json&per_page=5'),
 ('worldbank_bop_current_account','https://api.worldbank.org/v2/country/VN/indicator/BN.CAB.XOKA.CD?format=json&per_page=5'),
 ('worldbank_broad_money','https://api.worldbank.org/v2/country/VN/indicator/FM.LBL.BMNY.GD.ZS?format=json&per_page=5'),
 ('worldbank_credit_private','https://api.worldbank.org/v2/country/VN/indicator/FS.AST.PRVT.GD.ZS?format=json&per_page=5'),
 ('vcb_fx','https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10'),
 ('yahoo_vix','https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=1d&range=10d'),
 ('yahoo_dxy','https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?interval=1d&range=10d'),
 ('tradingeconomics_interbank_page','https://tradingeconomics.com/vietnam/interbank-rate'),
 ('gso_home','https://www.gso.gov.vn/'),
 ('gso_en_home','https://www.gso.gov.vn/en/homepage/'),
 ('sbv_home','https://www.sbv.gov.vn/vi/trang-chu'),
 ('sbv_omo','https://www.sbv.gov.vn/vi/web/sbv_portal/nghi%E1%BB%87p-v%E1%BB%A5-th%E1%BB%8B-tr%C6%B0%E1%BB%9Dng-m%E1%BB%9F'),
]

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json,text/html,application/xml,*/*'})
    with urllib.request.urlopen(req,timeout=20) as r:
        raw=r.read(200000)
        ctype=r.headers.get('content-type','')
        return r.status, ctype, raw

rows=[]
for name,url in TESTS:
    item={'id':name,'url':url,'testedAt':datetime.now().isoformat()}
    try:
        status,ctype,raw=fetch(url)
        text=raw.decode('utf-8',errors='ignore')
        item.update({'status':status,'contentType':ctype,'bytes':len(raw),'title': ''})
        m=re.search(r'<title[^>]*>(.*?)</title>',text,re.I|re.S)
        if m: item['title']=re.sub(r'\s+',' ',m.group(1)).strip()[:160]
        if text.lstrip().startswith('[') or text.lstrip().startswith('{'):
            try:
                js=json.loads(text)
                item['jsonOk']=True
                item['jsonSample']=str(js)[:500]
            except Exception as e: item['jsonError']=str(e)
        item['snippet']=re.sub(r'\s+',' ',text[:500]).strip()
    except Exception as e:
        item.update({'status':'error','error':str(e)[:300]})
    rows.append(item)

out=Path('data/source_discovery_public_2026-06-05.json')
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'createdAt':datetime.now().isoformat(),'tests':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),'ok':[r['id'] for r in rows if r.get('status')==200],'errors':[(r['id'],r.get('error')) for r in rows if r.get('status')=='error']},ensure_ascii=False,indent=2))
