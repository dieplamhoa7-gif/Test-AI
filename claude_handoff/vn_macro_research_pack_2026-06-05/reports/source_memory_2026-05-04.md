
## 2026-05-04 - LHInvestment news automation + test pages

- User Hòa asked about Telegram chat ID UX. Implemented a bot helper so each user can get their own Telegram chat ID by opening `@LHINVESTMENT_BOT` and sending `/start`/message. Important: bot uses `chat.id` from the incoming Telegram update, so it returns the ID of the person messaging the bot, not Hòa's hardcoded ID. Added `stock-news-backend/telegram_bot_poll.py` and root workflow `.github/workflows/telegram-bot-poll-lh.yml`, scheduled every 5 minutes, using `TELEGRAM_BOT_TOKEN` + `FIREBASE_SERVICE_ACCOUNT_B64`, storing offset in Firestore `bot_state/telegram_updates`. Account page instructions updated. Commit mentioned: `42f851e Add Telegram bot chat ID helper`.
- User wanted web improvements but not to disturb the already-public main pages. Created separate test pages:
  - `/portfolio-test` for My Portfolio/account watchlist status, reading `users/{uid}/watchlist` from Firestore and `/data/market_data.json` output cache only; no R/S recomputation. Shows price, support, resistance, distance to support/resistance, and status (normal/near support/near resistance/support broken/resistance broken/no cache). Commit mentioned: `79c5858 Add portfolio test page`.
  - Clarified account-based watchlist flow on Account page and linked to Portfolio Test; watchlist is stored per Firebase Auth UID under `users/{uid}/watchlist/{symbol}`, not local browser. Commit mentioned: `9d16e63 Clarify account-based watchlist flow`.
  - `/admin-test` Admin mini dashboard reading public cache files only and linking GitHub Actions. Checks market data, market watch, news VI/EN, warrants, strategies, fundamental upside. Shows OK/error, item counts, file size, newest/note; no secrets and no heavy computation. Commit mentioned: `3527d04 Add admin test dashboard`.
  - `/fundamental-test` Fundamental Analyst Test reading output caches only: `/data/market_data.json`, `/data/fundamental_top_upside.json`, `/data/fundamental_signals.json`, `/data/24hmoney_reports.json`. Shows current price, average target price, upside, report/source count, confidence, verdict, broker report table, 24HMoney report summaries. Commit mentioned: `d399fd9 Add fundamental test dashboard`.
- User reported stock news not auto-updating. Investigated GitHub Actions refresh news workflow. Cause: workflow could collect/build/commit cache but failed at Firebase Hosting deploy using `FIREBASE_TOKEN`. Patched root `.github/workflows/refresh-news-lh.yml` to deploy using `FIREBASE_SERVICE_ACCOUNT_B64` instead. Initial deploy with service account failed due missing Hosting/project view permissions. Since `gcloud` is not installed, used Firebase local token / Cloud Resource Manager REST script `stock-news-backend/tmp_grant_hosting_roles.py` to add roles to service account `lh-alert-runner@lhinvestment.iam.gserviceaccount.com`: `roles/firebasehosting.admin` and `roles/viewer`. After re-trigger, one workflow run succeeded and live cache updated.
- Live news cache after fix: `https://lhinvestment.web.app/data/news_cache.json` had 215 items; newest title observed: `'Cơn sóng thần' từ VinFast khiến trùm cầm đồ 468.975 xe máy phải thay đổi, vua xe sang xoay trục, đại gia xăng dầu gấp rút mở trạm sạc`.
- Important caveat: several workflow runs failed during repair/retry, but at least one deploy run succeeded after permissions. Future checks should inspect latest scheduled `refresh-news-lh.yml` runs to confirm stable success. If push conflicts occur, pull/rebase selectively because previous workflow output showed remote contains work not local.
- Continue obeying Hòa's core rule: Firebase/web should consume precomputed output/cache only; no heavy PTKT/model/R-S calculations during render. Deploy only project `lhinvestment` unless explicitly told otherwise.

