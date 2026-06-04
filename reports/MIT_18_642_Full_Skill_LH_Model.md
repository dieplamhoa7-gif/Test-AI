# MIT 18.642 Transcript-Trained LH Investment Model Skill — Full Edition

## 0. Skill purpose

Use this skill when Hòa Đại ka asks Tiểu đệ to self-study MIT 18.642 and use it to improve the LH Investment stock/CW/model system.

This is not just a short behavior note. This full skill is a compact internal textbook + operating procedure:

1. What was processed from MIT 18.642.
2. What each public lecture teaches.
3. What principles the model must learn.
4. How to map each topic into LH Investment features, backtests, risk rules, portfolio logic and CW scoring.
5. What Tiểu đệ must do when asked to “train the model”.

Important honesty note:

- Tiểu đệ processed the locally captured **transcripts** for all 22 public playlist videos.
- Tiểu đệ did **not** visually inspect every frame/slide unless explicitly using video/browser tools later.
- If slide diagrams, handwritten derivations, or visual examples are required, fetch/watch the video or source slides separately.

## 1. Source audit

Playlist:

- MIT 18.642 Topics in Mathematics with Applications in Finance, Fall 2024
- Playlist id: `PLUl4u3cNGP601Q2jo-J_3raNCMMs6Jves`
- Public videos captured: 22
- Transcript success: 22/22

Local files:

- `mit_18_642_transcripts_summary.json`
- `mit_18_642_transcripts/*.json`
- `reports/MIT_18_642_transcript_source_audit.md`

Processed lecture list:

1. Lecture 1, Part I: Introduction of the Class
2. Lecture 1, Part II: Introduction of Financial Markets, Financial Terms and Concepts
3. Lecture 1, Part III: Bond “Mathematics”
4. Lecture 2: Linear Algebra
5. Lecture 4: Linear Algebra (cont.); Probability Theory
6. Lecture 5: Probability Theory (cont.); Stochastic Processes I
7. Lecture 6: Stochastic Processes I (cont.); Regression Analysis
8. Lecture 7: Linear Rates, Products, and Models
9. Lecture 8: Regression Analysis (cont.)
10. Lecture 9: Principal Component Analysis in Finance
11. Lecture 10: Counterparty Risk Optimization
12. Lecture 11: Regression Analysis (cont.)
13. Lecture 13: Portfolio Management
14. Lecture 14: Stochastic Processes II
15. Lecture 12: Time Series Analysis
16. Lecture 18: Applying Data Science and Artificial Intelligence to Managing Biomedical Portfolios
17. Lecture 19: Volatility Modeling
18. Lecture 21: Black-Scholes Formula, Risk Neutral Valuation
19. Lecture 20: Building the First Federally Regulated Exchange Dedicated to Trading on Events
20. Lecture 23: Introduction to Machine Learning
21. Lecture 24: Stochastic Calculus
22. Lecture 25: Stochastic Calculus (cont.); Stochastic Differential Equations

## 2. Core thesis learned from the course

MIT 18.642 does not teach “find one magic indicator”. It teaches this mental model:

```text
financial decision = data + probability + model + validation + risk + implementation discipline
```

For LH Investment, this becomes:

```text
stock/CW recommendation = feature matrix + future labels + no-lookahead backtest + expected value + regime + risk-adjusted position sizing + explanation
```

The model should move from:

```text
indicator + rule + cảm tính
```

toward:

```text
measurable feature + probability + expected value + OOS evidence + portfolio/risk control
```

## 3. Lecture-by-lecture learning and LH mapping

### Lecture 1 Part I — Introduction of the Class

#### A. Lesson summary

The class introduces mathematics as a practical language for finance. The goal is not to memorize formulas but to learn how to formulate financial problems precisely. Core tools include linear algebra, probability, stochastic processes, regression, PCA, portfolio theory, volatility, derivatives and machine learning.

#### B. Key ideas

- Finance problems are uncertain and data-driven.
- Mathematical models simplify reality; they are useful but not perfect.
- A model should be judged by usefulness, assumptions and validation, not elegance alone.
- Course topics connect theory to real markets.

#### C. Investor meaning

Do not ask “is this stock guaranteed to rise?”. Ask:

