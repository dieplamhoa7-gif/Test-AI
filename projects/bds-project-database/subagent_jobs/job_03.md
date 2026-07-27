# OCR/extraction review job 3

Review these priority chunks. For each chunk/project:
- read raw text from teams_candidate_chunks_with_dates.json by chunk number (1-based)
- inspect linked reports in web/manual_records_merged_reports.js
- extract missing financial/planning/legal facts that are clearly in text
- if only image/attachment marker exists and no local file, mark as attachment_missing
- write JSON result to subagent_jobs/job_03_results.json

## Assigned chunks

### Chunk 63 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: 12ha KDC Vĩnh Phú gần Phú Quang
- Snippet: Khoa L - INVT 6/1 2:31 PM Translate Số thự tự 41, danh sách thí điểm đợt 3 năm 2025 ngày 12/12/2025 - Đề xuất giá bán tại thời điểm mở bán cho... by Admin 01

### Chunk 103 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Chung cư Hải Sơn - Huỳnh Văn Nghệ, Đồng Nai
- Snippet: P.ĐT xin báo cáo sếp Admin 01 về sơ bộ dự án chung cư Hải Sơn có diện tích đất 8.321 m2 (nguồn từ anh Sơn Trợ lý) tại đường Huỳnh Văn Nghệ, P. Biên Hòa, Thành phố Đồng Nai như sau: I. Vị trí và ranh đất: https://www.google.com/maps/d/edit?mid=1pYF3M65dQngj9P_VP8SbXUKy92nYnFo&usp=sharing => Đánh giá sơ bộ hiện trạng: Đường kết nối vào khu đất từ đườ

### Chunk 210 · 2026-03-25 · Admin 01
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Khách sạn Đông Á Premier, Lộc Thọ, Nha Trang
- Snippet: Admin 01 3/25/2026 2:20 PM Ủa bữa a David có gửi bài toán kinh doanh cho Casa rồi, mình có áp lại ra hiệu quả chưa BP.ĐT báo cáo Sếp Admin 01, về dự án khách sạn Đông Á Premier tại Phường Lộc Thọ, TP Nha Trang, Tỉnh Khánh Hòa như sau: I. SƠ BỘ VỀ DỰ ÁN Vị trí: Tọa lạc ở khu vực trung tâm thành phố. Hẻm nhỏ và cụt, rộng khoảng 5m, cách mặt tiền đường Hùng

