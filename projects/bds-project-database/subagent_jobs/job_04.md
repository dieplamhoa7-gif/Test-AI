# OCR/extraction review job 4

Review these priority chunks. For each chunk/project:
- read raw text from teams_candidate_chunks_with_dates.json by chunk number (1-based)
- inspect linked reports in web/manual_records_merged_reports.js
- extract missing financial/planning/legal facts that are clearly in text
- if only image/attachment marker exists and no local file, mark as attachment_missing
- write JSON result to subagent_jobs/job_04_results.json

## Assigned chunks

### Chunk 77 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Chung cư Hạnh Phúc
- Snippet: Phòng ĐT báo cáo Sếp Admin 01 về sơ bộ DA Chung cư Hạnh Phúc (Nguồn Mr.Khôi), diện tích đất gần 7.000 m2, đường Trần Đại Nghĩa, H.Bình Chánh, TPHCM : 1. Vị trí dự án: Số 10 Trần Đại Nghĩa, H. Bình Chánh, TP HCM, link map. 2. Hiện trạng: + Pháp lý: * Giấy CN QSD đất: 6.952 m2, đất SXKD cấp năm 2005 - thời hạn lâu dài - Chủ là DN tư nhân Thanh Tùng. * QĐ 54

### Chunk 133 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Khu đất Phú Thọ Hòa, Tân Phú
- Snippet: P.ĐT xin báo cáo Sếp Admin 01 về khu đất phường Phú Thọ Hòa, Quận Tân Phú, TP HCM (Nguồn Sếp Tâm) như sau: 1. Pháp lý đất: Diện tích: 13,907.5 m2 Mục đích: Đất trồng cây lâu năm Thời hạn: 50 năm ( 07/2011 – 07/2061) Nguồn gốc sử dụng: Nhà nước công nhận quyền sử dụng đất Vị trí: https://maps.app.goo.gl/v8GdHbU3xb5G8JFs9 Ranh đất: Hạ tang giao t

### Chunk 226 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Danh sách khu đất đấu giá Đồng Nai 2026
- Snippet: P.ĐT đã so sánh đối chiếu danh sách từ 3 phụ lục trên với danh sách đấu giá năm 2025. Qua đó nhận thấy có 1 số khu đất được chuyển tiếp từ kế hoạch 2025 và có bổ sung thêm những khu đất tiềm năng khác. Căn cứ vào vị trí, sự phát triển đô thị của một số khu vực, sự ưu tiên của Cơ quan NN trong triển khai đấu giá (phụ lục 2), phòng đầu tư đề xuất nghiên cứu c

### Chunk 253 · 2026-01-23 · Thao L - INVT
- Image marker: True · Fin text: False · extracted financial items: 1 · linked reports: 1
- Projects: Hoa viên Vĩnh Thanh
- Snippet: Thao L - INVT 1/23/2026 12:02 PM K.ĐT gửi anh Mr Mike1 -CEO cập nhật báo cáo dự án Hoa viên Vĩnh Thanh sau khi có Thông số từ P.QH v… Mà so sánh về hạ tầng, cảnh quan Sala vớ

### Chunk 292 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Đấu giá 102ha Phước An, Nhơn Trạch
- Snippet: P.ĐT báo cáo Sếp Mr Mike1 -CEO về hiệu quả cho dự án đấu giá 102ha, Phước An, Nhơn Trạch, Đồng Nai như sau: 1/ VỊ TRÍ DỰ ÁN ĐẤU GIÁ https://maps.app.goo.gl/QVMCmJp83pMBNKrL8 2/ THÔNG SỐ QUY HOẠCH DỰ ÁN: Theo Phương án đấu giá ngày 10/11/2025 giá khởi điểm 1.696 tỷ đồng. Tuy nhiên, Thông báo đấu giá ngày 24/11/2025 mức giá khởi điểm tăng lên 5.0

### Chunk 350 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Khu nhà ở công nhân và chuyên gia Nhơn Trạch - Công ty TNHH Vạn Phúc
- Snippet: P.ĐT sau khi nghiên cứu hồ sơ pháp lý, vị trí dự án. Có một số đánh giá như sau: 1. Về vị trí: Thuộc trung tâm hành chính mới xã Nhơn Trạch, vị trí cửa ngõ sân bay Long Thành. Xung quanh dự án là KCN, dự án đã triển khai và quy hoạch nhiều dự án nhà ở phát triển trong tương lai. 2. Về quy mô: Quy mô và cơ cấu sản phẩm theo 1/500 được duyệt, bao gồm: STT

### Chunk 408 · 2025-05-25 · Huy M - IM
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Khu đất/khu đô thị Hưng Yên gần Xuân Cầu và Trump International Hưng Yên
- Snippet: Huy M - IM 5/25/2025 4:39 PM Translate Chỗ mình quan tâm nằm giữa Xuân Cầu và Trump Vị trí ok mà, quan trọng là giá đấu thầu nh... by Unknown User

