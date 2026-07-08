# Codex Guide — LHINVT Latest Data / Indicators / Strategies

Use this guide whenever Codex works on LH Investment / LHINVT data, reports, Model3 context, strategy tables, or web cache.

## 0. Scope

Current canonical project:

- Repo: `C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend`
- Deploy/public folder: `stock-news-backend/firebase_public/`
- Current live site: `https://lhinvt.web.app`
- Firebase project: `security-1c731`
- Firebase hosting site: `lhinvt`
- Old site `https://lhinvestment.web.app` is legacy. Do not deploy there unless Hòa Đại ka explicitly asks.

## 1. Non-negotiable rules

1. Do not overwrite final frontend HTML unless Hòa Đại ka explicitly asks for frontend changes.
2. Treat `firebase_public/stocks.html` as fragile/canonical.
3. Do not invent numbers: prices, dates, close, indicators, strategy signals, win rates, PnL, support/resistance, or candidates must come from evidence files or live endpoints.
4. If data is missing/stale, report missing/stale. Do not fill by pattern.
5. Use UTF-8 safe scripts/files for Vietnamese. Do not patch Vietnamese through inline shell one-liners.
6. Avoid `git add .` and `git add -A`; add exact files only.
7. Before any data/report claim, check source dates and freshness.

## 2. Pull latest local repo first

Run from repo:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
git fetch origin
git rebase origin/master
```

If PowerShell reports `NativeCommandError`, verify refs before assuming failure:

```powershell
git rev-parse --short HEAD
git ls-remote origin refs/heads/master
```

## 3. Live web data source — use current deployed cache

When the user asks for latest web data, current stock info, indicators, or strategy data, compare local with live `lhinvt.web.app`.

Download live cache with cache-busting:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
$ts=Get-Date -Format yyyyMMddHHmmss
Invoke-WebRequest "https://lhinvt.web.app/data/market_data.json?ts=$ts" -OutFile tmp_live_market_data.json
Invoke-WebRequest "https://lhinvt.web.app/data/market_watch.json?ts=$ts" -OutFile tmp_live_market_watch.json
Invoke-WebRequest "https://lhinvt.web.app/data/strategy_results_cache.json?ts=$ts" -OutFile tmp_live_strategy_results.json
Invoke-WebRequest "https://lhinvt.web.app/data/strategy_matrix_cache.json?ts=$ts" -OutFile tmp_live_strategy_matrix.json
Invoke-WebRequest "https://lhinvt.web.app/data/warrants_data.json?ts=$ts" -OutFile tmp_live_warrants_data.json
Invoke-WebRequest "https://lhinvt.web.app/data/news_cache.json?ts=$ts" -OutFile tmp_live_news_cache.json
```

These `tmp_live_*` files are inspection-only. Do not commit them.

Quick endpoint check:

```powershell
$urls=@(
 'https://lhinvt.web.app/stocks',
 'https://lhinvt.web.app/data/market_data.json',
 'https://lhinvt.web.app/data/market_watch.json',
 'https://lhinvt.web.app/data/strategy_results_cache.json',
 'https://lhinvt.web.app/data/strategy_matrix_cache.json',
 'https://lhinvt.web.app/data/warrants_data.json',
 'https://lhinvt.web.app/data/news_cache.json'
)
foreach($u in $urls){
 try { $r=Invoke-WebRequest -Uri $u -Method Head -UseBasicParsing -TimeoutSec 20; "$($r.StatusCode) $u" }
 catch { "ERR $u $($_.Exception.Message)" }
}
```

Expected: all `200`.

## 4. Main local evidence files for stock data and indicators

Use these files before answering/reporting stock metrics:

### Public/live cache files

- `firebase_public/data/market_data.json`
- `firebase_public/data/market_watch.json`
- `firebase_public/data/charts/<SYMBOL>.json`
- `firebase_public/data/charts/<SYMBOL>_day.json`
- `firebase_public/data/charts/<SYMBOL>_week.json`
- `firebase_public/data/charts/<SYMBOL>_month.json`
- `firebase_public/data/charts/<SYMBOL>_touchzone_day.json`
- `firebase_public/data/strategy_results_cache.json`
- `firebase_public/data/strategy_matrix_cache.json`
- `firebase_public/data/lh2_final_current_watchlist.json`
- `firebase_public/data/warrants_data.json`
- `firebase_public/data/news_cache.json`

### Internal/source cache files

