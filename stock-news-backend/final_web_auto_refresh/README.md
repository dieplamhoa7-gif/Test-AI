# LH Investment FINAL Web Auto Refresh

Bộ này gom toàn bộ pipeline tự động cập nhật web LH Investment vào một chỗ.

## File chính

- `final_refresh.py` — runner duy nhất cho GitHub Actions/local.

## Mode

```bash
python final_web_auto_refresh/final_refresh.py --mode intraday
python final_web_auto_refresh/final_refresh.py --mode eod
python final_web_auto_refresh/final_refresh.py --mode warrants
python final_web_auto_refresh/final_refresh.py --mode news
python final_web_auto_refresh/final_refresh.py --mode all
```

## Workflow GitHub Actions

Root workflow dùng file:

- `.github/workflows/lh-final-web-auto-refresh.yml`

Lý do phải ở root `.github/workflows`: GitHub chỉ đọc workflow ở root repository, không đọc workflow nằm trong `stock-news-backend/.github/workflows` nếu repo root không phải `stock-news-backend`.

## Lịch chạy

- `intraday`: chart chứng khoán trong giờ giao dịch, 09:20-15:20 ICT, weekdays.
- `eod`: stock/EOD/charts/warrants sau đóng cửa, 15:30 ICT, weekdays.
- `warrants`: chứng quyền mỗi giờ trong giờ giao dịch.
- `news`: tin tức mỗi 2 giờ từ 08:10 đến 22:10 ICT.

## Output chính

- Chứng khoán/chart:
  - `data/vn100_history_2025_06_2026_05_cache.json`
  - `firebase_public/data/charts/*.json`
  - `firebase_public/data/charts/index.json`
- EOD/market:
  - `data/eod_all_stocks_hose_hnx.json`
  - `firebase_public/data/eod_all_stocks_hose_hnx.json`
  - `data/eod_top200_marketcap_hose_hnx.json`
  - `firebase_public/data/eod_top200_marketcap_hose_hnx.json`
- Chứng quyền:
  - `firebase_public/data/warrants_data.json`
- Tin tức:
  - `data/news_cache.json`
  - `data/news_cache_en.json`
  - `firebase_public/data/news_cache.json`
  - `firebase_public/data/news_cache_en.json`
- Report kiểm tra:
  - `data/final_auto_refresh_reports/<mode>_latest.json`
  - `firebase_public/data/final_auto_refresh_reports/<mode>_latest.json`

## Deploy

Workflow deploy Firebase Hosting bằng secret:

- `FIREBASE_SERVICE_ACCOUNT_B64`

Không dùng `FIREBASE_TOKEN` cũ.

## Ghi chú vận hành

- `build_stock_chart_cache.py` hiện đọc nguồn `data/vn100_history_2025_06_2026_05_cache.json`.
- Vì vậy chart chỉ mới nếu `refresh_vn100_history_for_core12.py` chạy thành công trước đó.
- Nếu chart web đứng ngày cũ, kiểm tra report:
  - `/data/final_auto_refresh_reports/intraday_latest.json`
  - field `chartMWGLastDate`.
