# IRR / NPV / Project Finance - Training notes

## Vai trò

IRR và NPV là công cụ sàng lọc hiệu quả dự án, nhưng dễ bị sai nếu giả định pháp lý/thuế/timing sai.

## Các biến ảnh hưởng mạnh nhất

1. Giá bán và tốc độ hấp thụ
   - Giá bán gồm VAT hay chưa?
   - Có đủ comparable thật không?
   - Tiến độ bán hàng có thực tế không?

2. Chi phí đất
   - Tiền sử dụng đất/tiền thuê đất.
   - Timing nộp tiền đất.
   - Rủi ro tăng tiền đất.

3. Chi phí xây dựng
   - Suất vốn đầu tư.
   - Trượt giá.
   - Dự phòng.
   - Timing giải ngân.

4. Lãi vay và cấu trúc vốn
   - Vốn chủ.
   - Tỷ lệ vay.
   - Lãi suất.
   - Vốn hóa lãi vay.
   - Thời điểm trả nợ.

5. Thuế
   - VAT phải nộp.
   - TNDN.
   - Lệ phí/chi phí giao dịch.

6. Pháp lý/timing
   - Trễ quy hoạch/phê duyệt/mở bán.
   - Trễ xây dựng/bàn giao.
   - Không đủ điều kiện huy động vốn.

## Checklist debug IRR lệch

Khi IRR trên web lệch Excel/ver đầu:

1. So dòng vào 274/doanh thu.
2. So chi phí đầu tư 389.
3. So chi phí hoạt động 421.
4. So lãi vay 425.
5. So VAT phải nộp 428.
6. So dòng tiền trước thuế 430.
7. So dòng tài chính 431: giải ngân vay, trả gốc, lãi tiền nhàn rỗi.
8. So công thức IRR dùng dòng nào: dự án hay vốn chủ.

## Quy tắc tư vấn

- Không chỉ nhìn IRR một điểm.
- Luôn chạy độ nhạy giá bán, tiền đất, chi phí xây dựng, lãi vay, timing pháp lý.
- Nếu dự án pháp lý chưa chắc, IRR phải có risk discount hoặc kịch bản delay.
