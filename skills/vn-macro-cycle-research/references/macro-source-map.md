# Macro Source Map - Vietnam/LH Investment

## 1. Pinetree Morning Brief

- URL pattern: `https://pinetree.vn/post/YYYYMMDD/ban-tin-sang-DD-MM-YYYY/`
- Frequency: trading-day/daily snapshot, not guaranteed.
- Access: public HTML.
- Fields observed:
  - Lãi suất liên NH
  - Lãi suất tiết kiệm 12T
  - TPCP 5Y/10Y
  - USD/VND, EUR/VND, CNY/VND
  - S&P500, NASDAQ, VIX
  - Brent, Gold
  - VNINDEX
  - Foreign net buy/sell
  - Market turnover
- Reliability: medium for daily snapshot, low for full historical backfill.
- Use: local macro filter, morning dashboard.

## 2. SBV/NHNN official site

- Official source for monetary policy and banking statistics.
- Problems observed:
  - Some old webcenter URLs redirect to `https://www.sbv.gov.vn/vi/trang-chu`.
  - Direct crawl may return page shell rather than structured data.
  - Need robust adapter/browser/manual export or official downloadable endpoint if discovered.
- Use: source-of-truth verification, not yet reliable for automation.

## 3. WiData / WiGroup / WiFeed

- Likely best Vietnam-specific source for:
  - bơm/hút ròng,
  - tín phiếu NHNN,
  - OMO,
  - liên ngân hàng,
  - money market,
  - macro/monetary datasets.
- Example routes observed:
  - `https://widata.vn/vi-mo/vn/bom-hut-rong`
  - `https://widata.vn/vi-mo/vn/outright-sbv-bills`
- Access: paywalled/API packages.
- Use: production-quality monetary data if subscribed.

## 4. TradingEconomics

- Example: `https://tradingeconomics.com/vietnam/interbank-rate`
- Vietnam Three Month Interbank Rate, historical/daily, source SBV.
- Access: full historical/API likely paid.
- Use: paid adapter or manual cross-check.

## 5. yfinance / market proxies

Useful tickers depend on Yahoo availability:

- VIX: `^VIX`
- S&P500: `^GSPC`
- NASDAQ: `^IXIC`
- DXY: `DX-Y.NYB` or alternatives
- US10Y: `^TNX`
- Brent: `BZ=F`
- WTI: `CL=F`
- Gold: `GC=F`

Use for global risk/rates/commodity pressure.

## 6. FRED / pandas-datareader

- US10Y, Fed Funds, DXY proxies, inflation, liquidity indicators.
- Good for global macro, not Vietnam-specific daily macro.

## 7. World Bank / wbgapi / DBnomics

- Good for annual/quarterly/slow macro:
  - GDP growth,
  - CPI/inflation,
  - trade,
  - FDI,
  - credit to private sector if available.
- Not enough for daily market timing.

## 8. vnstock/local market data

- VNINDEX, OHLCV, market breadth if built internally.
- Good for marketFlow/momentum/breadth component.

## Source reliability grading

| Source | Frequency | Cost | Automation | Best use |
|---|---|---:|---|---|
| Pinetree | daily snapshot | free | medium | morning macro dashboard |
| SBV | official/varies | free | low currently | verification/source-of-truth |
| WiData/WiFeed | daily/history | paid | high if API | OMO/interbank/bills |
| TradingEconomics | daily/history | paid | high if API | interbank/global macro |
| yfinance | daily/intraday | free | high | global risk proxies |
| WorldBank/DBnomics | annual/monthly | free | medium/high | slow macro context |
| vnstock | daily | free | medium | VN market proxy |
