# -*- coding: utf-8 -*-
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'firebase_public'
FILES=[PUBLIC/n for n in ['index.html','stocks.html','news-page.html','cw.html','warrants.html']]
old="""['input','keyup','change'].forEach(ev=>input.addEventListener(ev,run));"""
new="""['input','keyup','change'].forEach(ev=>input.addEventListener(ev,(e)=>{ setTimeout(run,0); },true));"""
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if old in s:
        s=s.replace(old,new)
        p.write_text(s,encoding='utf-8',newline='')
        print('patched',p.name)
    else: print('skip',p.name)
