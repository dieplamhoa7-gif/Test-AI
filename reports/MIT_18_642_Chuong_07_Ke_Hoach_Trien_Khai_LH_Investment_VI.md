# Chương 7 — Kế hoạch triển khai MIT 18.642 vào LH Investment

Mục tiêu của chương này: chuyển toàn bộ bài học MIT 18.642 thành việc cụ thể trong hệ thống của Hòa Đại ka.

Không học để biết cho vui. Học xong phải ra được:

- feature mới,
- backtest mới,
- risk rule mới,
- cache JSON mới,
- hiển thị web rõ hơn,
- và cuối cùng là chiến lược ít cảm tính hơn.

---

## 1. Kiến trúc định lượng nên có

Hệ thống LH Investment nên tách thành 7 lớp:

```text
1. Data Layer
2. Feature Layer
3. Signal Layer
4. Backtest / Validation Layer
5. Risk & Portfolio Layer
6. Explanation Layer
7. Frontend Display Layer
```

### 1.1. Data Layer

Nguồn dữ liệu:

- OHLCV daily/weekly/monthly,
- dữ liệu tài chính,
- ngành,
- market overview,
- VNINDEX/market regime,
- chart pattern cache,
- news/macro nếu có.

Nguyên tắc:

- Không tính toán nặng trên frontend.
- Backend/local build cache JSON trước.
- Firebase chỉ đọc JSON tĩnh.

### 1.2. Feature Layer

Feature nên chia nhóm:

**Trend**
- MA stack,
- slope MA20/50,
- price vs MA,
- ADX.

**Momentum**
- RSI,
- MACD histogram,
- ROC,
- stochastic.

**Volume / Money Flow**
- volume ratio,
- OBV,
- MFI,
- CMF,
- liquidity.

**Volatility**
- ATR%,
- realized volatility,
- Bollinger width,
- volatility regime.

**Support / Resistance**
- nearest support,
- nearest resistance,
- distance to support,
- resistance overhead.

**Pattern**
- pattern bias,
- pattern score,
- triple top/bottom,
- trendline,
- support/resistance cluster.

**Market / Sector**
- market regime,
- sector strength,
- correlation risk.

### 1.3. Signal Layer

Các chiến lược hiện có nên chuẩn hóa thành cùng schema:

```json
{
  "signalId": "support_rebound",
  "symbol": "MWG",
  "date": "2026-05-29",
  "horizon": "20d",
  "entryRules": [],
  "riskRules": [],
  "evidence": [],
  "why": "",
  "wrongIf": ""
}
```

### 1.4. Backtest Layer

Mỗi signal phải có:

- sample size,
- precision,
- average win,
- average loss,
- expected value,
- max drawdown after entry,
- result by regime.

### 1.5. Risk & Portfolio Layer

Không chỉ chọn mã. Phải quyết định:

- mua bao nhiêu,
- rủi ro bao nhiêu,
- có quá tập trung ngành không,
- có correlation cao không,
- thị trường chung có cho phép đánh không.

---

## 2. Việc ưu tiên số 1 — Feature Matrix VN100

### 2.1. Vì sao cần?

Muốn dùng regression, PCA, ML, backtest đúng thì phải có bảng nghiên cứu chuẩn.

Không có feature matrix thì mọi thứ chỉ là các script rời rạc.

### 2.2. Schema đề xuất

File output:

```text
stock-news-backend/data/research_feature_matrix_vn100.json
```

Mỗi dòng:

```json
{
  "symbol": "MWG",
  "date": "2026-05-29",
  "close": 76.3,
  "futureReturn5d": null,
  "futureReturn10d": null,
  "futureReturn20d": null,
  "futureMaxDrawdown20d": null,
  "trend": {
    "ma20Slope": 0.0,
    "ma50Slope": 0.0,
    "priceVsMa20Pct": 0.0,
    "adx14": 0.0
  },
  "momentum": {
    "rsi14": 0.0,
    "macdHist": 0.0,
    "roc20": 0.0
  },
  "volume": {
    "volumeRatio20": 0.0,
    "mfi14": 0.0
  },
  "volatility": {
    "atrPct": 0.0,
    "realizedVol20": 0.0,
    "volRegime": "normal"
  },
  "sr": {
    "nearestSupport": 0.0,
    "nearestResistance": 0.0,
    "distSupportPct": 0.0,
    "distResistancePct": 0.0
  },
  "pattern": {
    "bias": "neutral",
    "patternCount": 0,
    "topPattern": "",
    "patternBullScore": 0.0,
    "patternBearScore": 0.0
  },
  "market": {
    "marketRegime": "neutral",
    "sector": "retail",
    "sectorStrength": 0.0
  }
}
```

### 2.3. Cách dùng

Từ feature matrix, Tiểu đệ có thể làm:

- regression report,
- feature importance,
- PCA/correlation,
- strategy OOS,
- ML probability model,
- risk-adjusted ranking.

---

## 3. Việc ưu tiên số 2 — Expected Value cho từng chiến lược

### 3.1. Công thức

