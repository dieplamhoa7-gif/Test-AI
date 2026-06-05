# Nguồn tự động cập nhật cho các chỉ số vĩ mô trong ảnh

Ngày lập: 2026-06-05

Nguyên tắc:

- Chỉ số daily/trading-day: cập nhật hằng ngày thật sự.
- Chỉ số monthly/quarterly/yearly: daily job vẫn kiểm tra hằng ngày, nhưng giá trị chỉ đổi khi cơ quan công bố kỳ mới.
- Ưu tiên nguồn chính thức/public; FiinProX chỉ là fallback/manual backfill/cross-check.
- Không bypass paywall/login; với TradingEconomics chỉ lấy dữ liệu visible trên trang public bằng Chrome như người dùng thường.

## 1. Bảng nguồn theo nhóm chỉ số

| Nhóm chỉ số | Chỉ số trong hệ thống/ảnh | Nguồn ưu tiên tự động | Link/endpoint | Tần suất thật | Có cập nhật hằng ngày? | Trạng thái |
|---|---|---|---|---|---|---|
| Lãi suất liên ngân hàng | Interbank rate, ON/1W/2W/1M/3M | SBV, Pinetree, TradingEconomics visible | `sbv.gov.vn`, `https://tradingeconomics.com/vietnam/interbank-rate` | Daily/weekly | Có, nhưng có thể lag | Đã có Pinetree + TE visible; cần ổn định `sbv_rates.py` |
| Lãi suất điều hành | Policy rate, refinancing, discount | SBV, TradingEconomics visible | `https://tradingeconomics.com/vietnam/interest-rate` | Khi NHNN thay đổi | Daily job kiểm tra được | Đã có TE visible; cần SBV parser chắc hơn |
| OMO/bơm hút tiền | OMO, reverse repo, net injection | SBV OMO | SBV nghiệp vụ thị trường mở | Daily | Có | Đã có `sbv_omo.py` |
| Lãi suất huy động | Deposit 12M, bank deposit rates | Pinetree cho 12M tổng hợp; website từng ngân hàng cho chi tiết | Pinetree + bank websites | Daily/weekly | Có nếu scrape bank | Pinetree OK; bank scraper chưa làm |
| Tỷ giá | USD/VND, EUR/VND, CNY/VND, JPY, GBP, KRW | Vietcombank XML, SBV central rate | `https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx` | Daily/intraday | Có | Đã có `vcb_fx.py`; nên thêm SBV central rate |
| DXY/USD index | DXY | Yahoo Chart API | Yahoo chart API symbol `DX-Y.NYB` | Daily | Có | Đã có `yfinance_global.py` |
| US rates | US10Y | Yahoo/FRED | Yahoo `^TNX`, FRED `DGS10` | Daily | Có | Yahoo OK; có thể thêm FRED fallback |
| Global equity | S&P500, NASDAQ, DJIA | Yahoo Chart API | Yahoo symbols `^GSPC`, `^IXIC`, `^DJI` | Daily | Có | Đã có Yahoo fallback |
| Global risk | VIX | Yahoo Chart API/FRED | Yahoo `^VIX`, FRED `VIXCLS` | Daily | Có | Đã có Yahoo fallback |
| Commodities | Brent, Gold | Yahoo Chart API/FRED/EIA | Yahoo `BZ=F`, `GC=F` | Daily | Có | Đã có Yahoo fallback |
| VN market | VNINDEX, VN30, HNX, UPCOM, GTGD, khối ngoại | vnstock/SSI/iBoard/Pinetree | vnstock + Pinetree archive | Daily/trading-day | Có | vnstock/Pinetree OK; cần chuẩn hóa foreign flow/turnover |
| CPI headline | CPI YoY/MoM | GSO official, TradingEconomics visible | `gso.gov.vn`, TE CPI pages | Monthly | Daily job kiểm tra; không đổi mỗi ngày | TE visible OK; GSO đang timeout, cần browser scraper theo báo cáo tháng |
| Food CPI | CPI lương thực/thực phẩm | GSO report/table/PDF | GSO monthly socio-economic report | Monthly | Kiểm tra daily, đổi theo tháng | Chưa ổn định; cần GSO/PDF scraper |
| Retail sales | Tổng mức bán lẻ YoY/MoM/YTD | GSO, TradingEconomics visible | GSO, `https://tradingeconomics.com/vietnam/retail-sales-yoy` | Monthly | Kiểm tra daily, đổi theo tháng | TE visible OK; GSO history chưa ổn định |
| IIP/Industrial production | IIP YoY/MoM/YTD | GSO, TradingEconomics visible | GSO, TE industrial production | Monthly | Kiểm tra daily, đổi theo tháng | TE visible OK; cần GSO history |
| PMI | Vietnam PMI | S&P Global press releases, TradingEconomics visible | S&P Global PMI, TE PMI | Monthly | Kiểm tra daily, đổi theo tháng | TE visible có latest; S&P Global scraper chưa làm |
| FDI | FDI registered/disbursed/YTD/project count | FIA/MPI, GSO, TradingEconomics visible | `fia.mpi.gov.vn`, GSO, TE FDI | Monthly | Kiểm tra daily, đổi theo tháng | TE latest OK; FIA/GSO detail chưa code |
| Trade | Exports/imports/trade balance | GSO, Customs, TradingEconomics visible | GSO, Vietnam Customs, TE trade balance | Monthly | Kiểm tra daily, đổi theo tháng | TE latest OK; cần Customs/GSO history |
| Money supply | M0/M1/M2 | SBV, TradingEconomics visible, WorldBank annual proxy | TE M0/M1/M2, SBV if accessible | Monthly | Kiểm tra daily, đổi theo tháng | TE latest OK; SBV monthly history chưa ổn định |
| Credit growth | Private credit/loan growth | SBV/GSO/WorldBank annual proxy | SBV reports, WorldBank API | Monthly/annual | Kiểm tra daily, đổi theo kỳ | WorldBank annual OK; monthly SBV chưa code |
| GDP | GDP real/nominal/growth | GSO official, WorldBank annual | GSO quarterly, WorldBank API | Quarterly/annual | Kiểm tra daily, đổi theo quý/năm | WorldBank OK; GSO quarterly scraper chưa làm |
| Current account/BOP | Current account, capital account, financial account | SBV, IMF, WorldBank annual, FiinProX fallback | SBV/IMF/WorldBank | Quarterly/annual | Kiểm tra daily, đổi theo kỳ | WorldBank annual OK; chi tiết quarterly cần SBV/IMF/FiinProX |
| FX reserves | FX reserves | TradingEconomics visible, IMF, SBV if published | TE FX reserves, IMF IFS | Monthly/quarterly | Kiểm tra daily | TE latest OK; IMF/SBV history chưa code |

