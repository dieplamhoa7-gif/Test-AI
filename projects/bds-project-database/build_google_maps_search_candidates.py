from pathlib import Path
import csv,urllib.parse
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=list(csv.DictReader(open(base/'geocode_candidates.csv',encoding='utf-8-sig',newline='')))
out=[]
for r in rows:
    q=r.get('query','')
    out.append({**r,'google_maps_search_url':'https://www.google.com/maps/search/'+urllib.parse.quote_plus(q)})
with open(base/'google_maps_search_candidates.csv','w',encoding='utf-8-sig',newline='') as fp:
    fields=list(out[0].keys()) if out else ['master_id']
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(out)
print({'rows':len(out),'out':str(base/'google_maps_search_candidates.csv')})