- What is the probability?
- What is the payoff if right?
- What is the loss if wrong?
- In which market regime does the setup work?
- What assumptions must remain true?

#### D. LH Investment application

Every recommendation should include:

```json
{
  "signal": "",
  "probabilityOrPrecision": 0,
  "expectedValue": 0,
  "sampleSize": 0,
  "horizon": "20d",
  "risk": {},
  "wrongIf": ""
}
```

The system should not be only a display of indicators. It must become a decision-support engine.

---

### Lecture 1 Part II — Financial Markets, Terms and Concepts

#### A. Lesson summary

This lecture introduces basic financial markets, products and vocabulary: assets, securities, bonds, equities, rates, derivatives, risk, return, arbitrage and market participants.

#### B. Key ideas

- Assets represent claims on future cash flows or future states.
- Return must be understood relative to risk.
- Liquidity, transaction cost and market structure matter.
- Arbitrage logic anchors derivative pricing and relative valuation.

#### C. Investor meaning

A stock signal is incomplete without market context:

- liquidity,
- sector,
- market regime,
- macro/rates,
- transaction cost,
- slippage,
- position size.

#### D. LH Investment application

Add fields:

- `liquidityScore`
- `slippageRisk`
- `sectorRegime`
- `marketRegime`
- `riskAdjustedScore`
- `capitalSuitability`

For CW, add:

- `spreadPct`
- `daysToMaturity`
- `breakEvenDistancePct`
- `timeDecayPenalty`

---

### Lecture 1 Part III — Bond Mathematics

#### A. Lesson summary

Bond mathematics prices future cash flows by discounting. A cash flow received later is worth less today. Bond price is the present value of coupons and principal.

Core formula:

```text
PV = CF / (1 + r)^t
Bond Price = Σ Coupon_t/(1+y)^t + Face/(1+y)^T
```

Duration measures price sensitivity to interest-rate/yield changes:

```text
%ΔPrice ≈ -Duration × ΔYield
```

Convexity improves duration approximation when yield changes are large.

#### B. Key ideas

- Interest rates are the gravity of finance.
- Higher discount rates reduce present values.
- Longer-duration assets are more sensitive to rates.
- Cash-flow timing matters.

#### C. Investor meaning

Growth stocks behave like long-duration assets. When rates rise, valuation multiples can compress even if business quality remains good.

#### D. LH Investment application

Add macro/rate sensitivity fields:

- `rateSensitiveScore`
- `valuationDurationRisk`
- `peCompressionRisk`
- `macroRateRegime`

For valuation-heavy reports, note whether expected return comes from:

- earnings growth,
- multiple expansion,
- dividend/cash flow,
- mean reversion.

---

### Lecture 2 — Linear Algebra

#### A. Lesson summary

Linear algebra is the language for high-dimensional financial data. Stocks, indicators and returns can be represented as vectors and matrices.

Example stock feature vector:

```text
x_t = [RSI, ret20, volumeRatio, ATR%, distSupport, distResistance, patternScore]
```

A universe over time becomes a matrix:

```text
X = rows(stock-date observations) × columns(features)
```

#### B. Key ideas

- Vector = one observation or one asset profile.
- Matrix = many observations/features.
- Dot product = weighted scoring.
- Covariance/correlation matrix = how variables move together.
- Eigenvectors/eigenvalues later connect to PCA.

#### C. Investor meaning

A model cannot learn well from scattered indicators. It needs a clean feature matrix.

#### D. LH Investment application

Create and maintain:

- `stock-news-backend/data/research_feature_matrix_vn100.json`
- `stock-news-backend/data/research_feature_training_report.json`

Each row should contain:

- symbol/date,
- past-only features,
- future labels,
- regime,
- risk metrics.

---

### Lecture 4 — Linear Algebra continued; Probability Theory

#### A. Lesson summary

The lecture connects data representation with probability. Financial variables are random variables; model outputs should be probabilistic.

#### B. Key ideas

- Random variable: uncertain future return/outcome.
- Distribution: possible outcomes and probabilities.
- Expectation: average outcome weighted by probability.
- Variance: dispersion/risk.
- Conditional probability: probability after observing information.

#### C. Investor meaning