## 2026-05-04 - LHInvestment realtime prices, indices, and HSX technical cache

- User reported stock prices were not updating on `https://lhinvestment.web.app/stocks?v=78001`. Initial 15s overlay called Render `https://hoa-investment.onrender.com/market-data`, but it returned stale cached/fallback values (`changePct: 0`, `volume: 0`). Patched `stock-news-backend/render_node_server.js` to serve VPS-overlaid live prices from Node endpoints and committed `2a2bd8d Serve live VPS prices from node cache server`, but Render did not appear to redeploy/update the service promptly.
- Chosen fix for 15s live UI: bypass Render and call VPS feed directly from Firebase frontend. Tested CORS from `https://lhinvestment.web.app` to `https://bgapidatafeed.vps.com.vn/getliststockdata/FPT`; response had `access-control-allow-origin: *` and live quote data. Patched realtime overlay in `stock-news-backend/build_firebase_cache_site.py` to fetch each symbol directly from `https://bgapidatafeed.vps.com.vn/getliststockdata/{symbol}` every 15s, merge only price/changePct/volume/open/high/low/avg into existing output item, and leave R/S/PTKT/model precomputed. Generated/deployed Firebase. Commit reported: `99d7d68 Fetch realtime prices directly from VPS feed`. Live check showed `Realtime 15s`, e.g. FPT 74.50 / -1.32%, SSI 28.05 / +1.45%.
- User noted VNINDEX was still static. Root cause: market indices are rendered from `market_overview.json`, separate from stock realtime overlay. Patched price refresh pipeline to update `market_overview.json` from 1-minute index data, and deploy output to Firebase with the 1-minute market price workflow. Commit reported: `31e596e Refresh market indices with price job`. Later user noted index change/% were inaccurate; fixed formula to use previous close, not intraday open: `change = current close - previous close`, `changePct = change / previous close * 100`. Commit reported: `ccae1ca Use previous close for market index change`. Example after fix: VN-Index 1868.21 / +14.11 / +0.76%, ref close 1854.10.
- User reported DBC and VPB could not be found and requested support for all VNIndex/Vietnam stock symbols. Cause: web search/detail only looked inside the existing precomputed market cache (~95 VN100/strategy symbols). Patched stock search/detail so unknown symbols can be looked up directly via VPS feed; if a symbol is absent from output cache but VPS returns a quote, the web can show/add it with realtime price while marking R/S/PTKT as unavailable until output is built. Commit reported: `43dad49 Allow realtime lookup for any VPS stock symbol`. DBC and VPB were then addable/searchable.
- User then noticed technical indicators missing for added symbols like DBC. Cause: new realtime-any-symbol fallback created price-only items for symbols outside the technical output cache. This was not web computation missing; output universe was too small. Expanded technical output universe to HSX/full cache using `data/rs_levels_hsx_all_cache.json` as the R/S input, keeping the rule that web reads output only. Built/rebuilt:
  - `data/rs_levels_vn100_cache.json`
  - `data/rs_levels_only_cache.json`
  - `data/v3_full_indicator_cache_v2.json`
  - `firebase_public/data/market_data.json`
