from pathlib import Path
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
old="function renderOutputs(r){const link=u=>API+u;"
new="function renderOutputs(r){const link=u=>{u=String(u||'');if(!u)return '';if(/^https?:\/\//i.test(u))return u;if(/[A-Za-z]:\\\\|[A-Za-z]:\//.test(u)){u='/pipeline/model3/file/'+u.split(/[\\\\/]/).pop()}return API+u};"
if old in s:
    s=s.replace(old,new,1)
elif "function renderOutputs(r){const link=u=>" in s and "split(/[\\\\/]/).pop()" not in s:
    import re
    s=re.sub(r"function renderOutputs\(r\)\{const link=u=>.*?;", new, s, count=1)
p.write_text(s,encoding='utf-8')