A stock setup does not “cause” profit. It changes conditional probability:

```text
P(return20d > 6% | setup present)
```

#### D. LH Investment application

For each setup, compute:

- `pWin20d`
- `pHitTarget20d`
- `expectedReturn20d`
- `expectedValue`
- `tailRisk`
- `sampleSize`

Avoid language like “chắc chắn tăng”. Use probability language.

---

### Lecture 5 — Probability continued; Stochastic Processes I

#### A. Lesson summary

A stochastic process is a sequence of random variables over time. Price is not one random variable but a path.

```text
P_0, P_1, P_2, ..., P_t
```

#### B. Key ideas

- Time order matters.
- Returns may have noise, trend and regime shifts.
- Volatility clusters.
- Future labels must not contaminate current features.

#### C. Investor meaning

Backtesting with random shuffle is dangerous for stock data. Markets evolve; what worked in one period can fail in another.

#### D. LH Investment application

Validation must be chronological:

- train 2023–2024,
- validate 2025,
- test 2026,
- or rolling/walk-forward windows.

Never random-shuffle stock-date rows for live strategy validation.

---

### Lecture 6 — Stochastic Processes continued; Regression Analysis

#### A. Lesson summary

Regression estimates relationships between explanatory variables and outcomes.

Example:

```text
futureReturn20d = a + b1*ret20 + b2*rsi14 + b3*atrPct + b4*distSupport + error
```

#### B. Key ideas

- Coefficients estimate directional relationship.
- Error term captures what the model misses.
- Statistical significance is not the same as trading usefulness.
- Multicollinearity can distort interpretation.

#### C. Investor meaning

Regression helps answer: which indicators actually explain future returns, and which just look nice?

#### D. LH Investment application

Run feature validation:

- Spearman correlation vs future return,
- top quintile vs bottom quintile,
- regression coefficient stability,
- OOS performance.

Current first training finding:

- distance to support/resistance appears more useful than raw pattern score.

---

### Lecture 7 — Linear Rates, Products and Models

#### A. Lesson summary

This lecture goes deeper into interest-rate products and rate models. Rate curves, forwards and discounting are central in fixed income and derivatives.

#### B. Key ideas

- Yield curve encodes time-value of money.
- Forward rates imply future borrowing/lending terms.
- Models simplify how rates evolve.
- Rate products depend on curve shape, not just one rate.

#### C. Investor meaning

Even for equities, rate environment affects valuation and sector rotation. Banks, real estate, growth stocks and leveraged companies respond differently.

#### D. LH Investment application

Add macro/rates context when data available:

- `yieldCurveProxy`
- `depositRateRegime`
- `creditTightnessProxy`
- `rateSensitiveSectorFlag`

If macro data is unavailable, at least allow manual `macroRegime` override.

---

### Lecture 8 — Regression Analysis continued

#### A. Lesson summary

Continues regression: interpretation, residuals, model diagnostics, goodness of fit and pitfalls.

#### B. Key ideas

- A good in-sample fit can be useless out-of-sample.
- Residual analysis shows model misspecification.
- Feature selection must be disciplined.
- More variables can overfit.

#### C. Investor meaning

If a stock strategy only works after heavy parameter tuning, it may be curve-fitted.

#### D. LH Investment application

Every backtest report should include:

- in-sample result,
- out-of-sample result,
- parameter stability,
- sample size,
- regime split,
- baseline comparison.

---

### Lecture 9 — Principal Component Analysis in Finance

#### A. Lesson summary

PCA identifies major directions of variation in data. In finance, it helps find factors and reduce dimensionality.

#### B. Key ideas

- Eigenvectors = principal directions.
- Eigenvalues = amount of variance explained.
- PCA can identify market factor, sector factor and idiosyncratic components.
- PCA reduces redundant indicators.

#### C. Investor meaning

Ten indicators may only represent two real ideas. Counting all ten as independent confirmation creates false confidence.

#### D. LH Investment application

Build:

- `feature_correlation_report.json`
- `indicator_factor_groups.json`

Group examples:

- Momentum oscillators: RSI/Stoch/Williams.
- Trend: MA slope/EMA/price-vs-MA.
- Volatility: ATR/realizedVol/Bollinger width.
- Money flow: OBV/MFI/CMF.