### Chunk 421 · 2025-05-15 · Khang Do - CVDT
- Image marker: True · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: KCN Phước An / Cảng Phước An, Nhơn Trạch
- Snippet: Khang Do - CVDT 5/15/2025 5:11 PM Translate P. ĐT báo cáo anh Mr Mike1 -CEO về dự án KCN Phước An tại xã Phước An, huyện Nhơn Trạch, tỉnh Đồng Nai như sau: 1. THÔNG TIN TỔNG QUAN Tên dự án: Khu công nghiệp Phước An Vị trí: xã Phước An, huyện Nhơn Trạch, tỉnh Đồng Nai Định vị: KCN Phước An Giai đoạn 1+2 và Giai đoạn 3 – Cảng Phước An Diện tích:

### Chunk 482 · 2025-04-08 · Mr Mike1 -CEO
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Khách sạn 25 Trần Phú, Đà Lạt
- Snippet: Mr Mike1 -CEO 4/8/2025 7:38 PM Translate Cái 25 trần phú tính giá đất theo định giá hôm trước làm Begin quote, Thao Le-PTDT , 4/8/2025 7:37 P... by Unknown User

### Chunk 616 · 2024-12-11 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Căn hộ dịch vụ Quận 2 khoảng 1,1ha
- Snippet: Thao L - INVT 12/11/2024 5:31 PM Edited Translate K.ĐT báo cáo anh Mr Mike1 -CEO về Chung cư Phượng Hoàng, Dĩ An, Bình Dương (Nguồn: Mr. Khôi) như sau: 1. Thông tin, vị trí và hiện trạng: - Dự án cao tầng với tổng diện tích đất là 5,537m2, diện tích đất phù hợp quy hoạch là 4,926.4m2. - Giá chuyển nhượng: 275 tỷ ~ 55.8tr/m2 cho 4,926.4m2, cam kết thực hiện

### Chunk 693 · 2024-09-25 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án cao tầng diện tích đất khoảng 10ha
- Snippet: Thao L - INVT 9/25/2024 4:30 PM Edited Translate K.ĐT báo cáo anh Mr Mike1 -CEO về Chung cư Landmark, Dương Đông, Phú Quốc - Nguồn: Mr. Tâm , như sau: 1. Thông tin, vị trí và hiện trạng: - Dự án cao tầng với tổng diện tích đất dự án là 10,490m2 - Giá chuyển nhượng: 65tr/m2 cho phần diện tích chuyển mục đích sử dụng đất - 10,490m2 và đảm bảo phải phù hợp

### Chunk 716 · 2024-06-02 · Tuan Tran-CEO
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Dự án nghỉ dưỡng Greenhill Village / khoản nợ VietinBank Thủ Thiêm
- Snippet: Tuan Tran-CEO 6/2/2024 9:25 AM https://m.cafebiz.vn/ngan-hang-rao-ban-du-an-nghi-duong-nghin-ty-ba-truong-my-lan-tung-thau-tom-176240601115633272.chn?fbclid=IwZXh0bgNhZW0CMTEAAR0gCq068odDwfaVarWXMrVzKJsb5N8mA7iQBstez2vOEGsFuEzu6c2XlSg_aem_AcxQFSkDhP9A9hf7e1nWIyBRpzUs6iL9wF0qP3p0ABLJ4FzSDldhLOZLzi9adCYt-RhJ7elval4J1vy0KIB-0uoU Ngân hàng rao bán dự án nghỉ d

### Chunk 731 · 2023-09-25 · Binh Vo-GD-PTDT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Binh Vo-GD-PTDT 9/25/2023 9:57 AM Với phương án của mình trước là làm phân khúc trung cao cho notm, giá cũng trên 50 tr/m2 và thời điểm ra hàng cho notm a nghĩ cũng nên vào năm 2025, cũng sẽ phù hợp vs tiến độ thực hiện pháp lý hiện trạng của dự án do mình có điều chỉnh qh 1/500, rồi tính tssđ lại... Ok a by Unknown User

### Chunk 811 · 2023-06-16 · Tuan Tran-CEO
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Khu đô thị mới Hậu Nghĩa - Đức Hòa
- Snippet: Tuan Tran-CEO 6/16/2023 7:16 PM https://m.cafef.vn/dien-bien-moi-nhat-khu-do-thi-quy-mo-hon-1-ty-usd-tai-long-an-188230616170401978.chn Diễn biến mới nhất khu đô thị quy mô hơn 1 tỷ USD tại Long An Sở Kế hoạch và Đầu tư tỉnh Long An vừa có Thông báo số 773/TB-SKHĐT mời các nhà đầu tư quan tâm nộp hồ sơ đăng ký thực hiện dự án Khu đô thị mới Hậu Nghĩa - Đứ

### Chunk 919 · 2022-09-23 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Vương Bảo Long, An Bình, Dĩ An
- Snippet: Thao L - INVT 9/23/2022 5:58 PM Em gửi anh Tuan Tran-CEO báo cáo sơ bộ dự án Vương Bảo Long (kèm đánh giá pháp lý) *Hiện trạng: - Vị trí: Đường Bà Giang, An Bình, Dĩ An, Bình Dương. - Khu đất có 02 lối tiếp cận chính: + Đường Bà Giang - lối tiếp cận chính - bề rộng giáp đường rộng khoảng 16m. + Đường vào nghĩa trang - cập phía bên hông khu đất - bề rộng gi
