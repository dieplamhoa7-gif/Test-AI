# Hướng dẫn deploy phần Vĩ mô cho LHINVT

## Mục tiêu
Triển khai lại trang **Vĩ mô** cho `https://lhinvt.web.app` mà không làm hỏng các trang hiện có như Chứng Khoán, Chứng Quyền, Tin Tức, Báo cáo cổ phiếu, Account.

## Source cần kiểm tra
Thư mục chính phần Vĩ mô:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\Vi mo
```

Các file ứng viên trong thư mục này:

```text
vn_macro_cstt_v2_20260605_AXIS_VISIBLE_MMYY.html
vn_macro_cstt_v2_20260605_KEEP_FRONTEND_DATA_axis_fix.html
vn_macro_cstt_v2_20260605_visible_time_all_charts.html
vn_macro_cstt_v2_20260605_axis_month_year_FIXED.html
vn_macro_cstt_v2_20260605.html
```

Có một source dashboard khác từng được thử nhưng **không nên copy nguyên vào `/macro` nếu chưa tách kỹ router/script**:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\LHINVT_WEB_CLEAN\data\dashboard_static.html
```

Lý do: file này là full dashboard LH Investment, có router/script riêng. Copy nguyên sang `/macro` từng làm web bị lỗi/loạn data.

## Trạng thái live hiện tại
Phần Vĩ mô đã được tạm gỡ khỏi bản live:

- Đã xóa tab/link **Vĩ mô** khỏi nav các trang chính.
- `/macro` hiện là trang redirect/tạm gỡ về `/stocks`.
- Không nên dựa vào `firebase_public/macro.html` hiện tại làm source Vĩ mô vì nó chỉ là placeholder tạm gỡ.

## Project deploy hiện tại
Project frontend/Firebase:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
```

Public folder:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\firebase_public
```

Firebase config:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend\firebase.lhinvt.json
```

Deploy command:

```bash
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
python -X utf8 lhinvt_firebase_deploy.py
```

Live domain:

```text
https://lhinvt.web.app
```

## Cách triển khai khuyến nghị

### Cách A — Dùng file Vĩ mô standalone
Phù hợp nếu muốn trang `/macro` là một báo cáo Vĩ mô độc lập, có chart riêng.

1. Chọn file HTML đúng trong:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\Vi mo
```

2. Khi đưa vào:

```text
stock-news-backend\firebase_public\macro.html
```

**Bắt buộc giữ nguyên `<head>` gốc** của file Vĩ mô, vì trong đó có CSS/JS/chart config.

3. Nếu cần thêm header/nav LH Investment, chỉ inject vào ngay sau thẻ `<body>`, không thay thế head gốc.

Ví dụ nguyên tắc:

```html
<head>
  <!-- giữ nguyên toàn bộ head gốc của file Vĩ mô -->
</head>
<body>
  <!-- inject header/nav ở đây -->
  <!-- giữ nguyên body gốc phía dưới -->
</body>
```

Không được làm kiểu tạo head mới rồi chỉ copy body, vì sẽ mất CSS/JS khiến chart/data không chạy.

### Cách B — Tách phần Vĩ mô từ dashboard clean
Chỉ dùng nếu muốn phần Vĩ mô giống full LH Investment dashboard.

Source:

```text
C:\Users\HoaD-CVDT\.openclaw\workspace\LHINVT_WEB_CLEAN\data\dashboard_static.html
```

Cảnh báo:

- Không copy nguyên file này vào `/macro`.
- Cần tách riêng component hoặc chỉnh router/script cẩn thận.
- Cần đảm bảo `/macro` không làm active nhầm Stocks/Warrants/News.
- Cần test console/network trên live hoặc local trước deploy.

## Những lỗi đã gặp cần tránh

1. **Copy nguyên dashboard_static.html vào `/macro`**
   - Kết quả: script/router cũ làm trang bị lỗi/loạn.

2. **Tạo wrapper mới nhưng bỏ `<head>` gốc của file Vĩ mô**
   - Kết quả: chữ lên nhưng chart/data visual không chạy vì thiếu CSS/JS/chart config.

3. **Chỉ grep source rồi báo verified**
   - Cần mở live page, kiểm console, kiểm canvas/chart thật.

4. **Mojibake tiếng Việt**
   - Luôn đọc/ghi bằng UTF-8.
   - Dùng Python với `encoding='utf-8'` hoặc command `python -X utf8`.

## Checklist sau khi deploy

Sau khi deploy, kiểm:

```text
https://lhinvt.web.app/macro
https://lhinvt.web.app/stocks
https://lhinvt.web.app/cw
https://lhinvt.web.app/news-page
https://lhinvt.web.app/stock-report
https://lhinvt.web.app/account
```

Checklist:

- `/macro` HTTP 200.
- Header/nav hiển thị đúng.
- Chart Vĩ mô có render, không chỉ có text.
- Browser console không có error.
- Network không có 404 cho data/script/CSS quan trọng.
- Tiếng Việt không bị lỗi font/mojibake.
- Các trang khác không bị ảnh hưởng.

## Commit/deploy gần đây liên quan

Một số commit có thể tham khảo hoặc tránh:

```text
1d190c885 Use clean dashboard as macro page        # Không nên dùng lại trực tiếp, từng gây lỗi
19737d727 Restore safe standalone macro page       # Rollback trung gian
99e45b843 Preserve macro report head for charts    # Cách preserve head tốt hơn nhưng vẫn chưa đúng ý anh Hòa
```

Hiện trạng sau yêu cầu gỡ: phần Vĩ mô đã được tạm disable khỏi live để nhóm khác triển khai lại.
