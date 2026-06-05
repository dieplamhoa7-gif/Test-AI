# Tổng hợp dữ liệu vĩ mô đã thu thập cho LH Investment

Ngày đóng gói: 2026-06-05  
Phạm vi: tổng hợp lại các thông tin/source/code vĩ mô đã có trong workspace trước thời điểm đóng gói.

## 1. Mục tiêu ban đầu

Xây dựng một lớp **Yếu tố vĩ mô / Macro Cycle** để hỗ trợ hệ thống LH Investment đánh giá môi trường thị trường trước khi ra quyết định giải ngân. Lớp này không thay thế phân tích cổ phiếu, mà đóng vai trò filter/regime:

- Khi macro thuận lợi: có thể tăng tỷ trọng theo tín hiệu kỹ thuật/cơ bản tốt.
- Khi macro trung tính: chọn lọc, mua từng phần, tránh mua đuổi.
- Khi macro xấu/cuối chu kỳ: giảm tỷ trọng, ưu tiên tiền mặt, chỉ mua setup xác suất cao.
- Khi risk-off: bảo toàn vốn, hạn chế giải ngân mới.

## 2. Nguồn dữ liệu đã tìm/đã thử

### 2.1 Pinetree Morning Brief

Nguồn snapshot ngày:

```text
https://pinetree.vn/post/YYYYMMDD/ban-tin-sang-DD-MM-YYYY/
```

Ví dụ snapshot đã lưu:

```text
https://pinetree.vn/post/20260504/ban-tin-sang-04-05-2026/
```

Các field đã parse được từ Pinetree:

- Lãi suất liên NH
- Lãi suất tiết kiệm 12T
- TPCP - 5 năm
- TPCP - 10 năm
- USD/VND
- EUR/VND
- CNY/VND
- S&P500
- NASDAQ
- VIX
- Dầu Brent
- Vàng
- VN-INDEX
- Giá trị mua ròng NĐTNN
- Tổng giá trị giao dịch thị trường

Ưu điểm:

- Có snapshot thực dụng, gần với thị trường chứng khoán hằng ngày.
- Dễ parse HTML hơn nhiều nguồn chính thức.
- Có đủ cụm liquidity/rates/fx/global risk/market flow cho macro filter cơ bản.

Nhược điểm:

- Không phải API chính thức.
- Không có bảo đảm tồn tại mỗi ngày; cuối tuần/ngày nghỉ có thể thiếu.
- Layout HTML có thể thay đổi.
- Không đủ dữ liệu lịch sử 1 năm nếu chỉ crawl backward.
- Không có OMO/CPI/GDP/credit/PMI đầy đủ.

### 2.2 SBV/NHNN official site

Đã probe nhiều URL liên quan:

- `https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/hdh/lslnh`
- `https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/hdh/tttt`
- `https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/hdh/ttm`
- `https://www.sbv.gov.vn/webcenter/portal/vi/menu/trangchu/tk/ls`
- `https://www.sbv.gov.vn/vi/webcenter/portal/vi/menu/trangchu/hdh/lslnh`
- `https://www.sbv.gov.vn/vi/trang-chu`

Kết quả lưu ở:

```text
data/sbv_probe.json
```

Nhận xét:

- HTTP trả 200, không bị blocked theo nghĩa request fail.
- Nhưng nhiều URL bị đưa về trang chủ `https://www.sbv.gov.vn/vi/trang-chu`.
- Text có nhắc tới cấu trúc site/điều hành chính sách tiền tệ, nhưng chưa lấy được bảng dữ liệu liên ngân hàng/OMO có cấu trúc.
- Vì vậy SBV direct crawl hiện chưa đáng tin cho automation.

### 2.3 TradingEconomics

Thông tin đã tìm được:

- Trang `https://tradingeconomics.com/vietnam/interbank-rate` có Vietnam Three Month Interbank Rate.
- Metadata: giai đoạn 1998-2026, frequency daily, source SBV.
- Nhưng guest/free API lịch sử đầy đủ không còn thuận tiện; full API cần paid access.