- `data/v3_full_indicator_cache_v2.json`
- `data/rs_levels_vn100_cache.json`
- `data/rs_levels_hsx_all_cache.json`
- `data/hourly_indicators_vn100_cache.json`
- `data/weekly_indicators_vn100_cache.json`
- `data/monthly_indicators_vn100_cache.json`
- `data/core12_ml_sr_full_universe.json`
- `data/lh_canonical_indicators_daily.json`
- `data/market_data.json`
- `data/popup_ichimoku_update_summary.json`

## 5. Freshness checks for stock/current indicators

Before reporting a stock's latest/current data, verify:

1. `asOfDate`, `date`, `tradingDate`, `updated_at`, `time`, or equivalent timestamp.
2. Latest EOD data from chart/history file if available.
3. Live cache date vs local cache date.
4. Do not use stale cache if a newer EOD row exists.

Recommended priority for stock current values:

1. Manual override only if it has explicit evidence.
2. Latest EOD/chart data for that symbol.
3. `market_data.json` / `market_watch.json` only if not stale vs EOD/chart.
4. Indicator cache only if its row date is not older than the latest supported EOD/chart data.

If stale, write/report clearly:

```text
STALE_CACHE_GUARD: skipped <file/value> because its date < older date > is older than latest supported EOD < latest date >.
```

## 6. Refresh latest local web data

