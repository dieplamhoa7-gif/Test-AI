# OCR/extraction review job 1

Review these priority chunks. For each chunk/project:
- read raw text from teams_candidate_chunks_with_dates.json by chunk number (1-based)
- inspect linked reports in web/manual_records_merged_reports.js
- extract missing financial/planning/legal facts that are clearly in text
- if only image/attachment marker exists and no local file, mark as attachment_missing
- write JSON result to subagent_jobs/job_01_results.json

## Assigned chunks

### Chunk 3 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Richland Quận 9
- Snippet: Phòng Đầu Tư báo cáo Sếp Admin 01 về DA Richland Quận 9. Trên cơ sở báo cáo pháp lý từ phòng Pháp lý DA, P. Đầu tư xin tổng hợp những điểm chính cần lưu ý đối với dự án Richland Quận 9 như sau: 1 .Pháp lý đầu tư và đất : Dự án phải hoàn thành vào tháng 3/2011 => Dự án chậm tiến độ triển khai + Chậm đưa đất vào sử dụng. Cần làm rõ DA đã được gia hạn

### Chunk 86 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 2 · linked reports: 1
- Projects: Gladia Heights - thông tin thị trường tham chiếu
- Snippet: Dạ dự án Gladia heights dự kiến triển khai trong 2026 này, hiện thị trường đang rumor giá 100tr/m2 ạ image Dạ đây là bản đồ các dự án cao tầng g... by Khoa L - INVT

### Chunk 185 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: KDC An Tôn
- Snippet: P.ĐT báo cáo Sếp Admin 01 về hiệu quả dự án KDC An Tôn theo 02 phương án quy hoạch như sau: I. QUY HOẠCH 02 PHƯƠNG ÁN PA 1: Xây dựng NOXH 6 tầng (391 căn), 122 NLK (nhà liên kế) và 111 NBT (nhà biệt thự). PA 2 : Chuyển đổi quỹ đất NOXH -> NLK và NBT, gồm 134 NLK (tăng thêm 12 căn) và 165 NBT (tăng 54 căn). Lý do có PA 2: Tối ưu hóa quỹ đất, tăng giá t

### Chunk 228 ·  · 
- Image marker: True · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Phú Gia Khiêm / PGK
- Snippet: P.ĐT gửi anh Mr Mike1 -CEO cập nhật sau Cuộc họp dự án Phú Gia Khiêm về việc điều chỉnh chỉ tiêu dân số như sau: - Chỉ tiêu dân số của dự án PGK đang được tính: 3.973 dân, trong đó: + Dân số căn hộ ở: 3.500 dân + Dân số officetel: 473 dân - Chỉ tiêu dân số của dự án PGK dự kiến điều chỉnh: 3.673 dân, trong đó: + Dân số căn hộ ở: 3.200 dân (giảm 300 dân

### Chunk 256 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Khu nhà ở Tân Mai - danh sách đấu giá Đồng Nai 2026
- Snippet: P.ĐT báo cáo sếp Admin 01 dự án khu nhà ở Tân Mai (thuộc danh sách dự kiến đấu giá tại Đồng Nai 2026) A) Thông tin chung: - Vị trí: P.Trấn Biên, Đồng Nai - Diện tích toàn khu: 131.690,94 m2 - Mục đích dự án theo QH sử dụng đất và QH xây dựng: KDC nhà ở kết hợp TMDV, cơ sở giáo dục – văn hóa – y tế. B) Định giá đất theo hiệu quả dự án: - Giả định kinh

### Chunk 294 · 2025-09-10 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Dự án Phượng Hoàng
- Snippet: Thao L - INVT 9/10/2025 12:08 PM Translate K.ĐT báo cáo anh Mr Mike1 -CEO cập nhật hiệu quả đầu tư dự án Phượng Hoàng theo Chính sách bán hàng mới từ Mr Cường (SM) như sau: Đã thực hiện tính toán phương án độc lập để đối chiếu cùng với kết quả từ Ms.Hạnh – Phòng Đầu tư. Kết quả từ hai bên tương đương nhau, đảm bảo tính chính xác và đồng nhất của số liệu

### Chunk 351 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Khu nhà ở công nhân và chuyên gia Nhơn Trạch - Công ty TNHH Vạn Phúc
- Snippet: P.ĐT nhận thấy dự án này có các vấn đề pháp lý chưa rõ và cần Phòng pháp lý dự án đánh giá chi tiết, bao gồm: + Nguồn gốc đất ban đầu gồm đất bồi thường (89,166,3 m2) và UBND xã quản lý: 1.443,8 m2. Chưa xác định được hiện trạng mục đích sử dụng đất đã bồi thường. + Chồng ranh quy hoạch với trường Nguyễn Bỉnh Khiêm (khoảng hơn 1460 m2): Chênh lệch về diện

### Chunk 409 · 2025-05-25 · Mr Mike1 -CEO
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Khu đất/khu đô thị Hưng Yên gần Xuân Cầu và Trump International Hưng Yên
- Snippet: Mr Mike1 -CEO 5/25/2025 4:43 PM Translate Vị trí ok mà, quan trọng là giá đấu thầu như thế nào Begin quote, Mr Mike1 -CEO , 5/25/2025 4:43... by Huy M - IM

