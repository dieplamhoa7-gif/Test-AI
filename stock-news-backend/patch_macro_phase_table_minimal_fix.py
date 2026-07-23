from pathlib import Path

p=Path('firebase_public/macro.html')
s=p.read_text(encoding='utf-8')
changes={
"<h3>Vì sao hiện tại là cuối chu kỳ mở rộng?</h3>":"<h3>Vì sao hiện tại được xếp vào cuối pha mở rộng?</h3>",
"<div class=\"cap\">Đánh giá đa biến từ chính dữ liệu trên dashboard; không dựa vào một chỉ tiêu đơn lẻ.</div>":"<div class=\"cap\">Đánh giá đa biến từ dữ liệu hiện có; pha vĩ mô được xác định độc lập với diễn biến VN-Index.</div>",
"<h3>Bảng phân tích các giai đoạn chu kỳ vĩ mô và VN-Index</h3>":"<h3>Các giai đoạn chu kỳ vĩ mô và phản ứng của VN-Index</h3>",
"<div class=\"cap\">Thống kê theo khoảng thời gian đã tô nền trên chart. Lợi suất và drawdown VN-Index được tính trực tiếp từ chuỗi tháng của dashboard.</div>":"<div class=\"cap\">Thống kê mô tả theo các pha trên chart. VN-Index chỉ phản ánh phản ứng thị trường, không được dùng để tự xác nhận pha vĩ mô.</div>",
"<th style=\"padding:8px;border-bottom:1px solid var(--line)\">Max drawdown</th>":"<th style=\"padding:8px;border-bottom:1px solid var(--line)\">Drawdown tháng</th>",
"Lưu ý: đây là thống kê mô tả trên dữ liệu tháng của dashboard, không khẳng định quan hệ nhân quả và không phải dự báo lợi suất.":"Lưu ý: GDP là dữ liệu quý được đưa về trục tháng để hiển thị; CPI, tín dụng và M2 là dữ liệu tháng. Các số bình quân vì vậy chỉ mang tính mô tả. Drawdown được tính từ điểm đóng cửa tháng, không phải đáy trong ngày. Pha 2026 là YTD đến kỳ dữ liệu mới nhất, không phải cả năm."
}
for old,new in changes.items():
 if old not in s: raise SystemExit('missing target: '+old[:80])
 s=s.replace(old,new,1)
# Current phase period in table: replace the displayed end with latest dashboard month.
old="<div style=\"color:var(--mut2)\">${x.p.s} → ${x.p.e}</div>"
new="<div style=\"color:var(--mut2)\">${x.p.s} → ${x.p.e>M[M.length-1]?'YTD '+M[M.length-1]:x.p.e}</div>"
if old not in s: raise SystemExit('period target missing')
s=s.replace(old,new,1)
# Tone down causal wording in historical interpretation.
s=s.replace("Thuận lợi: tăng trưởng/thanh khoản hỗ trợ định giá; VN-Index tăng với drawdown được kiểm soát.","VN-Index tăng trong giai đoạn này; đây là phản ứng quan sát được, cần đọc cùng định giá, lãi suất và dòng tiền.",1)
s=s.replace("Bất lợi/risk-off: lợi nhuận kỳ vọng giảm, định giá co lại và VN-Index chịu drawdown mạnh.","VN-Index giảm mạnh trong giai đoạn này; dữ liệu vĩ mô là một phần bối cảnh, không phải nguyên nhân duy nhất.",1)
p.write_text(s,encoding='utf-8')
print('minimal phase table fixes applied')