Only keep features that add OOS value.

---

### Lecture 10 — Counterparty Risk Optimization

#### A. Lesson summary

Counterparty risk studies loss from the other party failing to fulfill obligations. Optimization allocates exposures while controlling risk.

#### B. Key ideas

- Risk is not only market direction.
- Exposure, concentration and dependency matter.
- Optimization must respect constraints.
- Tail events and wrong-way risk matter.

#### C. Investor meaning

For a stock portfolio, “counterparty” maps to concentration and hidden dependency:

- too many stocks in one sector,
- all positions depend on liquidity cycle,
- all positions high beta,
- all positions sensitive to same macro risk.

#### D. LH Investment application

Portfolio risk module should flag:

- sector concentration,
- correlation concentration,
- liquidity concentration,
- volatility concentration,
- market-beta concentration.

Add:

```json
{
  "portfolioRiskWarnings": [],
  "sectorExposure": {},
  "correlationCluster": [],
  "maxPositionHint": 0
}
```

---

### Lecture 11 — Regression Analysis continued

#### A. Lesson summary

Further regression diagnostics and practical modeling issues.

#### B. Key ideas

- Outliers can dominate models.
- Nonlinear relationships may not fit linear regression.
- Interactions matter.
- Residual behavior indicates missing structure.

#### C. Investor meaning

A feature may be useful only under certain regimes. Example: high volatility may help breakout trades but hurt mean-reversion trades.

#### D. LH Investment application

Use interaction/regime tests:

```text
futureReturn20d ~ distSupport + distResistance + atrPct + marketRegime + distSupport*marketRegime
```

Report features by:

- bull market,
- bear market,
- sideway,
- high volatility,
- low liquidity.

---

### Lecture 13 — Portfolio Management

#### A. Lesson summary

Portfolio management balances expected return against risk. Diversification depends on covariance, not just number of holdings.

#### B. Key ideas

- Expected return vector.
- Covariance matrix.
- Efficient frontier.
- Risk-return tradeoff.
- Constraints and real-world implementation.

#### C. Investor meaning

Owning many stocks does not guarantee diversification if they move together.

#### D. LH Investment application

Add portfolio layer:

- `positionSizeHint`
- `sectorCapWarning`
- `correlationWarning`
- `portfolioVolatilityEstimate`
- `cashAllocationHint`

Sizing formula concept:

```text
positionSize = baseSize × confidenceFactor × volatilityFactor × marketRegimeFactor × liquidityFactor
```

---

### Lecture 14 — Stochastic Processes II

#### A. Lesson summary

Extends stochastic processes and continuous-time thinking. Price paths, Brownian motion intuition and stochastic dynamics support derivative/risk modeling.

#### B. Key ideas

- Random paths matter, not only endpoint returns.
- Drawdown path affects real trade experience.
- Continuous-time models approximate market movement.

#### C. Investor meaning

A trade with good final return but huge interim drawdown may be unsuitable.

#### D. LH Investment application

Backtest must include path metrics:

- `maxDrawdownAfterEntry`
- `maxRunupAfterEntry`
- `timeToTarget`
- `timeUnderWater`
- `stopHitBeforeTarget`

---

### Lecture 12 — Time Series Analysis

#### A. Lesson summary

Time series analysis studies serial dependence, autocorrelation, stationarity, trend, seasonality and forecasting.

#### B. Key ideas

- Financial time series are noisy.
- Autocorrelation may exist over some horizons.
- Regime changes break static models.
- Stationarity assumptions must be checked.

#### C. Investor meaning

A strategy should specify horizon. A feature can work for 5 days but fail for 60 days.

#### D. LH Investment application

All model outputs need horizon:

- `5d`
- `10d`
- `20d`
- `60d`

Do not mix horizons in one score without making weights explicit.

---

### Lecture 18 — Data Science and AI in Biomedical Portfolios

#### A. Lesson summary

Although biomedical portfolio examples differ from Vietnamese stocks, the lecture is useful for AI/data science in uncertain, high-dimensional decision-making.

#### B. Key ideas

- Data quality dominates model sophistication.
- Domain knowledge matters.
- Portfolio decisions under uncertainty require probability and risk.
- AI should support expert decision, not replace judgment blindly.

