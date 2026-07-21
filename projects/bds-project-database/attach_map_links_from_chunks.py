from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))
chunks=json.load(open(base/'teams_candidate_chunks_with_dates.json',encoding='utf-8'))
res=json.load(open(base/'map_link_resolution_all.json',encoding='utf-8')) if (base/'map_link_resolution_all.json').exists() else []
coord={x['url']:(x.get('lat'),x.get('lng')) for x in res if x.get('lat') and x.get('lng')}
MAP_RE=re.compile(r'https?://(?:maps\.app\.goo\.gl|goo\.gl/maps|www\.google\.com/maps)[^\s)>\]]+',re.I)

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def norm(s):
    s=clean(s).lower(); s=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',s); return clean(s)
def toks(s): return [t for t in norm(s).split() if len(t)>=4][:10]
# chunk index with links
chunk_rows=[]
for c in chunks:
    links=[]
    for u in MAP_RE.findall(c.get('text','') or ''):
        u=u.rstrip('.,;)')
        if u not in links: links.append(u)
    if links:
        chunk_rows.append({'source_file':c.get('source_file',''),'date':c.get('report_date',''),'text':c.get('text',''),'norm':norm(c.get('text','')),'links':links})
attached=0; attached_coords=0
review=[]
for r in masters:
    existing=[u.strip() for u in re.split(r';\s*',r.get('map_urls','') or '') if u.strip()]
    if existing and r.get('latitude') and r.get('longitude'):
        continue
    name_tokens=toks(r.get('project_name',''))
    ex_key=norm((r.get('source_excerpt') or '')[:900])
    files=[clean(f) for f in re.split(r';\s*',r.get('source_files','') or '') if clean(f)]
    best=None; bestscore=0
    for c in chunk_rows:
        score=0
        if c['source_file'] in files: score+=12
        if ex_key and ex_key[:180] in c['norm']: score+=28
        for t in name_tokens:
            if t in c['norm']: score+=4
        # known distinct area/date hints
        for hint in [r.get('land_area_main_raw',''), r.get('latest_report_date',''), r.get('first_report_date','')]:
            h=norm(hint)
            if h and h in c['norm']: score+=5
        if score>bestscore:
            bestscore=score; best=c
    if best and bestscore>=12:
        merged=[]
        for u in existing+best['links']:
            if u and u not in merged: merged.append(u)
        r['map_urls']='; '.join(merged)
        r['map_link_attached_from_chunk']=best['source_file']
        r['map_link_match_score']=bestscore
        attached+=1
        # apply first resolved coordinate if missing
        if not (r.get('latitude') and r.get('longitude')):
            for u in merged:
                if u in coord:
                    lat,lng=coord[u]
                    r['latitude']=lat; r['longitude']=lng; r['coordinates']=f'{lat}, {lng}'
                    r['coordinate_source']='matched_teams_map_link'
                    attached_coords+=1
                    break
        if not (r.get('latitude') and r.get('longitude')):
            review.append({'master_id':r.get('master_id'),'project_name':r.get('project_name'),'match_score':bestscore,'links':'; '.join(merged),'source_file':best['source_file'],'reason':'links_not_resolved_yet'})
fields=list(masters[0].keys()) if masters else []
with open(base/'project_popup_master_clean.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(masters)
(base/'project_popup_master_clean.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
with open(base/'map_link_match_review.csv','w',encoding='utf-8-sig',newline='') as fp:
    fs=list(review[0].keys()) if review else ['master_id']
    w=csv.DictWriter(fp,fieldnames=fs,extrasaction='ignore'); w.writeheader(); w.writerows(review)
print({'chunks_with_maps':len(chunk_rows),'attached_links':attached,'attached_coords':attached_coords,'review_unresolved':len(review)})
