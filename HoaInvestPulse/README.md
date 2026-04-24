# HoaInvestPulse (PHP)

Website PHP tổng hợp tin **chứng khoán / kinh tế / BĐS** theo thời gian thực (pull RSS khi người dùng mở trang) và tóm tắt nhanh tự động.

## 1) Chạy local

```bash
cd HoaInvestPulse
php -S 127.0.0.1:8080 -t public
```

Mở: `http://127.0.0.1:8080`

## 2) Cấu trúc

- `public/index.php`: giao diện dashboard (auto refresh 60s)
- `public/api.php`: API JSON realtime + summary
- `src/FeedService.php`: đọc RSS + chuẩn hoá dữ liệu
- `src/Summarizer.php`: tóm tắt ngắn theo từ khóa
- `storage/cache/`: cache RSS giảm tải nguồn (tự tạo)

## 3) Nguồn RSS mặc định

- Chứng khoán: CafeF, Vietstock
- Kinh tế: VnExpress Kinh doanh, CafeBiz
- BĐS: VnExpress BĐS, Batdongsan

Bạn có thể sửa feed tại `src/FeedService.php`.

## 4) Gợi ý domain (bắt đầu bằng HoaInvest)

- hoainvestpulse.com
- hoainvesthub.com
- hoainvest360.com
- hoainvestinsight.com
- hoainvestdaily.com

## 5) Lưu ý

- Dữ liệu phụ thuộc RSS từ bên thứ ba.
- Tóm tắt chỉ mang tính tham khảo, không phải khuyến nghị đầu tư.
