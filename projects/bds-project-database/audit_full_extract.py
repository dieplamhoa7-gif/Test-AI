import csv,re,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
p=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\projects\bds-project-database')
rows=list(csv.DictReader(open(p/'projects_from_teams_draft.csv',encoding='utf-8-sig')))
print('rows',len(rows))
for r in rows[-20:]:
    print(r.get('project_id'), r.get('project_name'), r.get('status'))
text=(p/'teams_candidate_chunks.md').read_text(encoding='utf-8',errors='ignore')
links=sorted(set(re.findall(r'https://maps\.app\.goo\.gl/[A-Za-z0-9]+', text)))
print('maplinks',len(links))
for l in links: print(l)
