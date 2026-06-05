# Browser-based macro data fetch findings

Ngày: 2026-06-05

Hòa Đại ka yêu cầu thử dùng Chrome thao tác như người thường để lấy data.

## GSO

URL thử: `https://www.gso.gov.vn/`

Kết quả Chrome:

- Không vào được.
- Chrome báo `ERR_CONNECTION_TIMED_OUT`.
- Kết luận: trong môi trường hiện tại, GSO vẫn chưa lấy được kể cả bằng browser người thường.

## TradingEconomics

URL thử: `https://tradingeconomics.com/vietnam/interbank-rate`

Kết quả Chrome:

- Vào trang được.
- Đọc được visible public data:
  - Interbank Rate actual/previous/highest/lowest/date/frequency
  - Related table: FX reserves, interbank rate, interest rate, money supply M0/M1/M2
  - Related links: retail sales, inflation CPI, FDI, industrial production, balance of trade, PMI, etc.
- Bấm tab `Download` và `Download Data` được, nhưng hiện popup yêu cầu subscription/login.
- Kết luận: không thể tải CSV/full historical data nếu không login/subscription; nhưng có thể lấy **visible public latest data** bằng browser automation.

## Code mới

File mới:

`FA/macro/fetchers/tradingeconomics_browser.py`

Nó dùng Playwright/Chromium như người dùng thường, không bypass login, chỉ scrape dữ liệu public visible từ các trang:

- interbank-rate
- interest-rate
- money-supply-m0
- money-supply-m1
- money-supply-m2
- inflation-cpi
- inflation-rate-mom
- retail-sales-yoy
- foreign-direct-investment
- industrial-production
- balance-of-trade
- manufacturing-pmi
- foreign-exchange-reserves

Test result:

- Status: OK
- Pages fetched: 13
- Output:
  - `FA/data/tradingeconomics_visible_latest.json`

## Daily runner integration

Đã gắn vào `FA/macro/daily_runner.py`:

- Sau WorldBank, runner sẽ gọi TradingEconomics browser fetcher.
- Output summary được lưu trong snapshot ngày dưới key `tradingEconomicsVisible`.

## Giới hạn

- Đây là visible-data scraper, không phải full history downloader.
- CSV/history download của TradingEconomics yêu cầu subscription/login.
- Không dùng để bypass paywall.
- Dùng tốt cho latest macro public snapshot và cross-check với Pinetree/WorldBank/FiinProX.
