# VAT / Thuế GTGT trong BĐS và FS - Training notes

> Ghi chú nội bộ. Khi tư vấn case thật cần kiểm Luật Thuế GTGT, nghị định/thông tư hướng dẫn và quy định còn hiệu lực tại thời điểm giao dịch.

## Vai trò trong FS dự án BĐS

VAT ảnh hưởng mạnh đến dòng tiền nhưng dễ bị nhầm giữa:

1. VAT đầu ra từ doanh thu bán hàng/cho thuê.
2. VAT đầu vào từ chi phí xây dựng, tư vấn, vận hành được khấu trừ.
3. Chênh lệch VAT phải nộp theo kỳ.
4. Giá bán gồm VAT hay chưa gồm VAT.

## Checklist mô hình hóa VAT

- Giá bán nhập vào đã gồm VAT hay chưa?
- Sản phẩm có chịu VAT không?
- Tỷ lệ VAT áp dụng là bao nhiêu?
- Chi phí nào có VAT đầu vào được khấu trừ?
- Chi phí đất/tiền sử dụng đất có xử lý VAT riêng không?
- Timing VAT đầu ra theo doanh thu hay theo thu tiền?
- Timing VAT đầu vào theo chi phí hay theo hóa đơn?

## Bài học từ FS hiện tại

Trong file FS mẫu, logic dòng tiền dự án:

```text
F276 = Thuế VAT bán hàng
L110 = VAT đầu vào CPXD + VAT chi phí hoạt động
F428 = J107 = F276 - L110
H428 = $F$428 * H274 / $F$274
```

Ý nghĩa:

- Không lấy toàn bộ VAT bán hàng làm VAT phải nộp.
- Phải trừ VAT đầu vào đủ điều kiện.
- Phân bổ chênh lệch VAT phải nộp theo tỷ trọng thực thu từng kỳ.

## Sai lầm thường gặp

- Nhầm VAT đầu ra với VAT phải nộp.
- Nhập giá bán đã gồm VAT nhưng lại cộng VAT lần nữa.
- Không tách phần đất/tiền sử dụng đất khỏi nền tính VAT nếu quy định yêu cầu.
- Không xét timing VAT đầu vào, làm dòng tiền đẹp/sai.

## Cách trả lời khi anh hỏi về VAT dự án

1. Xác định loại sản phẩm và giao dịch.
2. Xác định giá đã gồm VAT hay chưa.
3. Tách doanh thu, VAT đầu ra, doanh thu chưa VAT.
4. Tách chi phí có VAT đầu vào và chi phí không được khấu trừ.
5. Tính chênh lệch VAT phải nộp.
6. Đưa vào FS theo timing hợp lý.

## Cần nạp văn bản gốc

- Luật Thuế GTGT hiện hành và sửa đổi.
- Nghị định/thông tư hướng dẫn VAT đối với BĐS.
- Quy định về giá đất/tiền sử dụng đất khi xác định VAT cho chuyển nhượng BĐS.
