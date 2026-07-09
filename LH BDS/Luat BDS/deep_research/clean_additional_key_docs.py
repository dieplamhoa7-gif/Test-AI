import pathlib, re, json, html
from bs4 import BeautifulSoup
root=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\deep_research\additional_text")
for name in ['274_2026_ND-CP_690308.txt','94_2024_ND-CP_619415.txt','50_2023_QD-UBND_580638.txt']:
    p=root/name
    if not p.exists(): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    if '<html' in s[:1000].lower():
        soup=BeautifulSoup(s,'html.parser')
        txt=soup.get_text('\n')
    else:
        txt=s
    txt=html.unescape(txt)
    txt=re.sub(r'\n\s*\n+', '\n', txt)
    (root/(p.stem+'.clean.txt')).write_text(txt,encoding='utf-8')
    print('\n---',name, 'chars', len(txt))
    lines=[re.sub(r'\s+',' ',x).strip() for x in txt.splitlines() if re.sub(r'\s+',' ',x).strip()]
    for x in lines[:40]: print(x[:240])
