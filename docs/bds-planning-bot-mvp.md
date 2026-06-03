# BĐS Planning Bot MVP

Mục tiêu: Hòa gửi tọa độ hoặc link Google Maps trong Telegram, bot tự trả báo cáo quy hoạch gồm:

- Mục đích sử dụng đất
- Dân số
- Tầng cao
- MĐXD
- HSSDĐ
- Nguồn và độ tin cậy

## File chính

- `bds_planning_checker.js`: lõi tra cứu quy hoạch theo tọa độ.
- `bds_planning_bot.js`: Telegram polling bot MVP.

## Chạy thử bot

```powershell
$env:TELEGRAM_BOT_TOKEN="<bot-token>"
$env:BDS_ALLOWED_CHAT_IDS="-5161160484"
node bds_planning_bot.js
```

Sau đó gửi vào group BĐS:

```text
10.845790835609225,106.76200727878299
```

hoặc link Google Maps có tọa độ.

## Cú pháp tiền đất / K1

Dùng cú pháp:

```text
TC 10.845790835609225,106.76200727878299
```

Bot sẽ:

- tra quy hoạch/tọa độ như pipeline hiện có;
- xác định đường/phường gần nhất;
- match phụ lục K1;
- hỏi chọn MĐSDĐ;
- hỏi chọn vị trí (VT1 hoặc VT2/3/4);
- trả ra:
  - đơn giá đất;
  - hệ số điều chỉnh mức biến động thị trường;
  - hệ số điều chỉnh quy hoạch (tạm để 1 nếu chưa có phụ lục/quy hoạch chi tiết);
  - hệ số điều chỉnh theo vị trí;
  - đoạn đường được match;
  - ảnh dẫn chứng trang phụ lục PDF.

## Nguyên tắc dữ liệu

- Không tự đoán MĐXD / tầng cao / HSSDĐ nếu chưa có đúng ô quy hoạch hoặc nguồn đủ chắc.
- Nguồn chính thống TP.HCM là ưu tiên cao nhất.
- QH Việt/Guland dùng làm nguồn đối chiếu.
- Nếu chỉ có dữ liệu cấp đồ án, phải ghi rõ là cấp đồ án, không nói thành cấp lô/ô phố.

## Trạng thái MVP

Đã có:

- Parse tọa độ/link.
- Tra endpoint chính thống TP.HCM `api/doan/ranhqhpk`.
- Reverse geocode OSM.
- Report format Telegram.
- Bot polling nhận message có tọa độ/link.

Còn cần làm:

- Connector QH Việt tự động lấy mục đích SDĐ theo tọa độ từ session đăng nhập.
- Mapping QH07/PDF theo mã ô để chốt dân số/tầng cao/HSSDĐ.
- Cơ chế triển khai chạy nền lâu dài.
