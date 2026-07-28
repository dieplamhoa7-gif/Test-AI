from pathlib import Path
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Restore visible Vietnamese labels in the compact Model3 page
repls={
'LH Investment - B�o c�o c? phi?u Model3':'LH Investment - Báo cáo cổ phiếu Model3',
'Ch��cng KhoA�n':'Chứng Khoán','V�c mA\'':'Vĩ mô','Ch��cng Quy��?n':'Chứng Quyền','Tin T��cc':'Tin Tức','BA�o cA�o c�� phi���u':'Báo cáo cổ phiếu',
'Nh?p ma: SSI, MWG...':'Nhập mã: SSI, MWG...','Ch?y Model3':'Chạy Model3',
'Link m? notebook sau khi export th�nh c�ng.':'Link mở notebook sau khi export thành công.',
'File NotebookLM ho?c fallback PDF t?i/xem tr�n web.':'File NotebookLM hoặc fallback PDF tải/xem trên web.',
'B�o c�o Word ch? hi?n khi backend da upload file.':'Báo cáo Word chỉ hiện khi backend đã upload file.',
'Chua c�':'Chưa có','Kh�ng g?i du?c l?nh Model3: ':'Không gửi được lệnh Model3: ',
'Dang g?i l?nh...':'Đang gửi lệnh...','Dang g?i l?nh ch?y Model3...':'Đang gửi lệnh chạy Model3...',
'L?i':'Lỗi','L?i poll':'Lỗi poll','?? L?i poll tr?ng th�i: ':'Lỗi poll trạng thái: ',
'dang test...':'đang test...','l?i':'lỗi','NotebookLM auth l?i: ':'NotebookLM auth lỗi: ',
'NotebookLM hi?n kh�ng kh? d?ng; Word v?n ch?y b�nh thu?ng.':'NotebookLM hiện không khả dụng; Word vẫn chạy bình thường.',
'T?i Word':'Tải Word','Chua c� Word':'Chưa có Word','T?i PDF fallback':'Tải PDF fallback','T?i PDF / Slide':'Tải PDF / Slide',
'PDF/Slide l?i NotebookLM':'PDF/Slide lỗi NotebookLM','Ch? NotebookLM t?o PDF/Slide':'Chờ NotebookLM tạo PDF/Slide',
'M? NotebookLM':'Mở NotebookLM','Da d�ng fallback PDF':'Đã dùng fallback PDF','NotebookLM l?i, Word v?n d�ng du?c':'NotebookLM lỗi, Word vẫn dùng được','Dang ch? NotebookLM':'Đang chờ NotebookLM'
}
for a,b in repls.items(): s=s.replace(a,b)
# Lavender action button style matching stock page
css='''\n<style id="lh-stock-report-lavender-actions">\nhtml body #runModel3, html body .tickerbar button:not(.secondary){background:linear-gradient(135deg,#f4eaff 0%,#d8ccff 38%,#b9a4ff 72%,#a78bfa 100%)!important;color:#1c1232!important;border:1px solid rgba(244,234,255,.58)!important;box-shadow:0 12px 30px rgba(167,139,250,.34),0 0 0 1px rgba(255,255,255,.35) inset!important;}\nhtml body button.secondary{background:rgba(244,234,255,.10)!important;color:#efe7ff!important;border:1px solid rgba(216,204,255,.32)!important;}\nhtml body .out a{background:linear-gradient(135deg,#f4eaff 0%,#d8ccff 42%,#a78bfa 100%)!important;color:#1c1232!important;}\n</style>\n'''
if 'lh-stock-report-lavender-actions' not in s:
    s=s.replace('</head>', css+'</head>')
p.write_text(s, encoding='utf-8', newline='')
print('patched stock-report')
