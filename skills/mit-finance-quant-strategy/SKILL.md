# MIT Finance Quant Strategy Skill

## Purpose

Use this skill when Hòa Đại ka asks to apply lessons from MIT 18.642 / quantitative finance / mathematics with applications in finance to LH Investment stock strategy, model design, backtesting, risk management, portfolio construction, volatility, derivatives/CW, or machine learning.

This skill turns the MIT finance course into practical rules for OpenClaw/Codex/Claude working on Hòa Đại ka's stock system.

## Source Material

Local references in this skill:

- `references/chapter-01-finance-foundations-vi.md` — Lecture 1 Part I–III: class intro, financial markets, bond mathematics.
- `references/chapter-02-linear-algebra-probability-vi.md` — Linear algebra, probability, stochastic processes.
- `references/chapter-03-regression-timeseries-pca-vi.md` — regression, time series, PCA for feature validation.
- `references/chapter-04-portfolio-risk-volatility-vi.md` — portfolio, risk, volatility modeling.
- `references/chapter-05-derivatives-blackscholes-cw-vi.md` — derivatives, Black-Scholes, CW/chứng quyền.
- `references/chapter-06-ml-stochastic-roadmap-vi.md` — ML, stochastic calculus, implementation roadmap.
- `references/playlist-lessons-auto-vi.md` — auto-generated Vietnamese notes for the currently public playlist videos.

Compiled guide for Hòa Đại ka:

- `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment.md`
- `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment.pdf`

Playlist:

- MIT 18.642 Topics in Mathematics with Applications in Finance, Fall 2024
- YouTube playlist id: `PLUl4u3cNGP601Q2jo-J_3raNCMMs6Jves`

Known local transcript files:

- `mit_18_642_transcripts/*.json`
- `mit_18_642_transcripts_summary.json`

Note: YouTube metadata returned 22 public videos during capture, not 25. If Hòa Đại ka provides missing lecture links, add them later.

## When to Use

Use this skill for requests like:

- "áp dụng bài MIT vào chiến lược cổ phiếu"
- "viết model/backtest theo tài chính định lượng"
- "học xong viết skill"
- "dùng regression/time series/PCA/volatility/portfolio vào stock model"
- "nâng cấp strategy cache/model LH Investment"
- "kiểm tra chiến lược có overfit không"
- "thêm expected value / risk / sizing"
- "áp dụng Black-Scholes/chứng quyền/CW"
- "làm bài học tiếng Việt từ MIT finance"

## Core Principles

### 1. Quant finance is decision support, not prophecy

Do not present a model as predicting certainty. Translate every signal into:

- probability / precision,
- expected value,
- average win,
- average loss,
- holding horizon,
- max drawdown,
- regime where it works,
- regime where it fails.

### 2. Every idea must become measurable

Never leave vague phrases like "mã khỏe", "setup đẹp", "rủi ro cao" without measurable fields.

Examples:

- `mã khỏe` → relative strength, MA trend, volume confirmation, drawdown control.
- `setup đẹp` → entry rules, support distance, trend state, pattern score, confirmation.
- `rủi ro cao` → ATR%, liquidity, gap risk, support break, market regime, sector concentration.

### 3. No look-ahead bias

For any backtest:

- signal at bar `t` can only use data up to `t`,
- entry should happen at next bar open/close depending on the explicit rule,
- future returns must only be used as labels/evaluation,
- time-series data must not be random-shuffled.

### 4. Optimize expected value, not just win rate

Always compute:

```text
EV = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

A high win-rate strategy can still be bad if losses are too large.

### 5. Use regime-aware evaluation

Evaluate each strategy under:

- bullish market,
- bearish market,
- sideway market,
- high volatility,
- low liquidity,
- sector rotation / sector pressure.

A strategy that only works in one regime must say so.

### 6. Simplicity before complexity

Prefer simple, inspectable models first:

- rules,
- regression,
- feature scoring,
- walk-forward backtest,
- small ML model.

Only use complex ML after data quality, labels, and OOS tests are strong.

## Required Output Fields for Strategy/Model Work

When generating or modifying a strategy cache, include as many of these fields as practical:

```json
{
  "symbol": "MWG",
  "signalName": "support_rebound",
  "horizon": "20d",
  "entryCondition": [],
  "riskCondition": [],
  "marketRegime": "neutral",
  "sectorRegime": "positive",
  "confidence": 0.0,
  "precision": 0.0,
  "expectedValue": 0.0,
  "avgWin": 0.0,
  "avgLoss": 0.0,
  "profitFactor": 0.0,
  "sampleSize": 0,
  "maxDrawdownAfterEntry": 0.0,
  "stopLoss": null,
  "target": null,
  "invalidation": null,
  "positionSizeHint": null,
  "evidence": [],
  "why": "",
  "wrongIf": ""
}
```

## Mapping MIT Lessons to LH Investment Features

### Bond mathematics / discounting

Use for:

- macro/rate context,
- valuation sensitivity,
- P/E compression risk,
- cashflow/DCF thinking,
- CW/phái sinh time value.

Possible fields:

- `rateSensitiveScore`
- `valuationRisk`
- `macroRateRegime`
- `discountPressure`

### Linear algebra

Use for:

- feature matrix,
- indicator redundancy,
- correlation/covariance,
- portfolio diversification.

Possible tasks:

- build `research_feature_matrix`,
- compute feature correlation,
- remove duplicate indicators,
- compute stock/sector correlation.

### Probability

Use for:

- precision,
- conditional probability,
- expectancy,
- distribution of returns,
- confidence calibration.

Possible fields:

- `pWin20d`
- `expectedReturn20d`
- `expectedValue`
- `tailRisk`
- `sampleSize`

### Stochastic processes / time series

Use for:

- no random split,
- walk-forward validation,
- market regime,
- volatility clustering,
- lag features.

Required checks:

- chronological train/test,
- rolling/walk-forward windows,
- stability across periods,
- no future leakage.

### Regression

Use for:

- testing whether features explain future returns,
- estimating signal strength,
- checking feature signs,
- avoiding multicollinearity.

Rules:

- use OOS validation,
- report coefficients only if stable,
- do not over-interpret noisy coefficients,
- compare to simple baseline.

### PCA

Use for:

- reducing indicator overlap,
- market/sector factor extraction,
- identifying shared movement across stocks,
- portfolio risk decomposition.

Good uses:

- group correlated indicators,
- separate market factor from idiosyncratic factor,
- reduce 40 indicators to a few canonical factor groups.

### Portfolio management

Use for:

- position sizing,
- sector caps,
- correlation caps,
- drawdown control,
- risk budgeting.

Do not only rank individual stocks. Also ask:

- Are selected stocks too correlated?
- Is the portfolio overloaded in one sector?
- Does position size match confidence and volatility?

### Volatility modeling

Use for:

- ATR stop,
- volatility-adjusted target,
- position sizing,
- high-volatility regime warnings,
- volatility clustering.

Possible fields:

- `atrPct`
- `realizedVol20`
- `volRegime`
- `stopByATR`
- `sizeByVolatility`

### Black-Scholes / risk-neutral valuation

Use for:

- chứng quyền/CW,
- option-like payoff,
- time decay,
- implied volatility,
- break-even.

CW ranking must not use underlying upside alone. Include:

- days to maturity,
- strike / moneyness,
- liquidity/spread,
- time decay penalty,
- volatility sensitivity.

### Machine learning

Use for:

- ranking candidates,
- probability calibration,
- feature interaction,
- model-assisted filtering.

Hard rules:

- no training on future labels,
- no random split for time series,
- compare against rule baseline,
- report OOS metrics,
- avoid black-box output without explanation.

## Workflow for Applying This Skill

### Step 1 — Identify the finance concept

Classify the user's request into one or more categories:

- market/valuation/rate,
- feature engineering,
- probability/expectancy,
- time series/backtest,
- regression/PCA,
- portfolio/risk,
- volatility,
- derivative/CW,
- ML.

### Step 2 — Translate to concrete fields

Convert the concept into data fields or rules that can be cached in JSON.

Example:

```text
"Dùng probability" → add precision, avgWin, avgLoss, expectedValue, sampleSize.
```

### Step 3 — Check data availability

Before coding, inspect existing data/cache:

- `stock-news-backend/data/*.json`
- `stock-news-backend/firebase_public/data/*.json`
- OHLCV history files,
- indicator cache,
- strategy cache,
- market overview,
- fundamental cache.

Do not invent official data.

### Step 4 — Build or modify cache script

Prefer creating/updating backend cache scripts under `stock-news-backend/` instead of calculating live in frontend.

Public web rule:

- Firebase frontend reads precomputed static JSON.
- Heavy calculations stay local/backend and export JSON.

### Step 5 — Validate

At minimum:

- run quick test on MWG/FPT/HPG/SSI,
- run full universe if quick test passes,
- inspect output JSON manually,
- confirm no NaN/Infinity,
- check sample sizes,
- report limitations.

### Step 6 — Explain in Vietnamese

When reporting to Hòa Đại ka, keep it practical:

- what was added,
- why it matters,
- where file is,
- what the model should/should not conclude,
- next recommended step.

## Backtest Discipline Checklist

Before trusting a strategy, verify:

- [ ] Entry uses only past/current data.
- [ ] Exit/label uses future data only for evaluation.
- [ ] Fees/slippage included.
- [ ] OOS period separated chronologically.
- [ ] Sample size sufficient.
- [ ] Compared against buy & hold / simple baseline.
- [ ] Metrics include precision, EV, avg win/loss, max drawdown.
- [ ] Results broken down by market regime.
- [ ] No feature leakage from future-generated cache.
- [ ] Strategy still works after removing redundant indicators.

## Vietnamese Teaching Style

When Hòa Đại ka asks to learn the course:

- Explain in Vietnamese.
- Use simple financial examples from Vietnamese stocks when possible.
- Always connect theory to LH Investment pipeline.
- Provide action items, not only academic summary.
- Mark what is immediately useful vs background theory.

Preferred structure:

1. Tóm tắt dễ hiểu.
2. Khái niệm chính.
3. Công thức nếu cần.
4. Ví dụ cổ phiếu/chứng quyền.
5. Áp dụng vào model của anh.
6. Checklist triển khai.

## Safety / Scope

- This skill is for research and decision support, not financial advice.
- Do not guarantee returns.
- Do not present unbacktested theory as production signal.
- Keep group-chat privacy: do not proactively push strategy lessons to group Investment unless Hòa Đại ka explicitly asks.
