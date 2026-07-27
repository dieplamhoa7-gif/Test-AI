# OCR/extraction review job 2

Review these priority chunks. For each chunk/project:
- read raw text from teams_candidate_chunks_with_dates.json by chunk number (1-based)
- inspect linked reports in web/manual_records_merged_reports.js
- extract missing financial/planning/legal facts that are clearly in text
- if only image/attachment marker exists and no local file, mark as attachment_missing
- write JSON result to subagent_jobs/job_02_results.json

## Assigned chunks

### Chunk 59 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: 12ha KDC Vĩnh Phú gần Phú Quang
- Snippet: Dạ em gởi sếp bảng độ nhạy theo đơn giá đất và tổng giá mua đất (kèm file pdf đã cập nhật bảng độ nhạy) 2026.06.01-Bao cao 12ha Vinh Phu.pdf Làm từ giá 12-14tr nha by Admin 01

### Chunk 102 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Holiday Beach Đà Nẵng
- Snippet: Phòng xin gửi đính kèm báo cáo lời và bảng trình bày + Bảng FS. Trân trọng, BC Trinh bay - DA Holiday Beach - 14.05.2026.pdf BC lời DA Holiday Beach - 14.5.2026.pdf FS Holiday Beach - PA Condotel + Hotel 14.5.2026.pdf Message by Admin 01

### Chunk 203 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Khu đất 35ha/38,8ha Kiên Giang - CKG
- Snippet: Phòng xin gửi đính kèm hình hiện trạng khu đất. DAT RACH GIA.mp4 Vi tri va Ranh dat DA 35ha 1.pdf DAT RACH GIA 1.mp4 Add a vào group Hội AN Riverside cái by Admin 01

### Chunk 235 · 2025-11-06 · Thoi L - ASST.
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Dự án Fenica
- Snippet: Thoi L - ASST. 11/6/2025 5:32 PM Translate Huy M - IM Anh gửi Huy xem qua b/c định giá của Fenica để rà soát điều chỉnh và b/c Sếp, nếu cần nhé. PP so sánh trực tiếp đề xuất giá bán trung bình là 38.4tr/m2. Fenica- Dự thảo định giá DA - Cty Định Giá Việt.pdf Begin quote, Thoi L - ASST. , 11/6/2025 5:3... by Huy M - IM

### Chunk 260 ·  · 
- Image marker: True · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Hoa viên Vĩnh Thanh
- Snippet: Thao L - INVT 1/23 12:02 PM Edited Translate K.ĐT gửi anh Mr Mike1 -CEO cập nhật báo cáo dự án Hoa viên Vĩnh Thanh sau khi có Thông số từ P.QH và S.ĐT từ P.QS như sau: 1. Cập nhật Thông số của P.QH và SĐT của P.QS: a. Diện tích thương phẩm: 290,217m2 ~ 51% b. SĐT All in gồm VAT: 1.898 tr.đ/m2 cho tổng 57ha ~ 1,081 tỷ * Phạm vi tính: - Đất mộ: Xử lý nề

### Chunk 295 · 2025-09-10 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Dự án Phượng Hoàng
- Snippet: Thao L - INVT 9/10/2025 12:08 PM K.ĐT báo cáo anh Mr Mike1 -CEO cập nhật hiệu quả đầu tư dự án Phượng Hoàng theo Chính sá… Vậy chốt PkD phương án này đi Ok Sếp. Anh sẽ báo lại A Cường. by Huy M - IM

### Chunk 391 · 2025-07-16 · Binh D - CVDT
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Định giá 6 tài sản - bổ sung 69 Võ Văn Tần
- Snippet: Binh D - CVDT 7/16/2025 7:01 PM Edited Translate Kính gửi Sếp Mr Mike1 -CEO, P.ĐT báo cáo định giá 6 tài sản như sau: 1.Tài sản 69 Võ Văn Tần, Phường Võ Thị Sáu, Quận 1, TP.HCM + Diện tích đất: 718.4 m2 (Chưa có GCN) + Diện tích xây dựng: nhà biệt thự, diện tích sàn khoảng 1118.3 m2 + Đơn giá đất ở định giá: 705 triệu/m2 đất + Giá trị định giá không ba

### Chunk 410 · 2025-05-25 · Unknown User
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Khu đất/khu đô thị Hưng Yên gần Xuân Cầu và Trump International Hưng Yên
- Snippet: Unknown User 5/25/2025 4:43 PM Vị trí ok mà, quan trọng là giá đấu thầu như thế nào A Hiếu - PL có báo cáo hồ sơ hiện tại xong sẽ đánh giá cần thông tin gì thêm vs mình cũng phải nghiên cứu chi tiết vào phần đấu thầu. Vì bây giờ thí điểm chỉ gỡ 30% cho các hồ sơ hiện trạng đất chưa full ở. Thì dự án sau này chỉ có đấu thầu, đấu giá. Chứ đất full 100% ở thì k

### Chunk 425 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Danh mục 10 khu đất khu đô thị đấu thầu tại Đà Nẵng
- Snippet: Phòng xin gửi kèm báo cáo có thể hiện ranh đất của 05 dự án đề xuất quan tâm theo file đính kèm. Trân Trọng. Message by Hanh T - INVT, has an attachment.

