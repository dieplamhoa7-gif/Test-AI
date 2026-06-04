# toliem212 FB/GitHub scan - stock model notes

Scan date: 2026-06-04
Scope: public/visible FB timeline through logged-in browser session + public GitHub/profile links. Private/inaccessible content not used.

## Executive summary

The profile is useful mostly for **risk framework / valuation framework / research discipline**, not for many code libraries. The strongest implementable ideas for Hòa's model are:

1. Baseline SMA cross benchmark from GitHub.
2. Macro early-risk overlay.
3. Structural/governance/liquidity/control risk overlay.
4. Corporate bond/rating-lag risk overlay.
5. Bank/BĐS collateral-cycle risk framing.
6. Holding-company/SOTP haircut framework.
7. Special-structure / option-like payoff analyzer.
8. Backtest integrity checklist: OOS, walk-forward, multiple-testing bias, correlation among strategies, costs/slippage.

## Libraries / repos / technical resources found

### 1) GitHub: `toliem212/sma-cross-vn30`
URL: https://github.com/toliem212/sma-cross-vn30

Status: useful as benchmark/baseline, not production strategy.

Observed contents from prior scan:
- `sma_cross_vn30.py`
- `backtest_sma.py`
- `backtest_all_vn30.py`
- `app_dashboard.py`
- `backtest_summary.csv`

Likely stack/ideas:
- Python
- `vnstock` or VN market data package usage
- Streamlit dashboard
- Plotly/charting
- SMA10/SMA50 cross
- VN30-wide backtest

How useful for Hòa:
- Use as a **baseline_sma_cross** module.
- Add `trend_following_score`: symbols where SMA/trend-following works vs fails.
- Compare model signals against simple SMA10/50 and Buy & Hold.
- Must improve methodology before trusting:
  - no lookahead
  - include fees/tax/slippage
  - OOS/walk-forward
  - real NAV max drawdown
  - parameter stability
  - alpha vs buy-and-hold

### 2) GitHub: `toliem212/quant-trading-sma-cross-vn30-python`
URL: https://github.com/toliem212/quant-trading-sma-cross-vn30-python

Status: repo exists but appears empty/size 0 at time of scan. Not useful yet.

### 3) Green Chart article: “THỐNG KÊ CÓ LỪA AI?”
URL: https://greenchart.vn/technical-insights-thong-ke-co-lua-ai/

Status: very useful for research discipline.

Important concepts:
- preprocessing data: OHLCV, split/dividend, timestamp, missing data
- feature engineering / signal testing
- rules-based + ML strategy skeleton
- backtesting with IS/OOS
- walk-forward testing
- Combinatorial Purged K-Fold (CPKF), Lopez de Prado reference
- transaction costs and random slippage
- HRP / inverse volatility / mean-risk portfolio weighting
- Sharpe ratio convergence over time
- high correlation among strategies (~0.81 example) means filters may not create genuinely independent alpha
- latent market factors
- selection bias
- multiple-testing bias / Type I error

How useful for Hòa:
- Turn into mandatory **Research Integrity Checklist**.
- Add strategy-correlation matrix to model research output.
- Add Sharpe/precision decay tracking over time.
- Do not accept a backtest just because equity curve looks good.

### 4) `giatrithinhvuong.com`
URL: https://giatrithinhvuong.com/

Status: not a code library; investing/media site linked from profile. Homepage shows Zstock/Zalo/VPS/TikTok and highlighted posts.

Visible highlighted themes:
- cash outside banking system
- SBV/State Treasury USD purchase impact on FX and system liquidity
- company update BAF Q1 2025
- global financial market volatility

How useful:
- Potential source for macro/liquidity narratives.
- Need separate scan if Hòa wants; not a library.

### 5) FiinGroup / FiinRatings
URLs:
- https://fiingroup.vn/
- https://fiinratings.vn/

Status: institutional data/rating sources, not open-source libraries.

Useful concepts seen via FB shares:
- corporate bond credit risk
- liquidity risk
- market maker importance
- transparency throughout bond lifecycle
- rating reports as input but not enough due to information lag/rating lag

How useful:
- Add `rating_lag_risk` and `credit_event_risk` concepts.
- For corporate bond/exposed stocks: monitor whether latest BCTC/news changed after rating report date.

## FB content themes captured

