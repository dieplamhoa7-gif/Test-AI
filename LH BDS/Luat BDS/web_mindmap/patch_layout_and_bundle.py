from pathlib import Path
import shutil
web=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap')
deploy=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process')
files=[web/'bds_process_timeline_lawfaithful.html', deploy/'bds_process_timeline_lawfaithful.html', deploy/'index.html']
for f in files:
    s=f.read_text(encoding='utf-8',errors='ignore')
    s=s.replace('.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}', '.grid{display:grid;grid-template-columns:1fr;gap:13px;align-items:stretch}')
    s=s.replace('.box{background:#fffdf8;border:1px solid var(--line);border-radius:16px;padding:14px;margin-top:13px}', '.box{background:#fffdf8;border:1px solid var(--line);border-radius:16px;padding:14px;margin-top:13px;min-width:0;max-width:100%;overflow:visible;overflow-wrap:anywhere;white-space:normal}')
    s=s.replace('.card{background:var(--paper);border:1px solid var(--line);border-radius:24px;padding:22px;box-shadow:0 12px 28px #0000000b}', '.card{background:var(--paper);border:1px solid var(--line);border-radius:24px;padding:22px;box-shadow:0 12px 28px #0000000b;min-width:0;max-width:100%;overflow:visible}')
    s=s.replace('.wrap{display:grid;grid-template-columns:430px 1fr;gap:22px;padding:22px clamp(18px,4vw,56px)}', '.wrap{display:grid;grid-template-columns:minmax(300px,430px) minmax(0,1fr);gap:22px;padding:22px clamp(18px,4vw,56px)}')
    s=s.replace('.line{padding:0;margin:0}', '.line{padding:0;margin:0;overflow-wrap:anywhere;word-break:normal;white-space:normal}')
    s=s.replace('<main><section', '<main style="min-width:0;overflow:visible"><section')
    f.write_text(s,encoding='utf-8')
final=Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\FINAL_BDS_LEGAL_WEB')
final.mkdir(parents=True,exist_ok=True)
shutil.copy2(web/'bds_process_timeline_lawfaithful.html', final/'index.html')
shutil.copy2(web/'bds_process_timeline_lawfaithful.html', final/'bds_process_timeline_lawfaithful.html')
shutil.copy2(web/'bds_process_timeline_lawfaithful.json', final/'bds_process_timeline_lawfaithful.json')
shutil.copy2(web/'bds_process_timeline_lawfaithful.json', deploy/'bds_process_timeline_lawfaithful.json')
print('layout fixed and bundled', final)
