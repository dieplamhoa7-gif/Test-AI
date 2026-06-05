# Public/Official Macro Sources to Reduce FiinProX Dependency

Ngày: 2026-06-05

Mục tiêu: FiinProX là nguồn anh xin được/manual, không đảm bảo có hằng ngày. Vì vậy hệ thống phải ưu tiên nguồn tự động free/official, chỉ dùng FiinProX để backfill/cross-check.

## Kết quả test nguồn public

File test: `FA/data/source_discovery_public_2026-06-05.json`
Script: `FA/macro/source_discovery_public.py`

Nguồn truy cập được:

- WorldBank GDP growth API — OK
- WorldBank CPI inflation API — OK
- WorldBank current account/BOP API — OK
- WorldBank broad money API — OK
- WorldBank private credit API — OK
- VCB FX XML — OK
- Yahoo Chart VIX/DXY — OK
- SBV homepage — OK
- SBV OMO page — OK

Nguồn chưa lấy được trong môi trường hiện tại:

- TradingEconomics interbank page — HTTP 403
- GSO Vietnamese homepage — timeout
- GSO English homepage — timeout

## Mapping thay thế FiinProX theo nhóm dữ liệu

| Nhóm data trong FiinProX | Nguồn public/official thay thế | Trạng thái code | Ghi chú |
|---|---|---|---|
| FX USD/VND, EUR/VND, CNY/VND | Vietcombank XML | Đã có `macro/fetchers/vcb_fx.py`; daily runner đang chạy OK | Dùng VCB làm source chính cho daily FX. FiinProX chỉ backfill/cross-check. |
| Global risk: VIX, S&P500, NASDAQ, DXY, US10Y, Brent, Gold | Yahoo Chart API / yfinance | Đã sửa `macro/fetchers/yfinance_global.py`; test 7/7 OK | Không cần FiinProX. |
| VNINDEX/market flow | vnstock/SSI/DNSE/VnDirect fallback | Đã có `macro/fetchers/vnstock_market.py`; run lấy VNINDEX OK | Cần giảm noise vnstock deprecation sau. |
| OMO/bơm hút ròng | SBV OMO page | Đã có `macro/fetchers/sbv_omo.py`; run lấy OMO OK | Cần cải thiện date parser và đối chiếu Excel FiinProX history. |
| Lãi suất liên NH/SBV rates | SBV weekly PDF + manual override + Pinetree fallback | Đã có `macro/fetchers/sbv_rates.py`, nhưng cần test thêm | Source public có thể dùng nhưng parse PDF cần ổn định. |
| GDP growth | WorldBank API | Đã sửa `macro/fetchers/worldbank_macro.py`; test OK | Annual/lagged, dùng context dài hạn. |
| CPI inflation | WorldBank API | Đã sửa, test OK | Annual; chưa thay thế được CPI monthly/food CPI. |
| Current account/BOP | WorldBank API | Đã sửa, test OK | Annual, thay thế cấp cao cho BOP; không chi tiết như FiinProX quarterly. |
| Broad money/M2 | WorldBank API broadMoney %GDP | Đã sửa, test OK | Annual proxy, không thay thế monthly M2 trong FiinProX. |
| Credit/private sector | WorldBank API creditPrivate %GDP | Đã sửa, test OK | Annual proxy, không thay thế monthly domestic credit. |
| Export/import % GDP | WorldBank API | Đã sửa, test OK | Annual proxy, không thay thế monthly customs/trade. |
| FDI | WorldBank API FDI net inflows | Đã sửa, test OK | Annual; không thay thế FiinProX monthly/YTD FDI cấp mới. |

## Các gap còn lại sau khi bổ sung public sources

Những mục này FiinProX vẫn mạnh hơn và chưa có nguồn free tự động tốt:

1. **Retail sales monthly / retail sales ex-inflation**
   - Cần GSO monthly, nhưng GSO currently timeout từ môi trường này.
   - Có thể thử browser/manual download hoặc RSS/API khác sau.

2. **Food CPI / CPI nhóm thực phẩm monthly**
   - WorldBank chỉ có CPI annual tổng.
   - Cần GSO detailed CPI hoặc nguồn trả phí.

3. **M2 monthly / tiền gửi TCKT / tiền gửi cư dân monthly**
   - WorldBank chỉ có broad money %GDP annual.
   - FiinProX/WiData/SBV statistical releases tốt hơn.

4. **FDI monthly/YTD chi tiết: số dự án cấp mới, vốn đăng ký cấp mới, vốn tăng thêm**
   - WorldBank chỉ có FDI annual net inflows.
   - Cần GSO/FIA monthly hoặc FiinProX.

5. **Lãi suất huy động theo ngân hàng/kỳ hạn**
   - Vẫn chưa có source free toàn bộ ngân hàng.
   - Có thể scrape từng bank nhưng phức tạp, không chuẩn hóa dễ.

6. **BOP/cán cân thanh toán chi tiết quarterly**
   - WorldBank/SBV có annual/current account tổng, nhưng không đủ chi tiết quarterly như FiinProX.

## Vận hành đề xuất

Thứ tự ưu tiên nguồn trong daily macro:

1. Public/official daily source:
   - VCB FX
   - Yahoo Chart global risk
   - SBV OMO
   - SBV rates/Pinetree fallback
   - VN market via vnstock/fallback APIs

2. Public slow macro:
   - WorldBank annual GDP/CPI/FDI/current account/M2 proxy/credit proxy/export/import

3. Manual/premium fallback:
   - FiinProX Excel importer for historical rich data and missing monthly/quarterly fields.

4. Paid production source nếu cần:
   - WiData/WiFeed hoặc TradingEconomics API for OMO/interbank/money market/full history.

## Kết luận

Đã giảm phụ thuộc FiinProX cho daily macro core: FX, global risk, VN market, OMO, WorldBank slow macro. FiinProX vẫn cần cho các series Việt Nam chi tiết/tháng/quý như retail sales, food CPI, M2/deposit monthly, FDI YTD, lãi suất huy động bank-by-bank, và BOP detail.
