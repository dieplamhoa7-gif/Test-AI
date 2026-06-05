# Trình bày & xuất báo cáo

Module này KHÔNG tự dựng lại công cụ tạo file — môi trường đã có sẵn các skill chuyên dụng. Việc của module: chọn đúng định dạng và **ủy thác** sang skill tương ứng, đồng thời giữ chuẩn trình bày của báo cáo equity research.

## Chọn định dạng theo nhu cầu

| Người dùng muốn | Định dạng | Ủy thác sang skill |
|---|---|---|
| Báo cáo phân tích/định giá dạng văn bản chuyên nghiệp (gửi đi, lưu trữ) | Word `.docx` | skill `docx` |
| Mô hình định giá có công thức, sensitivity, cross-check | Excel `.xlsx` | skill `xlsx` |
| Bản trình bày/pitch cho cổ phiếu | Slides `.pptx` | skill `pptx` |
| Tạo/điền/ghép PDF, hoặc xuất bản báo cáo PDF | `.pdf` | skill `pdf` |
| Dashboard/trang web tương tác hiển thị dữ liệu phân tích | web (HTML/React) | skill `frontend-design` |
| Phân tích nhanh, không cần file | trả lời inline trong chat | — |

**Quy trình ủy thác:** khi đã chốt định dạng file, `view` SKILL.md của skill tương ứng *trước khi* viết bất kỳ code/tạo file nào, rồi làm theo hướng dẫn của skill đó. Nhiều skill có thể cùng áp dụng (vd báo cáo Word có nhúng biểu đồ từ Excel).

## Cấu trúc chuẩn của báo cáo equity research

Khi xuất báo cáo định giá đầy đủ, theo bố cục:

1. **Tóm tắt điều hành:** luận điểm đầu tư, target price + dải giá trị, kết luận chính.
2. **Tổng quan doanh nghiệp & ngành:** mô hình kinh doanh, vị thế, vĩ mô liên quan.
3. **Phân tích cơ bản:** bức tranh tài chính 3–5 năm (số actual), chỉ số cốt lõi, chất lượng lợi nhuận, rủi ro.
4. **Định giá:** phương pháp + giả định (nêu rõ input), kết quả từng phương pháp, **bảng cross-check hội tụ**, sensitivity.
5. **Kịch bản:** thận trọng/cơ sở/lạc quan + dải giá trị.
6. **(Tùy chọn) Phân tích kỹ thuật:** xu hướng, S/R, gợi ý timing.
7. **Rủi ro & lưu ý kế toán:** headwinds, tác động NCI/pha loãng EPS (tách khỏi giá trị nội tại).
8. **Disclaimer:** tư liệu phân tích, không phải lời khuyên đầu tư cá nhân hóa; không thay dữ liệu thị trường cập nhật/ý kiến chuyên gia được cấp phép.

## Chuẩn trình bày số liệu

- Mọi con số kỳ đã qua: ghi rõ là **actual** và nguồn/thời điểm; con số tương lai: ghi rõ là **forecast** kèm giả định.
- Đơn vị nhất quán (tỷ đồng / triệu USD…); ghi rõ kỳ kế toán.
- Bảng biểu cho dữ liệu định lượng; văn xuôi cho luận điểm. Tránh khẳng định "rẻ/đắt" mà không gắn với giả định định giá.
- Ngôn ngữ: tiếng Việt, thuật ngữ tài chính giữ nguyên tiếng Anh (P/E, WACC, FCFF, SOTP…).