#### C. Investor meaning

ML is not magic. It can overfit noisy financial data quickly.

#### D. LH Investment application

Before ML:

1. Clean feature matrix.
2. Clear labels.
3. OOS split.
4. Baseline rule.
5. Explainability.
6. Risk controls.

Do not add complex ML before basic EV backtests are stable.

---

### Lecture 19 — Volatility Modeling

#### A. Lesson summary

Volatility is time-varying and clusters. Models such as historical volatility, EWMA/GARCH-style thinking and implied volatility help describe risk.

#### B. Key ideas

- Volatility is not constant.
- High volatility tends to persist.
- Volatility affects option pricing and risk management.
- Realized vs implied volatility differ.

#### C. Investor meaning

High volatility can mean both opportunity and danger. It may increase chance of hitting a target while worsening drawdown.

#### D. LH Investment application

Add:

- `atrPct`
- `realizedVol20`
- `bbWidth20`
- `volRegime`
- `volatilityAdjustedStop`
- `volatilityAdjustedPositionSize`

Do not rank stocks only by upside without volatility penalty.

---

### Lecture 21 — Black-Scholes Formula and Risk Neutral Valuation

#### A. Lesson summary

Black-Scholes prices options using stock price, strike, time, rate and volatility. Risk-neutral valuation prices derivatives by no-arbitrage logic.

Variables:

```text
S = underlying price
K = strike
T = time to maturity
r = risk-free rate
σ = volatility
```

#### B. Key ideas

- Option/CW price depends on direction, time and volatility.
- Time decay hurts long option/CW holders.
- Moneyness and break-even matter.
- Risk-neutral pricing is pricing math, not saying real-world risk is neutral.

#### C. Investor meaning

A bullish stock view is not enough to buy a CW. CW can lose even when underlying rises if spread/time decay/break-even is bad.

#### D. LH Investment application

CW score must include:

- `underlyingSignalScore`
- `daysToMaturity`
- `moneyness`
- `breakEvenDistancePct`
- `spreadPct`
- `liquidityScore`
- `timeDecayPenalty`
- `volatilityContext`

---

### Lecture 20 — Event Exchange / Event Contracts

#### A. Lesson summary

This lecture discusses trading on events and regulated event markets. It is about pricing probabilities of discrete outcomes.

#### B. Key ideas

- Event contracts map beliefs into probabilities/prices.
- Market design and regulation affect tradability.
- Binary outcomes can be priced probabilistically.

#### C. Investor meaning

Some stock outcomes are event-driven:

- earnings release,
- policy decision,
- listing/delist news,
- court/legal decision,
- project approval,
- dividend/corporate action.

#### D. LH Investment application

Add event-risk fields when news data supports it:

- `eventRiskFlag`
- `earningsUpcoming`
- `policyEventExposure`
- `binaryOutcomeRisk`
- `newsCatalystScore`

Do not use normal technical backtest blindly across event shocks.

---

### Lecture 23 — Introduction to Machine Learning

#### A. Lesson summary

Machine learning learns patterns from data. In finance, ML must be used carefully because data is noisy, nonstationary and prone to overfit.

#### B. Key ideas

- Train/test separation.
- Feature engineering.
- Labels.
- Classification/regression.
- Overfitting.
- Cross-validation must respect time.
- Interpretability matters.

#### C. Investor meaning

ML should output probability/ranking, not blind certainty.

#### D. LH Investment application

First ML models should be simple:

- logistic regression for `hitTarget6Pct20d`,
- gradient boosting for ranking,
- calibrated probabilities,
- SHAP/feature contribution if available.

Required output:

```json
{
  "pHitTarget20d": 0,
  "pLossMoreThan5Pct20d": 0,
  "expectedReturn20d": 0,
  "modelConfidence": 0,
  "topContributors": []
}
```

---

### Lecture 24 — Stochastic Calculus

#### A. Lesson summary

Stochastic calculus provides math for continuous-time random processes, especially Brownian motion and Ito calculus.

#### B. Key ideas

- Random process evolves continuously.
- Ito calculus handles functions of stochastic processes.
- Important for derivatives and risk models.

#### C. Investor meaning

