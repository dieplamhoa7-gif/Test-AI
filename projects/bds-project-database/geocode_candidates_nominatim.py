from pathlib import Path
import csv,json,re,time,urllib.parse,urllib.request
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
inp=base/'geocode_candidates.csv'
outp=base/'geocode_results_nominatim.csv'

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def norm(s):
    import unicodedata
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn')
    s=re.sub(r'[^a-z0-9]+',' ',s.lower())
    return clean(s)
def score_result(query, display, cls, typ):
    qtokens=[t for t in norm(query).split() if len(t)>=3]
    d=norm(display)
    sc=0
    for t in qtokens:
        if t in d: sc+=8
    if 'viet nam' in d or 'vietnam' in d: sc+=8
    if cls in ['place','building','amenity','tourism','landuse','boundary']: sc+=8
    if typ in ['residential','commercial','apartments','hotel','administrative','suburb','neighbourhood']: sc+=5
    if any(b in d for b in ['thailand','indonesia','china','japan','korea']): sc-=60
    return sc
rows=list(csv.DictReader(open(inp,encoding='utf-8-sig',newline='')))
# Only high quality queries first to avoid bad pins/rate abuse.
rows=[r for r in rows if int(r.get('priority') or 0)>=8][:80]
results=[]
headers={'User-Agent':'LH-BDS-dashboard-cleaner/1.0','Accept-Language':'vi,en;q=0.8'}
for idx,r in enumerate(rows,1):
    q=clean(r.get('query'))
    if not q: continue
    params={'q':q,'format':'jsonv2','limit':'5','countrycodes':'vn','addressdetails':'1'}
    url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(params)
    status=''; best=None
    try:
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=20) as resp:
            data=json.loads(resp.read().decode('utf-8','ignore'))
        for item in data:
            display=item.get('display_name','')
            sc=score_result(q,display,item.get('class',''),item.get('type',''))
            cand={'master_id':r['master_id'],'project_name':r['project_name'],'query':q,'lat':item.get('lat',''),'lng':item.get('lon',''),'display_name':display,'class':item.get('class',''),'type':item.get('type',''),'importance':item.get('importance',''),'confidence_score':sc,'status':'candidate'}
            if best is None or sc>best['confidence_score']: best=cand
        if best:
            best['status']='high_confidence' if best['confidence_score']>=55 else 'review'
            results.append(best)
        else:
            results.append({'master_id':r['master_id'],'project_name':r['project_name'],'query':q,'lat':'','lng':'','display_name':'','class':'','type':'','importance':'','confidence_score':0,'status':'no_result'})
    except Exception as e:
        results.append({'master_id':r['master_id'],'project_name':r['project_name'],'query':q,'lat':'','lng':'','display_name':'','class':'','type':'','importance':'','confidence_score':0,'status':'error:'+str(e)[:120]})
    time.sleep(1.05)
fields=['master_id','project_name','query','lat','lng','display_name','class','type','importance','confidence_score','status']
with open(outp,'w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(results)
print({'queried':len(rows),'results':len(results),'high_confidence':sum(1 for x in results if x.get('status')=='high_confidence'),'out':str(outp)})