### Chunk 251 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: 48 Nguyễn Thiện Thuật, Nha Trang
- Snippet: Hanh T - INVT 2/25 3:45 PM Edited Translate P. Đầu tư báo cáo Sếp Admin 01 về hiệu quả dự án 48 Nguyễn Thiện Thuật, TP Nha Trang theo phương án quy hoạch 20 tầng và hệ số 13 lần (phù hợp QH 1/2000, không phải điều chỉnh) như sau: 1. Thông tin pháp lý và quy hoạch: Pháp lý: Diện tích đất theo Giấy chứng nhận: 1.703,3 m2 (đất đã được cấp GCN, ở lâu dài

### Chunk 291 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Đấu giá 102ha Phước An, Nhơn Trạch
- Snippet: P.ĐT báo cáo Sếp Mr Mike1 -CEO về hiệu quả cho dự án đấu giá 102ha, Phước An, Nhơn Trạch, Đồng Nai như sau: 1/ VỊ TRÍ DỰ ÁN ĐẤU GIÁ https://maps.app.goo.gl/QVMCmJp83pMBNKrL8 2/ THÔNG SỐ QUY HOẠCH DỰ ÁN: Theo Phương án đấu giá ngày 10/11/2025 giá khởi điểm 1.696 tỷ đồng. Tuy nhiên, Thông báo đấu giá ngày 24/11/2025 mức giá khởi điểm tăng lên 5.0

### Chunk 304 ·  · 
- Image marker: True · Fin text: False · extracted financial items: 1 · linked reports: 1
- Projects: KĐT An Phú - PG
- Snippet: P.ĐT đã chuẩn bị file file đánh giá sơ bộ vị trí và nguồn cung khu vực. (đính kèm dưới) Cụ thể, dự án có vị trí gần với Fenica và Phú Gia Khiêm. Đây là khu vực có mật độ dân số và tốc độ đô thi hóa cao. Xung quanh tập trung nhiều nhà xưởng, nhà máy, KCN và các dự án cao tầng. Nguồn cung khu vực tính bán kính 4km từ tâm dự án là ~ 10k căn hộ. Do đó mức độ cạn

### Chunk 407 · 2025-05-25 · Huy M - IM
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Khu đất/khu đô thị Hưng Yên gần Xuân Cầu và Trump International Hưng Yên
- Snippet: Huy M - IM 5/25/2025 4:39 PM https://tuoitre.vn/thu-tuong-cung-ong-eric-khoi-cong-du-an-thuong-hieu-trump-dau-tien-tai-viet-nam-20250521175920379.htm Thủ tướng cùng ông Eric khởi công dự án thương hiệu Trump đầu tiên tại Việt Nam - Tuổi Trẻ Online Chiều 21-5, Thủ tướng Phạm Minh Chính dự lễ khởi công dự án khu phức hợp đô thị, du lịch sinh thái và sân g

### Chunk 411 · 2025-05-23 · Huy M - IM
- Image marker: True · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: Dự án NOXH Thiên Lộc / đối tác A Trường - A Tâm
- Snippet: Huy M - IM 5/23/2025 5:36 PM Edited Translate Anh có hỏi A Trường - Thiên Lộc về phương án đầu tư thì ảnh có nói sẽ trao đổi cái với A Tâm sau khi bên mình tính toán hiệu quả xong. Bên Thiên Lộc sẽ làm pháp lý. Bên mình sẽ bỏ vốn và triển khai dự án. Thiên Lộc trước đây cũng chưa làm NOXH. Họ chỉ triển khai NOTM ở Thái Nguyên à Ok by Unknown User

### Chunk 429 ·  · 
- Image marker: False · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Định giá Công ty DXG - Đất Xanh
- Snippet: Báo cáo anh Mr Mike1 -CEO, P.ĐT báo cáo tóm tắt định giá lại Công ty DXG: Áp dụng phương pháp định giá tài sản ròng bằng việc xác định lại giá trị của các dự án/quỹ đất của DXG được ghi nhận trên BCTC. P.ĐT thông tin thêm, việc trình bày thông tin các dự án đã và đang thực hiện trên BCTC, báo cáo thường niên, báo cáo bạch… DXG có phần hạn chế hơn so với DIG

### Chunk 601 · 2024-11-25 · Unknown User
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Dự án Chợ Lớn
- Snippet: Unknown User 11/25/2024 4:30 PM Làm nổi thì chắc dự án chợ lớn có khi phải điều chỉnh ranh Dự án Chợ Lớn đang làm quy hoạch anh Tài đã có cập nhật ranh Metro vào rồi à image by Huy M - IM

### Chunk 692 · 2024-01-09 · Thao L - INVT
- Image marker: False · Fin text: True · extracted financial items: 0 · linked reports: 1
- Projects: KCN/Khu phi thuế quan Xuân Cầu - Lạch Huyện
- Snippet: Thao L - INVT 1/9/2024 5:12 PM K.ĐT báo cáo anh Tuan Tran-CEO về dự án Khu Công Nghiệp Và Khu Phi Thuế Quan Xuân Cầu tại Khu Cảng Cửa Ngõ Quốc Tế Lạch Huyện, Khu Kinh Tế Đình Vũ – Cát Hải, Thành Phố Hải Phòng như sau: I. HIỆN TRẠNG DỰ ÁN 1. Vị trí: Thuộc khu vực cảng cửa ngõ quốc tế Lạch Huyện, Khu kinh tế Đình Vũ - Cát Hải, Thành phố Hải Phòng. Đối diện

### Chunk 715 · 2023-11-03 · Huy M - IM
- Image marker: True · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Huy M - IM 11/3/2023 8:09 AM KĐT đã gửi CEO phương án đề xuất triển khai cho dự án Phú Quang. Do có đính kèm cả dự hiệu quả đầu tư nên gửi bên group này trước à KĐT cũng xin lịch của CEO để có buổi báo cáo chi tiết này cùng các phòng ban liên quan. Begin quote, Huy Mai-PTDT , 11/3/2023 8:11 ... by Unknown User

### Chunk 730 · 2023-09-25 · Binh Vo-GD-PTDT
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: Dự án Phú Quang
- Snippet: Binh Vo-GD-PTDT 9/25/2023 9:55 AM Vì cùng khu, và noxh ko thể bán giá cao được vì bị giới hạn định mức ln 10%, lưu ý chi phí đất ko được phân bổ vào giá thành của noxh vì noxh được miễn tiền sử dụng đất, và tiền bồi thường đất thì được khấu trừ trong tssđ của toàn dự án Với phương án của mình trước là làm phân kh... by Unknown User

### Chunk 773 · 2023-07-07 · Huy M - IM
- Image marker: True · Fin text: False · extracted financial items: 0 · linked reports: 1
- Projects: Dự án 31ha trong Khu du lịch đô thị Đại Phước / Swan Bay và nhóm Swan Park - Sơn Tiên
- Snippet: Huy M - IM 7/7/2023 11:17 AM K. ĐT gửi CEO Tuan Tran-CEO tóm tắt các kết luận của Uỷ Ban Kiểm tra Trung ương ngày 14/06/2023 liên quan đến 3 dự án lớn xảy ra sai phạm nghiêm trọng trong quản lý đất đai của tỉnh Đồng Nai: Khu dân cư Phú Thịnh - Long Tân (tên thương mại: Swan Park); Khu đô thị du lịch sinh thái Đại Phước (tên thương mại: Swan Bay) Khu đô thị

### Chunk 859 · 2023-04-26 · Huy M - IM
- Image marker: False · Fin text: True · extracted financial items: 1 · linked reports: 1
- Projects: CCN Giao Yến, Giao Thủy, Nam Định
- Snippet: Huy M - IM 4/26/2023 10:10 AM Anh có đề xuất nếu được mình xin thêm 75ha bên cạnh để scale dự án mình lên gia tăng hiệu quả đầu tư vì không tốn thêm bộ máy vận hành. Và sẽ ăn theo được khu Vsip khi họ phát triển Link https://goo.gl/maps/nSTM1wgMZyyzcAhg9 by Unknown User

### Chunk 967 · 2022-08-11 · Trieu Nguyen-PTDT
- Image marker: True · Fin text: True · extracted financial items: 2 · linked reports: 1
- Projects: Quỹ đất 54ha liền kề sân bay Phan Thiết
- Snippet: Trieu Nguyen-PTDT 8/11/2022 12:10 PM Edited KĐT gửi anh Tuan Tran-CEO báo cáo dự án 54ha liền kề sân bay Phan Thiết có giá chào 860-900 tỷ: Vị trí và hạ tầng giao thông kết nối - Dự án nằm sát cảng hàng không nội địa Phan Thiết đang trong giai đoạn hoàn thành Chủ trương đầu tư, đã hoàn thành công tác đền bù và giải phóng mặt bằng, phục vụ dân dụng và q
