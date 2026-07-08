# LH Investment Web Full Runbook / Skill

Use this skill for **all LH Investment / lhinvestment.web.app / future LHINVT.web.app** work: deploys, data refresh, charts, warrants, news, strategies, frontend rollback protection, popup indicators, and migration to a new Firebase project.

## Core Rules

1. **Canonical deployed frontend/data folder:**
   - `stock-news-backend/firebase_public/`
   - Firebase Hosting deploys from this folder.
   - Do not rebuild/overwrite final HTML unless Hòa Đại ka explicitly requests frontend changes.

2. **Fragile final frontend:**
   - Main page: `firebase_public/stocks.html`
   - Final version marker must remain:
     - `20260621-lh-final-chartfix-1936`
   - Important markers/features that must remain:
     - `wyckoffDetailPane`
     - `loadWyckoffMethod`
     - `stockVolBox`
     - `loadAutoChart`
     - `Ichimoku`
     - `data-analysis-tab`
   - Forbidden rollback/fallback marker:
     - `lh-market-indicator-fallback-renderer`

3. **No blind frontend edits:**
   - If UI looks wrong, inspect JSON/schema/data first.
   - Only touch HTML/CSS/JS if data/schema is correct and user asked for UI/frontend change.

4. **Evidence-only data:**
   - Do not fabricate dates, close prices, performance, win rates, PnL, signals, or strategy mapping.
   - If a metric file is missing, say it is missing; search git history before declaring absent.

5. **Vietnamese UTF-8:**
   - Do not patch Vietnamese through inline shell one-liners.
   - Use UTF-8-safe Python/files.
   - Before deploy, guard against mojibake markers: `�`, `Ð`, `ThA`, `phá»`, `Ä‘`, broken `?` in Vietnamese text.

6. **Git discipline:**
   - Avoid `git add .` / `git add -A`.
   - Add exact files only.
   - Remote can advance; use `git fetch origin` + `git rebase origin/master`, never force-push.
   - PowerShell can show `NativeCommandError` for successful `git push`; verify with:
     - `git rev-parse --short HEAD`
     - `git ls-remote origin refs/heads/master`

## Repo / Project Paths

- Workspace root: `C:\Users\HoaD-CVDT\.openclaw\workspace`
- Main repo: `stock-news-backend/`
- Canonical public/deploy folder: `stock-news-backend/firebase_public/`
- Firebase config:
  - `stock-news-backend/firebase.json`
  - `stock-news-backend/.firebaserc`
- Old Firebase project/site (do not use unless Hòa explicitly asks):
  - Firebase project: `lhinvestment`
  - URL: `https://lhinvestment.web.app`
- Current primary Firebase project/account deployment:
  - Google account used by Firebase CLI after login: `lamhoabb1@gmail.com`
  - Project display name: `Security`
  - Project ID: `security-1c731`
  - Default project site: `security-1c731.web.app`
  - Added Hosting site for LH Investment: `lhinvt`
  - New live URL: `https://lhinvt.web.app`

## Main Deploy Command

Current primary deploy target is `https://lhinvt.web.app`. Do **not** deploy LH Investment routine updates to old `lhinvestment` unless Hòa explicitly asks.

From `stock-news-backend/`:

```powershell
firebase login:use lamhoabb1@gmail.com
firebase deploy --project security-1c731 --config firebase.lhinvt.json --only hosting
```

`firebase.lhinvt.json` is a deploy config copied from `firebase.json` with `hosting.site = "lhinvt"`.

Do not deploy until `.firebaserc`, `firebase.json` / `firebase.lhinvt.json`, and `firebase_public/` are verified.

## Mandatory Post-Deploy Verification

Run from `stock-news-backend/`:

```powershell
python verify_lh_final_frontend_markers.py
python lh_after_close_update\verify_no_old_version_regression.py
```

Live endpoint checks:

- `https://lhinvestment.web.app/stocks`
- `https://lhinvestment.web.app/data/market_data.json`
- `https://lhinvestment.web.app/data/market_watch.json`
- `https://lhinvestment.web.app/data/strategy_results_cache.json`
- `https://lhinvestment.web.app/data/strategy_matrix_cache.json`
- `https://lhinvestment.web.app/data/warrants_data.json` if warrants changed
- `https://lhinvestment.web.app/data/news_cache.json` if news changed

Check live `/stocks` retains final markers and does not contain forbidden fallback marker.