Kết luận: phù hợp nếu có account/API trả phí; không nên build free automation dựa vào scraping thiếu ổn định.

### 2.4 WiData / WiGroup / WiFeed

Các route/menu liên quan từng ghi nhận:

- `https://widata.vn/vi-mo/vn/bom-hut-rong`
- `https://widata.vn/vi-mo/vn/outright-sbv-bills`
- nhóm dữ liệu macro/monetary data, interest rates, money market, API/WiFeed/MCP.

Nhận xét:

- Có vẻ là nguồn phù hợp nhất cho Việt Nam về OMO/bơm hút ròng/tín phiếu/liên ngân hàng.
- Nhưng dữ liệu/API có paywall. Plan từng quan sát: LITE/PRO/ELITE/API/custom.

Kết luận: nếu cần dữ liệu 1 năm hoàn chỉnh cho OMO + interbank, khả năng cao phải dùng WiData/WiFeed hoặc nguồn trả phí tương đương.

### 2.5 Thư viện Python/GitHub đã đánh giá

- `dbnomics`: tốt cho macro multi-source như IMF/World Bank/OECD/BIS, nhưng cần discovery dataset và không phủ OMO Việt Nam sạch.
- `wbgapi`: tốt cho World Bank annual indicators: GDP growth, CPI annual, FDI, trade; không dùng cho timing ngày/tuần.
- `pandasdmx`: tốt cho SDMX/statistical agencies, nhưng cần map dataset/code.
- `yfinance`: tốt cho global market/risk: S&P500, NASDAQ, VIX, DXY, US10Y, Brent/WTI, gold, regional indices; không có macro Việt Nam sâu.
- `pandas-datareader`/FRED: tốt cho US/global macro; hạn chế cho Việt Nam.
- `vnstock`: tốt cho VNINDEX/OHLCV/market history; không phải macro library.

Kết luận: chưa thấy thư viện free nào cung cấp đầy đủ Vietnam OMO + interbank + CPI + FX + credit/PMI.

## 3. Snapshot dữ liệu đã lưu

File:

```text
data/macro_cycle_local.json
```

Ngày snapshot: `2026-05-04`  
Nguồn: Pinetree Morning Brief  
Status: `local-test`

Các con số chính trong snapshot:

| Nhóm | Field | Giá trị |
|---|---:|---:|
| Liquidity | Lãi suất liên NH | 6.4% |
| Rates | Lãi suất tiết kiệm 12T | 5.9% |
| Rates | TPCP 5 năm | 3.93% |
| Rates | TPCP 10 năm | 4.22% |
| FX | USD/VND | 26,368 |
| FX | EUR/VND | 31,643 |
| FX | CNY/VND | 3,915 |
| Global | S&P500 | 7,209.01 |
| Global | NASDAQ | 27,452.12 |
| Global | VIX | 16.99 |
| Commodity | Brent | 108.17 |
| Commodity | Gold | 4,614.95 |
| Vietnam market | VNINDEX | 1,854.1 |
| Flow | Khối ngoại mua ròng | -1,297.34 tỷ |
| Flow | Tổng GTGD | 22,651.97 tỷ |

Lưu ý: một số số liệu global trong snapshot có thể là dữ liệu từ trang Pinetree giả định theo môi trường tương lai/nguồn tại thời điểm đó; cần kiểm tra lại nếu dùng thật.

## 4. Macro scoring model hiện tại

File code:

```text
code/macro_cycle.py
```

Các component:

1. `liquidity` — trọng số 30%
2. `fx` — trọng số 20%
3. `rates` — trọng số 15%
4. `globalRisk` — trọng số 15%
5. `marketFlow` — trọng số 20%

Kết quả snapshot 2026-05-04:

```text
macroScore: 43.6
phase: Cuối chu kỳ / Phòng thủ
marketView: Giảm tỷ trọng, ưu tiên tiền mặt, chỉ mua setup xác suất cao.
```

Component chính:

