from pathlib import Path
import json,csv,re
base=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
masters=json.load(open(base/'project_popup_master_clean.json',encoding='utf-8'))

def clean(s): return re.sub(r'\s+',' ',str(s or '')).strip()
def category(r):
    links=clean(r.get('map_urls',''))
    if not links:
        return 'no_map_link_matched'
    if '/maps/d/' in links or 'google.com/maps/d/' in links:
        return 'google_my_maps_needs_open'
    if '…' in links or '...' in links or '**' in links or links.endswith('-') or links.endswith('mid'):
        return 'truncated_or_dirty_link'
    if 'maps.app.goo.gl' in links or 'goo.gl/maps' in links:
        return 'short_link_unresolved'
    if 'google.com/maps?q=' in links or 'google.com/maps/search' in links:
        return 'direct_google_maps_unparsed'
    return 'other_unresolved_link'
rows=[]
for r in masters:
    if r.get('latitude') and r.get('longitude'): continue
    rows.append({
        'master_id':r.get('master_id'),
        'project_name':r.get('project_name'),
        'category':category(r),
        'latest_report_date':r.get('latest_report_date') or r.get('first_report_date'),
        'map_urls':r.get('map_urls',''),
        'location':r.get('location',''),
        'province_city':r.get('province_city',''),
        'district_area':r.get('district_area',''),
        'source_files':r.get('source_files',''),
        'source_excerpt':clean(r.get('source_excerpt',''))[:900],
    })
rows.sort(key=lambda x:(x['category'],x['project_name']))
with open(base/'coordinate_gap_report.csv','w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0].keys()) if rows else ['master_id']); w.writeheader(); w.writerows(rows)
from collections import Counter
cnt=Counter(r['category'] for r in rows)
md=['# Coordinate Gap Report\n',f'- Missing coordinates: {len(rows)}','']
for k,v in cnt.most_common(): md.append(f'- {k}: {v}')
md.append('\n## Samples\n')
for r in rows[:100]:
    md.append(f"### {r['master_id']} — {r['project_name']}\n- Category: {r['category']}\n- Date: {r['latest_report_date']}\n- Map URLs: {r['map_urls']}\n- Location: {r['location']} {r['district_area']} {r['province_city']}\n- Source files: {r['source_files']}\n")
(base/'coordinate_gap_report.md').write_text('\n'.join(md),encoding='utf-8')
print({'missing_coordinates':len(rows),'categories':dict(cnt),'out':str(base/'coordinate_gap_report.csv')})