For normal stock ranking, stochastic calculus is more conceptual than directly needed. For options/CW and volatility, it is foundational.

#### D. LH Investment application

Use conceptually for:

- dynamic risk,
- volatility path,
- option/CW pricing intuition,
- scenario simulation.

Do not overcomplicate equity model with SDE unless data/need justifies it.

---

### Lecture 25 — Stochastic Calculus continued; Stochastic Differential Equations

#### A. Lesson summary

SDEs model how financial variables evolve with deterministic drift and random shock:

```text
dS = μSdt + σSdW
```

#### B. Key ideas

- Drift = expected direction.
- Diffusion = random volatility component.
- GBM is a basic stock-price model.
- Real markets deviate from simple models.

#### C. Investor meaning

Forecasting a single path is fragile. Scenario distribution is better.

#### D. LH Investment application

Use scenario thinking:

- base case,
- bull case,
- bear case,
- stop case,
- gap-risk case.

For CW, simulate underlying movement + time decay if possible.

## 4. Model-training principles distilled

### Principle 1 — No look-ahead bias

At date `t`, features can only use data up to date `t`. Future returns are labels only.

Bad:

```text
using future support/resistance calculated from full chart as historical feature
```

Good:

```text
rolling support/resistance calculated only from bars <= t
```

### Principle 2 — Expected value over win rate

```text
EV = P(win) × AvgWin - P(loss) × AvgLoss - Cost
```

Report:

- precision,
- avgWin,
- avgLoss,
- EV,
- profitFactor,
- sampleSize,
- max drawdown.

### Principle 3 — Regime-aware validation

Evaluate every strategy under:

- bullish market,
- bearish market,
- sideway market,
- high volatility,
- low liquidity,
- sector pressure.

### Principle 4 — Simple before complex

Use this order:

1. Rule backtest.
2. Feature report.
3. Regression.
4. PCA/correlation.
5. Logistic regression/GBM.
6. More complex ML only if simple methods justify it.

### Principle 5 — Explainability required

Every model output should answer:

- why this stock,
- what can go wrong,
- where invalidation is,
- what risk-adjusted size is,
- what historical evidence supports it.

## 5. LH Investment feature map

### Trend features

- `ret5`, `ret20`, `ret60`
- `ma20Slope20`
- `ma50Slope20`
- `priceVsMa20Pct`
- `priceVsMa50Pct`
- `trendRegime`

### Momentum features

- `rsi14`
- `macdHist`
- `macdHistSlope3`
- `roc20`

### Volume/liquidity features

- `volumeRatio20`
- `liquidityScore`
- `turnoverValue`
- `slippageRisk`

### Volatility/risk features

- `atrPct`
- `realizedVol20`
- `bbWidth20`
- `volRegime`
- `maxDrawdownAfterEntry`

### Support/resistance features

- `nearestSupport`
- `nearestResistance`
- `distSupportPct`
- `distResistancePct`
- `roomToResistance`
- `supportBreakRisk`

### Pattern features

- `patternBias`
- `patternBullScore`
- `patternBearScore`
- `topPattern`
- `topPatternScore`

Pattern should be overlay until rolling OOS proves it works.

### Market/sector features

- `marketRegime`
- `sectorRegime`
- `sectorRelativeStrength`
- `vnindexTrend`

### Fundamental/valuation features

- `peRelative`
- `earningsGrowth`
- `valuationRisk`
- `rateSensitiveScore`

### CW features

- `underlyingSignalScore`
- `daysToMaturity`
- `moneyness`
- `breakEvenDistancePct`
- `spreadPct`
- `liquidityScore`
- `timeDecayPenalty`

## 6. Current first training finding from VN100 feature matrix

Local artifacts:

- `stock-news-backend/build_research_feature_matrix_vn100.py`
- `stock-news-backend/analyze_research_feature_matrix.py`
- `stock-news-backend/data/research_feature_matrix_vn100.json`
- `stock-news-backend/data/research_feature_training_report.json`
- `stock-news-backend/reports/research_feature_training_report_vn100.md`

Initial finding:

1. `sr_distSupportPct` is the strongest early feature vs 20-day forward return.
   - Interpretation: nearer support performed better than far above support.
