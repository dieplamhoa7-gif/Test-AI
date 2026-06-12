# FS Legal & Finance Assumptions

Dùng để nối phần pháp lý/thuế với module FS hiệu quả dự án.

## Thuế/phí ảnh hưởng FS

1. VAT/GTGT
   - VAT đầu ra từ doanh thu bán hàng/cho thuê.
   - VAT đầu vào từ chi phí xây dựng, tư vấn, hoạt động đủ điều kiện khấu trừ.
   - Dòng tiền FS cần phân biệt: VAT bán hàng, VAT đầu vào, chênh lệch VAT phải nộp.

2. TNDN/CIT
   - Thuế trên lợi nhuận chịu thuế của doanh nghiệp.
   - Cần tách lợi nhuận kế toán, lợi nhuận tính thuế và timing nộp thuế.

3. Tiền sử dụng đất / tiền thuê đất
   - Là biến số pháp lý-tài chính lớn nhất trong nhiều dự án.
   - Ảnh hưởng trực tiếp TMĐT, vốn chủ/nợ vay và IRR.

4. Lãi vay
   - Lãi vay giai đoạn đầu tư có thể vốn hóa tùy chuẩn mực/kế toán và model.
   - Lãi vay giai đoạn kinh doanh ảnh hưởng dòng tiền và chi phí tài chính.

5. Thuế TNCN
   - Liên quan khi giao dịch là cá nhân/chuyển nhượng tài sản.
   - Không thay thế TNDN trong FS doanh nghiệp chủ đầu tư.

## Bài học từ file FS hiện tại

Dòng VAT phải nộp trong dòng tiền dự án nên theo logic Excel gốc:

```text
F428 = J107 = F276 - L110
H428 = $F$428 * H274 / $F$274
```

Trong đó:

- F276: VAT bán hàng.
- L110: VAT đầu vào CPXD + chi phí hoạt động.
- F428: chênh lệch VAT phải nộp.
- H274/F274: tỷ trọng thực thu từng kỳ.

## Cảnh báo

- Nếu nhầm VAT bán hàng thành VAT phải nộp, dòng tiền bị âm quá mức và IRR lệch mạnh.
- Nếu timing tiền đất/lãi vay sai, IRR cũng lệch đáng kể.
