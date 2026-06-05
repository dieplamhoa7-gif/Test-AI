# Nguồn dữ liệu vĩ mô tập trung - LH Investment

Ngày lập: 2026-06-05

File này là bản **curated** từ inventory rộng `macro_data_inventory.*`. Mục tiêu là gom các dữ liệu/code/skill vĩ mô dùng được thật, loại bớt file MIT/PDF/training chỉ có nhắc tới lãi suất/bond nhưng không phải nguồn data macro.

## 1. Bảng nguồn vĩ mô chính

| Nhóm | File | Loại | Nguồn/luồng | Nội dung | Trạng thái sử dụng |
|---|---|---|---|---|---|
| Pinetree daily snapshot | `stock-news-backend/data/macro_cycle_local.json` | data JSON | OpenClaw làm | Snapshot 2026-05-04: liên NH, deposit 12T, TPCP 5Y/10Y, USD/VND, EUR/VND, CNY/VND, S&P500, NASDAQ, VIX, Brent, Gold, VNINDEX, khối ngoại, turnover; có macroScore/phase | Dùng được cho local-test; cần daily history trước khi production |
| Macro overview cache | `stock-news-backend/data/macro_overview.json` | data JSON | OpenClaw làm | Macro score static/older cache với weights marketMomentum, breadth, fx, rates, inflation, credit, pmi, globalRisk | Chỉ tham khảo; thiếu nhiều input thực |
| SBV/NHNN probe | `stock-news-backend/data/macro_probe_local/sbv_probe.json` | data JSON | OpenClaw probe | Kết quả thử crawl các URL SBV/NHNN, HTTP 200 nhưng redirect/trả page shell | Chỉ dùng làm bằng chứng source chưa crawl ổn |
| Pinetree fetch/parser/scorer | `stock-news-backend/app/macro_cycle.py` | code Python | OpenClaw làm | Fetch Pinetree Morning Brief theo ngày, strip HTML, parse metrics, score liquidity/fx/rates/globalRisk/marketFlow | Dùng được bản local-test; cần refactor storage/history |
| Local macro page builder | `stock-news-backend/build_macro_local_page.py` | code Python | OpenClaw làm | Tạo local preview page `local_preview/macro.html` từ macro score | Local-only; không deploy production |
| Macro handoff pack | `claude_handoff/vn_macro_research_pack_2026-06-05.zip` | archive ZIP | OpenClaw tạo để gửi Claude | Gói gồm README, code, data, skill/source map | Đã gửi anh để chuyển Claude |
| Macro skill | `skills/vn-macro-cycle-research/SKILL.md` | skill | OpenClaw làm | Quy trình phân tích/lưu trữ macro regime filter | Dùng làm chuẩn vận hành từ nay |
| Macro source map | `skills/vn-macro-cycle-research/references/macro-source-map.md` | reference | OpenClaw làm | Map nguồn Pinetree, SBV, WiData, TradingEconomics, yfinance, FRED, WorldBank/DBnomics, vnstock | Dùng làm registry nguồn ban đầu |
| Macro inventory full | `macro_data_inventory/macro_data_inventory.csv` | data CSV | OpenClaw làm | Inventory rộng 264 file keyword liên quan macro | Dùng để audit/tìm file; có nhiễu |
| Macro inventory JSON | `macro_data_inventory/macro_data_inventory.json` | data JSON | OpenClaw làm | Bản JSON của inventory rộng | Dùng cho script lọc tiếp |
| Macro inventory report | `macro_data_inventory/macro_data_inventory.md` | report MD | OpenClaw làm | Báo cáo inventory rộng | Dùng đọc nhanh; có nhiễu |

## 2. File Excel/CSV macro

Tại thời điểm quét, không thấy file Excel `.xlsx/.xls` macro rõ ràng trong các vùng chính (`stock-news-backend`, `skills`, `memory`, `claude_handoff`, `reports`, root). Nếu Claude có làm file Excel ở nơi khác hoặc anh có file ngoài workspace, cần gửi/đặt vào workspace rồi em thêm vào registry.

CSV macro rõ ràng hiện có:

- `macro_data_inventory/macro_data_inventory.csv`: inventory do em vừa tạo, không phải dữ liệu thị trường gốc.

## 3. Nguồn bên ngoài đã xác định nhưng chưa có data lịch sử hoàn chỉnh

| Nguồn | Có gì | Tình trạng |
|---|---|---|
| Pinetree Morning Brief | Daily snapshot liên NH, deposit, TPCP, FX, global, VNINDEX, foreign flow, turnover | Public HTML; dùng tốt để bắt đầu lưu daily snapshot từ nay; backfill 1 năm không chắc đủ |
| SBV/NHNN official | Official monetary data | Crawl hiện chưa lấy được bảng cấu trúc; nhiều URL redirect/trả page shell |
| WiData/WiGroup/WiFeed | OMO, bơm hút ròng, tín phiếu, liên ngân hàng, money market | Có vẻ tốt nhất nhưng paywalled/API |
| TradingEconomics | Vietnam interbank rate/history | API/historical full likely paid |
| yfinance/Yahoo | VIX, S&P500, NASDAQ, DXY, US10Y, Brent, WTI, Gold | Dùng tốt cho global risk proxy |
| FRED/pandas-datareader | US/global rates/liquidity | Dùng bổ sung global macro |
| WorldBank/DBnomics/wbgapi | GDP, CPI, trade, FDI, macro chậm | Không dùng timing ngày; dùng context dài hạn |
| vnstock/local market data | VNINDEX/OHLCV/breadth/market liquidity nếu tự tính | Dùng cho marketFlow component |

## 4. Data fields hiện đã có trong `macro_cycle_local.json`

- `interbankOvernight`
- `deposit12m`
- `govBond5y`
- `govBond10y`
- `usdVnd`
- `eurVnd`
- `cnyVnd`
- `sp500`
- `nasdaq`
- `vix`
- `brent`
- `gold`
- `vnindex`
- `foreignNetBuyBn`
- `marketTurnoverBn`

Kết quả mẫu 2026-05-04:

- `macroScore`: 43.6
- `phase`: Cuối chu kỳ / Phòng thủ
- `marketView`: Giảm tỷ trọng, ưu tiên tiền mặt, chỉ mua setup xác suất cao.

## 5. Thiếu quan trọng

Các phần cần bổ sung nếu muốn macro layer nghiêm túc:

1. Daily history 6-12 tháng cho Pinetree snapshot.
2. OMO/bơm hút ròng/tín phiếu NHNN có lịch sử.
3. Lãi suất liên ngân hàng theo kỳ hạn, ít nhất ON/1W/2W/1M.
4. CPI monthly, PMI monthly, credit growth, retail sales/IIP nếu muốn economic cycle thật.
5. Global risk tự fetch hằng ngày qua yfinance/FRED.
6. Market breadth và foreign flow chuẩn hóa từ market data nội bộ.
7. Backtest macroScore theo VNINDEX/VN100 strategy để hiệu chỉnh weights/thresholds.

## 6. Cấu trúc lưu trữ đề xuất cho một nguồn thống nhất

```text
stock-news-backend/data/macro/
├─ registry/
│  └─ macro_sources_registry.json
├─ raw/
│  ├─ pinetree/YYYY-MM-DD.html_or_txt
│  ├─ sbv/YYYY-MM-DD.json
│  └─ global/YYYY-MM-DD.json
├─ parsed/
│  ├─ pinetree/YYYY-MM-DD.json
│  └─ global/YYYY-MM-DD.json
├─ score/
│  └─ YYYY-MM-DD.json
└─ history/
   └─ macro_history.parquet_or_csv
```

## 7. Kết luận vận hành

- Nguồn macro **đã chạy được ngay**: Pinetree snapshot + macro_cycle.py.
- Nguồn macro **chỉ là probe/chưa ổn**: SBV direct crawl.
- Nguồn macro **nên mua/đăng ký nếu muốn production**: WiData/WiFeed hoặc TradingEconomics.
- Nguồn macro **nên thêm ngay bằng free code**: yfinance global risk + daily Pinetree snapshot storage.