## Scheduling / GitHub Actions

Workflows under `.github/workflows/`:

- `refresh-eod-stocks-lh.yml`
  - Main after-close EOD stock/data pipeline.
  - Cron: `30 8 * * 1-5` UTC = `15:30 Asia/Saigon` weekdays.
- `refresh-news-lh.yml`
  - News refresh pipeline.
- `refresh-warrants-lh.yml`
  - Warrants refresh pipeline.
- `refresh-warrants-intraday-lh.yml`
  - Intraday warrants refresh.
- `check-user-alerts-lh.yml`
  - User alert checks.

When changing data pipelines, update workflows if needed and verify schedule still matches Hòa Đại ka's requested time.

## After-Close / Daily Stock Pipeline

Main runner:

```powershell
python lh_after_close_update\run_lh_after_close_update.py
```

Related files:

- `lh_after_close_update/run_lh_after_close_update.py`
- `lh_after_close_update/README.md`
- `lh_after_close_update/file_manifest.json`
- `run_after_close_output_lh.py`
- `run_after_close_output_lh.bat`
- `refresh_eod_all_stocks_lh.py`
- `refresh_market_prices_lh.py`
- `build_firebase_cache_site.py`
- `apply_lh_live_overrides.py`

Important: `apply_lh_live_overrides.py` restores files from `data/live_overrides/`. If strategy or matrix output is corrected, update live overrides too or next pipeline may revert.

## Cache Builder / Old-Version Rollback Guard

`build_firebase_cache_site.py` is dangerous if it overwrites final public HTML or fresh popup data.

Required behavior:

- HTML rebuild must be hard-skipped; expected log:
  - `[build_html] HARD-SKIPPED: firebase_public HTML is canonical; data refresh only.`
- It must preserve fresh market data using `popupIndicatorUpdatedAt` before falling back to other timestamps.
- If cache build causes missing popup fields or old frontend, revert/patch builder before deploy.

## Stock / Chart Data

Important chart/data scripts:

- `build_stock_chart_cache.py`
- `export_touchzone_all_day.py`
- `refresh_vn100_history_for_core12.py`
- `build_v3_full_indicator_cache_v2.py`
- `build_hourly_indicators_vn100_cache.py`
- `build_lh_canonical_indicators_daily.py`

Important outputs:

- `firebase_public/data/charts/*.json`
- `firebase_public/data/charts/*_day.json`
- `firebase_public/data/charts/*_week.json`
- `firebase_public/data/charts/*_month.json`
- `firebase_public/data/charts/*_touchzone_day.json`
- `data/v3_full_indicator_cache_v2.json`
- `data/rs_levels_vn100_cache.json`
- `data/rs_levels_hsx_all_cache.json`
- `data/hourly_indicators_vn100_cache.json`
- `data/weekly_indicators_vn100_cache.json`
- `data/monthly_indicators_vn100_cache.json`
- `data/core12_ml_sr_full_universe.json`
- `data/lh_canonical_indicators_daily.json`
- public copies in `firebase_public/data/` where required.

Known issue:

- `rs_levels_hsx_all_cache.json` may be stale (e.g. `2026-05-04`) if `run_rs_levels_hsx_all_safe.py` cannot find `..\vnstock\assets\data\symbols_by_exchange.csv`.
- `build_lh_canonical_indicators_daily.py` must skip stale HSX-all cache via `staleSkipped: true`, not ingest old values.

## Popup / Market Indicator Data

Main script:

```powershell
python update_popup_ichimoku_all_symbols.py
```

Important outputs:

- `data/market_data.json`
- `firebase_public/data/market_data.json`
- `firebase_public/data/market_watch.json`
- `data/popup_ichimoku_update_summary.json`

Fields expected for popup across Day/Hour/Week/Month where evidence exists:

- RSI
- MA20 / MA50 including monthly `ma20Month`, `ma50Month`
- ADX
- Bollinger Bands
- `%BB`
- Ichimoku fields

Verify representative symbols such as MWG/FPT after refresh.

## Strategies / LH1-LH4 Final

Current required public strategy contract from Hòa Đại ka:

- `LH1_FINAL`
- `LH2_FINAL`
- `LH3_FINAL`
- `LH4_FINAL`

Do not deploy only the old public IDs as visible final strategy names unless user explicitly asks:

- `b4_trend_pullback`
- `shakeout_breakdown_rebound`
- `clean_split_a_bottom`

### Strategy files and outputs

