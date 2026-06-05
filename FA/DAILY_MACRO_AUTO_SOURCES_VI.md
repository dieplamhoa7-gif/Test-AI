# Bản đồ nguồn tự động cập nhật dữ liệu vĩ mô - LH Investment

Ngày lập: 2026-06-05

Mục tiêu: tìm nguồn **tự động cập nhật** thay vì phụ thuộc FiinProX. Không ép tất cả chỉ tiêu thành daily: chỉ tiêu nào bản chất là ngày thì cập nhật hằng ngày; chỉ tiêu tháng/quý/năm thì runner kiểm tra hằng ngày nhưng chỉ đổi khi nguồn phát hành dữ liệu mới.

## 1. Nguồn đã code và chạy được

| Nhóm dữ liệu | Tần suất | Nguồn tự động | File code | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| Bản tin sáng, lãi suất liên NH, deposit 12T, TPCP, FX, VIX, Brent, vàng, VNINDEX, khối ngoại, thanh khoản | Daily/trading-day | Pinetree Bản tin sáng | `FA/macro/fetchers/pinetree.py`, `FA/macro/fetchers/pinetree_archive.py` | **OK** | Đã crawl archive 342 bài, 7,462 dòng. Daily job cập nhật trang mới. |
| FX USD/VND, EUR/VND, CNY/VND, JPY, GBP, KRW | Daily/multiple intraday | Vietcombank XML | `FA/macro/fetchers/vcb_fx.py` | **OK** | Nguồn daily tốt nhất cho FX public. |
| VIX, S&P500, NASDAQ, DXY, US10Y, Brent, Gold | Daily | Yahoo Chart API / yfinance fallback | `FA/macro/fetchers/yfinance_global.py` | **OK** | Đã sửa fallback Yahoo Chart; test 7/7 tickers OK. |
| VNINDEX / VN market | Daily | vnstock/SSI/DNSE/VnDirect fallback | `FA/macro/fetchers/vnstock_market.py` | **OK nhưng có warning** | Lấy được VNINDEX; cần migrate vnstock API mới để bớt warning. |
| OMO / nghiệp vụ thị trường mở | Daily, có lag 1-2 ngày | SBV OMO page qua browser/HTTP | `FA/macro/fetchers/sbv_omo.py` | **OK** | Lấy được bơm/hút ròng và lãi suất OMO. Nên đối chiếu FiinProX lịch sử. |
| TradingEconomics latest visible: interbank, interest rate, M0/M1/M2, CPI, retail sales, FDI, IIP, trade balance, PMI, FX reserves | Daily/latest visible | TradingEconomics bằng headed Chrome | `FA/macro/fetchers/tradingeconomics_browser.py`, `tradingeconomics_deep_scrape.py` | **OK visible data** | Không download CSV, không bypass paywall. Lấy latest visible table; full history cần API/subscription. |
| GDP, CPI annual, FDI annual, current account, broad money %GDP, credit/private %GDP, export/import %GDP | Annual/lagged | WorldBank API | `FA/macro/fetchers/worldbank_macro.py` | **OK** | Runner kiểm tra hằng ngày nhưng số liệu thật cập nhật chậm. |

## 2. Nguồn public có thể bổ sung thêm bằng code