### Chunk 424 · 2025-05-13 · Hanh T - INVT
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Danh mục 10 khu đất khu đô thị đấu thầu tại Đà Nẵng
- Snippet: Hanh T - INVT 5/13/2025 7:09 PM Edited Translate P.Đầu tư báo cáo Anh Mr Mike1 -CEO về các khu đất dự án đấu thầu tại Đà Nẵng như sau: Theo Báo cáo số 106/BC-UBND của UBND Đà Nẵng ngày 20 tháng 3 năm 2025 về Danh mục các khu đất thực hiện đấu thầu thì có tất cả là 13 khu đất, trong đó gồm 10 khu đất khu đô thị (thông qua Hội đồng nhân dân) và 03 dự án g

### Chunk 489 · 2025-04-03 · Mr Mike1 -CEO
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Khách sạn 25 Trần Phú, Đà Lạt
- Snippet: Mr Mike1 -CEO 4/3/2025 2:35 PM 300 tỷ QĐ 2805 UBNDTP - QUY HOẠCH 1-2000 1.7.2019 (4).pdf Bản vẽ hiện trạng Gia Long.pdf SO DO Gia Long.pdf

### Chunk 669 · 2024-11-09 · Thao L - INVT
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Thấp tầng Phú An Hội, mặt tiền Tôn Đức Thắng (25B)
- Snippet: Thao L - INVT 11/9/2024 11:58 AM Edited Translate K.ĐT báo cáo anh Mr Mike1 -CEO về dự án thấp tầng Phú An Hội giáp mặt tiền Tôn Đức Thắng (25B), Phú Hội, Nhơn Trạch, Đồng Nai như sau (Nguồn: Mr. Ka): I. THÔNG TIN DỰ ÁN - Vị trí: + Tiếp giáp mặt tiền Tôn Đức Thắng (25B), Phú Hội, Nhơn Trạch, Đồng Nai. + Cách ngã tư Tôn Đức Thắng – Nguyễn Hữu Cảnh khoảng

### Chunk 705 · 2023-11-27 · Sinh Nguyen-Dau Tu
- Image marker: True · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Quỹ đất xã Tân Hiệp, Long Thành, Đồng Nai
- Snippet: Sinh Nguyen-Dau Tu 11/27/2023 3:24 PM KĐT gửi anh Tuan Tran-CEO về báo cáo Nghiên cứu Quỹ đất thuộc xã Tân Hiệp, huyện Long Thành, tỉnh Đồng Nai: 1/ Hạ tầng giao thông 1.1/ Hạ tầng trọng điểm Đồng Nai: ● Giao thông: Cao tốc Bến Lức – Long Thành, cao tốc Biên Hòa – Vũng Tàu, cao tốc Long Thành – Dầu Giây; Đường Vành Đai 3, đường Vành Đai 4; Đường Quốc lộ

### Chunk 717 · 2023-10-17 · Unknown User
- Image marker: True · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Unknown User 10/17/2023 4:44 PM KĐT gửi anh Tuan Tran-CEO Báo cáo Đề xuất phát triển và cập nhật hiệu quả dự án Phú Quang. Anh cho team biết ngày phù hợp để sắp xếp 1 cuộc họp với các phòng ban để trình bày về dự án này nhé. Link One Drive: https://belgroupvn.sharepoint.com/:f:/s/BeeGroupCEOOffice-03.KhiuT/Eh2-qh03-h1Mg8xRS… KĐT đã gửi CEO phương án đề xuất

### Chunk 733 · 2023-09-07 · Huy M - IM
- Image marker: True · Fin text: False · extracted financial items: 1 · linked reports: 1
- Projects: Khu du lịch sinh thái biển cao cấp Lạc Việt
- Snippet: Huy M - IM 9/7/2023 5:14 PM Dự án này hồi xưa mình có thông tin nhưng sau đó đề xuất là không quan tâm sâu do có 2 nhược điểm lớn là : Dự án làm khu cao tầng nhưng có khu mộ rất lớn ở sát ngây phía sau 2. Ngay phía trong ranh dự án quy hoạch có đường sắt cắt ngang qua chia làm 2 phần thì phần bên trong không tiếp cận được từ lối chính của dự án mà phải đi

### Chunk 830 · 2023-07-03 · Sinh Nguyen-Dau Tu
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Khảo sát Long Phước/Đông Thủ Đức/Nhơn Trạch
- Snippet: Sinh Nguyen-Dau Tu 7/3/2023 3:17 PM K.ĐT (kết hợp P.R&D) gửi báo cáo anh Tuan Tran-CEO về khảo sát giá mặt tiền các trục đường chính - phía đông TP. Thủ Đức và các dự án phân lô bán nền (không xây nhà) giá rẻ ở Nhơn Trạch, T.Đồng Nai như sau: A/ Khảo sát giá mặt tiền các trục đường chính - phía đông TP. Thủ Đức (Quận 9): Nhận xét về thị trường: Đơn giá

### Chunk 948 · 2022-12-27 · Trieu Nguyen-PTDT
- Image marker: True · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Khách sạn Regalia Gold, Nha Trang
- Snippet: Trieu Nguyen-PTDT 12/27/2022 3:31 PM KĐT gửi anh Tuan Tran-CEO báo cáo dự phòng P&L 5 năm từ 2023 - 2027 cho Khách sạn Regalia Gold 4 sao tại Nha Trang, cụ thể: 1/ Vị trí và hiện trạng: Khách sạn nằm tại đường Nguyễn Thị Minh Khai, P. Tân Lập, Nha Trang, cách bãi biển khoảng 400m Công trình khách sạn 4 sao cao 40 tầng, có 850 phòng 2/ Pháp lý đất: Th
