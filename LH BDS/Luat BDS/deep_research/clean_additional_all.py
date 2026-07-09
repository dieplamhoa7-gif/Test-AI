import pathlib, re, html
from bs4 import BeautifulSoup
root=pathlib.Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\deep_research\additional_text")
for p in root.glob('*.txt'):
    if p.name.endswith('.clean.txt'): continue
    s=p.read_text(encoding='utf-8',errors='ignore')
    if '<html' in s[:2000].lower(): s=BeautifulSoup(s,'html.parser').get_text('\n')
    s=html.unescape(s); s=re.sub(r'\n\s*\n+','\n',s)
    (root/(p.stem+'.clean.txt')).write_text(s,encoding='utf-8')