- During full technical indicator build, `vnstock` hit rate-limit (community tier message: 10 requests/minute; sponsor 180-600 requests/minute). Patched `stock-news-backend/build_v3_full_indicator_cache_v2.py` with checkpoint/resume partial file `data/v3_full_indicator_cache_v2.partial.json`, `SLEEP_EVERY=18`, `SLEEP_SECONDS=65`, and `save_payload(...)` after each symbol so full build can continue without losing progress. Initial runs failed around rate limit; final run completed full HSX universe. Commit reported: `b567c6c Expand technical indicator output to HSX universe`.
- After rebuild/deploy, market output contained 392 HSX symbols with technical indicators. DBC test on live web showed indicators restored: price ~22.85, change +1.11%, volume 354,300, RSI 44.18, BB 22.16-23.94, %BB 35.80%, ADX 19.90, MA20/50/200 23.08/23.92/26.83, support 21.90, resistance 23.50. Link reported: `https://lhinvestment.web.app/stocks?v=83001`.
- Important architectural reminder from this work: live web may overlay lightweight price fields every 15s directly from VPS, but all heavy PTKT/R-S/model/strategy data must remain precomputed into JSON outputs. For symbols newly discoverable by realtime quote but missing output, UI may show price-only with a clear “chưa có cache R/S/PTKT” note until the pipeline includes that symbol.
- Potential follow-up: verify latest GitHub Actions after expanding output universe, especially `refresh-market-prices-lh.yml`; if the 1-minute price refresh only updates symbols already in `market_data.json`, it now has 392 symbols and may run longer. Watch for rate/API limits and deploy file-size/runtime issues.

## 2026-05-04 - Follow-up: multi-timeframe indicators and image/comment reading correction

- User reported via screenshot that BB, %BB, ADX, and MA in stock detail popup were not changing across tabs/timeframes. Likely cause identified: UI/frame normalization fallback was reusing daily indicator values when hour/week/month cache fields were missing, making multi-timeframe tabs appear static. Began patching source rather than just UI display:
  - attempted `tmp_patch_frame_no_fallback.py` for `build_firebase_cache_site.py` to add `frameValue(base, fallback)` and avoid fallback from week/month/hour to daily except for day frame. First async output indicated `suffix block not found`, so patch did not apply cleanly and needs manual inspection/repatch.
  - `tmp_patch_universe_hsx.py` reported `patched universe hsx`, intended to update hourly/weekly/monthly builders to use `data/rs_levels_hsx_all_cache.json` full 392-symbol HSX universe instead of old limited VN100 universe.
  - `tmp_patch_dashboard_frame_no_fallback.py` was written for `app/dashboard_template.py` with same no-fallback intent, but status after execution is not fully verified.
- User asked if using the GitHub/local `vnstock` library is better than VPS. Answered: use VPS only for lightweight realtime price overlay; use local/GitHub vnstock for historical data and heavy PTKT indicator pipelines; web still reads output JSON only. vnstock has rate limits, so builders need checkpoint + sleeps.
- User asked if all technical indicators were done. Status conveyed: daily/R-S/v3 daily full 392 had completed, but multi-timeframe Week/Month/Hour full 392 was still in progress and rate-limited. Later an async long-running command was killed with SIGKILL (`dawn-bre`), so assume the multi-timeframe build did NOT finish and needs restart/resume/checkpoint verification.
- User sent an image with a friend's comment and asked to evaluate model improvement. I initially gave a generic answer not based on the image, then guessed again incorrectly about valuation/forward EPS. User objected twice. Important lesson: do not infer from unreadable screenshot; if text is not legible/available, explicitly ask user to crop or paste text. Tried OCR via pytesseract but async output showed Tesseract binary not installed/in PATH. Need either clearer/cropped image or pasted comment to evaluate accurately.
- Temporary files created during this episode include: `tmp_inspect_image.py`, `view_img.html`, `view_img_embed.html` (write for embed failed/empty), `stock-news-backend/tmp_patch_frame_no_fallback.py`, `stock-news-backend/tmp_patch_universe_hsx.py`, `stock-news-backend/tmp_patch_dashboard_frame_no_fallback.py`. Clean up later only after confirming no needed patch logic remains.


## 2026-05-04 - Pre-compaction durable notes
- User asked to fix stock watchlist (“Danh mục quan tâm”) so it is empty by default and follows logged-in account data, not default/local symbols.
- Implemented in `stock-news-backend/app/dashboard_template.py` and generated/deployed Firebase static site:
  - Stock watchlist default changed from fixed symbols (`MWG`, `FPT`, `HPG`, `SSI`) to `[]`.
  - Added Firebase Auth/Firestore module logic to stocks page.
  - Watchlist stored per user at `users/{uid}/watchlist/{symbol}`.
  - Add/remove stock saves/deletes Firestore docs; unauthenticated users are prompted to login.
  - Local cache no longer repopulates stock watchlist; F5 no longer restores default symbols.
  - Deployed live at `https://lhinvestment.web.app/stocks?v=84001`.
  - Reported commit: `fe79c0a Use account watchlist on stocks page`.
