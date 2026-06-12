# LH Legal & Investment AI - Knowledge Base Index

Mục tiêu: xây một AI nội bộ hỗ trợ Hòa Đại ka trong đầu tư BĐS và chứng khoán, có khả năng trả lời dựa trên nguồn pháp lý/tài chính đã lưu, có trích căn cứ và cảnh báo rủi ro.

## Phạm vi tư vấn ưu tiên

1. Bất động sản / dự án
   - Quy hoạch, đất đai, chuyển mục đích sử dụng đất.
   - Tiền sử dụng đất, tiền thuê đất, bảng giá đất, hệ số K.
   - Luật Kinh doanh BĐS, Luật Nhà ở, điều kiện mở bán/chuyển nhượng/huy động vốn.
   - Quy trình đầu tư dự án, chấp thuận chủ trương đầu tư, đấu giá/đấu thầu dự án có sử dụng đất.

2. Tài chính dự án
   - VAT, TNDN/CIT, TNCN, lệ phí trước bạ, phí/lệ phí liên quan.
   - Lãi vay, vốn hóa lãi vay, dòng tiền dự án, IRR/NPV, độ nhạy.
   - Cấu trúc vốn, vốn chủ, nợ vay, doanh thu/chi phí.

3. Chứng khoán / doanh nghiệp
   - Thuế chuyển nhượng chứng khoán, chuyển nhượng vốn, đầu tư vốn.
   - Công bố thông tin doanh nghiệp niêm yết/chủ đầu tư.
   - Rủi ro pháp lý ảnh hưởng định giá cổ phiếu BĐS.

## Nguyên tắc trả lời

- Không bịa luật, không trả lời chắc chắn nếu chưa có căn cứ.
- Luôn phân biệt: quy định pháp luật, diễn giải, giả định tài chính, nhận định đầu tư.
- Nếu câu hỏi có rủi ro pháp lý cao, phải nêu: `cần kiểm văn bản gốc/cơ quan có thẩm quyền/luật sư`.
- Với số liệu thuế/phí, phải ghi rõ: căn cứ, công thức, phạm vi áp dụng, thời điểm cập nhật.
- Với chứng khoán, không khuyến nghị mua/bán mù; phải nêu rủi ro, giả định, vùng kiểm chứng.

## Các thư mục

```text
tax/                    Thuế, phí, lệ phí
land/                   Đất đai, tiền đất, quy hoạch sử dụng đất
housing/                Nhà ở, mở bán, huy động vốn
real_estate_business/   Kinh doanh BĐS, chuyển nhượng, đặt cọc
investment/             Đầu tư dự án, chủ trương đầu tư, đấu thầu/đấu giá
securities/             Chứng khoán, chuyển nhượng vốn, công bố thông tin
finance/                FS, IRR/NPV, tài chính dự án
prompts/                Prompt/role/checklist cho Legal AI
sources/                Registry nguồn đã đọc/tải
```
