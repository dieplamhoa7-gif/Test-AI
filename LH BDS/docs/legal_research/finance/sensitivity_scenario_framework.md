# Sensitivity & Scenario Framework cho dự án BĐS

## Mục tiêu

Không đánh giá dự án chỉ bằng một kịch bản base. Dự án BĐS nhạy với giá bán, tiền đất, chi phí xây dựng, lãi vay và pháp lý.

## Các biến nên chạy độ nhạy

1. Giá bán
   - -10%, base, +10%.
   - Riêng căn hộ nên so với comparable gần nhất và median ref.

2. Tốc độ bán hàng/thu tiền
   - Bán đúng kế hoạch.
   - Chậm 6 tháng.
   - Chậm 12 tháng.
   - Tỷ lệ hấp thụ thấp hơn.

3. Tiền đất
   - Base.
   - +10%.
   - +20%.
   - Chưa xác định tiền đất: tạo risk buffer riêng.

4. Chi phí xây dựng
   - Base.
   - +5%.
   - +10%.
   - Trượt giá theo thời gian.

5. Lãi vay
   - Base.
   - +1%.
   - +2%.
   - Không giải ngân/không huy động được vốn đúng kế hoạch.

6. Timing pháp lý
   - Đúng kế hoạch.
   - Trễ quy hoạch/giấy phép/mở bán 6-12 tháng.

## Scenario mẫu

### Base case

- Pháp lý đi đúng kế hoạch.
- Giá bán theo median/average ref đã điều chỉnh.
- Chi phí theo dự toán.
- Lãi vay theo giả định hiện tại.

### Downside case

- Giá bán giảm 5-10%.
- Tiền đất tăng 10-20%.
- Chi phí xây dựng tăng 5-10%.
- Mở bán/bàn giao trễ 6-12 tháng.
- Lãi vay tăng 1-2%.

### Stress case

- Không đủ điều kiện mở bán đúng kế hoạch.
- Trễ pháp lý >12 tháng.
- Tiền đất chưa xác định hoặc tăng mạnh.
- Thanh khoản thị trường yếu.

## Cách trình bày cho anh

```text
Base IRR: ...
Downside IRR: ...
Stress IRR: ...
Biến nhạy nhất: ...
Điểm gãy dự án: giá bán tối thiểu / tiền đất tối đa / lãi vay tối đa.
```