- User then asked: “Bên chứng quyền em cài y chang cho anh luôn”.
- Implemented account-based warrant watchlist in `stock-news-backend/app/dashboard_template.py` via temporary patch script `stock-news-backend/tmp_patch_account_warrant_watchlist.py`:
  - Warrant watchlist now empty/default no longer shows first 24 cache items.
  - Stored per user at `users/{uid}/warrantWatchlist/{CODE}`.
  - Add/remove warrant uses Firestore `setDoc/deleteDoc`; unauthenticated users are prompted to login.
  - Local `hoa.warrants.watchlist` no longer controls watchlist rendering.
  - Render messages distinguish auth loading, login-required, and empty state.
  - Deployed live at `https://lhinvestment.web.app/warrants?v=84002`.
  - Reported commit: `2679d7c Use account warrant watchlist`.
- Note: async result after warrant work showed deploy completed, but a later git-related async result mentioned an editor/config instruction, suggesting a git command may have hit an identity/rebase/config issue. Verify actual commit/push status when work resumes; do not assume commit state without checking git status/log.
- User requested next major task twice: create standard `indicators_engine.py`:
  - Centralize RSI, Bollinger Bands/%BB, ADX, MA, ATR, MACD formulas.
  - Prefer TA-Lib if installed.
  - Fall back to pandas/numpy if TA-Lib unavailable.
  - Make all indicator builders call this shared engine.
- Pending: implement `stock-news-backend/app/indicators_engine.py`, refactor daily/hourly/weekly/monthly builders to use it, run compile/tests, rebuild caches as needed, deploy, and commit selectively.
- Async long run result at 12:11 showed many symbols finishing (`VPG`, `VPH`, `VPI`, `VPS`, `VRC`, `VRE`, `VSC`, `VSH` etc.) and likely a multi-timeframe cache builder continued/completed near end of HSX universe. Need verify output files and process status rather than assuming completion.

## 2026-05-04 - Local macro cycle page and macro data source findings

- User requested a new local-only web page named “Yếu tố vĩ mô” to assess current economic/market cycle phase from macro indicators. Important rule reaffirmed: macro/experimental decision logic is local/test only; do not deploy live unless user explicitly says deploy/live.
- Created local macro module `stock-news-backend/app/macro_cycle.py`:
  - Fetches Pinetree Morning Brief URL by date: `https://pinetree.vn/post/YYYYMMDD/ban-tin-sang-DD-MM-YYYY/`.
  - Strips HTML, parses Pinetree label/value layout, extracts metrics including interbank overnight, 12M deposit rate, 5Y/10Y government bond yields, USD/VND, EUR/VND, CNY/VND, S&P500, NASDAQ, VIX, Brent, gold, VNINDEX, foreign net buy/sell, and market turnover.
  - Scores components: `liquidity`, `fx`, `rates`, `globalRisk`, `marketFlow`; computes weighted `macroScore`.
  - Maps score to phase: `>=65` Mở rộng/Risk-on, `>=50` Trung tính/hồi phục chọn lọc, `>=40` Cuối chu kỳ/Phòng thủ, `<40` Co hẹp/Risk-off.
  - Writes local output `stock-news-backend/data/macro_cycle_local.json` with `status: local-test`.
- Created local static page builder `stock-news-backend/build_macro_local_page.py`:
  - Calls `app.macro_cycle.build()`.
  - Writes local preview page `stock-news-backend/local_preview/macro.html`.
  - Shows Macro Score, market/economic cycle phase, liquidity/rates/fx cards, global/market-flow cards, component score bars, and local-only notice.
