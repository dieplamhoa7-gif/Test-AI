from pathlib import Path
files=[Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\LH BDS\Luat BDS\web_mindmap\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\bds_process_timeline_lawfaithful.html'),Path(r'C:\Users\HoaD-CVDT\.openclaw\workspace\deploy_bds_legal_process\public\bds-legal-process\index.html')]
needle="${arr('Route/rẽ nhánh cần quyết',s.routes)}"
insert="${s.deep_summary?`<div class=box><h3>Phân tích sâu</h3><div class=line>${s.deep_summary}</div></div>`:''}${arr('Điều kiện pháp lý chi tiết',s.detail_conditions||[])}${arr('Trình tự thực hiện',s.detail_steps||[])}${arr('Cơ quan xử lý/tham gia',s.detail_authority||[])}${arr('Thời hạn / thời gian thực tế',s.detail_timeline||[])}${arr('Lỗi thực chiến thường gặp',s.detail_mistakes||[],'risk')}"
for f in files:
    s=f.read_text(encoding='utf-8',errors='ignore')
    if insert not in s:
        s=s.replace(needle, needle+insert)
    f.write_text(s,encoding='utf-8')
print('render deep patched')