Core files:

- `build_strategy_results_from_indicator_cache.py`
- `tmp_build_lh_final_strategy_payload_fresh.py`
- `scan_lh2_final_current_watchlist.py`
- `build_lh2_v6.py`
- `build_lh_canonical_indicators_daily.py`

Outputs that must stay in sync:

- `data/strategy_results_cache.json`
- `firebase_public/data/strategy_results_cache.json`
- `data/live_overrides/strategy_results_cache.json`
- `data/strategy_matrix_cache.json`
- `firebase_public/data/strategy_matrix_cache.json`
- `data/live_overrides/strategy_matrix_cache.json`
- `firebase_public/data/lh2_final_current_watchlist.json`

### Frontend mapping requirement

`strategy_matrix_cache.json` columns must include `signalKey` so the final LH columns can display data from the engine output:

- `LH1_FINAL` -> `signalKey: b4_trend_pullback`
- `LH2_FINAL` -> `signalKey: lh2_final`
- `LH3_FINAL` -> `signalKey: clean_split_a_bottom`
- `LH4_FINAL` -> `signalKey: LH4_FINAL`

Without `signalKey`, frontend may show the LH column name but not the data.

### LH2 Final evidence

Git history proves LH2 final exists:

- `b577b030 Publish LH2 final to Firebase web cache`
- `c88ceb1d Use chart resistance targets for LH2 watchlist`
- Files restored/needed:
  - `build_lh2_v6.py`
  - `scan_lh2_final_current_watchlist.py`
  - `firebase_public/data/lh2_final_current_watchlist.json`

LH2 final preset: `v6 BALANCED`.

LH2 final performance from `lh2_final_backtest.json`:

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

LH2 final rule:

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

### LH4 Final evidence

LH4 performance evidence from wave-entry backtests:

- `data/wave_entry_base_6m_target20_h60_backtest.json`
- Current best displayed metric used:
  - `WaveA_base_breakout_safe`, `current180`
  - trades: 4
  - wins: 3
  - losses: 1
  - win rate: 75.0%
  - avg PnL: +14.29%
  - sum PnL: +57.15%
  - avg hold: 30.5 sessions

LH4 current scan can be 0 BUY/0 WATCH due strict filters. Do not invent candidates.

## Strategy freshness requirement

Hòa Đại ka requires strategies to run on latest close / close phiên trước.

Before publishing strategy:

1. Check input source dates:
   - `data/v3_full_indicator_cache_v2.json`
   - `data/rs_levels_vn100_cache.json`
   - `data/lh_canonical_indicators_daily.json`
   - `firebase_public/data/charts/*.json` if strategy engine uses chart rows.
2. If source rows are stale (e.g. strategy output built today but row `date` is `2026-07-01`), fix data source first.
3. Do not merely update timestamps.
4. For all watch/buy items, verify `asOfDate` and `lastClose` are latest supported by concrete source.

## Warrants / Chứng quyền

Important files/scripts:

- `refresh_warrants_cache_lh.py`
- `build_warrants_data.py`
- `build_warrant_catalog_cache.py`
- `refresh_warrants_lh.yml`
- `refresh_warrants_intraday_lh.yml`

Important outputs:

- `firebase_public/data/warrants_data.json`
- warrant catalog/cache JSON under `data/` and/or `firebase_public/data/` depending script output.
- frontend warrant page/section in `firebase_public/stocks.html` / related final HTML.

When warrants look wrong:

1. Verify source JSON first.
2. Verify schema expected by frontend.
3. Verify `/warrants` or warrant tab on live page only after data is correct.
4. Do not patch layout unless schema/data is correct.

## News / Tin tức

Important scripts:

- `refresh_news_cache_lh.py`
- `build_news_translate_cache.py`
- `notify_news_alerts.py`

Important workflow:

- `.github/workflows/refresh-news-lh.yml`

Important outputs:

- `data/news_cache.json`
- `firebase_public/data/news_cache.json` if copied/deployed by pipeline
- Any translated/summary cache generated by `build_news_translate_cache.py`

Caution:

- `data/news_cache.json` often changes as unrelated live data; stash or exclude before rebases/strategy commits if it is not part of the task.

## Frontend Files

Canonical public frontend under `firebase_public/`.

Key files:

- `firebase_public/stocks.html`
- `firebase_public/index.html` if used as entry/redirect
- `firebase_public/data/app_version.json`
- `firebase_public/assets/lh-logo.jpg`
- `firebase_public/data/*.json`

