# Đối chiếu data vĩ mô trong file FA/Excel MWG

Phạm vi: chỉ đọc file FA `skills/vn-equity-research/references/phan-tich-co-ban.md` và các Excel định giá/FA MWG ở root workspace (`MWG_valuation_model*.xlsx`, `MWG_SOTP_Scenarios.xlsx`).

## 1. File FA yêu cầu các mục vĩ mô nào?

Trong `phan-tich-co-ban.md`, mục **Vĩ mô liên quan** nêu rõ:

- GDP
- Tăng trưởng bán lẻ thực
- CPI
- Mặt bằng lãi suất tiền gửi
- Chu kỳ ngành

## 2. Excel FA MWG có thêm các mục vĩ mô nào?

Các sheet `Macro_VN`, `Macro_Drivers`, `Industry_Drivers`, `Methodology`, `Sources` trong bộ Excel MWG có các biến:

| Nhóm | Biến trong Excel | Ý nghĩa trong FA/định giá MWG |
|---|---|---|
| Tăng trưởng tiêu dùng | `VN nominal retail sales growth` | Anchor tổng cầu retail/TGDD/ĐMX |
| Tăng trưởng thực/thu nhập | `GDP/thu nhập hộ gia đình`, `retail sales ex-inflation` | Sức mua hộ gia đình, nhu cầu ICT/CE/grocery |
| CPI | `Food CPI / pricing pass-through`, `CPI thực phẩm` | Doanh thu danh nghĩa BHX, gross margin, sức mua |
| Lãi suất/tín dụng | `Lãi suất/tín dụng tiêu dùng`, `Policy rate`, `consumer finance growth` | Mua trả góp điện thoại/điện máy, cost of capital |
| Tỷ giá | `USD/VND pressure` | Hàng nhập khẩu electronics/phones, vendor pricing |
| Ngành bán lẻ thực phẩm | `Food retail modern trade growth`, `modern trade penetration` | Anchor cho BHX |
| Niềm tin tiêu dùng | `consumer confidence`, `chu kỳ thay máy` | Replacement cycle điện thoại/điện máy |
| Chi phí vốn | `WACC`, `risk-free/cost of capital` | DCF/sensitivity |
| Nguồn đề xuất | `General Statistics Office Vietnam` | GDP/CPI/retail sales |

## 3. Mục Excel có nhưng nguồn hệ thống mình CHƯA lấy được tự động

| Mục data | Excel có? | Hệ thống mình đã có? | Kết luận |
|---|---:|---:|---|
| GDP / thu nhập hộ gia đình | Có | Chưa có fetcher actual định kỳ | **Thiếu nguồn tự động**. Nên lấy GSO/WorldBank/DBnomics, nhưng dữ liệu chậm/quý/năm. |
| Tăng trưởng bán lẻ thực / retail sales ex-inflation | Có | Chưa có | **Thiếu**. Cần GSO monthly retail sales + CPI để deflate. |
| VN nominal retail sales growth | Có | Chưa có | **Thiếu**. Cần GSO monthly retail sales. |
| Food CPI / CPI thực phẩm | Có | Chưa có | **Thiếu**. Cần GSO CPI nhóm lương thực/thực phẩm hoặc nguồn macro trả phí. |
| Consumer finance growth / tín dụng tiêu dùng | Có | Chưa có | **Thiếu**. Khó lấy free; có thể cần NHNN/Fiin/WiData/consumer finance reports. |
| Policy rate | Có | Một phần gián tiếp qua Pinetree/deposit/interbank | **Chưa chuẩn**. Cần NHNN policy rates hoặc nguồn lịch sử. |
| Deposit rate / mặt bằng lãi suất tiền gửi | File FA yêu cầu; Pinetree có snapshot | Có snapshot 1 ngày trong `macro_cycle_local.json` | **Có tạm**, nhưng thiếu lịch sử daily/monthly. |
| USD/VND pressure | Có | Có snapshot USD/VND từ Pinetree | **Có tạm**, nhưng thiếu lịch sử/pressure YTD tự động. |
| Modern trade grocery growth / penetration | Có | Chưa có | **Thiếu**. Có thể phải dùng báo cáo ngành/Euromonitor/Statista/AC Nielsen/Kantar/Masan/WinCommerce/BHX disclosures; không phải macro free chuẩn. |
| Consumer confidence | Có | Chưa có | **Thiếu**. Có thể dùng Nielsen/Conference Board/Google Trends/proxy; thường không free đầy đủ. |
| WACC inputs: risk-free, equity risk premium, cost of debt | Có | Có TPCP 5Y/10Y snapshot từ Pinetree, chưa có ERP/cost debt chuẩn | **Thiếu một phần**. Cần TPCP history + ERP assumption registry + cost of debt từ BCTC. |

## 4. Mục hệ thống đã lấy được hiện tại

Từ `stock-news-backend/data/macro_cycle_local.json`:

- `deposit12m` — lãi suất tiết kiệm 12T snapshot
- `usdVnd` — tỷ giá USD/VND snapshot
- `govBond5y`, `govBond10y` — TPCP 5Y/10Y snapshot
- `interbankOvernight` — lãi suất liên ngân hàng ON snapshot
- `vix`, `sp500`, `nasdaq`, `brent`, `gold` — global risk snapshot
- `vnindex`, `foreignNetBuyBn`, `marketTurnoverBn` — market flow snapshot

Nhưng các mục này mới là **snapshot 2026-05-04**, chưa phải chuỗi lịch sử dùng production.

## 5. Ưu tiên bổ sung nguồn

1. **GSO monthly retail sales + CPI / food CPI**: quan trọng nhất cho MWG/BHX.
2. **SBV/NHNN hoặc WiData policy/deposit/interbank history**: lãi suất/tín dụng.
3. **USD/VND history + DXY**: tỷ giá và FX pressure.
4. **TPCP 5Y/10Y history**: risk-free/WACC.
5. **Consumer confidence / modern trade penetration**: nếu không có source free thì để manual assumption có citation.

## 6. Kết luận ngắn

Excel FA MWG có nhiều assumption vĩ mô hơn hệ thống hiện lấy được. Hệ thống hiện mới có snapshot Pinetree tốt cho lãi suất/tỷ giá/global/market flow, nhưng **chưa có nguồn tự động cho GDP, retail sales, CPI/food CPI, consumer finance growth, modern trade penetration, consumer confidence** — đây là các gap chính cần báo anh.