- `liquidity`: 32 — bị trừ vì lãi suất liên ngân hàng cao.
- `fx`: 50 — trung tính do thiếu change/ytd.
- `rates`: 50 — trung tính theo threshold hiện tại.
- `globalRisk`: 58 — VIX thấp hỗ trợ.
- `marketFlow`: 39 — khối ngoại bán ròng mạnh, thanh khoản cao.

## 5. Mapping score sang regime

```text
score >= 65: Mở rộng / Risk-on
score >= 50: Trung tính - hồi phục chọn lọc
score >= 40: Cuối chu kỳ / Phòng thủ
score < 40 : Co hẹp / Risk-off
```

## 6. Code đã tạo

### `macro_cycle.py`

Chức năng:

- Build URL Pinetree theo ngày.
- Fetch HTML.
- Strip HTML sang text.
- Parse label/value + optional 1D/YTD.
- Tính macro score.
- Ghi `macro_cycle_local.json`.

Lệnh mẫu:

```bash
py -3 code/macro_cycle.py --date 2026-05-04
```

### `build_macro_local_page.py`

Chức năng trong repo gốc:

- Gọi `app.macro_cycle.build()`.
- Tạo local preview page `stock-news-backend/local_preview/macro.html`.
- Hiển thị score, phase, cards liquidity/rates/fx/global/market flow.

## 7. Đề xuất lưu trữ dữ liệu về sau

### 7.1 Daily snapshots từ Pinetree

Folder đề xuất:

```text
stock-news-backend/data/macro_history/pinetree/YYYY-MM-DD.json
```

Mỗi record nên có:

```json
{
  "date": "YYYY-MM-DD",
  "source": "Pinetree Morning Brief",
  "url": "...",
  "status": "ok|partial|missing|error",
  "fetchedAt": "ISO timestamp",
  "rawTextHash": "sha256",
  "data": {},
  "macroScore": 0,
  "phase": "...",
  "warnings": []
}
```

### 7.2 Source registry

Folder/file đề xuất:

```text
stock-news-backend/data/macro_sources_registry.json
```

Nội dung: danh sách source, fields, frequency, access method, reliability, paid/free, notes.

### 7.3 Không overwrite dữ liệu raw

- Raw/snapshot đã lấy nên immutable theo ngày.
- Nếu parser thay đổi, tạo version mới hoặc lưu `parserVersion`.
- Tách `raw`, `parsed`, `score` để dễ audit.

## 8. Việc Claude nên làm tiếp

1. Review `macro_cycle.py` và tách thành module production-safe hơn:
   - `fetchers/pinetree.py`
   - `scoring/macro_regime.py`
   - `storage/macro_history.py`
   - `reports/macro_summary.py`
2. Thêm job daily snapshot:
   - fetch Pinetree mỗi sáng,
   - lưu `macro_history/pinetree/YYYY-MM-DD.json`,
   - không gửi Telegram group trừ khi user bật.
3. Backfill 1 năm Pinetree:
   - probe từng ngày,
   - status `ok/partial/missing`,
   - không giả định ngày nào cũng có bài.
4. Thêm source global bằng `yfinance` hoặc FRED:
   - VIX, DXY, US10Y, Brent, Gold, S&P500/NASDAQ.
5. Thêm source macro chậm bằng World Bank/DBnomics:
   - GDP, CPI annual/monthly nếu tìm được, credit, trade.
6. Thiết kế source paid adapter placeholder cho WiData/TradingEconomics:
   - không hard-code credentials,
   - dùng env vars,
   - lưu audit log.
7. Backtest macro score với VNINDEX/VN100 strategy:
   - không look-ahead,
   - dùng dữ liệu score snapshot trước phiên,
   - đo EV, drawdown, hit rate, profit factor theo regime.

## 9. Rủi ro và cảnh báo

- Dữ liệu hiện tại chưa đủ để đưa vào production signal.
- Các thresholds scoring hiện là heuristic, chưa được backtest.
- Snapshot Pinetree có thể sai/thiếu/đổi format.
- Source SBV official chưa crawl được bảng cấu trúc.
- OMO/interbank full history cần nguồn trả phí hoặc manual data.
- Đây là tư liệu phân tích, không phải lời khuyên đầu tư cá nhân hóa.