Do not use archived deploy folders unless explicitly restoring with evidence:

- `_ARCHIVE_DO_NOT_DEPLOY_20260706/`
- `_backups/`

## New Firebase Project Migration to LHINVT.web.app

Current migration status:

- Firebase CLI added and switched to `lamhoabb1@gmail.com`.
- Project confirmed:
  - `security-1c731`
- Hosting site created:
  - `lhinvt`
  - URL: `https://lhinvt.web.app`
- Deploy config created:
  - `stock-news-backend/firebase.lhinvt.json`
- First deploy completed successfully to `https://lhinvt.web.app`.

Deploy command:

```powershell
firebase login:use lamhoabb1@gmail.com
firebase deploy --project security-1c731 --config firebase.lhinvt.json --only hosting
```

Verify new live URL:

- `https://lhinvt.web.app/stocks`
- `https://lhinvt.web.app/data/strategy_matrix_cache.json`
- `https://lhinvt.web.app/data/strategy_results_cache.json`
- `https://lhinvt.web.app/data/market_data.json`
- `https://lhinvt.web.app/data/warrants_data.json`
- `https://lhinvt.web.app/data/news_cache.json`

Run marker checks on live HTML manually/curl for the new URL, since local guard scripts may point at current project.

## Emergency Rollback / Regression Checklist

If site reverts to old version:

1. Check live `/stocks` markers.
2. Check `firebase_public/stocks.html` vs deployed source.
3. Check `build_firebase_cache_site.py` did not rebuild HTML.
4. Check `apply_lh_live_overrides.py` did not restore stale strategy/data.
5. Check GitHub Actions last run and deployed commit.
6. Check `firebase_public/data/app_version.json`.
7. Re-deploy only after verifying canonical `firebase_public/` is correct.

## Exact Files Usually Committed After LH Data/Strategy Work

Add exact paths only, as relevant:

```powershell
git add build_lh_canonical_indicators_daily.py build_lh2_v6.py scan_lh2_final_current_watchlist.py tmp_build_lh_final_strategy_payload_fresh.py
git add data/strategy_results_cache.json data/strategy_matrix_cache.json data/live_overrides/strategy_results_cache.json data/live_overrides/strategy_matrix_cache.json
git add firebase_public/data/strategy_results_cache.json firebase_public/data/strategy_matrix_cache.json firebase_public/data/lh2_final_current_watchlist.json
git add firebase_public/data/lh_canonical_indicators_daily.json firebase_public/data/v3_full_indicator_cache_v2.json firebase_public/data/rs_levels_vn100_cache.json
```

If `data/` is ignored, tracked ignored files may require `git add -f <path>` only when intentionally adding new data files.

## Done Criteria

A task is not done until:

- Correct files are updated in both `data/`, `firebase_public/data/`, and `data/live_overrides/` where applicable.
- Firebase deploy succeeds.
- Live endpoints show expected data.
- Frontend markers pass.
- No forbidden rollback marker appears.
- Git commit and push are verified against remote.
- User-facing summary states exact live state and any caveat.


## 2026-07-08 Cleanup State / Final-Only Rule

Hòa Đại ka explicitly requested that old LHInvestment / CK / non-final strategy files be deleted/cleaned to stop repeated rollback/back-version confusion.

### Clean working folders

- Main repo remains: `C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend`
- Clean deploy/reference copy: `C:\Users\HoaD-CVDT\.openclaw\workspace\LHINVT_WEB_CLEAN`
- Old local material was moved to recoverable trash, not permanently destroyed:
  - `workspace\trash\lhinvestment_old_cleanup_20260708_152124`
  - `workspace\trash\ck_outside_workspace_cleanup_20260708_154951`

### Git cleanup commits

- `68a23466 Clean old LHInvestment temp files`
- `749408a7 Remove obsolete LHInvestment archives and refresh live cache`
- `b71199e0 Keep only final LH strategy backtest files`

### Ignore rules added

`stock-news-backend/.gitignore` blocks re-adding rollback-prone files:

```gitignore
tmp_*
*.pyc
__pycache__/
.firebase/
_ARCHIVE_DO_NOT_DEPLOY_*/
_backups/
archive_unused_strategy_files/
logs/
node_modules/
```

### Final LH strategy files only

The repository should only retain final strategy evidence and live output files listed in:

