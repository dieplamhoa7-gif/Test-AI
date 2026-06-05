---
name: vn-macro-cycle-research
description: >-
  Skill phân tích và lưu trữ dữ liệu vĩ mô cho thị trường chứng khoán Việt Nam/LH Investment. Dùng khi cần thu thập Pinetree Morning Brief, SBV/NHNN, WiData/TradingEconomics/FRED/WorldBank/yfinance, xây macro regime score, lưu snapshot lịch sử, hoặc viết báo cáo vĩ mô. Skill này tạo khung phân tích/regime filter, không đưa khuyến nghị đầu tư cá nhân hóa.
---

# VN Macro Cycle Research

## Mục tiêu

Xây một lớp **macro regime filter** cho hệ thống phân tích cổ phiếu Việt Nam:

- Đánh giá môi trường thanh khoản/lãi suất/tỷ giá/rủi ro toàn cầu/dòng tiền thị trường.
- Phân loại phase: Risk-on, trung tính, phòng thủ, risk-off.
- Hỗ trợ position sizing và điều kiện giải ngân, không thay thế phân tích cổ phiếu.

## Khi nào dùng skill này

Dùng khi người dùng hỏi về:

- vĩ mô, macro, chu kỳ kinh tế, cycle, market regime;
- lãi suất liên ngân hàng, OMO, bơm hút ròng, tín phiếu NHNN;
- tỷ giá USD/VND, DXY, US10Y, VIX, Brent, gold;
- CPI, GDP, credit growth, PMI;
- tạo/lưu dữ liệu macro hằng ngày;
- backtest chiến lược có filter vĩ mô;
- dashboard hoặc báo cáo “Yếu tố vĩ mô”.

## Nguyên tắc bắt buộc

1. **Không dùng dữ liệu tương lai.** Macro snapshot dùng cho phiên T phải là dữ liệu biết được trước hoặc tại thời điểm ra quyết định.
2. **Tách raw/parsed/score.** Không overwrite raw snapshot; parser/score có thể version hóa.
3. **Ghi nguồn và timestamp.** Mỗi con số quan trọng cần source URL, fetchedAt, frequency, parserVersion.
4. **Phân biệt actual, delayed, estimate.** CPI/GDP/credit thường trễ; không coi là realtime.
5. **Không giả định source free là hoàn chỉnh.** Pinetree hữu ích nhưng không phải historical database; SBV có thể redirect/block; WiData/TradingEconomics có thể trả phí.
6. **Backtest trước khi dùng trong model.** Macro score là heuristic nếu chưa kiểm định OOS.
7. **Không đưa khuyến nghị cá nhân hóa.** Kết luận là tư liệu phân tích/regime, không phải lời khuyên đầu tư.

## Nguồn dữ liệu ưu tiên

Đọc thêm `references/macro-source-map.md`.

### Daily/market timing

- Pinetree Morning Brief: snapshot lãi suất liên NH, deposit, TPCP, FX, global risk, VNINDEX, foreign flow, turnover.
- yfinance/FRED: VIX, DXY, US10Y, Brent/WTI, Gold, S&P500/NASDAQ.
- vnstock/local market data: VNINDEX/OHLCV/breadth/liquidity.

### Vietnam monetary/macro depth

- SBV/NHNN official: nguồn gốc nhưng khó crawl; cần adapter thận trọng.
- WiData/WiGroup/WiFeed: tốt cho OMO/bơm hút ròng/liên ngân hàng nếu có quyền truy cập.
- TradingEconomics: interbank/macro history nếu có paid API.
- WorldBank/DBnomics: macro dài hạn/annual/monthly, không dùng cho daily timing.

## Data model khuyến nghị

```json
{
  "date": "YYYY-MM-DD",
  "source": "Pinetree Morning Brief",
  "url": "https://...",
  "status": "ok|partial|missing|error",
  "fetchedAt": "ISO timestamp",
  "parserVersion": "pinetree_v1",
  "rawTextHash": "sha256",
  "data": {
    "interbankOvernight": {"value": 6.4, "change1d": null, "ytd": null},
    "usdVnd": {"value": 26368, "change1d": null, "ytd": null}
  },
  "macroScore": 43.6,
  "phase": "Cuối chu kỳ / Phòng thủ",
  "components": {},
  "warnings": []
}
```

## Macro score skeleton

Các component gợi ý:

- `liquidity` — interbank, OMO/net injection, deposit rate.
- `fx` — USD/VND, DXY, FX pressure YTD.
- `rates` — deposit, gov bond yields, yield changes.
- `inflationGrowth` — CPI, PMI, credit growth, GDP/retail sales.
- `globalRisk` — VIX, S&P500/NASDAQ, US10Y, oil.
- `marketFlow` — VNINDEX momentum, breadth, turnover, foreign flow.

Regime mapping mẫu:

```text
score >= 65: Mở rộng / Risk-on
score >= 50: Trung tính - hồi phục chọn lọc
score >= 40: Cuối chu kỳ / Phòng thủ
score < 40 : Co hẹp / Risk-off
```

## Quy trình phân tích

1. Xác định ngày phân tích và thời điểm ra quyết định.
2. Thu thập dữ liệu từ source có sẵn.
3. Lưu raw snapshot trước.
4. Parse sang schema chuẩn.
5. Tính macro score + component notes.
6. Viết nhận định regime bằng tiếng Việt, giữ thuật ngữ như risk-on/risk-off, liquidity, FX pressure.
7. Nêu rõ missing data và giới hạn.
8. Nếu dùng trong chiến lược: chạy backtest OOS/walk-forward.

## Quy trình code/lưu trữ

- Code fetcher: `code/macro_cycle.py` hiện có bản Pinetree local-test.
- Output hiện có: `data/macro_cycle_local.json`.
- Nên mở rộng thành:

```text
stock-news-backend/app/macro/
├─ fetchers/
│  ├─ pinetree.py
│  ├─ yfinance_global.py
│  ├─ fred_global.py
│  ├─ widata_paid.py
│  └─ tradingeconomics_paid.py
├─ scoring/
│  └─ regime_score.py
├─ storage/
│  └─ macro_history.py
└─ reports/
   └─ macro_summary.py
```

## Output format báo cáo nhanh

```text
TÓM TẮT VĨ MÔ
- Macro score: ... / 100
- Regime: ...
- Market view: ...

DRIVERS
- Liquidity: ...
- FX: ...
- Rates: ...
- Global risk: ...
- Market flow: ...

WATCHLIST
- Dữ liệu thiếu/cần cập nhật: ...
- Ngưỡng cần theo dõi: ...

ỨNG DỤNG CHO CHIẾN LƯỢC
- Tỷ trọng gợi ý theo regime: ...
- Điều kiện tăng/giảm risk: ...

DISCLAIMER
- Đây là tư liệu phân tích, không phải lời khuyên đầu tư cá nhân hóa.
```
