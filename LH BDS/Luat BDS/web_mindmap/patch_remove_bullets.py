from pathlib import Path
files=[Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\index.html')]
for f in files:
    s=f.read_text(encoding='utf-8',errors='ignore')
    s=s.replace("<ul>${a.map(x=>`<li>${x}</li>`).join('')}</ul>","<div class=lines>${a.map(x=>`<div class=line>${x}</div>`).join('')}</div>")
    s=s.replace("<ul>${b.points.map(p=>`<li>${p}</li>`).join('')}</ul>","<div class=lines>${b.points.map(p=>`<div class=line>${p}</div>`).join('')}</div>")
    s=s.replace('ul{margin:0;padding-left:18px}', 'ul{margin:0;padding-left:0;list-style:none}.lines{display:grid;gap:6px}.line{padding:0;margin:0}')
    f.write_text(s,encoding='utf-8')
print('removed bullets')
