# BĐS Bot - K1 / Tiền sử dụng đất

## Cú pháp

```text
TC <tọa độ hoặc link Google Maps>
```

Ví dụ:

```text
TC 10.761185107473432, 106.69015545196933
```

## Files chính

- `bds_planning_bot.js`
  - nhận command `TC` trong `commandKind()`;
  - tạo pending request K1;
  - hỏi chọn MĐSDĐ;
  - hỏi chọn vị trí;
  - gọi `lookupK1LandFee()`;
  - gửi text report + ảnh dẫn chứng.

- `k1_land_fee_lookup.js`
  - đọc `exports/k1_pdf_relevant_extract.json`;
  - normalize tên đường, xử lý hẻm/đường/ký tự Đ/Ð;
  - match phụ lục theo phường + tên đường + đoạn đường;
  - chọn dòng ứng viên có score cao nhất;
  - tính đơn giá điều chỉnh;
  - render ảnh trang PDF dẫn chứng qua `tools/render_pdf_page.py`.

- `tools/render_pdf_page.py`
  - render trang PDF gốc sang PNG để bot gửi ảnh dẫn chứng.

## Flow xử lý

1. User gửi `TC <tọa độ>`.
2. Bot parse tọa độ bằng `parseCoordinateInput()`.
3. Bot gọi `lookupHcmPlanning()` và `summarize()` để lấy:
   - geocode;
   - road/ward/district;
   - thông tin quy hoạch nếu có.
4. Bot lưu request vào `pendingK1Requests`.
5. Bot hỏi chọn MĐSDĐ:
   - `ODT / Đất ở`;
   - `TMD / TMDV`;
   - `SKC / SXKD`.
6. Bot hỏi chọn vị trí:
   - `VT1`;
   - `VT2/3/4`.
7. Bot gọi `lookupK1LandFee()`.
8. Bot trả output gồm:
   - đường/phường phụ lục;
   - đoạn đường;
   - độ tin cậy;
   - đơn giá bảng;
   - hệ số điều chỉnh mức biến động thị trường;
   - hệ số điều chỉnh quy hoạch;
   - hệ số điều chỉnh theo vị trí;
   - tổng hệ số;
   - đơn giá điều chỉnh;
   - chi phí đất sơ bộ nếu tin nhắn có diện tích `m2`;
   - ảnh dẫn chứng trang PDF.

## Logic match đường/đoạn

### Normalize tên đường

`k1_land_fee_lookup.js` xử lý các case:

- `Hẻm 73 Trần Ðình Xu` → `Trần Đình Xu`;
- `Hẻm 623 Đường Cách Mạng Tháng 8` → `Cách Mạng Tháng 8`;
- `Đường 3 Tháng 2` → `3 Tháng 2`;
- ký tự `Đ`, `Ð`, `đ`, `ð` normalize về `d`.

### Match phụ lục

Score ưu tiên:

1. đúng phường/xã header phụ lục;
2. đúng tên đường;
3. đoạn đường có endpoint/POI xuất hiện trong geocode context;
4. loại trừ hit giả nếu tên đường chỉ là endpoint của một đường khác.

Nếu cùng tên đường có nhiều đoạn, bot trả:

- đoạn được chọn;
- độ tin cậy `high/medium`;
- các đoạn ứng viên khác để đối chiếu.

## Công thức tính

```text
Đơn giá điều chỉnh = Đơn giá bảng × K thị trường × K quy hoạch × K vị trí
```

Trong code hiện tại:

- `K thị trường`: đọc từ phụ lục K1 theo loại đất;
- `K quy hoạch`: mặc định `1` nếu chưa có module phụ lục/quy hoạch chi tiết;
- `K vị trí`:
  - `VT1 = 1`;
  - `VT2/3/4 = 1.35`.

Nếu có diện tích trong tin nhắn:

```text
Chi phí đất sơ bộ = Diện tích × Đơn giá điều chỉnh
```

## Các test đã dùng

```text
10.77391896642519, 106.67817857328815
```

- Match: `Vườn Lài | 3 Tháng 2 | Nguyễn Tri Phương - Lê Hồng Phong`.

```text
10.772917530732201, 106.66887977823308
```

- Match: `Hòa Hưng | Sư Vạn Hạnh | Tô Hiến Thành - 3 Tháng 2`.

```text
10.780564556775266, 106.67626666833122
```

- Match: `Hòa Hưng | Cách Mạng Tháng 8 | 3 Tháng 2 - giáp ranh phường Nhiêu Lộc`.

```text
10.761185107473432, 106.69015545196933
```

- Match: `Cầu Ông Lãnh | Trần Đình Xu | Trọn đường`.

## Lưu ý

Đây là bản screening/ước tính sơ bộ. Nghĩa vụ tài chính cuối cùng vẫn cần kiểm tra:

- vị trí 1/2/3/4 thực tế;
- loại đất hiện trạng;
- mục đích sau chuyển;
- diện tích tính tiền;
- hệ số quy hoạch/yếu tố khác nếu áp dụng;
- quy định chuyển tiếp hồ sơ cũ/mới.
