import json,re,unicodedata
from pathlib import Path
BASE=Path(__file__).resolve().parent
MAN=BASE/'manual_10parts'

def norm(s):
    s=unicodedata.normalize('NFD',s or '')
    s=''.join(c for c in s if unicodedata.category(c)!='Mn').lower()
    s=re.sub(r'\b(du an|khu|kdc|kdt|khu do thi|khu dan cu|chung cu|ccn|kcn|resort|the|toa nha)\b',' ',s)
    s=re.sub(r'[^a-z0-9]+',' ',s).strip()
    return ' '.join(w for w in s.split() if len(w)>1)

aliases={
 'the bale phan thiet':'the bale mui ne phan thiet',
 'the bale mui ne':'the bale mui ne phan thiet',
 'green hill quy nhon':'green hill quy nhon',
 'greenhill village quy nhon':'green hill quy nhon',
 'ccn giao yen 75ha giao thuy nam dinh':'ccn giao yen giao thuy nam dinh',
 'cum cong nghiep giao yen giao thuy nam dinh':'ccn giao yen giao thuy nam dinh',
 'kcn thai hoa lien son lien hoa vinh phuc':'kcn thai hoa lien son lien hoa vinh phuc',
 'thai hoa lien son lien hoa vinh phuc':'kcn thai hoa lien son lien hoa vinh phuc',
 'quy dat nguyen huu tho nha be cap nhat 3 97ha':'nguyen huu tho nha be',
 'quy dat 3 4ha nguyen huu tho nha be':'nguyen huu tho nha be',
 'khu nha o dai quang minh thuan giao binh duong':'dai quang minh thuan giao',
 'cao tang viet an thuan giao binh duong':'viet an thuan giao',
 'du an toan thinh phat bai truong phu quoc':'toan thinh phat bai truong phu quoc',
 'hai au bai truong phu quoc':'hai au bai truong phu quoc',
 'redstar to hop van phong khach san chung cu pham van dong da nang':'redstar pham van dong da nang',
 'stown gateway thuan an binh duong':'stown gateway thuan an',
 'du an phu quang cap nhat pa2 pa3':'phu quang',
 'du an 2 769m2 da nang hoang sa':'hoang sa 2769m2 da nang',
}

def key(name):
    n=norm(name)
    return aliases.get(n,n)

records=[]
for fp in sorted(MAN.glob('part_*_manual_records.json')):
    d=json.loads(fp.read_text(encoding='utf-8'))
    for r in d.get('records',[]):
        r=dict(r); r['part']=d.get('part'); r['_key']=key(r.get('project_name',''))
        records.append(r)

groups={}
for r in records: groups.setdefault(r['_key'],[]).append(r)
# heuristic: also group duplicate decisions by extracting after 'existing_project' left as own if no alias
out=[]
for k,rs in groups.items():
    if len(rs)>1 or any('duplicate' in (r.get('decision','')).lower() or 'update' in (r.get('decision','')).lower() for r in rs):
        out.append((k,[(r['part'],r['id'],r['project_name'],r.get('report_date',''),r.get('decision','')) for r in rs]))
for k,items in sorted(out, key=lambda x:(-len(x[1]),x[0])):
    print('\n##',k,'count',len(items))
    for it in items: print(' ',it)