```text
EV = precision × avgWin - (1 - precision) × avgLoss - cost
```

Trong đó:

- precision = tỷ lệ lệnh đạt target hoặc return dương theo horizon,
- avgWin = lợi nhuận trung bình khi thắng,
- avgLoss = mức lỗ trung bình khi thua,
- cost = phí/slippage.

### 3.2. Vì sao quan trọng?

Một chiến lược win rate 70% chưa chắc tốt. Nếu lãi mỗi lần 2%, lỗ mỗi lần 8%, EV có thể âm.

Một chiến lược win rate 45% vẫn tốt nếu lời/lỗ tốt.

### 3.3. Output nên có

```json
{
  "strategy": "trend_pullback",
  "horizon": "20d",
  "sampleSize": 184,
  "precision": 0.58,
  "avgWin": 0.087,
  "avgLoss": -0.042,
  "expectedValue": 0.032,
  "profitFactor": 1.9,
  "maxDrawdownAfterEntry": -0.071
}
```

---

## 4. Việc ưu tiên số 3 — Market Regime Filter

### 4.1. Regime đề xuất

```text
bullish_market
bearish_market
sideway_market
high_volatility
low_liquidity
risk_off
```

### 4.2. Tác động lên chiến lược

Nếu market regime xấu:

- giảm position size,
- yêu cầu setup mạnh hơn,
- ưu tiên mã RS cao,
- tránh breakout yếu,
- ưu tiên hỗ trợ gần và stop rõ.

Nếu market regime tốt:

- cho phép breakout/trend following,
- position size cao hơn,
- target rộng hơn.

---

## 5. Việc ưu tiên số 4 — PCA / Correlation để lọc indicator trùng

### 5.1. Vấn đề hiện tại

Nếu hệ thống có 40 indicator, nhiều indicator trùng thông tin:

- RSI/Stoch/Williams %R,
- MA20/MA50/EMA,
- Bollinger width/ATR/volatility,
- OBV/MFI/CMF.

### 5.2. Cách làm

1. Tính correlation matrix của các feature.
2. Gom nhóm indicator correlation cao.
3. Chọn đại diện mỗi nhóm.
4. Backtest nhóm đại diện.
5. Loại feature không tăng EV/OOS.

### 5.3. Output

```text
stock-news-backend/data/feature_correlation_report.json
stock-news-backend/data/indicator_factor_groups.json
```

---

## 6. Việc ưu tiên số 5 — Portfolio Risk

### 6.1. Cảnh báo cần có

Khi model chọn nhiều mã, cần cảnh báo:

- quá nhiều mã cùng ngành,
- correlation cao,
- volatility danh mục cao,
- thanh khoản yếu,
- market regime xấu.

### 6.2. Position size hint

```text
positionSizeHint = baseSize × confidenceFactor × volatilityFactor × marketRegimeFactor
```

Ví dụ:

- confidence cao → tăng size,
- volatility cao → giảm size,
- market xấu → giảm size,
- thanh khoản yếu → giảm size.

---

## 7. Việc ưu tiên số 6 — CW / Chứng quyền

CW ranking nên dùng:

- underlying signal,
- days to maturity,
- moneyness,
- break-even,
- spread,
- liquidity,
- time decay penalty.

Không chọn CW chỉ vì leverage cao.

Output đề xuất:

```json
{
  "cw": "CMWGxxxx",
  "underlying": "MWG",
  "underlyingSignalScore": 72,
  "daysToMaturity": 45,
  "moneyness": "near_the_money",
  "breakEvenDistancePct": 6.8,
  "spreadPct": 2.1,
  "liquidityScore": 70,
  "timeDecayPenalty": 18,
  "finalCWScore": 64,
  "warning": "spread acceptable, time decay moderate"
}
```

---

## 8. Thứ tự triển khai đề xuất cho Tiểu đệ

### Phase 1 — Nền dữ liệu

1. Build feature matrix VN100.
2. Merge chart pattern cache vào feature matrix.
3. Add future return labels.
4. Validate no look-ahead.

### Phase 2 — Backtest định lượng

1. Backtest 3 chiến lược hiện có theo EV.
2. Tách theo market regime.
3. Báo cáo strategy nào thật sự tốt.

### Phase 3 — Feature/PCA

1. Correlation matrix.
2. Indicator factor groups.
3. Loại feature trùng.

### Phase 4 — Risk/portfolio

1. ATR/volatility regime.
2. Position sizing.
3. Sector/correlation risk.

### Phase 5 — CW

1. CW score mới.
2. Break-even/time decay/spread.
3. Kết hợp underlying signal.

### Phase 6 — ML nhẹ

1. Logistic regression / gradient boosting.
2. Probability calibration.
3. Walk-forward OOS.
4. Explainability.

---

## 9. Kết luận cho Hòa Đại ka

Nếu làm theo MIT 18.642, hệ thống của anh nên chuyển từ:

```text
indicator + rule + cảm tính
```

sang:

```text
feature matrix + probability + expected value + regime + risk-adjusted ranking
```

Bước tiếp theo đáng làm nhất: **build feature matrix VN100**.
