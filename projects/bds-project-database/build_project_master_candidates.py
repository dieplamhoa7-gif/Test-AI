from pathlib import Path
import csv,re,collections
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
mentions=list(csv.DictReader(open(base/'project_mentions_from_teams_full.csv',encoding='utf-8-sig')))

def norm(s): return re.sub(r'\s+',' ',s or '').strip()
def clean_name(n):
    n=norm(n)
    n=re.sub(r'^(về|sơ bộ|cập nhật|tính toán fs sơ bộ|phân tích đầu tư)\s+','',n,flags=re.I)
    n=re.sub(r'\s+(như sau|với.*|theo.*)$','',n,flags=re.I)
    return n.strip(' -:;,.')[:100]
def key_name(n):
    n=clean_name(n).lower()
    n=re.sub(r'[^0-9a-zA-ZÀ-ỹ]+',' ',n)
    return norm(n)
# seed aliases from existing CSV names
existing=list(csv.DictReader(open(base/'projects_from_teams_draft.csv',encoding='utf-8-sig')))
existing_names={key_name(r['project_name']):r['project_id'] for r in existing if r.get('project_name')}
# group mention name hints
buckets=collections.defaultdict(list)
for m in mentions:
    name=clean_name(m.get('project_name_hint',''))
    if len(name)<4: continue
    if re.search(r'^(này|như sau|theo|sếp|anh|em|vị trí|nguồn|phương án|thay đổi|có giá|không phải)',name,re.I): continue
    k=key_name(name)
    if len(k)<4: continue
    buckets[k].append(m)
rows=[]
for k,ms in buckets.items():
    # keep if repeated or has strong facts/map/area/price
    strong=[m for m in ms if m.get('map_urls') or m.get('land_area_mentions') or m.get('price_mentions')]
    if len(ms)<1 or not strong: continue
    first=ms[0]
    rows.append({
        'candidate_key':k,
        'existing_project_id':existing_names.get(k,''),
        'project_name_candidate':clean_name(first.get('project_name_hint','')),
        'mention_count':len(ms),
        'first_report_date':min([m['report_date'] for m in ms if m.get('report_date')] or ['']),
        'latest_report_date':max([m['report_date'] for m in ms if m.get('report_date')] or ['']),
        'map_urls':'; '.join(dict.fromkeys('; '.join(m.get('map_urls','') for m in ms).split('; '))).strip('; '),
        'land_area_mentions':'; '.join(dict.fromkeys('; '.join(m.get('land_area_mentions','') for m in ms).split('; '))).strip('; ')[:500],
        'price_mentions':'; '.join(dict.fromkeys('; '.join(m.get('price_mentions','') for m in ms).split('; '))).strip('; ')[:500],
        'sample_excerpt':first.get('excerpt','')[:1000]
    })
rows.sort(key=lambda r:(r['existing_project_id']=='', -int(r['mention_count']), r['first_report_date']))
with open(base/'project_master_candidates_from_mentions.csv','w',encoding='utf-8-sig',newline='') as fp:
    f=list(rows[0].keys()) if rows else ['candidate_key']
    w=csv.DictWriter(fp,fieldnames=f); w.writeheader(); w.writerows(rows)
print({'candidates':len(rows),'out':str(base/'project_master_candidates_from_mentions.csv')})
