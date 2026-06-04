# MIT 18.642 Transcript-Trained LH Model Skill

## Purpose

Use this skill when Hòa Đại ka asks Tiểu đệ to **self-study MIT 18.642** and apply it to **training/improving the LH Investment stock model**.

This skill is based on the locally captured public YouTube transcripts for:

- MIT 18.642 Topics in Mathematics with Applications in Finance, Fall 2024
- Playlist id: `PLUl4u3cNGP601Q2jo-J_3raNCMMs6Jves`
- Captured public videos: **22/22 available public videos**
- Transcript summary file: `mit_18_642_transcripts_summary.json`
- Raw transcripts: `mit_18_642_transcripts/*.json`

Important wording: Tiểu đệ has read/processed the transcript set, not watched every frame/slide of every video. If visual slide details matter, fetch the video/slides separately.

## Local Learning Artifacts

Main Vietnamese guides:

- `reports/MIT_18_642_Bai_Hoc_Truoc_Ap_Dung_Sau_v3.md`
- `reports/MIT_18_642_Bai_Hoc_Truoc_Ap_Dung_Sau_v3.pdf`
- `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment_v2.md`
- `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment_v2.pdf`

Core quant skill already created:

- `skills/mit-finance-quant-strategy/SKILL.md`

Current model-training artifacts:

- `stock-news-backend/build_research_feature_matrix_vn100.py`
- `stock-news-backend/analyze_research_feature_matrix.py`
- `stock-news-backend/summarize_research_training_report.py`
- `stock-news-backend/data/research_feature_matrix_vn100.json`
- `stock-news-backend/data/research_feature_training_report.json`
- `stock-news-backend/reports/research_feature_training_report_vn100.md`

## What This Skill Teaches the Model Builder

### 1. Think in probability, not certainty

Do not output only `BUY`, `SELL`, or `WATCH`. Every signal should move toward:

- probability of positive return,
- probability of reaching target,
- expected value,
- average win,
- average loss,
- drawdown risk,
- market/sector regime dependency.

### 2. Create a feature matrix before ML

For each stock/date, build a vector like:

```json
{
  "symbol": "MWG",
  "date": "2026-05-29",
  "trend": {},
  "momentum": {},
  "volume": {},
  "volatility": {},
  "supportResistance": {},
  "pattern": {},
  "marketRegime": {},
  "labels": {
    "futureReturn20d": null
  }
}
```

Rules:

- Features at date `t` may use only data up to `t`.
- Future returns are labels only.
- Never random-shuffle time-series data for OOS validation.
- Prefer walk-forward or chronological train/test.

### 3. Validate features before trusting them

For each feature, test:

- correlation with future return,
- top-quintile vs bottom-quintile performance,
- performance by regime,
- stability across time,
- sample size,
- whether the feature leaks future data.

### 4. Use expected value, not win rate alone

```text
EV = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

A feature/setup can have high hit rate but negative EV if losers are too large.

### 5. Use PCA/correlation to avoid duplicate indicators

Many indicators overlap:

- RSI/Stochastic/Williams %R,
- MA trend/EMA trend,
- ATR/realized volatility/Bollinger width,
- OBV/MFI/CMF.

Cluster features and avoid counting the same evidence many times.

### 6. Portfolio and risk come after stock ranking

A good model must answer:

- how much to buy,
- when the setup is invalidated,
- whether the portfolio is overconcentrated,
- whether correlation/sector risk is too high,
- whether market regime allows the trade.

### 7. CW/chứng quyền needs derivative logic

CW ranking must include:

- underlying stock signal,
- days to maturity,
- moneyness,
- break-even distance,
- spread,
- liquidity,
- time decay,
- volatility.

Do not rank CW by leverage alone.

## Current Learned Signal From First Training Run

From the first VN100 feature training dataset:

- `sr_distSupportPct` showed the strongest relationship with 20-day future return: closer-to-support groups performed better than far-from-support groups.
- `sr_distResistancePct` was also meaningful: more room to resistance was associated with better future return.
- Volatility features (`atrPct`, `realizedVol20`) were mixed: high volatility increased hit-target chances but worsened average risk/return. Use for sizing/risk, not simple buy/sell.
- Pattern score was weaker than support/resistance distance. Pattern should be confluence/overlay until rolling OOS backtest proves otherwise.

Caution: the first matrix merged the latest pattern/SR snapshot. Before production use, build rolling support/resistance features at each historical date to avoid leakage.

## Default Action Plan When Hòa Says “Train the Model”

1. Read this skill and `skills/mit-finance-quant-strategy/SKILL.md`.
2. Build/update feature matrix.
3. Check for data leakage.
4. Generate exploratory report.
5. Build explicit strategy rules.
6. Backtest chronologically.
7. Report EV/avgWin/avgLoss/profitFactor/sampleSize/regime.
8. Only then consider ML probability ranking.
9. Do not deploy production or send group Telegram notifications unless explicitly asked.

## What Not To Do

- Do not claim visual video watching if only transcripts were processed.
- Do not use future returns as live features.
- Do not optimize on the full sample then report it as objective performance.
- Do not deploy to Firebase production unless Hòa Đại ka asks.
- Do not send strategy alerts to Investment group by default.
