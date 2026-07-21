from pathlib import Path
import json,re,csv,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
records=json.load(open(base/'project_popup_records_full.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def norm_name(s):
    s=clean(s).lower()
    s=re.sub(r'^(dự án|da|khu đất|lô đất)\s+','',s)
    s=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',s)
    return clean(s)
def good_name(s):
    s=clean(s)
    bad=re.compile(r'^(link|image|vị trí|xung quanh|gộp là|này$|cao tầng$|nhà ở$|\(nguồn|có lợi thế|được tính|không đạt|phải nộp|có giá|thì họ|mention)',re.I)
    return bool(s and len(s)>=5 and not bad.search(s))
def merge_text(vals,limit=900):
    out=[]
    for v in vals:
        v=clean(v)
        if not v: continue
        parts=[p.strip() for p in re.split(r';\s*',v) if p.strip()]
        for p in parts or [v]:
            if p and p not in out: out.append(p)
    txt='; '.join(out)
    return txt[:limit]
def first_nonempty(vals):
    for v in vals:
        if clean(v): return clean(v)
    return ''
def best_name(items):
    names=[clean(r.get('project_name')) for r in items if good_name(r.get('project_name'))]
    if not names: return clean(items[0].get('project_name')) or 'Chưa đặt tên'
    # prefer shorter meaningful names, not sentence fragments
    names=sorted(set(names), key=lambda x:(len(x)>80, len(x)))
    return names[0]
def key_for(r):
    lat=clean(r.get('latitude')); lng=clean(r.get('longitude'))
    if lat and lng:
        try: coord=f"{round(float(lat),5)},{round(float(lng),5)}"
        except Exception: coord=f"{lat},{lng}"
    else: coord=''
    name=norm_name(r.get('project_name'))
    if coord: return 'coord:'+coord+'|'+name[:32]
    return 'name:'+name[:56]

buckets=collections.defaultdict(list)
for r in records:
    # keep project-like only: has name + at least one meaningful data point
    blob=' '.join(str(r.get(k,'')) for k in ['map_urls','land_area','planning_summary','legal_summary','asking_price','price_mentions','irr','npv','source_excerpt'])
    if not clean(blob): continue
    buckets[key_for(r)].append(r)

fields=['master_id','project_name','mention_count','first_report_date','latest_report_date','source_files','senders','map_urls','latitude','longitude','coordinates','location','province_city','district_area','land_area','project_type','land_type','planning_summary','max_floors','far','building_density','population','legal_summary','legal_status','asking_price','price_mentions','selling_price','land_cost','total_investment','revenue','profit','irr','npv','payback','risks','next_actions','attachments','source_excerpt','data_completeness_score']
masters=[]
for idx,(k,items) in enumerate(buckets.items(),1):
    dates=sorted([clean(r.get('report_date')) for r in items if clean(r.get('report_date'))])
    # choose coordinate from first with coords
    coord_item=next((r for r in items if clean(r.get('latitude')) and clean(r.get('longitude'))),items[0])
    m={'master_id':f'BDS-MASTER-{idx:04d}','project_name':best_name(items),'mention_count':len(items),'first_report_date':dates[0] if dates else '','latest_report_date':dates[-1] if dates else '',
       'source_files':merge_text([r.get('source_file','') for r in items],500),'senders':merge_text([r.get('sender','') for r in items],500),'latitude':clean(coord_item.get('latitude')),'longitude':clean(coord_item.get('longitude')),'coordinates':clean(coord_item.get('coordinates'))}
    for f in fields:
        if f in m: continue
        if f in ['source_excerpt']:
            # keep top 3 source excerpts, dated
            snippets=[]
            for r in sorted(items,key=lambda x:x.get('report_date',''),reverse=True)[:3]:
                ex=clean(r.get('source_excerpt'))[:1200]
                if ex: snippets.append(f"[{r.get('report_date','') or r.get('report_datetime_raw','')}] {ex}")
            m[f]='\n\n---\n\n'.join(snippets)
        elif f=='data_completeness_score':
            pass
        else:
            vals=[r.get(f,'') for r in items]
            m[f]=merge_text(vals,900) if f not in ['location','province_city','district_area','project_type','land_type','legal_status'] else first_nonempty(vals)
    score_keys=['project_name','latest_report_date','map_urls','coordinates','location','land_area','project_type','planning_summary','legal_summary','asking_price','selling_price','total_investment','revenue','profit','irr','npv','risks']
    m['data_completeness_score']=round(sum(1 for f in score_keys if clean(m.get(f,'')))/len(score_keys)*100)
    masters.append(m)
masters.sort(key=lambda r:(not bool(r['latitude'] and r['longitude']),-r['data_completeness_score'],r['project_name']))
(base/'project_popup_master.csv').write_text('',encoding='utf-8')
with open(base/'project_popup_master.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=fields); w.writeheader(); w.writerows(masters)
(base/'project_popup_master.json').write_text(json.dumps(masters,ensure_ascii=False,indent=2),encoding='utf-8')
print({'masters':len(masters),'with_coords':sum(1 for r in masters if r['latitude'] and r['longitude']),'out':str(base/'project_popup_master.csv')})