### Full after-close stock/chart/strategy/popup refresh

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
python lh_after_close_update\run_lh_after_close_update.py
```

### Popup indicators only

```powershell
python update_popup_ichimoku_all_symbols.py
python build_firebase_cache_site.py
```

Expected cache builder log:

```text
[build_html] HARD-SKIPPED: firebase_public HTML is canonical; data refresh only.
```

If HTML is rebuilt/overwritten, stop and fix builder before deploy.

### News only

```powershell
python refresh_news_cache_lh.py
python build_news_translate_cache.py
```

### Warrants only

```powershell
python refresh_warrants_cache_lh.py
python build_warrant_catalog_cache.py
```

### Canonical indicators only

```powershell
python build_lh_canonical_indicators_daily.py
```

## 7. Popup / stock indicator fields Codex should extract

When writing Model3 / reports / strategy context, extract these when evidence exists:

- price / close / lastClose
- asOfDate / date / tradingDate
- volume
- avgVol20
- volumeRatio
- MA10 / MA20 / MA50 / MA100 / MA200
- RSI14
- MACD
- MACD signal
- MACD histogram
- ADX
- +DI
- -DI
- Bollinger upper / mid / lower
- bbPercent / %BB
- Ichimoku Tenkan / Kijun / cloud fields if present
- ROC20 / ret5
- support
- resistance
- RS levels
- stop / invalid
- rankScore
- buyScore
- riskScore
- timeframe: day / hour / week / month

If the field is missing, leave blank or say missing. Do not infer.

## 8. Strategy contract — final strategies only

The only public/final strategy contract is:

- `LH1_FINAL`
- `LH2_FINAL`
- `LH3_FINAL`
- `LH4_FINAL`

Do not revive old/non-final variants.

### Required strategy output files

Keep these in sync:

- `data/strategy_results_cache.json`
- `firebase_public/data/strategy_results_cache.json`
- `data/live_overrides/strategy_results_cache.json`
- `data/strategy_matrix_cache.json`
- `firebase_public/data/strategy_matrix_cache.json`
- `data/live_overrides/strategy_matrix_cache.json`
- `firebase_public/data/lh2_final_current_watchlist.json`

### Matrix signalKey mapping

`strategy_matrix_cache.json` columns must include `signalKey`:

- `LH1_FINAL` -> `b4_trend_pullback`
- `LH2_FINAL` -> `lh2_final`
- `LH3_FINAL` -> `clean_split_a_bottom`
- `LH4_FINAL` -> `LH4_FINAL`

Without `signalKey`, the frontend may show the final column name but not the engine data.

## 9. Final strategy evidence files only

Use `FINAL_STRATEGY_FILES.md` as the authoritative list.

Keep:

### Shared live output

- `data/strategy_results_cache.json`
- `firebase_public/data/strategy_results_cache.json`
- `data/live_overrides/strategy_results_cache.json`
- `data/strategy_matrix_cache.json`
- `firebase_public/data/strategy_matrix_cache.json`
- `data/live_overrides/strategy_matrix_cache.json`

### LH1_FINAL

- `data/b4_trend_pullback_dist3_target8_from_saved_trades.json`
- `B4_TREND_PULLBACK_SPEC.md`

### LH2_FINAL

- `build_lh2_v6.py`
- `scan_lh2_final_current_watchlist.py`
- `data/lh2_final_current_watchlist.json`
- `firebase_public/data/lh2_final_current_watchlist.json`

### LH3_FINAL

- `data/v3_clean_split_rs_action_backtest.json`
- `data/v3_clean_split_baseline_locked.json`
- `save_v3_clean_split_baseline.py`

### LH4_FINAL

- `backtest_wave_entry_base_6m_target20_h60.py`
- `data/wave_entry_base_6m_target20_h60_backtest.json`

Do not re-add old/non-final files such as:

- `backtest_a4_*`
- old `backtest_b4_*` variants
- `v3_target*`
- `v3_two_strategies*`
- non-H60 `wave_entry*`
- `archive_unused_strategy_files`
- `tmp_*`

## 10. Strategy freshness rule

Before publishing strategy data:

1. Check source dates in:
   - `data/v3_full_indicator_cache_v2.json`
   - `data/rs_levels_vn100_cache.json`
   - `data/lh_canonical_indicators_daily.json`
   - `firebase_public/data/charts/*.json` if strategy engine uses chart rows.
2. If source rows are stale, fix data source first.
3. Do not merely update timestamp.
4. For all BUY/WATCH items, verify `asOfDate` and `lastClose` are latest supported by evidence.

## 11. LH2_FINAL known evidence

Git evidence:

- `b577b030 Publish LH2 final to Firebase web cache`
- `c88ceb1d Use chart resistance targets for LH2 watchlist`

Files:

- `build_lh2_v6.py`
- `scan_lh2_final_current_watchlist.py`
- `firebase_public/data/lh2_final_current_watchlist.json`

Preset: `v6 BALANCED`.

Performance from `lh2_final_backtest.json`:

- OOS 2025-2026:
  - trades: 13
  - win rate: 53.85%
  - avg net PnL: +3.85%
  - sum net PnL: +50.02%
  - avg hold: 6.31
- FULL 2023-now:
  - trades: 24
  - win rate: 58.33%
  - avg net PnL: +4.02%
  - sum net PnL: +96.38%
  - avg hold: 8.67

LH2 rule:

- breakout high20/high50
- RS rank >= 70
- volume ratio 1.8..2.5
- OBV slope20 >= 0.9
- VWAP slope5 >= 0.6
- breadth >= 55
- rangePos60 >= 0.9
- ADX14 >= 20
- RSI14 50..100
- nearHigh252 >= 0.95

## 12. LH4_FINAL known evidence

Evidence file:

- `data/wave_entry_base_6m_target20_h60_backtest.json`

Displayed metric:

- `WaveA_base_breakout_safe`, `current180`
- trades: 4
- wins: 3
- losses: 1
- win rate: 75.0%
- avg PnL: +14.29%
- sum PnL: +57.15%
- avg hold: 30.5 sessions

LH4 current scan can be `0 BUY / 0 WATCH` due strict filters. Do not invent candidates.

## 13. Deploy refreshed data to current site

Only after verifying data/frontend guard:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
firebase login:use lamhoabb1@gmail.com
firebase deploy --project security-1c731 --config firebase.lhinvt.json --only hosting
```

## 14. Post-deploy guard

Run:

```powershell
python verify_lh_final_frontend_markers.py
python lh_after_close_update\verify_no_old_version_regression.py
```

Verify live markers:

```powershell
$h=(Invoke-WebRequest -Uri "https://lhinvt.web.app/stocks?verify=$(Get-Date -Format yyyyMMddHHmmss)" -UseBasicParsing -TimeoutSec 30).Content
@('20260621-lh-final-chartfix-1936','wyckoffDetailPane','loadWyckoffMethod','loadAutoChart','stockVolBox','Ichimoku','data-analysis-tab') | ForEach-Object { "$($_): $($h.Contains($_))" }
"forbidden lh-market-indicator-fallback-renderer: $($h.Contains('lh-market-indicator-fallback-renderer'))"
```

Expected:

- Required markers: all `True`
- Forbidden marker: `False`

## 15. Codex response checklist

When Codex reports back to Hòa Đại ka, include:

- Which live/local files were used.
- The latest supported `asOfDate` / data date.
- Whether any source was stale and skipped.
- Whether strategy files were updated in all 3 places: `data/`, `firebase_public/data/`, `data/live_overrides/`.
- Whether deploy went to `https://lhinvt.web.app`.
- Post-deploy marker results.
- Commit hash and push verification if code/data changed.