### Chunk 517 · 2025-03-12 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: 02 lô đất đấu giá ven sông Hàn Đà Nẵng - A1-6 Thuận Phước và lô liên quan
- Snippet: Thao L - INVT 3/12/2025 10:17 AM Edited Translate K.ĐT gửi anh Mr Mike1 -CEO báo cáo về 02 lô đất đấu giá tại Đà Nẵng như sau: A. KHU ĐẤT A1 – 6 DỰ ÁN VEN SÔNG HÀN, PHƯỜNG THUẬN PHƯỚC, QUẬN HẢI CHÂU I. THÔNG TIN KHU ĐẤT: - Vị trí : Tiếp giáp Đường Như Nguyệt và Đường Đức Lợi 3, phường Thuận Phước, Quận Hải Châu. - Link: https://maps.app.goo.gl/wbNj

### Chunk 678 · 2024-06-03 · Huy M - IM
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Cảng tổng hợp và container Cái Mép Hạ
- Snippet: Huy M - IM 6/3/2024 9:16 AM https://vnexpress.net/de-xuat-dau-tu-sieu-cang-cai-mep-ha-don-tau-bien-lon-nhat-the-gioi-4753385.html Đề xuất đầu tư 'siêu cảng' Cái Mép Hạ đón tàu biển lớn nhất thế giới Bà Rịa - Vũng Tàu- Dự án cảng tổng hợp và container Cái Mép Hạ được đề xuất đầu tư với tổng vốn 50.820 tỷ đồng, quy mô 351 ha, có thể đón các tàu biển lớn nhấ

### Chunk 707 · 2023-11-27 · Trieu Nguyen-PTDT
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Trieu Nguyen-PTDT 11/27/2023 3:01 PM Edited KĐT gửi anh Tuan Tran-CEO báo cáo Thu gom quỹ đất thuộc phường Bình Chiểu, Thủ Đức, TPHCM: I/ Vị trí: + Khu đất có mặt tiền rộng khoảng 200m, tiếp giáp đường 4A đi ra hướng đường Ngô Chí Quốc và Quốc lộ 13 + Cách Dự án Phú Quang khoảng 350m + Có 2 mặt tiếp xúc kênh rạch II/ Kết nối giao thông đến dự

### Chunk 718 · 2023-10-17 · Trieu Nguyen-PTDT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Trieu Nguyen-PTDT 10/17/2023 4:44 PM Edited KĐT gửi anh Tuan Tran-CEO Báo cáo Đề xuất phát triển và cập nhật hiệu quả dự án Phú Quang. Anh cho team biết ngày phù hợp để sắp xếp 1 cuộc họp với các phòng ban để trình bày về dự án này nhé. Link One Drive: https://belgroupvn.sharepoint.com/:f:/s/BeeGroupCEOOffice-03.KhiuT/Eh2-qh03-h1Mg8xRSbMKqhcBsWsV-FgVm

### Chunk 736 · 2023-09-06 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Khu du lịch sinh thái biển cao cấp Lạc Việt
- Snippet: Thao L - INVT 9/6/2023 3:05 PM Edited K.ĐT báo cáo anh Tuan Tran-CEO về dự án KHU DU LỊCH SINH THÁI BIỂN CAO CẤP LẠC VIỆT như sau: I/ THÔNG TIN DỰ ÁN 1. Vị trí: Xã Thắng Hải, huyện Hàm Tân, tỉnh Bình Thuận. 2. Link map: https://goo.gl/maps/JhPoRTM15vQA7Kk6A 3. Diện tích: 72ha. II/ PHÁP LÝ DỰ ÁN 1. Pháp lý đất: Chưa có hồ sơ. 2. Pháp lý

### Chunk 856 · 2023-04-26 · Huy M - IM
- Image marker: True · Fin text: False · extracted financial items: 1 · linked reports: 1
- Projects: CCN Giao Yến, Giao Thủy, Nam Định
- Snippet: Huy M - IM 4/26/2023 6:11 PM Edited Việc lựa chọn Đầu tư Cụm công nghiệp Giao Yến - Nam Định dựa trên: - Hưởng lợi từ việc đẩy mạnh phát triển hạ tầng giao thông tương lai của Nam Định - Hưởng lợi từ KCN VSIP khi triển khai sẽ tạo thị trường đẩy giá cho KCN khu vực. Dự án CCN Giao Yến cũng đang ở bước đầu xin dự án, sẽ phải thực hiện bồi thường giải p

### Chunk 949 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Khách sạn Regalia Gold, Nha Trang
- Snippet: Báo cáo này không đánh giá chi phí đầu vào bao gồm chi phí duy tu sửa chữa vì khách sạn đã không hoạt động trong giai đoạn dịch và chi phí mua dự án => Nên chưa đánh giá hiệu quả dự án theo yếu tố dòng tiền ** Link Drive: Dự án Regalia - OneDrive (sharepoint.com) ** Nguồn thông tin: chị Ngoc Vo-TL-TGD