| Nhóm dữ liệu cần thêm | Nguồn đề xuất | Tần suất | Khả năng | Việc cần code |
|---|---|---|---|---|
| CPI monthly / Food CPI | GSO / TradingEconomics visible / báo cáo Tổng cục Thống kê | Monthly | Trung bình | GSO đang timeout; có thể dùng browser khi truy cập được hoặc scrape TradingEconomics latest CPI. Food CPI chi tiết có thể cần GSO PDF/xlsx. |
| Retail sales monthly | GSO / TradingEconomics visible retail-sales-yoy | Monthly | Trung bình | Đã scrape TradingEconomics latest; cần GSO để có lịch sử monthly chuẩn. |
| FDI monthly/YTD | GSO/FIA/MPI hoặc TradingEconomics visible | Monthly | Trung bình | Đã có latest visible TE; cần GSO/FIA để lấy chi tiết số dự án/vốn đăng ký/vốn thực hiện. |
| IIP monthly | GSO hoặc TradingEconomics visible | Monthly | Trung bình | Đã có latest visible TE; cần GSO history. |
| PMI monthly | S&P Global / TradingEconomics visible | Monthly | Trung bình | TE visible có latest; full history có thể trả phí. |
| Lãi suất huy động từng ngân hàng/kỳ hạn | Website từng ngân hàng hoặc aggregator | Daily/weekly | Khó | Phải scrape nhiều ngân hàng, schema không đồng nhất. Có thể ưu tiên Big4 + một số NHTM lớn. |
| Interbank đầy đủ kỳ hạn ON/1W/2W/1M/3M | SBV weekly PDF / TradingEconomics | Weekly/daily | Trung bình | `sbv_rates.py` đã có, cần ổn định PDF parser và lưu lịch sử. |
| Cán cân thanh toán chi tiết quarterly | SBV/GSO/WorldBank/IMF | Quarterly/annual | Khó | WorldBank chỉ có annual tổng. Chi tiết quarterly thường cần SBV report/FiinProX/IMF SDMX. |
| Money supply M2 monthly | SBV/TradingEconomics visible/WorldBank annual proxy | Monthly | Trung bình-khó | TE visible có latest M2; WorldBank annual proxy; cần SBV/GSO để có monthly history. |

## 3. Nguồn đã thử nhưng đang bị giới hạn

| Nguồn | Kết quả | Kết luận |
|---|---|---|
| GSO `https://www.gso.gov.vn/` | Browser và web_fetch đều timeout | Tạm chưa dùng được từ môi trường hiện tại. Cần thử lại lúc khác, dùng browser thật, hoặc tìm endpoint/pdf/xlsx cụ thể. |
| TradingEconomics download CSV | Chrome vào được trang nhưng Download Data yêu cầu subscription/login | Chỉ scrape visible/latest data; không dùng Download. |
| TradingEconomics HTTP thường | `web_fetch`/urllib bị 403 | Dùng headed Chrome Playwright thay thế. |
| SBV qua web_fetch | Một số URL bị Request Rejected | Dùng browser/urllib có User-Agent hoặc parser riêng; OMO hiện OK. |

## 4. Chiến lược cập nhật hằng ngày

Daily job hiện có:

- Windows Task: `LHInvestment Daily Macro Update`
- Giờ chạy: 08:15 mỗi ngày
- Script: `FA/run_daily_macro_update.py`

Mỗi ngày job sẽ:

1. Lấy Pinetree ngày mới và cập nhật Pinetree archive.
2. Lấy VCB FX.
3. Lấy Yahoo/yfinance global risk.
4. Lấy VN market.
5. Lấy SBV rates/OMO.
6. Import FiinProX nếu có file mới trong `FA/`.
7. Lấy WorldBank annual context.
8. Scrape TradingEconomics visible data bằng Chrome.
9. Lưu status/log/history.

## 5. Ưu tiên code tiếp theo

1. **Ổn định SBV rates PDF parser** để lấy đủ ON/1W/2W/1M/3M và policy rates.
2. **GSO browser scraper**: thử lại GSO theo các trang báo cáo tháng cụ thể, không chỉ homepage.
3. **TradingEconomics visible → monthly snapshot history**: lưu mỗi ngày latest CPI/retail/FDI/IIP/PMI để tạo lịch sử từ nay.
4. **Bank deposit scraper**: bắt đầu với Big4 + TCB/MBB/VPB/ACB nếu cần lãi suất huy động từng bank.
5. **Chuẩn hóa scoring mapping**: đưa M2/credit/retail/CPI/FDI/OMO vào macro score có trọng số.

## 6. Kết luận ngắn

Nguồn hằng ngày đã đủ để chạy macro regime core: Pinetree, VCB FX, Yahoo global, VN market, SBV OMO, TradingEconomics visible. Các dữ liệu monthly/quarterly sâu như Food CPI, retail sales history, FDI chi tiết, M2 monthly, BOP chi tiết vẫn cần GSO/SBV cụ thể hoặc FiinProX/WiData/TradingEconomics paid để có lịch sử đầy đủ.
