# VAT cho giao dịch BĐS - công thức/checklist cần kiểm

> Trạng thái: notes khung. Cần đối chiếu Luật Thuế GTGT và văn bản hướng dẫn.

## Vấn đề cốt lõi

Trong BĐS, VAT không chỉ là `giá bán * thuế suất`. Cần xác định:

- giá đã gồm VAT hay chưa;
- phần giá đất có được trừ khỏi doanh thu tính VAT không;
- chi phí nào có VAT đầu vào được khấu trừ;
- thời điểm phát sinh nghĩa vụ thuế.

## Công thức tư duy cho FS

```text
VAT đầu ra = doanh thu tính VAT * thuế suất
VAT đầu vào = VAT từ chi phí đủ điều kiện khấu trừ
VAT phải nộp = VAT đầu ra - VAT đầu vào
```

Với giá bán đã gồm VAT:

```text
VAT trong giá = Giá gồm VAT * thuế suất / (1 + thuế suất)
Doanh thu chưa VAT = Giá gồm VAT - VAT trong giá
```

## Checklist giao dịch BĐS

1. Loại giao dịch
   - Bán căn hộ/nhà ở.
   - Chuyển nhượng quyền sử dụng đất.
   - Cho thuê BĐS.
   - Chuyển nhượng dự án/công ty dự án.

2. Giá và hợp đồng
   - Giá gồm VAT/chưa VAT?
   - Có tách giá đất không?
   - Có phụ phí/dịch vụ đi kèm không?

3. Đầu vào
   - Chi phí xây dựng có hóa đơn VAT không?
   - Tư vấn/QLDA/bán hàng có VAT không?
   - Chi phí đất/tiền sử dụng đất xử lý ra sao?

4. Timing
   - VAT phát sinh theo hóa đơn/thu tiền/bàn giao?
   - Dòng tiền FS đang phân bổ theo doanh thu hay thực thu?

## Sai số thường gặp trong model

- Dùng doanh thu gồm VAT làm doanh thu thuần.
- Đưa toàn bộ VAT đầu ra vào dòng tiền phải nộp mà không trừ VAT đầu vào.
- Không tách phần đất khỏi giá tính VAT nếu quy định áp dụng.
- Không phân biệt chủ đầu tư doanh nghiệp và cá nhân chuyển nhượng.

## Liên quan trực tiếp FS hiện tại

Logic đang dùng cho file FS mẫu:

```text
VAT phải nộp = VAT bán hàng - VAT đầu vào CPXD/hoạt động
Phân bổ VAT phải nộp theo tỷ trọng thực thu từng kỳ
```
