from pathlib import Path
for p in [Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\bds_process_timeline_lawfaithful.html'), Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\bds_process_timeline_lawfaithful.html'), Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\index.html')]:
    s=p.read_text(encoding='utf-8',errors='ignore')
    old="${arr('Route/rẽ nhánh cần quyết',s.routes)}<div class=box><h3>Thủ tục con trong bước này</h3>"
    new="${arr('Route/rẽ nhánh cần quyết',s.routes)}${arr('Điều kiện chi tiết',s.detail_conditions||[])}${arr('Các bước thực hiện',s.detail_steps||[])}${arr('Hồ sơ cần chuẩn bị',s.detail_dossier||[])}${arr('Thời hạn / thời gian thực tế',s.detail_timeline||[])}<div class=box><h3>Thủ tục con trong bước này</h3>"
    if old not in s:
        old="${arr('Route/r? nhánh c?n quy?t',s.routes)}<div class=box><h3>Th? t?c con trong bu?c này</h3>"
        new="${arr('Route/r? nhánh c?n quy?t',s.routes)}${arr('Điều kiện chi tiết',s.detail_conditions||[])}${arr('Các bước thực hiện',s.detail_steps||[])}${arr('Hồ sơ cần chuẩn bị',s.detail_dossier||[])}${arr('Thời hạn / thời gian thực tế',s.detail_timeline||[])}<div class=box><h3>Th? t?c con trong bu?c này</h3>"
    if old in s:
        s=s.replace(old,new)
    else:
        print('pattern not found', p)
    p.write_text(s,encoding='utf-8')
print('html patched')