- `stock-news-backend/FINAL_STRATEGY_FILES.md`

Final public contract:

- `LH1_FINAL`
- `LH2_FINAL`
- `LH3_FINAL`
- `LH4_FINAL`

Keep these final/evidence files:

#### Shared live strategy output

- `data/strategy_results_cache.json`
- `firebase_public/data/strategy_results_cache.json`
- `data/live_overrides/strategy_results_cache.json`
- `data/strategy_matrix_cache.json`
- `firebase_public/data/strategy_matrix_cache.json`
- `data/live_overrides/strategy_matrix_cache.json`

#### LH1_FINAL

- `data/b4_trend_pullback_dist3_target8_from_saved_trades.json`
- `B4_TREND_PULLBACK_SPEC.md`

#### LH2_FINAL

- `build_lh2_v6.py`
- `scan_lh2_final_current_watchlist.py`
- `data/lh2_final_current_watchlist.json`
- `firebase_public/data/lh2_final_current_watchlist.json`

#### LH3_FINAL

- `data/v3_clean_split_rs_action_backtest.json`
- `data/v3_clean_split_baseline_locked.json`
- `save_v3_clean_split_baseline.py`

#### LH4_FINAL

- `backtest_wave_entry_base_6m_target20_h60.py`
- `data/wave_entry_base_6m_target20_h60_backtest.json`

Do not re-add old/non-final variants like `backtest_a4_*`, old `backtest_b4_*` variants, `v3_target*`, `v3_two_strategies*`, non-H60 `wave_entry*`, `archive_unused_strategy_files`, or `tmp_*`.

## How to Get the Latest Web Data

Use this section when Hòa asks “lấy data mới nhất của web”, “update data web”, “check data live”, or when debugging stale UI.

### A. Pull the latest code/cache from GitHub first

From workspace root or repo:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
git fetch origin
git rebase origin/master
```

If PowerShell reports a git push/pull `NativeCommandError`, verify with refs before assuming failure.

### B. Download live data currently served by `lhinvt.web.app`

Use this to compare local cache vs deployed live cache:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
Invoke-WebRequest "https://lhinvt.web.app/data/market_data.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_market_data.json
Invoke-WebRequest "https://lhinvt.web.app/data/market_watch.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_market_watch.json
Invoke-WebRequest "https://lhinvt.web.app/data/strategy_results_cache.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_strategy_results.json
Invoke-WebRequest "https://lhinvt.web.app/data/strategy_matrix_cache.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_strategy_matrix.json
Invoke-WebRequest "https://lhinvt.web.app/data/warrants_data.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_warrants_data.json
Invoke-WebRequest "https://lhinvt.web.app/data/news_cache.json?ts=$(Get-Date -Format yyyyMMddHHmmss)" -OutFile tmp_live_news_cache.json
```

These `tmp_live_*` files are for inspection only. Do not commit them.

### C. Check live endpoint status quickly

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

All should return `200`.

### D. Generate/refresh latest local web data

For after-close stock/chart/strategy/popup refresh:

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
python lh_after_close_update\run_lh_after_close_update.py
```

For popup technical indicators only:

```powershell
python update_popup_ichimoku_all_symbols.py
python build_firebase_cache_site.py
```

For news only:

```powershell
python refresh_news_cache_lh.py
python build_news_translate_cache.py
```

For warrants/CW only:

```powershell
python refresh_warrants_cache_lh.py
python build_warrant_catalog_cache.py
```

For canonical indicators:

```powershell
python build_lh_canonical_indicators_daily.py
```

### E. Deploy refreshed data to current site

```powershell
cd C:\Users\HoaD-CVDT\.openclaw\workspace\stock-news-backend
firebase login:use lamhoabb1@gmail.com
firebase deploy --project security-1c731 --config firebase.lhinvt.json --only hosting
```

### F. Verify no rollback after deploy

Run local guards:

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

- All required markers: `True`
- Forbidden fallback marker: `False`

### G. Commit refreshed data safely

Avoid broad `git add .`. Add exact files that changed, then commit/push:

```powershell
git status --short stock-news-backend
# add exact changed files only, for example:
git add stock-news-backend/firebase_public/data/market_data.json stock-news-backend/firebase_public/data/market_watch.json
git commit -m "Refresh LHINVT web data"
git push origin master
```

If push output has PowerShell `NativeCommandError`, verify:

```powershell
git rev-parse --short HEAD
git ls-remote origin refs/heads/master
```
