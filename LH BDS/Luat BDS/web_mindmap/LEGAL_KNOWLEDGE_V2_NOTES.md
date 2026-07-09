# Legal Knowledge Web v2 Notes

## Yêu cầu mới từ Hòa Đại ka

Vai trò nội dung: **Chuyên gia BĐS 30 năm**.

Input:
- Web demo BĐS hiện có, cần fix lại cho rõ hơn.
- Luật file markdown trong `_converted_md_from_docx`.
- Bổ sung luật quan trọng nếu thiếu.
- Tham khảo cách trình bày: https://quytrinhlcndt.netlify.app/

Output mong muốn:
- Một trang web luật về dự án BĐS.
- Tổng hợp, tóm tắt và thông tin liên quan đến dự án BĐS.
- Từ tổng thể, bấm vào ra detail, rồi detail hơn nữa.
- Ví dụ:
  - Bấm “Quy trình phát triển dự án BĐS nhà ở” → ra nhiều bước.
  - Bấm “Chấp thuận chủ trương đầu tư” → ra lựa chọn nhà đầu tư, đấu giá, đấu thầu.
  - Bấm “Đấu giá” → ra điều kiện đất nào phải thông qua đấu giá, căn cứ điều luật.
- Bên cạnh nội dung có flowchart thể hiện luồng.
- Trích dẫn điều luật rõ ràng.
- Tóm tắt điều luật nhưng không mất ý chính và chi tiết quan trọng.

## Bản v2 đã triển khai

Link deploy:

https://hoa-investment.web.app/bds-legal-process/

Files:

- `legal_knowledge_v2.html` — UI web luật mới.
- `legal_knowledge_v2.json` — dữ liệu phân cấp tổng thể → bước → nhánh → căn cứ pháp lý.
- `build_legal_knowledge_v2.py` — script build dữ liệu v2 từ markdown luật.

## Cấu trúc dữ liệu hiện tại

Các node chính:

- `root`: Tổng hợp pháp lý dự án BĐS
- `housing`: Quy trình phát triển dự án BĐS nhà ở
- `p0`: Rà soát quỹ đất và quy hoạch
- `p1`: Quy hoạch, chương trình phát triển nhà ở
- `p2`: Chấp thuận chủ trương đầu tư và lựa chọn NĐT
- `p2_ctdt`: Chấp thuận chủ trương đầu tư
- `p2_lcnt`: Lựa chọn nhà đầu tư
- `p2_daugia`: Đấu giá quyền sử dụng đất
- `p2_dauthau`: Đấu thầu lựa chọn NĐT dự án có sử dụng đất
- `p2_thoathuan`: Thỏa thuận nhận quyền sử dụng đất / đang có quyền sử dụng đất
- `p3`: Giao đất, thuê đất, chuyển mục đích, GPMB
- `p4`: Nghĩa vụ tài chính đất đai
- `p5`: Môi trường, PCCC, hạ tầng đấu nối
- `p6`: Thiết kế, thẩm định, giấy phép xây dựng
- `p7`: Thi công, nghiệm thu, hoàn công
- `p8`: Huy động vốn, bán nhà ở hình thành trong tương lai
- `p9`: Cấp sổ, bàn giao, vận hành, hậu kiểm

## Flowchart hiện tại

Flow chính:

`root → housing → p0 → p1 → p2 → {p2_ctdt, p2_lcnt → p2_daugia/p2_dauthau/p2_thoathuan} → p3 → p4 → p5 → p6 → p7 → p8 → p9`

## Ghi chú nội dung

Bản v2 đã ưu tiên các nhánh trọng yếu:

- Chủ trương đầu tư
- Lựa chọn nhà đầu tư
- Đấu giá quyền sử dụng đất
- Đấu thầu lựa chọn nhà đầu tư
- Thỏa thuận nhận quyền sử dụng đất
- Giao đất/cho thuê đất/chuyển mục đích
- Nghĩa vụ tài chính đất đai
- Bán BĐS hình thành trong tương lai
- Cấp GCN/sổ, bàn giao, vận hành

Một số trích dẫn đã được lấy từ:

- Luật Đất đai 2024 file `31_2024_qh15_523642_full.md`
- Nghị định 102/2024 file `102_2024_nd-cp_603982_full.md`
- Nghị định 103/2024 file `103_2024_nd-cp_550020_full.md`
- Luật Quy hoạch đô thị và nông thôn file `47_2024_qh15_583645_full.md`
- Luật Kinh doanh BĐS/Nghị định hướng dẫn trong các file hiện có

## Thiếu cần bổ sung

Link tham khảo dùng Nghị định 274/2026/NĐ-CP về lựa chọn nhà đầu tư dự án đầu tư kinh doanh. Trong thư mục luật hiện tại có thể chưa có văn bản này, hoặc chưa được parse rõ. Cần bổ sung nếu muốn phần đấu thầu lựa chọn nhà đầu tư giống link mẫu.

Nên bổ sung/rà thêm:

1. Nghị định 274/2026/NĐ-CP và phụ lục quy trình nếu có.
2. Luật Đấu thầu bản hợp nhất/sửa đổi mới nhất liên quan lựa chọn nhà đầu tư.
3. Luật Đầu tư và nghị định hướng dẫn mới nhất về chấp thuận chủ trương đầu tư/chấp thuận nhà đầu tư.
4. Luật Nhà ở 2023 và nghị định/thông tư hướng dẫn nhà ở thương mại, nhà ở xã hội, chung cư.
5. Văn bản địa phương nếu áp cho dự án cụ thể.

## Việc cần làm tiếp

1. Bổ sung nguồn luật còn thiếu.
2. Parse lại điều/khoản/điểm thay vì chỉ Điều.
3. Với mỗi node, chuẩn hóa:
   - Điều kiện áp dụng
   - Hồ sơ
   - Cơ quan xử lý
   - Thời hạn
   - Output
   - Rủi ro
   - Căn cứ pháp lý
4. Thêm nhánh loại dự án:
   - Nhà ở thương mại
   - Nhà ở xã hội
   - Khu đô thị
   - Chung cư
   - Dự án có đất công/đất hỗn hợp
   - Dự án đấu giá đất
   - Dự án đấu thầu lựa chọn NĐT
   - Dự án nhận chuyển nhượng QSDĐ
5. Làm flowchart responsive tốt hơn cho mobile.