### A) Vicostone - Phenikaa / reverse takeover: governance-control-liquidity risk
Core idea:
- A deal may not be analyzable by gross margin, NPAT, P/E, DCF alone.
- For institutional investors, risk can be dominated by:
  - fund life pressure
  - exit pressure
  - veto/control/governance bottlenecks
  - delisting/liquidity lock risk
  - strategic asset/control bargaining power

Model implication:
```text
structural_risk_score =
  governance_risk
+ control_risk
+ liquidity_exit_risk
+ free_float_risk
+ delisting_or_corporate_action_risk
+ fund_exit_pressure_if_known
```

Use cases:
- small/mid caps
- low free float
- M&A/restructuring
- delisting risk
- foreign fund large ownership

### B) Vinhomes gold-to-property product: option-like payoff / structured product thinking
Core idea:
- Do not read it only as “gold to house”.
- Economically, it resembles a product with option-like payoff: customer can keep property or receive converted value after 5 years.
- Risks:
  - gold market risk
  - property market risk
  - liquidity risk if many exercise cash option
  - basis risk between reference gold prices
  - legal risk
  - communication/misunderstanding risk
  - hedging risk for company if gold spikes

Model implication:
```text
special_structure_type:
- plain equity
- option-like payoff
- embedded guarantee
- commodity-linked structure
- conversion-linked structure
- repo-like/economic financing structure
```

Use cases:
- warrants/CW
- convertible bonds
- guaranteed buyback products
- gold/FX-linked products
- real estate companies with structured sales campaigns

### C) Backtest/statistics self-deception
Core idea:
- Statistics do not lie; misuse of data/parameters/time windows does.
- Backtest can mislead through cherry-picking, multiple testing, strategy correlation, selection bias, and ignoring regime changes.

Model implication:
Mandatory checklist:
```text
1. In-sample vs out-of-sample split?
2. Walk-forward or rolling validation?
3. Transaction costs, tax, slippage included?
4. Parameter stability checked?
5. Neighboring parameters still work?
6. Strategy performance decay tracked?
7. Sharpe/precision convergence tracked?
8. Correlation between strategy variants checked?
9. Multiple-testing bias controlled?
10. Survivorship/selection/lookahead bias avoided?
```

### D) World Bank Vietnam macro update
Core idea:
- Follow WB macro updates for Vietnam growth, risks, reforms.
- Another comment said the report was somewhat shallow, so do not blindly overweight.

Model implication:
- Use as context source for `macro_risk_score`, not as direct signal.
- Track: growth outlook, inflation, FX, external demand, credit/liquidity, reforms.

### E) Corporate bond / rating lag / information lag
Core idea:
- Rating report is useful but can lag reality.
- Rating often based on past financial statements; BCTC itself has publication lag.
- By rating publication time, company may already have new changes in cash flow, leverage, collateral, liquidity, debt service ability.

Model implication:
```text
credit_rating_lag_risk =
  days_since_rating_report
+ days_since_latest_financials
+ leverage_change_flag
+ cashflow_stress_flag
+ collateral_liquidity_flag
+ new_debt_maturity_pressure
```

Use cases:
- bond issuers
- real estate developers
- banks/securities with bond exposure
- stocks sensitive to credit stress

### F) Primary capital market / PIPE / private placement / block trade risk
Core idea seen from post titles:
- “Quản trị rủi ro trong đầu tư vốn tư nhân trên thị trường chứng khoán thứ cấp: Từ PIPE, phát hành riêng lẻ đến giao dịch thỏa thuận tại Việt Nam.”
- “Quản trị rủi ro trên thị trường vốn sơ cấp: Nghệ thuật định giá sự bất định.”

Model implication:
Track special issuance/capital-market risks:
```text
capital_market_event_risk:
- private placement dilution
- lock-up expiry
- PIPE discount
- block trade overhang
- liquidity after issuance
- use-of-proceeds execution risk
- information asymmetry
```

### G) Techcombank / bank as capital-management machine vs BĐS collateral cycle
Core idea:
- Leadership statements at AGM can reveal risk appetite, balance sheet strategy, capital strategy, liquidity, market positioning, investor narrative.
- TCB wants premium positioning like JPMorgan/DBS-style efficient capital allocator, not merely cyclical real-estate lender.
- But Vietnam banking system remains tied to real estate collateral.
- Collateral cycle:
  - BĐS price up -> collateral value up -> LTV appears safer -> more lending -> supports asset price.
  - BĐS price down -> collateral value down -> real LTV up -> LGD/RWA/provisions up -> credit tightens -> market liquidity worsens.

