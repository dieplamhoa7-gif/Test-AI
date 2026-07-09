from pathlib import Path
files=[Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\index.html')]
old="${arr('Điều kiện chi tiết',s.detail_conditions||[])}${arr('Các bước thực hiện',s.detail_steps||[])}${arr('Hồ sơ cần chuẩn bị',s.detail_dossier||[])}${arr('Thời hạn / thời gian thực tế',s.detail_timeline||[])}"
for f in files:
    s=f.read_text(encoding='utf-8',errors='ignore')
    # keep only if this block appears after the newer PHÂN TÍCH SÂU insertion; remove duplicates by replacing all occurrences of old compact block
    s=s.replace(old,'')
    f.write_text(s,encoding='utf-8')
print('removed duplicate compact detail render')