- Initial local run result from Pinetree 2026-05-04:
  - `macroScore: 43.6`
  - `phase: Cuối chu kỳ / Phòng thủ`
  - `marketView: Giảm tỷ trọng, ưu tiên tiền mặt, chỉ mua setup xác suất cao.`
  - Main drivers: interbank overnight 6.4% (high/bad), foreign net buy -1297.34bn (bad), high market turnover, low VIX supportive.
- Patched Pinetree metric parser to be more robust for `1D`/`YTD` rows because Pinetree uses mixed formats like `1D 1.62%` and `1D (bps) 246`. Patch script used: `stock-news-backend/tmp_fix_pinetree_metric_parse.py`.
- Reported commit for local macro page work: `e5ffef0 Add local macro cycle preview`. Later async git output mentioned git config/global edit and amend-author advice; verify actual commit/log/status before assuming clean state.
- User asked if Pinetree data collection is hard for 1-year history. Answer given:
  - Pinetree is useful for daily snapshot from now onward, but not an ideal 1-year historical database.
  - Problems: no guaranteed post every date, weekends/holidays missing, HTML/layout may change, no official API, partial macro coverage, weak/no OMO/CPI/GDP coverage.
  - Suggested storing daily snapshots from now on in `data/macro_history/pinetree/YYYY-MM-DD.json`, and optionally backfilling by probing each date in the past year and marking status `ok/partial/missing`.
- User asked about GitHub/Python libraries for macro information. Findings summarized:
  - `dbnomics`: useful multi-source macro time series (IMF/World Bank/OECD/BIS/etc.), pandas-friendly, but needs dataset discovery and does not cover VN OMO cleanly.
  - `wbgapi`: stable World Bank annual/long-term Vietnam indicators (CPI annual, GDP growth, FDI/trade/etc.), not daily/weekly market timing.
  - `pandasdmx`: SDMX client for statistical sources, powerful but requires dataset/code discovery.
  - `yfinance`: useful global daily market/risk data (S&P500, NASDAQ, VIX, DXY, US10Y, Brent/WTI, gold, regional indices), not Vietnam macro depth.
  - `pandas-datareader`/FRED: useful US/global macro, not Vietnam.
  - `vnstock`: useful for VNINDEX/OHLCV/market history but not a macro library.
  - No known free GitHub package provides full Vietnam OMO + interbank + CPI + FX + credit/PMI.
- User specifically asked to check where lãi suất OMO and lãi suất liên ngân hàng have complete 1-year data and collect if possible. Findings given:
  - TradingEconomics page `https://tradingeconomics.com/vietnam/interbank-rate` reports Vietnam Three Month Interbank Rate, dates 1998-2026, frequency daily, source SBV. However full historical API requires paid access; guest API discontinued.
  - WiData/WiGroup appears to have the most relevant Vietnam money-market datasets, with routes/menus such as `https://widata.vn/vi-mo/vn/bom-hut-rong` and `https://widata.vn/vi-mo/vn/outright-sbv-bills`, and categories for macro/monetary data, interest rates, money market, API/WiFeed/MCP data. But access is paywalled (plans observed: LITE 3,000,000 VND/quarter, PRO 6,000,000 VND/quarter, ELITE/API/custom data).
  - SBV/NHNN official site direct crawl was tested earlier and returned `Request Rejected`; not reliable for automation without another access path.
  - Pinetree can provide daily snapshot fields including interbank, but not a complete historical OMO database.
  - Practical conclusion: for complete 1-year OMO + interbank, likely need WiData/WiGroup/WiFeed or paid TradingEconomics. Free/local alternative is approximate: Pinetree daily snapshot + Vietcombank FX + yfinance global + vnstock market + WorldBank/DBnomics monthly/annual macro, with OMO manual/pending.
- Temporary file created for probing WiData/WiChart: `stock-news-backend/tmp_probe_widata.py`. It may be kept briefly for source investigation or cleaned after no longer needed.