Model implication:
For banks:
```text
bank_quality_premium_score:
- ROE sustainability
- CASA / funding quality
- fee/wealth/securities ecosystem
- NPL/provision trend
- BĐS collateral dependency
- capital allocation discipline
- through-cycle earnings stability
```

And:
```text
real_estate_collateral_cycle_risk:
- BĐS price trend
- legal/project liquidity
- collateral concentration
- provisioning pressure
- credit growth vs collateral values
```

### H) Masan / SOTP with haircut
Core idea:
- Do not mechanically add SOTP pieces.
- Each asset should be haircut by business quality, liquidity, cashflow generation, and execution risk.
- For MSN:
  - MCH: FMCG valuation using P/E, EV/EBITDA, DCF, ROIC, EBIT margin, category growth, brand power, pricing power.
  - WinCommerce: retail valuation using revenue/store, EBITDA margin, SSSG, store density, gross margin, shrinkage, logistics cost, working capital, FCF. P/S only secondary.
  - Phúc Long: F&B chain with revenue/store, EBITDA/store, store-level margin, expansion speed, payback period, flagship vs kiosk economics.
  - Trusting Social / Reddi / Wintel / consumer-tech: scenario valuation with fundraising, execution, exit, dilution haircuts.
  - subtract net debt, parent company costs, minority interests, taxes/exit costs, then apply holding discount.

Model implication:
```text
sotp_adjusted_value =
  sum(segment_value_i * quality_haircut_i * liquidity_haircut_i * execution_haircut_i)
- net_debt
- parent_costs
- minority_interest
- tax_exit_costs
- holding_discount
```

Use cases:
- MSN
- VIC/VHM/VRE group
- multi-segment holding companies
- conglomerates with listed/unlisted assets

## Total count summary

### Code libraries/repos found
- Total GitHub repos found from toliem212: **2**
  1. `sma-cross-vn30` — useful baseline.
  2. `quant-trading-sma-cross-vn30-python` — empty/not useful now.

### Non-code resources found
- `greenchart.vn/technical-insights-thong-ke-co-lua-ai/` — very useful for backtest discipline.
- `giatrithinhvuong.com` — possible macro/market article source.
- `fiingroup.vn` — data/industry/capital market source, commercial.
- `fiinratings.vn` — credit rating/corporate bond source, commercial.
- World Bank Vietnam macro livestream/report — macro context.
- YouTube Vicostone/VCS reverse takeover case — governance/control/liquidity risk case.
- Vnstockmarket.com FB content around Masan valuation — SOTP/holding-company valuation framework.

## Ranking for Hòa's model

### Highest priority to implement
1. Research integrity checklist from Green Chart article.
2. SMA baseline/trend-following score from `sma-cross-vn30`.
3. Structural risk overlay: governance/control/liquidity/free-float/corporate-action risk.
4. Adjusted SOTP/haircut framework for holding companies.
5. Bank/BĐS collateral-cycle risk overlay.

### Medium priority
6. Corporate bond/rating-lag risk overlay.
7. Capital-market event risk: PIPE/private placement/block trade/lock-up.
8. Special structure/option-like payoff analyzer.
9. Macro risk overlay using WB/other macro sources.

### Low priority / watchlist
10. giatrithinhvuong.com as a narrative source unless it has RSS/API/data later.
11. Empty GitHub repo unless updated.

## Proposed next coding plan

1. Add `MODEL_RISK_OVERLAY_NOTES.md` under stock-news-backend to formalize these rules.
2. Implement `baseline_sma_cross.py`:
   - SMA10/50
   - Buy & Hold comparison
   - fees/tax/slippage
   - OOS/walk-forward
   - trend_following_score
3. Add `research_integrity.py` checklist output for any backtest.
4. Add risk fields to dashboard JSON:
   - `trendFollowingScore`
   - `structuralRiskScore`
   - `ratingLagRisk`
   - `capitalMarketEventRisk`
   - `bankCollateralCycleRisk`
   - `sotpHaircutRisk`
5. Discuss with Hòa before production changes.