## 2. Nguồn ưu tiên để code tiếp

### A. FRED fallback cho Mỹ/global risk

Dùng FRED API không cần login cho nhiều series public:

- `DGS10`: US 10Y Treasury yield
- `VIXCLS`: VIX close
- `DCOILBRENTEU`: Brent crude
- `DTWEXBGS`: broad dollar index proxy

Tần suất: daily. Dùng làm fallback cho Yahoo.

### B. GSO browser scraper cho dữ liệu tháng/quý Việt Nam

Nguồn cần lấy:

- CPI headline và CPI nhóm food
- Retail sales
- IIP
- FDI YTD
- Trade exports/imports
- GDP quarterly

Cách làm:

1. Không gọi homepage chung vì đang timeout.
2. Tìm theo trang/bài báo cáo tháng cụ thể.
3. Dùng Chrome/browser giống người thường.
4. Nếu có bảng hoặc PDF public thì scrape/parse.
5. Lưu raw snapshot trước, parsed sau.

### C. FIA/MPI cho FDI

Nguồn: Cục Đầu tư nước ngoài / Bộ KHĐT.

Chỉ số cần lấy:

- Vốn FDI đăng ký cấp mới
- Vốn FDI điều chỉnh
- Góp vốn/mua cổ phần
- Vốn FDI thực hiện
- Số dự án cấp mới

Tần suất: monthly/YTD.

### D. Vietnam Customs/GSO cho trade

Chỉ số cần lấy:

- Xuất khẩu
- Nhập khẩu
- Cán cân thương mại
- Tăng trưởng YoY/YTD

Tần suất: monthly/YTD.

### E. SBV rates parser

Cần ổn định:

- ON
- 1W
- 2W
- 1M
- 3M
- Refinancing rate
- Discount rate
- OMO rate

Tần suất: daily/weekly.

### F. Bank deposit scraper

Ưu tiên ngân hàng:

- VCB
- BIDV
- CTG/VietinBank
- Agribank
- TCB
- MBB
- VPB
- ACB

Kỳ hạn:

- 1M
- 3M
- 6M
- 12M
- 24M

Tần suất: daily/weekly.

## 3. Gắn vào daily job hiện tại

Daily job đã có:

- Task: `LHInvestment Daily Macro Update`
- Script: `FA/run_daily_macro_update.py`
- Giờ chạy: 08:15 mỗi ngày

Việc cần gắn thêm:

1. `fred_global.py` fallback cho Yahoo.
2. `gso_browser.py` cho CPI/retail/IIP/FDI/trade/GDP.
3. `fia_fdi.py` cho FDI chi tiết.
4. `bank_deposit_rates.py` cho lãi suất huy động ngân hàng.
5. Chuẩn hóa `tradingeconomics_visible_history.csv` để daily snapshot tích lũy lịch sử từ nay.

## 4. Kết luận ngắn

Có thể tự động hóa daily khá tốt cho nhóm **market/liquidity/FX/global risk**: Pinetree, VCB, Yahoo/FRED, SBV OMO, TradingEconomics visible.

Nhóm **macro real economy** như CPI, retail sales, IIP, FDI, GDP không thật sự daily; nên daily job chỉ kiểm tra hằng ngày và cập nhật khi có kỳ tháng/quý mới. Nguồn cần ưu tiên là GSO/FIA/Customs/SBV browser scraper; FiinProX chỉ giữ làm manual fallback và backfill lịch sử.