2. `sr_distResistancePct` is also meaningful.
   - Interpretation: more room to resistance improved expected future return.
3. Volatility is mixed.
   - High volatility can raise hit-target probability but also worsens average/risk.
   - Use volatility for sizing and risk control, not pure buy/sell.
4. Pattern score is weaker than S/R distance.
   - Use pattern as confluence/overlay for now.

Critical caution:

- The first matrix merged latest chart pattern/SR snapshot.
- For production training, build rolling S/R/pattern features at each historical date to avoid leakage.

## 7. Strategy backtest template

For each strategy:

```json
{
  "strategy": "near_support_room_to_resistance",
  "horizon": "20d",
  "entryRules": [
    "distSupportPct <= 0.04",
    "distResistancePct >= 0.08",
    "volRegime != high",
    "marketRegime != bearish"
  ],
  "sampleSize": 0,
  "precision": 0,
  "avgWin": 0,
  "avgLoss": 0,
  "expectedValue": 0,
  "profitFactor": 0,
  "maxDrawdownAfterEntry": 0,
  "regimeBreakdown": {},
  "wrongIf": "breaks support with volume or market regime turns bearish"
}
```

## 8. Training SOP when Hòa Đại ka says “em tự training model đi”

### Step 1 — Load rules and skill

Read:

- this skill,
- `skills/mit-finance-quant-strategy/SKILL.md`,
- relevant stock pipeline/cache discipline skill if needed.

### Step 2 — Update feature matrix

Run/build:

- OHLCV features,
- rolling support/resistance,
- pattern features,
- volatility,
- market/sector regime,
- future labels.

### Step 3 — Leakage audit

Check:

- no future data in feature,
- labels separate,
- chronological sorting,
- rolling windows only use past bars.

### Step 4 — Exploratory report

Compute:

- feature correlation vs future return,
- top/bottom quintile spread,
- hit target probability,
- drawdown risk,
- high-correlation feature pairs,
- regime summary.

### Step 5 — Backtest explicit rules

Start with simple inspectable setups:

- near support + room to resistance,
- trend pullback,
- breakout retest,
- volatility contraction then expansion,
- sector leader pullback.

### Step 6 — Compute EV

For every strategy:

- precision,
- avgWin,
- avgLoss,
- EV,
- profitFactor,
- sampleSize,
- drawdown.

### Step 7 — OOS/walk-forward

Use chronological splits. Never random split.

### Step 8 — Only then ML

Train simple models:

- logistic regression for hit target,
- gradient boosting for ranking,
- probability calibration,
- feature importance/explainability.

### Step 9 — Do not deploy without permission

Do not push production Firebase or send Investment group alerts unless Hòa Đại ka explicitly asks.

## 9. Output format required for future model recommendations

```json
{
  "symbol": "MWG",
  "horizon": "20d",
  "setup": "near_support_room_to_resistance",
  "score": 0,
  "probability": {
    "pPositiveReturn": 0,
    "pHitTarget6Pct": 0,
    "pLossMoreThan5Pct": 0
  },
  "expectedValue": {
    "ev": 0,
    "avgWin": 0,
    "avgLoss": 0,
    "profitFactor": 0,
    "sampleSize": 0
  },
  "risk": {
    "atrPct": 0,
    "maxDrawdownAfterEntry": 0,
    "stopLoss": null,
    "invalidation": ""
  },
  "regime": {
    "market": "",
    "sector": "",
    "volatility": ""
  },
  "evidence": [],
  "why": "",
  "wrongIf": "",
  "positionSizeHint": ""
}
```

## 10. Red lines

- Do not claim certainty.
- Do not use future labels as features.
- Do not random-shuffle time-series data for final validation.
- Do not over-optimize parameters on full sample.
- Do not treat pattern score as main signal before rolling OOS backtest.
- Do not deploy production or send group notifications without explicit request.

## 11. Practical next task after this skill

The highest-value next model task:

```text
Build rolling support/resistance features historically, then backtest:
near support + room to resistance + volatility filter + market regime filter.
```

Why this first?

- It directly follows the strongest first training observation.
- It fixes the possible leakage risk.
- It is simple, explainable and useful for Hòa Đại ka.
- It creates EV metrics that can later feed ML.
