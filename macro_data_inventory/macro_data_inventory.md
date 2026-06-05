# Macro Data Inventory - LH Investment Workspace

Created: 2026-06-05T14:05:42

Total macro-related files detected: **562**

## Counts by role

- archive/handoff: 1
- code: 190
- data: 213
- notes/report/skill: 131
- preview/html: 27

## Counts by source hint

- Internal macro score: 65
- Market flow/local: 16
- Pinetree: 27
- SBV/NHNN: 29
- WorldBank/DBnomics/FRED: 4
- unknown/mixed: 384
- yfinance/Yahoo: 37

## High-priority usable macro data/code

- `claude_handoff/vn_macro_research_pack_2026-06-05.zip` — archive/handoff — unknown/mixed — Macro-related file detected by keywords 
- `stock-news-backend/app/macro_cycle.py` — code — Pinetree — Fetcher/parser/scorer for Pinetree Morning Brief macro cycle 
- `stock-news-backend/build_macro_local_page.py` — code — Pinetree — Builds local macro preview HTML page 
- `stock-news-backend/data/macro_overview.json` — data — Internal macro score — Older/static macro overview score cache keys=createdAt,source,input,score,regime,label,allocationHint,components,weights,note; createdAt=2026-05-04T08:16:51.118344+00:00
- `stock-news-backend/data/macro_cycle_local.json` — data — Pinetree — Pinetree daily macro snapshot + local macro regime score keys=createdAt,date,status,data,macroScore,phase,marketView,components,weights; createdAt=2026-05-04T15:54:43.492984; date=2026-05-04; macroScore=43.6; phase=Cuối chu kỳ / Phòng thủ; dataFields=source,url,interbankOvernight,deposit12m,govBond5y,govBond10y,usdVnd,eurVnd,cnyVnd,sp500,nasdaq,vix,brent,gold,vnindex,foreignNetBuyBn
- `stock-news-backend/data/macro_probe_local/sbv_probe.json` — data — SBV/NHNN — Probe results for SBV/NHNN URLs; mostly redirects/page shell keys=createdAt,source,rows; createdAt=2026-05-04T16:22:57.305259; rows=6
- `skills/vn-macro-cycle-research/SKILL.md` — notes/report/skill — Pinetree — Macro skill/source map for regime filter 
- `skills/vn-macro-cycle-research/references/macro-source-map.md` — notes/report/skill — Pinetree — Macro skill/source map for regime filter 

## Full inventory

### `claude_handoff/vn_macro_research_pack_2026-06-05.zip`
- role: archive/handoff
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 27210 bytes; modified: 2026-06-05T11:40:13
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `build_mit18642_50_slide_skill_pdf.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 12338 bytes; modified: 2026-06-05T09:01:53
- keyword_hits: bond; breadth; fx; liquidity; lãi suất; yield

### `build_mit_44page_video_course.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 26269 bytes; modified: 2026-06-04T16:36:39
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `build_mit_50page_original_quality_guide.py`
- role: code
- source_hint: Internal macro score
- owner_hint: Claude/Claude handoff or backup
- size: 33146 bytes; modified: 2026-06-04T22:39:39
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; liquidity; lãi suất; macro; yield

### `build_mit_50page_training_guide_quality.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 24471 bytes; modified: 2026-06-04T22:31:10
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; liquidity; lãi suất; macro; yield

### `build_mit_deep_full_curriculum.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 14799 bytes; modified: 2026-06-04T22:44:27
- keyword_hits: bond; liquidity; lãi suất; yield

### `build_mit_finance_lessons_vi.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 7490 bytes; modified: 2026-06-04T14:54:23
- keyword_hits: bond; lãi suất

### `build_mit_investor_course_full.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 24981 bytes; modified: 2026-06-04T16:32:07
- description: Macro-related file detected by keywords
- keyword_hits: bond; cycle; lãi suất; macro; yield

### `build_mit_pdf_v3_lesson_first.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 15105 bytes; modified: 2026-06-04T15:52:14
- keyword_hits: bond; liquidity; lãi suất; yield

### `build_mit_professional_lecture_deck.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 17734 bytes; modified: 2026-06-04T16:46:04
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `build_mit_remaining_chapters_and_pdf.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 22521 bytes; modified: 2026-06-04T15:13:44
- keyword_hits: liquidity; lãi suất

### `build_mit_training_guide_html_premium.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 15119 bytes; modified: 2026-06-04T16:25:20
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `build_mit_training_guide_pretty.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 17121 bytes; modified: 2026-06-04T16:22:42
- description: Macro-related file detected by keywords
- keyword_hits: bond; gold; liquidity; lãi suất; macro; yield

### `create_trading_strategy_ppt.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 13300 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: vix

### `stock-news-backend/analyze_research_feature_matrix.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 5812 bytes; modified: 2026-06-04T15:58:01
- keyword_hits: pmi

### `stock-news-backend/app/ml_smart_money_features.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 6097 bytes; modified: 2026-05-05T09:59:30
- keyword_hits: liquidity

### `stock-news-backend/archive_unused_strategy_files/20260430_200953/backtest_v3_midcap50_other.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 3779 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: vix

### `stock-news-backend/backtest_b4_shakeout_v2_regime.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 8103 bytes; modified: 2026-05-19T15:36:32
- keyword_hits: breadth

### `stock-news-backend/predict_ml_today.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 8201 bytes; modified: 2026-05-14T14:44:00
- keyword_hits: liquidity

### `stock-news-backend/render_mwg_latest_chart.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 5312 bytes; modified: 2026-06-05T10:06:03
- keyword_hits: liquidity

### `stock-news-backend/render_mwg_pattern_map_chart.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 6923 bytes; modified: 2026-06-05T10:32:39
- keyword_hits: liquidity

### `stock-news-backend/summarize_research_training_report.py`
- role: code
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 3169 bytes; modified: 2026-06-04T15:58:48
- keyword_hits: pmi

### `vendor_audit/TradingAgents/lh_generate_mobile_macro_pdf.py`
- role: code
- source_hint: Internal macro score
- owner_hint: workspace
- size: 10172 bytes; modified: 2026-06-04T10:37:08
- description: Macro-related file detected by keywords
- keyword_hits: cpi; lãi suất; macro; pmi; vĩ

### `FA/macro/fetchers/vnstock_market.py`
- role: code
- source_hint: Market flow/local
- owner_hint: workspace
- size: 10224 bytes; modified: 2026-06-05T13:20:07
- description: Macro-related file detected by keywords
- keyword_hits: breadth; foreign; macro

### `stock-news-backend/analyze_lh1_v2_indicator_conflicts.py`
- role: code
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 3370 bytes; modified: 2026-06-05T13:45:02
- keyword_hits: breadth; liquidity

### `stock-news-backend/build_lh1_premium_v2_four_groups.py`
- role: code
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 11936 bytes; modified: 2026-06-04T17:14:31
- keyword_hits: breadth; liquidity

### `stock-news-backend/build_lh1_premium_v2_four_groups_medium.py`
- role: code
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 12243 bytes; modified: 2026-06-05T13:58:06
- keyword_hits: breadth; liquidity

### `stock-news-backend/build_lh1_premium_v2_four_groups_tight.py`
- role: code
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 12357 bytes; modified: 2026-06-05T10:54:03
- keyword_hits: breadth; liquidity

### `stock-news-backend/optimize_b4_high_precision_core12.py`
- role: code
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 6680 bytes; modified: 2026-05-19T16:58:39
- keyword_hits: breadth

### `vnstock/vnstock/core/utils/parser.py`
- role: code
- source_hint: Market flow/local
- owner_hint: workspace
- size: 47045 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/explorer/kbs/const.py`
- role: code
- source_hint: Market flow/local
- owner_hint: workspace
- size: 18268 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond; foreign

### `vnstock/vnstock/explorer/vci/const.py`
- role: code
- source_hint: Market flow/local
- owner_hint: workspace
- size: 6727 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond; foreign

### `FA/macro/daily_runner.py`
- role: code
- source_hint: Pinetree
- owner_hint: workspace
- size: 15707 bytes; modified: 2026-06-05T13:32:46
- description: Macro-related file detected by keywords
- keyword_hits: brent; cpi; dxy; foreign; fx; gdp; gold; interbank; liên nh; lãi suất; macro; omo; pinetree; sbv; usdvnd; vix; vĩ; worldbank; yfinance

### `FA/macro/fetchers/pinetree.py`
- role: code
- source_hint: Pinetree
- owner_hint: workspace
- size: 6903 bytes; modified: 2026-06-05T13:19:02
- description: Macro-related file detected by keywords
- keyword_hits: bond; brent; foreign; fx; gold; interbank; liên nh; lãi suất; macro; pinetree; turnover; usdvnd; vix

### `FA/macro/fetchers/sbv_rates.py`
- role: code
- source_hint: Pinetree
- owner_hint: workspace
- size: 14757 bytes; modified: 2026-06-05T13:29:15
- description: Macro-related file detected by keywords
- keyword_hits: fx; interbank; lãi suất; macro; nhnn; pinetree; sbv; usdvnd

### `FA/macro/scoring/regime_score.py`
- role: code
- source_hint: Pinetree
- owner_hint: workspace
- size: 9172 bytes; modified: 2026-06-05T11:49:56
- description: Macro-related file detected by keywords
- keyword_hits: bond; brent; dxy; foreign; fx; interbank; liquidity; liên nh; lãi suất; macro; market_flow; pinetree; turnover; usdvnd; vix; yfinance

### `FA/macro/source_probe.py`
- role: code
- source_hint: Pinetree
- owner_hint: workspace
- size: 11278 bytes; modified: 2026-06-05T13:22:32
- description: Macro-related file detected by keywords
- keyword_hits: brent; cpi; dxy; foreign; fx; gdp; gold; interbank; liên nh; lãi suất; macro; nhnn; omo; pinetree; sbv; tradingeconomics; vi-mo; vix; wbgapi; widata; yfinance

### `build_macro_data_inventory.py`
- role: code
- source_hint: Pinetree
- owner_hint: Claude/Claude handoff or backup
- size: 9306 bytes; modified: 2026-06-05T14:01:04
- description: Macro-related file detected by keywords
- keyword_hits: bom_hut; bond; breadth; brent; bơm hút; cpi; credit; cycle; dbnomics; dxy; foreign; fred; fx; gdp; gold; inflation; interbank; kinh_te; kinhte; lai-suat; lai_suat; lien_ngan_hang; liennh; liquidity; liên nh

### `stock-news-backend/app/macro_cycle.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 8216 bytes; modified: 2026-05-04T15:54:42
- description: Fetcher/parser/scorer for Pinetree Morning Brief macro cycle
- keyword_hits: bond; brent; cpi; cycle; foreign; fx; gold; interbank; liquidity; liên nh; lãi suất; macro; market_flow; pinetree; turnover; usdvnd; vix

### `stock-news-backend/build_macro_local_page.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 4578 bytes; modified: 2026-05-04T15:53:35
- description: Builds local macro preview HTML page
- keyword_hits: bond; brent; cycle; foreign; interbank; lãi suất; macro; pinetree; turnover; usdvnd; vix; vĩ

### `stock-news-backend/build_vn_monetary_policy_warehouse.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 13299 bytes; modified: 2026-06-04T11:15:04
- description: Macro-related file detected by keywords
- keyword_hits: bond; foreign; fx; interbank; liquidity; lãi suất; macro; omo; pinetree; sbv; tradingeconomics; turnover; tín phiếu; usd_vnd; usdvnd; vix; yield

### `stock-news-backend/collect_daily_vn_macro.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 4196 bytes; modified: 2026-06-04T11:13:59
- description: Macro-related file detected by keywords
- keyword_hits: interbank; macro; omo; pinetree; sbv

### `stock-news-backend/parse_pinetree_today_to_warehouse.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 6584 bytes; modified: 2026-06-04T10:52:52
- description: Macro-related file detected by keywords
- keyword_hits: bond; brent; foreign; fx; gold; interbank; liên nh; lãi suất; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/summarize_macro_probe_local.py`
- role: code
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 750 bytes; modified: 2026-05-19T09:13:37
- description: Macro-related file detected by keywords
- keyword_hits: macro; pinetree

### `FA/macro/fetchers/sbv_omo.py`
- role: code
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 10215 bytes; modified: 2026-06-05T13:32:14
- description: Macro-related file detected by keywords
- keyword_hits: liên nh; lãi suất; macro; nhnn; omo; sbv; tín phiếu

### `stock-news-backend/scrape_sbv_browser_cdp.py`
- role: code
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 2274 bytes; modified: 2026-06-04T11:01:53
- description: Macro-related file detected by keywords
- keyword_hits: interbank; macro; sbv

### `stock-news-backend/scrape_sbv_visible_pages_to_warehouse.py`
- role: code
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 6675 bytes; modified: 2026-06-04T11:06:08
- description: Macro-related file detected by keywords
- keyword_hits: interbank; liquidity; lãi suất; macro; nhnn; omo; sbv; turnover

### `vendor_audit/TradingAgents/lh_macro_agent_report.py`
- role: code
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 11352 bytes; modified: 2026-06-04T10:44:00
- description: Macro-related file detected by keywords
- keyword_hits: breadth; brent; cpi; dxy; fred; gold; lãi suất; macro; pmi; sbv; vix; vĩ; worldbank; yield

### `vendor_audit/TradingAgents/lh_macro_data_tools.py`
- role: code
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 7714 bytes; modified: 2026-06-04T10:43:16
- description: Macro-related file detected by keywords
- keyword_hits: breadth; cpi; credit; dxy; fx; gold; inflation; interbank; liquidity; macro; pmi; sbv; vix; yield

### `FA/macro/fetchers/worldbank_macro.py`
- role: code
- source_hint: WorldBank/DBnomics/FRED
- owner_hint: workspace
- size: 3320 bytes; modified: 2026-06-05T13:21:09
- description: Macro-related file detected by keywords
- keyword_hits: cpi; credit; dbnomics; gdp; inflation; macro; wbgapi; worldbank

### `BDS_Ver2_9router_test/google_maps_geocoder.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6848 bytes; modified: 2026-05-27T13:25:21
- keyword_hits: gold

### `CLAUDE_FIX_RUN_BACKUP_20260526_113714/stock-news-backend_review_before_run/app/strategy_recommendations.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5940 bytes; modified: 2026-06-04T08:30:49
- keyword_hits: vix

### `CLAUDE_FIX_RUN_BACKUP_20260526_113714/stock-news-backend_review_before_run/app/web_app.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 13698 bytes; modified: 2026-06-04T08:30:49
- keyword_hits: yield

### `CLAUDE_FIX_RUN_BACKUP_20260526_113714/stock-news-backend_review_before_run/auto_refresh_news_15m.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 932 bytes; modified: 2026-06-04T08:30:49
- keyword_hits: cycle

### `CLAUDE_FIX_RUN_BACKUP_20260526_113714/stock-news-backend_review_before_run/build_two_core_strategy_cache.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5433 bytes; modified: 2026-06-04T08:30:49
- keyword_hits: vix

### `CLAUDE_FIX_RUN_BACKUP_20260526_113714/stock-news-backend_review_before_run/run_v1_method_a.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 2591 bytes; modified: 2026-06-04T08:30:50
- keyword_hits: vix

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/app/strategy_recommendations.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5940 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: vix

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/app/web_app.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 13740 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: yield

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/app/wyckoff_vn_specific.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 13051 bytes; modified: 2026-05-29T11:16:52
- keyword_hits: foreign

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/auto_refresh_news_15m.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 898 bytes; modified: 2026-05-24T22:26:55
- keyword_hits: cycle

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/build_two_core_strategy_cache.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5433 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `CLAUDE_INVESTMENT_MODEL_REVIEW/stock-news-backend/run_v1_method_a.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 2591 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `FA/macro/fetchers/__init__.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 0 bytes; modified: 2026-06-05T11:48:26
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `FA/macro/fetchers/vcb_fx.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 4547 bytes; modified: 2026-06-05T13:19:27
- description: Macro-related file detected by keywords
- keyword_hits: fx; kinhte; macro; usdvnd

### `FA/macro/scoring/__init__.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 0 bytes; modified: 2026-06-05T11:48:27
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `FA/macro/storage/__init__.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 0 bytes; modified: 2026-06-05T11:48:27
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `FA/macro/storage/macro_history.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1654 bytes; modified: 2026-06-05T11:50:06
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/docx/scripts/accept_changes.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 4051 bytes; modified: 2026-06-03T16:18:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/xlsx/scripts/recalc.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5782 bytes; modified: 2026-06-03T16:18:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/docx/scripts/accept_changes.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 4051 bytes; modified: 2026-06-03T15:57:29
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/xlsx/scripts/recalc.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5782 bytes; modified: 2026-06-03T15:57:30
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `build_mit_comprehensive_transcript_notes.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11931 bytes; modified: 2026-06-04T16:41:32
- keyword_hits: bond; lãi suất; yield

### `build_mwg_model.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 14878 bytes; modified: 2026-06-04T08:31:01
- description: Macro-related file detected by keywords
- keyword_hits: cpi; gdp; lãi suất; macro

### `build_mwg_model_v3.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 19591 bytes; modified: 2026-06-04T08:31:01
- description: Macro-related file detected by keywords
- keyword_hits: cpi; cycle; macro; vĩ

### `enhance_mwg_model_v4.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7314 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: cycle

### `fix_mwg_model_v4.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7862 bytes; modified: 2026-06-04T08:31:01
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `inject_segment_inputs_v3.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 4702 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: cycle

### `inspect_donga_model.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3690 bytes; modified: 2026-05-19T09:13:36
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `skills/video-to-pdf-trainer/scripts/generate_pdf.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 15685 bytes; modified: 2026-06-05T01:51:56
- keyword_hits: gold

### `stock-news-backend/analyze_momentum_breakout_core_vn30.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9366 bytes; modified: 2026-05-28T21:27:45
- keyword_hits: omo

### `stock-news-backend/app/main.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4389 bytes; modified: 2026-05-03T14:03:17
- keyword_hits: yield

### `stock-news-backend/app/ml_support_model.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4337 bytes; modified: 2026-05-14T14:44:00
- keyword_hits: liquidity

### `stock-news-backend/app/services/summarizer.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4918 bytes; modified: 2026-05-26T08:49:51
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `stock-news-backend/app/strategy_recommendations.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 5940 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: vix

### `stock-news-backend/app/web_app.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 13698 bytes; modified: 2026-05-26T08:49:51
- keyword_hits: yield

### `stock-news-backend/archive_unused_strategy_files/20260430_200953/analyze_midcap_shakeout_strategy.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7277 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: vix

### `stock-news-backend/archive_unused_strategy_files/20260430_200953/backtest_sr_indicator_combo.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 8153 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: omo

### `stock-news-backend/archive_unused_strategy_files/20260501_231939_helper_cache_scans_not_canonical/scan_three_strategies_vn100_current.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 5155 bytes; modified: 2026-05-01T22:56:33
- keyword_hits: vix

### `stock-news-backend/auto_refresh_news_15m.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 1093 bytes; modified: 2026-06-05T13:38:21
- keyword_hits: cycle

### `stock-news-backend/backtest_breakdown_rebound_midcap50_target6.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7032 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/backtest_breakout_score_vn30.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7945 bytes; modified: 2026-05-28T21:46:21
- keyword_hits: omo

### `stock-news-backend/backtest_special_wave_premium_bds_ck_2025h2.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4361 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/backtest_strategies_2023_to_2026q1.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 8587 bytes; modified: 2026-05-30T07:14:53
- keyword_hits: vix

### `stock-news-backend/build_indicator40_sector_features.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 10276 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/build_ml_support_dataset.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 8308 bytes; modified: 2026-05-14T14:44:00
- keyword_hits: liquidity

### `stock-news-backend/build_sr_cluster_features_by_sector.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7467 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/build_two_core_strategy_cache.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 5433 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/lh1_lh4_walkforward_2023_to_now.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9804 bytes; modified: 2026-06-02T13:03:38
- keyword_hits: vix

### `stock-news-backend/lh_fast_selective_2023_summary.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9050 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: liquidity

### `stock-news-backend/lh_fast_selective_v2_2023_summary.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 3920 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: liquidity

### `stock-news-backend/lh_fast_selective_v3_fee_2023_summary.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4031 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: liquidity

### `stock-news-backend/make_vn100_remaining.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 834 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/ml_core12_group_combo_search.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 15032 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/ml_core12_param_optimizer.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 12834 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/ml_core12_parameter_search.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 13697 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/ml_core12_single_param_rank.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 10954 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/ml_indicator40_sector_research.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 8274 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: fx

### `stock-news-backend/ml_indicator_param_search_by_sector_task.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 11941 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/pattern_engine/backtest_indicators.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9467 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: gold

### `stock-news-backend/pattern_engine_v2/backtest_indicators.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9236 bytes; modified: 2026-06-02T14:30:25
- keyword_hits: gold

### `stock-news-backend/remove_manual_tools.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 3891 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: cpi

### `stock-news-backend/run_v1_method_a.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 2591 bytes; modified: 2026-05-19T09:13:37
- keyword_hits: vix

### `stock-news-backend/tmp_create_strategy_rs_ppt.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 15509 bytes; modified: 2026-06-04T08:30:44
- keyword_hits: gold

### `tmp_claude_pattern_pack/stock-news-backend/pattern_engine/backtest_indicators.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 9236 bytes; modified: 2026-06-02T07:18:46
- keyword_hits: gold

### `tmp_claude_pattern_pack/stock-news-backend/run_backtest.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7807 bytes; modified: 2026-06-02T07:18:46
- keyword_hits: gold

### `tmp_claude_pattern_pack_v2/stock-news-backend/pattern_engine/backtest_indicators.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 9236 bytes; modified: 2026-06-02T14:30:25
- keyword_hits: gold

### `tmp_claude_pattern_pack_v2/stock-news-backend/run_backtest.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7807 bytes; modified: 2026-06-02T14:30:25
- keyword_hits: gold

### `tmp_claude_v1_src/stock-news-backend/pattern_engine/backtest_indicators.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 9236 bytes; modified: 2026-06-02T07:30:26
- keyword_hits: gold

### `tmp_claude_v1_src/stock-news-backend/run_backtest.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7807 bytes; modified: 2026-06-02T07:30:26
- keyword_hits: gold

### `tmp_mit18642_trainer_zip/video-to-pdf/scripts/generate_pdf.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 15685 bytes; modified: 2026-06-05T01:51:56
- keyword_hits: gold

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/analysts/market_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6872 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/analysts/news_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3137 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/analysts/sentiment_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 9905 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/researchers/bear_researcher.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3294 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/trader/trader.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2480 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/alpha_vantage_indicator.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11371 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/alpha_vantage_news.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2419 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/build/lib/tradingagents/graph/checkpointer.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3020 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yield

### `vendor_audit/TradingAgents/tests/conftest.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1152 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yield

### `vendor_audit/TradingAgents/tests/test_analyst_execution.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3723 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tests/test_deepseek_reasoning.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 10168 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yield

### `vendor_audit/TradingAgents/tests/test_ollama_base_url.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7375 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yield

### `vendor_audit/TradingAgents/tests/test_signal_processing.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3656 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: cycle

### `vendor_audit/TradingAgents/tests/test_structured_agents.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 14547 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: cycle

### `vendor_audit/TradingAgents/tradingagents/agents/analysts/market_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6872 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/tradingagents/agents/analysts/news_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3137 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tradingagents/agents/analysts/sentiment_analyst.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 9905 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tradingagents/agents/researchers/bear_researcher.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3294 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tradingagents/agents/trader/trader.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2480 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tradingagents/dataflows/alpha_vantage_indicator.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11371 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/tradingagents/dataflows/alpha_vantage_news.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2419 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `vendor_audit/TradingAgents/tradingagents/graph/checkpointer.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3020 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yield

### `vnstock/tests/conftest_enhancements.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 12223 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: yield

### `vnstock/tests/fixtures/__init__.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 667 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/tests/fixtures/symbols.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7716 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/tests/integration/test_vnstock_client.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3027 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: fx; usdvnd

### `vnstock/tests/unit/explorer/test_vci_listing_comprehensive.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 9486 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/tests/unit/explorer/test_vci_quote_comprehensive.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11937 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: liquidity

### `vnstock/vnstock/api/listing.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6083 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/api/trading.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6089 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: foreign

### `vnstock/vnstock/common/client.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 6861 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: fx

### `vnstock/vnstock/common/data.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 21930 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/core/types.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 15567 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/core/utils/client.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11435 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: cycle

### `vnstock/vnstock/core/utils/field/kbs_mappings.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 56590 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: credit; foreign; gold

### `vnstock/vnstock/core/utils/field/normalizer.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 10557 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: credit; fx

### `vnstock/vnstock/explorer/fmarket/const.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2341 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/explorer/fmarket/fund.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 17977 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/explorer/kbs/listing.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 24680 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `vnstock/vnstock/explorer/misc/__init__.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 55 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: gold

### `vnstock/vnstock/explorer/misc/gold_price.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 4018 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: gold

### `vnstock/vnstock/explorer/msn/const.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 4223 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: fx; usdvnd

### `vnstock/vnstock/explorer/vci/company.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 20584 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: foreign

### `vnstock/vnstock/explorer/vci/listing.py`
- role: code
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 12190 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: bond

### `FA/macro/fetchers/yfinance_global.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 3840 bytes; modified: 2026-06-05T13:21:30
- description: Macro-related file detected by keywords
- keyword_hits: brent; dxy; gold; macro; vix; yfinance

### `probe_vietstock_mwg_data.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 1002 bytes; modified: 2026-05-31T19:04:36
- keyword_hits: yfinance

### `tools/pull_mwg_daily_2023_yahoo_stooq.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 4061 bytes; modified: 2026-06-02T13:49:19
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/agents/utils/agent_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7451 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/interface.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7373 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/stockstats_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 6313 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance; yield

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/symbol_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 5535 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: brent; gold; yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/y_finance.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 18797 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold; yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/dataflows/yfinance_news.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7088 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro; yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/default_config.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 6715 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: gdp; inflation; macro; yfinance

### `vendor_audit/TradingAgents/build/lib/tradingagents/graph/trading_graph.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 19303 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/lh_mwg_mock_llm_test.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 5381 bytes; modified: 2026-06-04T09:07:44
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/test.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 648 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tests/test_dataflows_config.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 2436 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tests/test_instrument_identity.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7062 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tests/test_memory_log.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 40777 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tests/test_no_data_handling.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 3623 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tests/test_safe_ticker_component.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 2257 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/tests/test_symbol_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 3040 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold

### `vendor_audit/TradingAgents/tradingagents/agents/utils/agent_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7451 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tradingagents/dataflows/interface.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7373 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tradingagents/dataflows/stockstats_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 6313 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance; yield

### `vendor_audit/TradingAgents/tradingagents/dataflows/symbol_utils.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 5535 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: brent; gold; yfinance

### `vendor_audit/TradingAgents/tradingagents/dataflows/y_finance.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 18797 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: gold; yfinance

### `vendor_audit/TradingAgents/tradingagents/dataflows/yfinance_news.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 7088 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: macro; yfinance

### `vendor_audit/TradingAgents/tradingagents/default_config.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 6715 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: gdp; inflation; macro; yfinance

### `vendor_audit/TradingAgents/tradingagents/graph/trading_graph.py`
- role: code
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 19303 bytes; modified: 2026-06-04T08:43:43
- keyword_hits: yfinance

### `skills/vn-macro-cycle-research/metadata.json`
- role: data
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 221 bytes; modified: 2026-06-05T11:40:02
- description: Macro skill/source map for regime filter
- json_summary: keys=name,description,version,language,status
- keyword_hits: cycle; macro

### `stock-news-backend/data/backtest_b4_shakeout_v2_regime.json`
- role: data
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 2809232 bytes; modified: 2026-05-19T16:40:25
- json_summary: keys=createdAt,method,windows; createdAt=2026-05-19T16:40:25.528188
- keyword_hits: breadth

### `stock-news-backend/data/macro_overview.json`
- role: data
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 834 bytes; modified: 2026-05-04T15:16:51
- description: Older/static macro overview score cache
- json_summary: keys=createdAt,source,input,score,regime,label,allocationHint,components,weights,note; createdAt=2026-05-04T08:16:51.118344+00:00
- keyword_hits: breadth; credit; fx; inflation; macro; pmi; usd_vnd

### `stock-news-backend/data/research_feature_training_report.json`
- role: data
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 9687 bytes; modified: 2026-06-04T15:58:21
- json_summary: keys=createdAt,source,rows,trainRowsWith20dLabel,featureReport,highCorrelationPairs,regimeSummary,note; createdAt=2026-06-04T08:58:21.977024+00:00
- keyword_hits: pmi

### `stock-news-backend/data/v3_midcap50_other_backtest.json`
- role: data
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 54055 bytes; modified: 2026-04-30T07:58:38
- json_summary: keys=createdAt,description,strategy,symbols,trainCandles,testCandles,horizonCandles,minHoldCandles,feePct,progress,failed,trainSummary,testSummary,trainTrades,testTrades; createdAt=2026-04-30T07:58:38.722480
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/research_feature_training_report.json`
- role: data
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 9687 bytes; modified: 2026-06-04T15:58:21
- json_summary: keys=createdAt,source,rows,trainRowsWith20dLabel,featureReport,highCorrelationPairs,regimeSummary,note; createdAt=2026-06-04T08:58:21.977024+00:00
- keyword_hits: pmi

### `stock-news-backend/data/lh1_lh2_walkforward_audit.json`
- role: data
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 2933 bytes; modified: 2026-05-20T14:47:42
- json_summary: keys=createdAt,LH1_Pullback,LH2_Shakeout_Rebound,notes; createdAt=2026-05-20
- keyword_hits: breadth

### `stock-news-backend/data/lh1_premium_v2_four_groups_backtest.json`
- role: data
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 346113 bytes; modified: 2026-06-05T10:48:11
- json_summary: keys=status,createdAt,method,gate,exitPlan,baseCandidates,v2Candidates,windows,trades; createdAt=2026-06-05T10:48:11.261765
- keyword_hits: breadth; liquidity

### `stock-news-backend/data/lh1_premium_v2_four_groups_backtest.partial.json`
- role: data
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 346113 bytes; modified: 2026-06-05T10:48:11
- json_summary: keys=status,createdAt,method,gate,exitPlan,baseCandidates,v2Candidates,windows,trades; createdAt=2026-06-05T10:48:11.261765
- keyword_hits: breadth; liquidity

### `stock-news-backend/data/lh1_premium_v2_four_groups_tight_backtest.json`
- role: data
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 9652 bytes; modified: 2026-06-05T12:46:09
- json_summary: keys=status,createdAt,method,gate,exitPlan,baseCandidates,v2Candidates,windows,trades; createdAt=2026-06-05T12:46:09.485477
- keyword_hits: breadth; liquidity

### `stock-news-backend/data/lh1_premium_v2_four_groups_tight_backtest.partial.json`
- role: data
- source_hint: Market flow/local
- owner_hint: LH Investment backend/OpenClaw
- size: 9652 bytes; modified: 2026-06-05T12:46:09
- json_summary: keys=status,createdAt,method,gate,exitPlan,baseCandidates,v2Candidates,windows,trades; createdAt=2026-06-05T12:46:09.485477
- keyword_hits: breadth; liquidity

### `FA/data/history/2026-06-05.json`
- role: data
- source_hint: Pinetree
- owner_hint: workspace
- size: 1825 bytes; modified: 2026-06-05T11:51:27
- description: Macro-related file detected by keywords
- json_summary: keys=date,fetchedAt,pinetreeStatus,pinetreeError,pinetree,global,scoreVersion,macroScore,phase,marketView,components,weights,warnings; date=2026-06-05; macroScore=50.0; phase=Trung tính - hồi phục chọn lọc
- keyword_hits: brent; dxy; foreign; fx; gold; interbank; liquidity; macro; pinetree; usdvnd; vix; yfinance

### `FA/data/source_registry.json`
- role: data
- source_hint: Pinetree
- owner_hint: workspace
- size: 6315 bytes; modified: 2026-06-05T13:24:30
- description: Macro-related file detected by keywords
- json_summary: keys=_lastUpdated,_description,sources
- keyword_hits: bond; breadth; brent; cpi; credit; dxy; foreign; fx; gdp; gold; inflation; interbank; liên nh; lãi suất; macro; nhnn; omo; pinetree; sbv; tradingeconomics; turnover; tín phiếu; usdvnd; vi-mo; vix

### `stock-news-backend/data/macro_cycle_local.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 2482 bytes; modified: 2026-05-04T15:54:43
- description: Pinetree daily macro snapshot + local macro regime score
- json_summary: keys=createdAt,date,status,data,macroScore,phase,marketView,components,weights; createdAt=2026-05-04T15:54:43.492984; date=2026-05-04; macroScore=43.6; phase=Cuối chu kỳ / Phòng thủ; dataFields=source,url,interbankOvernight,deposit12m,govBond5y,govBond10y,usdVnd,eurVnd,cnyVnd,sp500,nasdaq,vix,brent,gold,vnindex,foreignNetBuyBn
- keyword_hits: bond; brent; cycle; foreign; fx; gold; interbank; liquidity; liên nh; lãi suất; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/data/macro_probe_local/pinetree_1y_probe.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 169272 bytes; modified: 2026-05-04T16:22:40
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,days,start,end,summary,rows; createdAt=2026-05-04T16:22:40.590365; rows=365
- keyword_hits: bond; foreign; interbank; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/data/macro_probe_local/pinetree_1y_probe.partial.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 167700 bytes; modified: 2026-05-04T16:22:36
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,days,start,end,summary,rows; createdAt=2026-05-04T16:22:36.225693; rows=360
- keyword_hits: bond; foreign; interbank; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/data/macro_warehouse/daily_collect_state.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 11498 bytes; modified: 2026-06-04T11:15:24
- description: Macro-related file detected by keywords
- json_summary: keys=startedAt,finishedAt,ok,results,snapshotPath,publicPath,dataQuality,latest
- keyword_hits: interbank; macro; nhnn; omo; pinetree; sbv; turnover; tín phiếu

### `stock-news-backend/data/macro_warehouse/pinetree_daily_raw/pinetree_2026-06-04.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 943 bytes; modified: 2026-06-04T10:52:58
- description: Macro-related file detected by keywords
- json_summary: keys=date,source,sourceUrl,status,interbankOvernight,interbankOvernight_1d_bps,interbankOvernight_ytd_bps,deposit12m,deposit12m_ytd_bps,govBond5y,govBond5y_ytd_bps,govBond10y,govBond10y_1d_bps,govBond10y_ytd_bps,usdVnd,eurVnd,cnyVnd,vnindex,hnx,vn30; date=2026-06-04
- keyword_hits: bond; brent; foreign; gold; interbank; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/data/macro_warehouse/tradingeconomics_vn_monetary_policy.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 1742 bytes; modified: 2026-06-04T10:58:07
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,sourceUrls,licenseNote,items,omo; createdAt=2026-06-04T10:58:00
- keyword_hits: interbank; liquidity; macro; omo; pinetree; sbv; tradingeconomics

### `stock-news-backend/data/macro_warehouse/vn_monetary_policy_series.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 108276 bytes; modified: 2026-06-04T11:15:22
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,rows; createdAt=2026-06-04T11:15:22; rows=236
- keyword_hits: bond; foreign; interbank; macro; pinetree; turnover; usdvnd; vix

### `stock-news-backend/data/macro_warehouse/vn_monetary_policy_snapshot.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 9531 bytes; modified: 2026-06-04T11:15:22
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,status,sources,coverage,monetaryPolicy,marketContextProxy,dataQuality; createdAt=2026-06-04T11:15:22
- keyword_hits: bond; foreign; fx; interbank; macro; nhnn; omo; pinetree; sbv; turnover; tín phiếu; usdvnd; vix; yield

### `stock-news-backend/firebase_public/data/vn_monetary_policy_snapshot.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 9531 bytes; modified: 2026-06-04T11:15:22
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,status,sources,coverage,monetaryPolicy,marketContextProxy,dataQuality; createdAt=2026-06-04T11:15:22
- keyword_hits: bond; foreign; fx; interbank; macro; nhnn; omo; pinetree; sbv; turnover; tín phiếu; usdvnd; vix; yield

### `stock-news-backend/local_ui_redesign_preview/data/vn_monetary_policy_snapshot.json`
- role: data
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 9531 bytes; modified: 2026-06-04T11:15:22
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,status,sources,coverage,monetaryPolicy,marketContextProxy,dataQuality; createdAt=2026-06-04T11:15:22
- keyword_hits: bond; foreign; fx; interbank; macro; nhnn; omo; pinetree; sbv; turnover; tín phiếu; usdvnd; vix; yield

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_metadata/verified_contents.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 53157 bytes; modified: 2026-05-25T19:05:06
- json_summary: listRows=1
- keyword_hits: fx; sbv; vix

### `.bds-browser-profile/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.106.1_0/_metadata/computed_hashes.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 5891 bytes; modified: 2026-06-02T15:03:16
- json_summary: keys=file_hashes,version
- keyword_hits: fx; sbv

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_metadata/verified_contents.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 53157 bytes; modified: 2026-05-19T09:13:29
- json_summary: listRows=1
- keyword_hits: fx; sbv; vix

### `FA/FiinProX_Lai suat thong ke cua NHNN_20266_20260605.xlsx`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 66599 bytes; modified: 2026-06-05T13:45:28
- keyword_hits: nhnn

### `FA/data/manual_override.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 499 bytes; modified: 2026-06-05T13:23:47
- json_summary: keys=_comment,_usage,date,sbvRates,cpi,notes; date=
- keyword_hits: cpi; omo; sbv

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/es-ES.overrides.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: Claude/Claude handoff or backup
- size: 42243 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+1SyE+C2xv,+AcqvUzRry,+B03WuEdbO,+DB/t6WTki,+Ia6/wGZK4,+On7CFwfGv,+S9q8ZixeF,+mv46Ajpn5,/4ALKl4036,/ErDP0ZXGb,/UoXLuqkgW,/aEI3wDjzi,/an+9Ro/tl,/fIS96TPUC,/gqNPEsOxr,/hxHKlyJ0e,/okDC/2QP0,020bYsGb7x,0HnZ1ci6be,0IRRBJERmK
- keyword_hits: fx; omo; sbv

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/fr-FR.overrides.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: Claude/Claude handoff or backup
- size: 53498 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=++xtsf8Ql7,+1SyE+C2xv,+3o7Nj27R7,+AcqvUzRry,+B03WuEdbO,+DB/t6WTki,+Ia6/wGZK4,+S9q8ZixeF,+aOqA2AKhH,+q7p7p/pIw,/1g2b/LSBL,/8fG7YnSUb,/ErDP0ZXGb,/QQeHodk3M,/UoXLuqkgW,/aEI3wDjzi,/fIS96TPUC,/okDC/2QP0,/sbPIW+aJK,00Mje2JKlx
- keyword_hits: fx; sbv

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/it-IT.overrides.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: Claude/Claude handoff or backup
- size: 28478 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+1SyE+C2xv,+3o7Nj27R7,+58sOh/MFo,+B03WuEdbO,+Ia6/wGZK4,+aOqA2AKhH,/8fG7YnSUb,/ErDP0ZXGb,/JqNbmPyxX,/UoXLuqkgW,/qafcqxKzR,0HnZ1ci6be,0IRRBJERmK,0RNkUIUdjA,0bEawu9OB2,0bTASvhRJV,0fJp1i8jLI,0kvM4mSQmv,0uIYueAyDB,0zCqdBEnn7
- keyword_hits: credit; fx; sbv

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/ja-JP.overrides.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: Claude/Claude handoff or backup
- size: 33567 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+1SyE+C2xv,+S9q8ZixeF,+qSf1b/LLJ,+vVZ/G11Zg,/4ALKl4036,/8fG7YnSUb,/UoXLuqkgW,/aEI3wDjzi,/an+9Ro/tl,/fIS96TPUC,/gqNPEsOxr,/hxHKlyJ0e,/okDC/2QP0,/qafcqxKzR,020bYsGb7x,0HnZ1ci6be,0IRRBJERmK,0L0VGgMTRs,0TqmonlxQo,0nXCMmUrgP
- keyword_hits: fx; sbv

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/pt-BR.overrides.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: Claude/Claude handoff or backup
- size: 49655 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=++xtsf8Ql7,+1SyE+C2xv,+3o7Nj27R7,+58sOh/MFo,+AcqvUzRry,+B03WuEdbO,+DB/t6WTki,+Ia6/wGZK4,+On7CFwfGv,+aOqA2AKhH,+pwUpZdss7,+q7p7p/pIw,+qSf1b/LLJ,+qVLDhaj5k,+vVZ/G11Zg,/1g2b/LSBL,/4ALKl4036,/8fG7YnSUb,/ErDP0ZXGb,/aEI3wDjzi
- keyword_hits: fx; omo; sbv

### `stock-news-backend/data/macro_probe_local/sbv_probe.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 11008 bytes; modified: 2026-05-04T16:22:57
- description: Probe results for SBV/NHNN URLs; mostly redirects/page shell
- json_summary: keys=createdAt,source,rows; createdAt=2026-05-04T16:22:57.305259; rows=6
- keyword_hits: interbank; macro; nhnn; omo; sbv

### `stock-news-backend/data/macro_warehouse/sbv_browser_scrape.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 1212 bytes; modified: 2026-06-04T11:02:26
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,results; createdAt=2026-06-04T11:02:26
- keyword_hits: interbank; macro; sbv

### `stock-news-backend/data/macro_warehouse/sbv_monetary_policy_probe.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 8668 bytes; modified: 2026-06-04T11:15:22
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,rows,note; createdAt=2026-06-04T11:15:22; rows=4
- keyword_hits: interbank; macro; omo; sbv

### `stock-news-backend/data/macro_warehouse/sbv_official_visible_scrape.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: LH Investment backend/OpenClaw
- size: 8608 bytes; modified: 2026-06-04T11:15:11
- description: Macro-related file detected by keywords
- json_summary: keys=createdAt,source,policyRates,interbankRates,omo,rawHeads; createdAt=2026-06-04T11:15:11
- keyword_hits: cpi; interbank; lãi suất; macro; nhnn; omo; sbv; turnover; tín phiếu

### `vendor_audit/TradingAgents/lh_test_outputs/lh_macro_snapshot.json`
- role: data
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 5569 bytes; modified: 2026-06-04T11:15:24
- description: Macro-related file detected by keywords
- json_summary: keys=generatedAt,scope,dataQualityScore,counts,globalProxies,vietnamMacro,localMarketProxy,notes
- keyword_hits: breadth; cpi; credit; dxy; fx; gold; inflation; interbank; liquidity; macro; pmi; sbv; vix; yield

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/en/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 95261 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/es/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 101420 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: bond; omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/es_419/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 102056 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/hr/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 98779 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/hu/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 109333 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: gold; omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/nl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 98493 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=LICENSE_URL,PRIVACY_URL,annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title
- keyword_hits: omo; pmi

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/pl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 105101 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/pt_BR/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 100222 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: credit; omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/pt_PT/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 101318 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: credit; omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/sk/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 105606 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo; pmi

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/_locales/sr/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 99034 bytes; modified: 2026-06-02T15:03:14
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/json/engines.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 47969 bytes; modified: 2026-05-25T19:05:04
- json_summary: keys=searchengines
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.106.1_0/_locales/cs/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 913 bytes; modified: 2026-06-02T15:03:16
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.106.1_0/_locales/gl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 927 bytes; modified: 2026-05-05T14:18:52
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.106.1_0/_locales/sk/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 934 bytes; modified: 2026-06-02T15:03:16
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-browser-profile/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.106.1_0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11914 bytes; modified: 2026-06-02T15:03:15
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-browser-profile/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/_metadata/computed_hashes.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11217 bytes; modified: 2026-06-02T15:03:16
- json_summary: keys=file_hashes,version
- keyword_hits: fx; pmi

### `.bds-browser-profile/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7780 bytes; modified: 2021-01-28T22:51:02
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-browser-profile/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/manifest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1322 bytes; modified: 2026-06-02T15:03:15
- json_summary: keys=app,default_locale,description,display_in_launcher,display_in_new_tab_page,icons,key,manifest_version,minimum_chrome_version,name,oauth2,permissions,update_url,version
- keyword_hits: fx

### `.bds-headless-chrome/CertificateRevocation/10542/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1512 bytes; modified: 2026-05-22T19:26:04
- json_summary: listRows=1
- keyword_hits: cpi; fx

### `.bds-headless-chrome/CertificateRevocation/10544/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1512 bytes; modified: 2026-05-23T19:18:34
- json_summary: listRows=1
- keyword_hits: gdp

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/en/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 95261 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/es/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 101420 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: bond; omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/es_419/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 102056 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/hr/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 98779 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/hu/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 109333 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: gold; omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/nl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 98493 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=LICENSE_URL,PRIVACY_URL,annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title
- keyword_hits: omo; pmi

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/pl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 105101 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/pt_BR/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 100222 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: credit; omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/pt_PT/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 101318 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: credit; omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/sk/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 105606 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo; pmi

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/_locales/sr/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 99034 bytes; modified: 2026-05-19T09:13:29
- json_summary: keys=annotation_balloon_color_green,annotation_balloon_color_grey,annotation_balloon_color_red,annotation_balloon_color_yellow,annotation_balloon_info_hint,annotation_balloon_view_site_report,aps_expanded_shield_site_ecommerce,aps_expanded_shield_site_email,aps_expanded_shield_site_financial,aps_expanded_shield_site_signup,aps_expanded_shield_site_unknown,aps_toast_button,aps_toast_list_bullet_four,aps_toast_list_bullet_one,aps_toast_list_bullet_three,aps_toast_list_bullet_two,aps_toast_paragraph,aps_toast_title,category_id_103_name,category_id_ac_description
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/json/engines.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 47969 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=searchengines
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.104.1_0/_locales/cs/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 913 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.104.1_0/_locales/gl/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 928 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.104.1_0/_locales/sk/messages.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 934 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=createnew,explanationofflinedisabled,explanationofflineenabled,extdesc,extname,learnmore,popuphelptext
- keyword_hits: omo

### `.bds-headless-chrome/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.104.1_0/_metadata/computed_hashes.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 5844 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=file_hashes,version
- keyword_hits: fx; omo; vix

### `.bds-headless-chrome/Default/Extensions/ghbmnnjooekpmoecnnnilnnbdlolhkhi/1.104.1_0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11914 bytes; modified: 2026-05-19T09:13:30
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/_metadata/computed_hashes.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 11217 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=file_hashes,version
- keyword_hits: fx; pmi

### `.bds-headless-chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7780 bytes; modified: 2026-05-19T09:13:30
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/Default/Extensions/nmmhkkegccagdldgiimedpiccmgmieda/1.0.0.6_0/manifest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1322 bytes; modified: 2026-05-19T09:13:30
- json_summary: keys=app,default_locale,description,display_in_launcher,display_in_new_tab_page,icons,key,manifest_version,minimum_chrome_version,name,oauth2,permissions,update_url,version
- keyword_hits: fx

### `.bds-headless-chrome/FileTypePolicies/145.0.7584.0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1439 bytes; modified: 2025-12-18T07:40:20
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/FirstPartySetsPreloaded/2025.7.24.0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1864 bytes; modified: 1980-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/FirstPartySetsPreloaded/2025.7.24.0/sets.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 10367 bytes; modified: 1980-01-01T07:00:00
- keyword_hits: omo

### `.bds-headless-chrome/MEIPreload/1.1.0.3/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1766 bytes; modified: 2000-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: pmi

### `.bds-headless-chrome/OnDeviceHeadSuggestModel/20251024.824731831.14/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1796 bytes; modified: 2025-10-31T15:38:04
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/OptimizationHints/677/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1766 bytes; modified: 1980-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/PKIMetadata/1674/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1969 bytes; modified: 1980-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/SSLErrorAssistant/7/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1765 bytes; modified: 1980-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/SafetyTips/3091/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1758 bytes; modified: 2026-01-07T18:49:18
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/Subresource Filter/Unindexed Rules/9.68.0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1529 bytes; modified: 2026-05-01T19:24:30
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/TrustTokenKeyCommitments/2026.3.23.1/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1864 bytes; modified: 2026-03-23T13:11:18
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/TrustTokenKeyCommitments/2026.3.23.1/keys.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 8756 bytes; modified: 2026-03-23T13:11:18
- json_summary: keys=https://issuer.captchafox.com,https://my.contentpass.net,https://privatetokens.dev,https://pst-issuer.hcaptcha.com,https://pst.authfy.tech,https://trusttoken.dev,https://www.amazon.com
- keyword_hits: fx; pmi; vix

### `.bds-headless-chrome/WasmTtsEngine/20260514.1/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2610 bytes; modified: 2026-05-14T21:41:50
- json_summary: listRows=1
- keyword_hits: fx

### `.bds-headless-chrome/WasmTtsEngine/20260514.1/wasm_tts_manifest_v3.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1151 bytes; modified: 2026-05-14T21:41:50
- json_summary: keys=name,manifest_version,version,key,background,permissions,host_permissions,content_security_policy,description,tts_engine,web_accessible_resources
- keyword_hits: fx

### `.bds-headless-chrome/ZxcvbnData/3/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2437 bytes; modified: 2023-02-22T06:20:38
- json_summary: listRows=1
- keyword_hits: dxy; fx

### `.bds-headless-chrome/component_crx_cache/metadata.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 2028 bytes; modified: 2026-05-24T14:11:36
- json_summary: keys=hashes
- keyword_hits: omo

### `.bds-headless-chrome/hyphen-data/120.0.6050.0/_metadata/verified_contents.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7328 bytes; modified: 2001-01-01T07:00:00
- json_summary: listRows=1
- keyword_hits: fx

### `FA/FiinProX_DE_Du_lieu_vi_mo_20260605 (1).xlsx`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 109994 bytes; modified: 2026-06-05T13:45:21
- keyword_hits: vi_mo

### `FA/FiinProX_DE_Du_lieu_vi_mo_20260605 (2).xlsx`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 107303 bytes; modified: 2026-06-05T13:45:23
- keyword_hits: vi_mo

### `FA/FiinProX_DE_Du_lieu_vi_mo_20260605 (3).xlsx`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 103019 bytes; modified: 2026-06-05T13:45:25
- keyword_hits: vi_mo

### `FA/FiinProX_DE_Du_lieu_vi_mo_20260605.xlsx`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 106380 bytes; modified: 2026-06-05T13:45:24
- keyword_hits: vi_mo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/en-US.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 23033 bytes; modified: 2026-06-03T15:52:37
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/es-419.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 26179 bytes; modified: 2026-06-03T15:52:37
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx; omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/es-ES.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 26265 bytes; modified: 2026-06-03T15:52:37
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx; omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/hi-IN.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 46475 bytes; modified: 2026-06-03T15:52:37
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/id-ID.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 24269 bytes; modified: 2026-06-03T15:52:37
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/de-DE.overrides.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 31086 bytes; modified: 2026-06-03T15:52:45
- json_summary: keys=+DB/t6WTki,+Ia6/wGZK4,/8fG7YnSUb,/EOHq8rYPc,/ErDP0ZXGb,/QQeHodk3M,/UoXLuqkgW,0BUTMvePvK,0IRRBJERmK,0Lg76lu7jn,173M62fqu+,1QrgLETRoY,1VbFlPsYRL,1w/eI79UGE,22xRfj5yTg,28SCwGqtr4,2ERgiFTuIj,2JyXZfrx4Q,2RlHRCLVt2,2UBSOFErlV
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/en-US.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 984658 bytes; modified: 2026-06-03T15:52:45
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: credit

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/es-419.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1133876 bytes; modified: 2026-06-03T15:52:45
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/es-419.overrides.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7484 bytes; modified: 2026-06-03T15:52:45
- json_summary: keys=/an+9Ro/tl,1WkY08RVLW,28SCwGqtr4,2qm6Zfzfx3,3Rx6Qo1x+1,3bWVrLD+vH,3cc4CtJM5h,4NN360t3FW,4eIHICfKCI,61mw3AJ22Y,6ggpfr/8lV,8HhujmKGx8,8roPPb2821,B2A4x/wbTg,Bkwi02OgIx,CVYZCBlaq8,CpMRWoMeT/,Dkm/p8uJYU,EDSOnVbVPo,EY1nHGV6e9
- keyword_hits: fx; omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/es-ES.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1134494 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/hi-IN.overrides.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 162033 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=++xtsf8Ql7,+1SyE+C2xv,+3o7Nj27R7,+58sOh/MFo,+AcqvUzRry,+B03WuEdbO,+DB/t6WTki,+HVP+jKuCF,+Ia6/wGZK4,+J3ndTpec1,+On7CFwfGv,+RS2SvTPaG,+S9q8ZixeF,+aOqA2AKhH,+mv46Ajpn5,+pwUpZdss7,+q7p7p/pIw,+qSf1b/LLJ,/4ALKl4036,/8fG7YnSUb
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/id-ID.overrides.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 28746 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+1SyE+C2xv,+Ia6/wGZK4,/1g2b/LSBL,/QQeHodk3M,/aEI3wDjzi,/an+9Ro/tl,0L0VGgMTRs,0RNkUIUdjA,0bTASvhRJV,0fJp1i8jLI,0kvM4mSQmv,0r1iTiKoSi,0uIYueAyDB,1WkY08RVLW,1YyB53/KOc,1w/eI79UGE,2/2yg+qAwp,22xRfj5yTg,28SCwGqtr4,2RlHRCLVt2
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/it-IT.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1125778 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: credit

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/ja-JP.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1345865 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/ko-KR.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1185206 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/ko-KR.overrides.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 52492 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+1SyE+C2xv,+3o7Nj27R7,+AcqvUzRry,+Ia6/wGZK4,+RGRu5gbzd,+a+2ugZ5sB,/8fG7YnSUb,/ErDP0ZXGb,/UoXLuqkgW,/aEI3wDjzi,/fIS96TPUC,/gqNPEsOxr,/okDC/2QP0,/pKvFi9Ak4,0BUTMvePvK,0L0VGgMTRs,0TqmonlxQo,0g7deXDj3b,0r1iTiKoSi,0zCqdBEnn7
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/i18n/pt-BR.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1122491 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/yYn89HLV,+09/bm5myh,+0AXIvgEHO,+0Oum8s8/p,+0X5KLGaKQ,+0zv6gS/c6,+1VvTZ4Z9R,+1pcHyi+yy,+2cz4BweqX,+2dA44o2yx,+2vOinwM7O,+3JTZ35T5m,+3dQ8dsCYA,+3syH4VjJv,+4Rjm0+q1q,+4bzVsrqlB,+4r/aaeR9v,+4sNMiL2sh,+4tCWjrGJc,+4z6kt5Wz4
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/it-IT.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 26098 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ja-JP.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 30580 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ko-KR.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 26989 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/pt-BR.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 25712 bytes; modified: 2026-06-03T15:52:46
- json_summary: keys=+/cwsayrqk,+7sd9hoyZA,+Fax0wMvjs,+NwlCZ9GfR,+W0xFi2jhJ,+qat3UyOdy,+rUDCO79Js,+vRFr4+yQ/,/6Btt89krf,/PgA81GVOD,/Rj+1w2qLm,/bRGKhnXQ6,/eO5H6Jz2q,/waNG9D45T,06KK1e0srf,075Zq8hhWT,0Ezrt/NNqd,0GT0SIETlE,0NmcPHSn/L,0eJo9Vzuvt
- keyword_hits: fx; omo

### `backups/claude-before-reinstall-20260603-163449/Claude/ChromeNativeHost/com.anthropic.claude_browser_extension.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 454 bytes; modified: 2026-06-03T16:33:38
- json_summary: keys=name,description,path,type,allowed_origins
- keyword_hits: cpi

### `backups/claude-before-reinstall-20260603-163449/Claude/config.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1893 bytes; modified: 2026-06-03T16:33:40
- json_summary: keys=updaterLastSeenVersion,locale,lastSeenRequireCoworkFullVmSandbox,hasTrackedInitialActivation,userThemeMode,oauth:tokenCache,dxt:allowlistEnabled:de02162d-3c69-412e-9024-f5352028d7fc,dxt:allowlistLastUpdated:de02162d-3c69-412e-9024-f5352028d7fc,dxt:allowlistCache:de02162d-3c69-412e-9024-f5352028d7fc
- keyword_hits: fx

### `backups/claude-reset-20260603-161427/Claude/ChromeNativeHost/com.anthropic.claude_browser_extension.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 454 bytes; modified: 2026-06-03T16:10:57
- json_summary: keys=name,description,path,type,allowed_origins
- keyword_hits: cpi

### `backups/claude-reset-20260603-161427/Claude/config.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 1893 bytes; modified: 2026-06-03T16:11:51
- json_summary: keys=updaterLastSeenVersion,locale,lastSeenRequireCoworkFullVmSandbox,hasTrackedInitialActivation,userThemeMode,oauth:tokenCache,dxt:allowlistEnabled:de02162d-3c69-412e-9024-f5352028d7fc,dxt:allowlistLastUpdated:de02162d-3c69-412e-9024-f5352028d7fc,dxt:allowlistCache:de02162d-3c69-412e-9024-f5352028d7fc
- keyword_hits: fx; vix

### `mit_18_642_playlist.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 42028 bytes; modified: 2026-06-04T14:52:41
- json_summary: keys=id,title,availability,channel_follower_count,description,tags,thumbnails,modified_date,view_count,playlist_count,channel,channel_id,uploader_id,uploader,channel_url,uploader_url,_type,entries,extractor_key,extractor
- keyword_hits: bond; fx

### `mit_18_642_transcripts/01_b8u2CQLQBVU.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 41654 bytes; modified: 2026-06-04T14:53:07
- json_summary: keys=index,id,title,rows,text; rows=250
- keyword_hits: bond

### `mit_18_642_transcripts/02_z4p87TPCnQc.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 99046 bytes; modified: 2026-06-04T14:53:13
- json_summary: keys=index,id,title,rows,text; rows=603
- keyword_hits: bond; omo

### `mit_18_642_transcripts/03_NZ3Mva95UsQ.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 49691 bytes; modified: 2026-06-04T14:53:15
- json_summary: keys=index,id,title,rows,text; rows=311
- keyword_hits: bond

### `mit_18_642_transcripts/08_RvXwSoGDYvg.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 328354 bytes; modified: 2026-06-04T14:53:22
- json_summary: keys=index,id,title,rows,text; rows=1995
- keyword_hits: bond; yield

### `mit_18_642_transcripts/11_VbtXo62ROC4.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 278004 bytes; modified: 2026-06-04T14:53:26
- json_summary: keys=index,id,title,rows,text; rows=1674
- keyword_hits: credit; liquidity

### `mit_18_642_transcripts/18_2UCHztlWuZg.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 144952 bytes; modified: 2026-06-04T14:53:36
- json_summary: keys=index,id,title,rows,text; rows=894
- keyword_hits: bond; yield

### `mit_18_642_transcripts/19_8XrYjnDHmE4.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 166730 bytes; modified: 2026-06-04T14:53:38
- json_summary: keys=index,id,title,rows,text; rows=1019
- keyword_hits: gold

### `mit_18_642_transcripts_summary.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 5287 bytes; modified: 2026-06-04T14:53:42
- json_summary: listRows=22
- keyword_hits: bond

### `project_coordinates.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 16175 bytes; modified: 2026-05-27T15:56:34
- json_summary: keys=_README,projects
- keyword_hits: gold

### `report_signal_mvp/all_report_signals.csv`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 194951 bytes; modified: 2026-05-19T09:13:36
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `stock-news-backend/data/24hmoney_reports.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 30495 bytes; modified: 2026-04-28T17:34:13
- json_summary: keys=source,updatedAt,items,count
- keyword_hits: lãi suất

### `stock-news-backend/data/breakdown_rebound_midcap50_target6.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 38226 bytes; modified: 2026-04-30T18:23:19
- json_summary: keys=createdAt,description,symbols,targetPct,stopPct,failed,progress,trainSummary,oosSummary,oosBySymbol,trainTrades,oosTrades,excel; createdAt=2026-04-30T18:23:19.722546
- keyword_hits: vix

### `stock-news-backend/data/breakout_score_vn30.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 429658 bytes; modified: 2026-05-06T13:40:09
- json_summary: keys=createdAt,universe,dateWindows,design,thresholdResults,ranked,recommendation; createdAt=2026-05-06T13:40:09.495600
- keyword_hits: omo

### `stock-news-backend/data/common_pre_wave_features_discovery.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 113734 bytes; modified: 2026-05-07T11:58:43
- json_summary: keys=createdAt,researchOnly,method,seedSymbols,positiveEventDefinition,positiveCount,negativeCount,commonPreWaveFeatures,failureFeatures,contrastVsFailures,proposedPreWaveIndicatorSet,perSymbol; createdAt=2026-05-07T11:58:43.705653
- keyword_hits: vix

### `stock-news-backend/data/core12_technical_indicators_spec.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4453 bytes; modified: 2026-05-19T09:11:12
- json_summary: keys=createdAt,purpose,selectionCriteria,core12,initialTaskMapping,replacementNote; createdAt=2026-05-15T15:11:00+07:00
- keyword_hits: foreign

### `stock-news-backend/data/d1_accumulated_exclusive_is_oos_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 196059 bytes; modified: 2026-05-09T20:33:25
- json_summary: keys=createdAt,method,runs; createdAt=2026-05-09T20:33:25
- keyword_hits: vix

### `stock-news-backend/data/d1_independent_models_is_oos_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 299919 bytes; modified: 2026-05-09T20:59:57
- json_summary: keys=createdAt,method,runs; createdAt=2026-05-09T20:59:57
- keyword_hits: vix

### `stock-news-backend/data/d1_phase_strategy_is_oos_accuracy_optimization.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 291814 bytes; modified: 2026-05-09T19:53:06
- json_summary: keys=createdAt,method,features,runs; createdAt=2026-05-09T19:53:06
- keyword_hits: vix

### `stock-news-backend/data/d1_rs_leakage_check_examples.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 4596 bytes; modified: 2026-05-09T20:09:16
- json_summary: keys=createdAt,purpose,examples; createdAt=2026-05-09T20:09:16
- keyword_hits: cycle

### `stock-news-backend/data/d1_two_models_rs_mtf_is_oos_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 206587 bytes; modified: 2026-05-09T20:14:42
- json_summary: keys=createdAt,method,features,runs; createdAt=2026-05-09T20:14:42
- keyword_hits: vix

### `stock-news-backend/data/d1a_d1b_adaptive_ml_is_oos_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 257762 bytes; modified: 2026-05-09T14:26:30
- json_summary: keys=createdAt,method,features,runs; createdAt=2026-05-09T14:26:30
- keyword_hits: cycle; vix

### `stock-news-backend/data/d1a_independent_precision_is_oos.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 227345 bytes; modified: 2026-05-09T21:20:09
- json_summary: keys=createdAt,method,runs; createdAt=2026-05-09T21:20:09
- keyword_hits: vix

### `stock-news-backend/data/d1a_v2_hardgate_ml_rank_is_oos.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 234864 bytes; modified: 2026-05-09T20:41:50
- json_summary: keys=createdAt,method,runs; createdAt=2026-05-09T20:41:50
- keyword_hits: vix

### `stock-news-backend/data/discovered_pre_wave_model_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 848000 bytes; modified: 2026-05-07T12:05:46
- json_summary: keys=createdAt,researchOnly,sourceDiscovery,weights,profiles,trainSymbols,oosSymbols,window,ranked,diagnostics; createdAt=2026-05-07T12:05:46.218628
- keyword_hits: vix

### `stock-news-backend/data/five_strategies_by_sector_variant_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 9330 bytes; modified: 2026-05-10T07:39:24
- json_summary: keys=createdAt,method,sectors,results; createdAt=2026-05-10T07:39:24
- keyword_hits: vix

### `stock-news-backend/data/layered_mtf_launch_signal_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 668801 bytes; modified: 2026-05-07T11:38:50
- json_summary: keys=createdAt,researchOnly,window,principle,profiles,trainSymbols,oosSymbols,ranked,diagnostics; createdAt=2026-05-07T11:38:50.486015
- keyword_hits: omo; vix

### `stock-news-backend/data/lh_fast_selective_2023_summary.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 21348 bytes; modified: 2026-06-02T17:16:21
- json_summary: keys=createdAt,method,strategyMap,windows,allTradesSample; createdAt=2026-06-02T17:16:21.393085
- keyword_hits: liquidity

### `stock-news-backend/data/lh_fast_selective_v2_2023_summary.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 22328 bytes; modified: 2026-06-02T17:18:12
- json_summary: keys=createdAt,method,strategyMap,windows,allTradesSample; createdAt=2026-06-02T17:18:12.164047
- keyword_hits: liquidity

### `stock-news-backend/data/lh_fast_selective_v3_fee_2023_summary.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 22410 bytes; modified: 2026-06-02T17:21:22
- json_summary: keys=createdAt,method,strategyMap,windows,allTradesSample; createdAt=2026-06-02T17:21:22.084414
- keyword_hits: liquidity

### `stock-news-backend/data/midcap_shakeout_strategy_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 854434 bytes; modified: 2026-04-30T19:11:52
- json_summary: keys=createdAt,description,symbols,failed,trainCandles,oosCandles,horizonCandles,windows,fixedCurrent; createdAt=2026-04-30T19:11:52.352250
- keyword_hits: vix

### `stock-news-backend/data/ml/support_model_report.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 1625 bytes; modified: 2026-05-05T10:53:15
- json_summary: keys=createdAt,dataset,featureColumns,supportHoldModel,reboundModel,supportHoldLatest20Pct,reboundLatest20Pct,note; createdAt=2026-05-05T10:53:15.201272
- keyword_hits: liquidity

### `stock-news-backend/data/ml/support_rebound_dataset_meta.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 701 bytes; modified: 2026-05-14T14:44:00
- json_summary: keys=createdAt,rows,symbols,errors,featureColumns; createdAt=2026-05-05T10:53:05.942941
- keyword_hits: liquidity

### `stock-news-backend/data/ml_position_management_is_oos_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 44829 bytes; modified: 2026-05-09T13:28:43
- json_summary: keys=createdAt,method,source,sourceSummary,eventCount,runs,recommendedUse; createdAt=2026-05-09T13:28:43
- keyword_hits: vix

### `stock-news-backend/data/momentum_breakout_core_vn30.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 205880 bytes; modified: 2026-05-28T21:52:57
- json_summary: keys=createdAt,universe,dateWindows,design,thresholdResults; createdAt=2026-05-28T21:52:57.504321
- keyword_hits: omo

### `stock-news-backend/data/normal_launch_loss_and_2026_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 43127 bytes; modified: 2026-05-07T14:51:07
- json_summary: keys=createdAt,source,overall,periods,byMonth,byGroup,lossSummary,winnerSummary,featureStatsWorstToBest,numericBins,recommendations; createdAt=2026-05-07T14:51:07.448025
- keyword_hits: vix

### `stock-news-backend/data/normal_launch_v2_filter_existing_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 165736 bytes; modified: 2026-05-07T15:10:11
- json_summary: keys=createdAt,method,baseline,summary,bySector,lossSummary,keptTrades,rejected,rejectCounts; createdAt=2026-05-07T15:10:11.652359
- keyword_hits: vix

### `stock-news-backend/data/normal_launch_v2_from_cache_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 449680 bytes; modified: 2026-05-07T15:12:02
- json_summary: keys=createdAt,researchOnly,sourceCache,strategy,summary,bySector,byMonth,lossSummary,trades,diagnostics; createdAt=2026-05-07T15:12:02.253357
- keyword_hits: vix

### `stock-news-backend/data/patterns/BSR_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 27730 bytes; modified: 2026-06-02T15:51:28
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:51:28.252978+00:00
- keyword_hits: gold

### `stock-news-backend/data/patterns/GAS_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 30699 bytes; modified: 2026-06-02T15:51:49
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:51:49.175555+00:00
- keyword_hits: gold

### `stock-news-backend/data/patterns/PVS_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 29609 bytes; modified: 2026-06-02T15:52:27
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:52:27.296519+00:00
- keyword_hits: gold

### `stock-news-backend/data/patterns/SBT_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 29465 bytes; modified: 2026-06-02T15:52:31
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:52:31.374402+00:00
- keyword_hits: gold

### `stock-news-backend/data/patterns/SSI_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 30685 bytes; modified: 2026-06-02T15:52:37
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:52:37.265162+00:00
- keyword_hits: gold

### `stock-news-backend/data/patterns/VIX_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 27909 bytes; modified: 2026-06-02T15:52:51
- json_summary: keys=symbol,timeframe,bars,createdAt,period,lastClose,engineFlags,config,patterns,forecast,summary; createdAt=2026-06-02T08:52:51.689804+00:00
- keyword_hits: vix

### `stock-news-backend/data/position_management_indicator_outputs_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 35343 bytes; modified: 2026-05-09T13:23:20
- json_summary: keys=createdAt,method,sourceFiles,d1OutputSummary,strictStateRecomputedFromOutputEvents,currentMtfWithRsExamples,interpretation,recommendedPolicy; createdAt=2026-05-09T13:23:20
- keyword_hits: omo

### `stock-news-backend/data/position_management_ml_weight_optimization_is_oos.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 150139 bytes; modified: 2026-05-09T13:36:16
- json_summary: keys=createdAt,method,source,sourceSummary,eventCount,features,runs,notes; createdAt=2026-05-09T13:36:16
- keyword_hits: vix

### `stock-news-backend/data/s2_full_sector_ml_2025_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 505609 bytes; modified: 2026-05-08T10:09:42
- json_summary: keys=createdAt,window,universe,available,missing,candidateCount,baseline,rules,bestCombos,singleIndicatorEdgesInS2Near3,trades; createdAt=2026-05-08T10:09:42
- keyword_hits: vix

### `stock-news-backend/data/s2_full_sector_ml_oos_2026_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 162525 bytes; modified: 2026-05-08T10:28:11
- json_summary: keys=createdAt,window,universe,available,missing,candidateCount,baseline,rules,bestCombos,singleIndicatorEdgesInS2Near3,trades; createdAt=2026-05-08T10:28:11
- keyword_hits: vix

### `stock-news-backend/data/s2_ml_signal_quality_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 59543 bytes; modified: 2026-05-08T09:00:00
- json_summary: keys=createdAt,source,method,split,baseline,mlThresholdResults,selected,topPositiveWeights,topNegativeWeights,focusSymbols; createdAt=2026-05-08T09:00:00
- keyword_hits: cycle

### `stock-news-backend/data/s2_v2_lifecycle_ml_analysis.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 477795 bytes; modified: 2026-05-08T10:42:20
- json_summary: keys=createdAt,missing,train2025,oos2026; createdAt=2026-05-08T10:42:20
- keyword_hits: cycle

### `stock-news-backend/data/sector_wave_full_indicator_sets_checkpoint.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 1527683 bytes; modified: 2026-05-07T10:01:15
- json_summary: keys=createdAt,window,stop,target,horizon,indicatorGroups,setDefs,chunks,researchOnly,aggregate,ranked,updatedAt; createdAt=2026-05-07T09:53:38.529405
- keyword_hits: vix

### `stock-news-backend/data/sector_wave_monthly_accumulation_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 324241 bytes; modified: 2026-05-07T11:25:05
- json_summary: keys=createdAt,researchOnly,window,monthlyLookbackBars,minMonthlyScore,minCombinedScore,horizon,profiles,summary,byGroup,bySymbol,topMonthlyAccumulationWatch,trades,diagnostics; createdAt=2026-05-07T11:25:05.859514
- keyword_hits: omo

### `stock-news-backend/data/sector_wave_patterns_ohlcv_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 233246 bytes; modified: 2026-05-07T11:00:21
- json_summary: keys=createdAt,window,horizon,groups,profiles,summary,byGroup,bySymbol,trades,diagnostics,researchOnly; createdAt=2026-05-07T11:00:21.729749
- keyword_hits: vix

### `stock-news-backend/data/special_wave_premium_bds_ck_2025h2.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 260706 bytes; modified: 2026-05-07T09:02:56
- json_summary: keys=createdAt,window,symbols,target,horizon,stop,results,diagnostics,researchOnly; createdAt=2026-05-07T09:02:56.677673
- keyword_hits: vix

### `stock-news-backend/data/sr_indicator_combo_backtest_3m.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 365843 bytes; modified: 2026-04-29T11:16:10
- json_summary: keys=createdAt,lookbackDays,horizonSessions,summary,rows; createdAt=2026-04-29T11:16:10.992627; rows=996
- keyword_hits: omo

### `stock-news-backend/data/support_buy_3strategies_core12_summary.csv`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 52808 bytes; modified: 2026-05-12T10:47:18
- keyword_hits: vix

### `stock-news-backend/data/three_phase_wave_recall_evaluation.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 5410 bytes; modified: 2026-05-07T13:52:07
- json_summary: keys=createdAt,researchOnly,objective,window,summary,byDetectionKindExact,detectedExamples,missedExamples,missedFeatureAbsence,perSymbol; createdAt=2026-05-07T13:52:07.696995
- keyword_hits: vix

### `stock-news-backend/data/translation_memory_vi_en.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 697989 bytes; modified: 2026-06-05T13:54:31
- description: Macro-related file detected by keywords
- json_summary: keys=b161324f1e248d413e9ebcd51d8d45b47196cd73,03f99a2b96f742accf94a2e6e8411f7fb93ebec7,5a8d5d9e549b9d585c69b00acbc935f3a9f6ed01,879d3aaf1f8bef1ec72ac32e8cda679deb047a71,dcb8fee332817e5f2635d17a2ca2f2b2fb400a8f,bce80de85fa6ffaf5112d87a5511a5d6b6d38bd4,b68fb4a70b0fdec981094b880999c8170a1cd9c4,6664270bbf8f18f0b90404a2c705688940c2ff02,badcd95b93594348ee9fa778e985cc41d399b17a,c076555e37fdc9b4e6a0047332bd527252e3d5ba,1eb4b529aa16d99b7468b0b36105cb1018eb32c8,3c4503b2b5dea9b3c08be10cad1488ce8f573907,486f24380a024f764167cc768b0591223b87e590,bac04cad8b33347f9c9bed4a16af64cadb585fa8,edf9890c1ef337180ecdd278d16fb4c684ba8e91,e7724246439900003071cd1742fd6a5fe06a86c9,6cd4f54587d2d6c9e645944859d9c6491be5bea9,60e66d638e26b3847412593d80ab4aca4ef26c1a,59b2f024ad2b5da90ece68b05a411b79eda196ef,f818f6e628e9b5c866484cabcfe9023a08434135
- keyword_hits: bond; gold; inflation; macro; omo

### `stock-news-backend/data/v1_method_a_results.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 5922 bytes; modified: 2026-04-30T21:18:43
- json_summary: keys=updatedAt,method,items,errors
- keyword_hits: vix

### `stock-news-backend/data/v2_plus_s1_existing_candidates_2025_to_now.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 802475 bytes; modified: 2026-05-07T15:48:54
- json_summary: keys=createdAt,method,sources,allCandidates,v2_plus_s1_score3,v2_plus_s1_score4,v2_plus_s1_strict5; createdAt=2026-05-07T15:48:54.577534
- keyword_hits: vix

### `stock-news-backend/data/v2_plus_s1_long_2025_to_now_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 493248 bytes; modified: 2026-05-07T15:51:10
- json_summary: keys=createdAt,window,method,v2_plus_s1_score3,v2_plus_s1_strict5; createdAt=2026-05-07T15:51:10.775144
- keyword_hits: vix

### `stock-news-backend/data/v3_target_pct_exact_vn100_remaining_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 91356 bytes; modified: 2026-05-01T10:57:58
- json_summary: keys=createdAt,sample,symbols,config,summary,trades,counts; createdAt=2026-05-01T10:57:58.545202
- keyword_hits: vix

### `stock-news-backend/data/v3_unified_recall_30pct.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 48033 bytes; modified: 2026-05-07T17:19:24
- json_summary: keys=createdAt,target,horizonSessions,window,definition,summary,detectedSymbols,missedSymbols,detectedEvents,missedEvents,selectedSignalCount; createdAt=2026-05-07T17:19:24.133891
- keyword_hits: vix

### `stock-news-backend/data/v3_union_s1_v2_acceleration_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 304614 bytes; modified: 2026-05-07T17:26:41
- json_summary: keys=createdAt,strategy,window,result,candidateCount; createdAt=2026-05-07T17:26:40.988768
- keyword_hits: vix

### `stock-news-backend/data/vn100_remaining_symbols.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 633 bytes; modified: 2026-05-01T10:48:11
- json_summary: keys=baseCount,combinedCount,remainingCount,symbols
- keyword_hits: vix

### `stock-news-backend/data/wyckoff_sr_vn100_local_backtest.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 314774 bytes; modified: 2026-05-29T13:12:14
- json_summary: keys=variants,params
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/24hmoney_reports.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 30495 bytes; modified: 2026-06-02T09:01:42
- json_summary: keys=source,updatedAt,items,count
- keyword_hits: lãi suất

### `stock-news-backend/firebase_public/data/charts/VIX.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 129492 bytes; modified: 2026-06-04T15:25:21
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,patterns; rows=260
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/charts/VIX_month.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 11852 bytes; modified: 2026-06-04T15:25:21
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,patterns; rows=32
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/charts/VIX_touchzone_day.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 11282 bytes; modified: 2026-06-04T15:26:46
- json_summary: keys=symbol,asOfDate,asOfPrice,createdAt,summary,trendlines,srLevels,patterns,candlestickSignals,rows; createdAt=2026-05-28T09:55:00+00:00; rows=0
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/charts/VIX_week.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 64988 bytes; modified: 2026-06-04T15:25:21
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,patterns; rows=133
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/charts/index.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 45159 bytes; modified: 2026-06-04T15:25:27
- json_summary: keys=count,items
- keyword_hits: vix

### `stock-news-backend/firebase_public/data/fundamental_top_upside.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 14321 bytes; modified: 2026-06-05T13:54:31
- description: Macro-related file detected by keywords
- json_summary: keys=items,source
- keyword_hits: vĩ

### `stock-news-backend/firebase_public/data/market_symbols.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 2851 bytes; modified: 2026-06-05T13:54:31
- json_summary: listRows=95
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/24hmoney_reports.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 30495 bytes; modified: 2026-06-02T09:01:42
- json_summary: keys=source,updatedAt,items,count
- keyword_hits: lãi suất

### `stock-news-backend/local_ui_redesign_preview/data/charts/VIX.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 129365 bytes; modified: 2026-06-04T08:31:01
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,srZones,patterns,patternLines; rows=260
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/charts/VIX_month.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 13804 bytes; modified: 2026-06-04T08:31:01
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,srZones,patterns,patternLines; rows=32
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/charts/VIX_touchzone_day.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 11280 bytes; modified: 2026-06-04T08:31:01
- json_summary: keys=symbol,asOfDate,asOfPrice,createdAt,summary,trendlines,srLevels,patterns,candlestickSignals,rows; createdAt=2026-05-28T09:55:00+00:00; rows=0
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/charts/VIX_week.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 64278 bytes; modified: 2026-06-04T08:31:01
- json_summary: keys=symbol,frame,source,rows,ma20,ma50,ema20,ema50,bollinger,macd,rsi,trendline,trendlines,srZones,patterns,patternLines; rows=133
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/charts/index.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 45159 bytes; modified: 2026-06-04T08:31:02
- json_summary: keys=count,items
- keyword_hits: vix

### `stock-news-backend/local_ui_redesign_preview/data/fundamental_top_upside.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 14321 bytes; modified: 2026-06-04T08:42:39
- description: Macro-related file detected by keywords
- json_summary: keys=items,source
- keyword_hits: vĩ

### `stock-news-backend/local_ui_redesign_preview/data/market_symbols.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 2851 bytes; modified: 2026-06-04T08:42:39
- json_summary: listRows=95
- keyword_hits: vix

### `tmp_mwg_bhx_dmx_research.json`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 54460 bytes; modified: 2026-05-31T22:01:35
- description: Macro-related file detected by keywords
- json_summary: listRows=20
- keyword_hits: vĩ

### `vnstock/assets/data/all_symbols.csv`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 95405 bytes; modified: 2026-04-23T14:16:09
- description: Macro-related file detected by keywords
- keyword_hits: vix; vĩ

### `vnstock/assets/data/industries_icb.csv`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 7723 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: gold; omo

### `vnstock/assets/data/symbols_by_exchange.csv`
- role: data
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 232546 bytes; modified: 2026-04-23T14:16:09
- description: Macro-related file detected by keywords
- keyword_hits: bond; vix; vĩ

### `vendor_audit/TradingAgents/lh_test_outputs/mwg_tradingagents_mock_result.json`
- role: data
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 12710 bytes; modified: 2026-06-04T09:08:08
- json_summary: keys=ticker,date,mode,startedAt,ok,decision,state_keys,final_state_preview; date=2026-06-03
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/lh_test_outputs/results/MWG.VN/TradingAgentsStrategy_logs/full_states_log_2026-06-03.json`
- role: data
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 8816 bytes; modified: 2026-06-04T09:08:08
- json_summary: keys=company_of_interest,trade_date,market_report,sentiment_report,news_report,fundamentals_report,investment_debate_state,trader_investment_decision,risk_debate_state,investment_plan,final_trade_decision
- keyword_hits: yfinance

### `.bds-headless-chrome/ZxcvbnData/3/english_wikipedia.txt`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 277015 bytes; modified: 2020-06-02T15:10:56
- keyword_hits: foreign; gold; omo

### `memory/2026-04-29.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw memory notes
- size: 21725 bytes; modified: 2026-04-29T22:33:32
- keyword_hits: liquidity

### `memory/2026-05-07.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw memory notes
- size: 16938 bytes; modified: 2026-05-07T14:47:47
- keyword_hits: breadth; vix

### `memory/2026-05-08.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw memory notes
- size: 2982 bytes; modified: 2026-05-08T08:51:16
- keyword_hits: cycle

### `memory/2026-06-04.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: Claude/Claude handoff or backup
- size: 14723 bytes; modified: 2026-06-04T10:20:58
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; cycle; fx; gold; liquidity; macro

### `reports/MIT18642_Trainer_50_Slide_Deck.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 22403 bytes; modified: 2026-06-05T09:02:00
- keyword_hits: bond; fx; lãi suất; yield

### `reports/MIT_18_642_22_Video_44_Trang_Giang_Day.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 21436 bytes; modified: 2026-06-04T16:36:49
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_50_Trang_ChatGPT_Original_Quality.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 26781 bytes; modified: 2026-06-04T22:39:48
- keyword_hits: bond; credit; liquidity; lãi suất; yield

### `reports/MIT_18_642_Bai_Giang_Chuyen_Nghiep_Cho_Nha_Dau_Tu.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 14714 bytes; modified: 2026-06-04T16:46:11
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_Bai_Hoc_Truoc_Ap_Dung_Sau_v3.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 12558 bytes; modified: 2026-06-04T15:52:24
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_Chuong_01_Lecture_1_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 15103 bytes; modified: 2026-06-04T14:58:40
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_Chuong_02_Linear_Algebra_Probability_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 9528 bytes; modified: 2026-06-04T14:59:35
- description: Macro-related file detected by keywords
- keyword_hits: liquidity; vĩ

### `reports/MIT_18_642_Chuong_04_Portfolio_Risk_Volatility_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 4282 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity

### `reports/MIT_18_642_Chuong_06_MachineLearning_StochasticCalculus_Roadmap_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 4406 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity

### `reports/MIT_18_642_Chuong_07_Ke_Hoach_Trien_Khai_LH_Investment_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 8288 bytes; modified: 2026-06-04T15:26:51
- description: Macro-related file detected by keywords
- keyword_hits: liquidity; macro

### `reports/MIT_18_642_Comprehensive_Transcript_Notes_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 138823 bytes; modified: 2026-06-04T16:41:41
- keyword_hits: bond; credit; gold; lãi suất; omo; yield

### `reports/MIT_18_642_Full_Skill_LH_Model.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 30785 bytes; modified: 2026-06-04T16:16:48
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; liquidity; macro; yield

### `reports/MIT_18_642_Giao_Trinh_Day_Du_Chinh_Chu_VI.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 121397 bytes; modified: 2026-06-04T22:44:36
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 44451 bytes; modified: 2026-06-04T15:13:50
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment_v2.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 53206 bytes; modified: 2026-06-04T15:27:35
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_Khoa_Hoc_Nha_Dau_Tu_22_Video_FULL.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 17888 bytes; modified: 2026-06-04T16:32:18
- description: Macro-related file detected by keywords
- keyword_hits: bond; cycle; lãi suất; macro; yield

### `reports/MIT_18_642_Training_Guide_50_Trang_CHATGPT_FIX.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 20494 bytes; modified: 2026-06-04T22:31:23
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; liquidity; lãi suất; macro; yield

### `reports/MIT_18_642_Training_Guide_LH_Investment_PREMIUM.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: workspace
- size: 13074 bytes; modified: 2026-06-04T16:22:47
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `skills/mit-18-642-transcript-trained-lh-model/SKILL.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 29549 bytes; modified: 2026-06-04T16:16:12
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; liquidity; macro; yield

### `skills/mit-finance-quant-strategy/SKILL.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: Claude/Claude handoff or backup
- size: 10854 bytes; modified: 2026-06-04T15:27:50
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; macro

### `skills/mit-finance-quant-strategy/references/chapter-01-finance-foundations-vi.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 15103 bytes; modified: 2026-06-04T14:58:40
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; lãi suất; macro; yield

### `skills/mit-finance-quant-strategy/references/chapter-02-linear-algebra-probability-vi.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 9528 bytes; modified: 2026-06-04T14:59:35
- description: Macro-related file detected by keywords
- keyword_hits: liquidity; vĩ

### `skills/mit-finance-quant-strategy/references/chapter-04-portfolio-risk-volatility-vi.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 4282 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity

### `skills/mit-finance-quant-strategy/references/chapter-06-ml-stochastic-roadmap-vi.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 4406 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity

### `skills/safe-finance-investing-skill-pack/SKILL.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: OpenClaw skill
- size: 7760 bytes; modified: 2026-06-05T09:21:44
- description: Macro-related file detected by keywords
- keyword_hits: fx; gold; macro

### `stock-news-backend/WYCKOFF_RESEARCH.md`
- role: notes/report/skill
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 11576 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: breadth

### `memory/2026-05-06.md`
- role: notes/report/skill
- source_hint: Market flow/local
- owner_hint: OpenClaw memory notes
- size: 19695 bytes; modified: 2026-05-06T17:05:16
- description: Macro-related file detected by keywords
- keyword_hits: breadth; cycle; macro

### `vnstock/README.md`
- role: notes/report/skill
- source_hint: Market flow/local
- owner_hint: workspace
- size: 48613 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: lãi suất

### `skills/vn-macro-cycle-research/SKILL.md`
- role: notes/report/skill
- source_hint: Pinetree
- owner_hint: OpenClaw skill
- size: 5689 bytes; modified: 2026-06-05T11:39:35
- description: Macro skill/source map for regime filter
- keyword_hits: bond; breadth; brent; bơm hút; cpi; credit; cycle; dbnomics; dxy; foreign; fred; fx; gdp; gold; inflation; interbank; liquidity; liên nh; lãi suất; macro; nhnn; omo; pinetree; pmi; sbv

### `skills/vn-macro-cycle-research/references/macro-source-map.md`
- role: notes/report/skill
- source_hint: Pinetree
- owner_hint: OpenClaw skill
- size: 3063 bytes; modified: 2026-06-05T11:39:56
- description: Macro skill/source map for regime filter
- keyword_hits: breadth; brent; cpi; credit; cycle; dbnomics; dxy; foreign; fred; gdp; gold; inflation; interbank; liquidity; liên nh; lãi suất; macro; nhnn; omo; pinetree; sbv; tradingeconomics; turnover; tín phiếu; vi-mo

### `exports/toliem212_fb_stock_model_scan.md`
- role: notes/report/skill
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 12661 bytes; modified: 2026-06-04T08:56:36
- description: Macro-related file detected by keywords
- keyword_hits: bond; credit; cycle; foreign; fx; gold; inflation; liquidity; macro; sbv

### `f319_tomriddle1234_posts.txt`
- role: notes/report/skill
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 212537 bytes; modified: 2026-06-01T17:33:02
- description: Macro-related file detected by keywords
- keyword_hits: lãi suất; nhnn; pmi; vĩ

### `report_signal_mvp/symbols.txt`
- role: notes/report/skill
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 2215 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: fx; sbv; vix

### `report_signal_mvp/symbols_hose_hnx.txt`
- role: notes/report/skill
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 2215 bytes; modified: 2026-05-19T09:13:36
- keyword_hits: fx; sbv; vix

### `vendor_audit/TradingAgents/lh_test_outputs/mwg_tradingagents_9router_apifree_macro_report.md`
- role: notes/report/skill
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 5734 bytes; modified: 2026-06-04T10:44:19
- description: Macro-related file detected by keywords
- keyword_hits: breadth; brent; cpi; credit; dxy; fred; gold; interbank; lãi suất; macro; pmi; sbv; vix; vĩ; worldbank; yield

### `.bds-headless-chrome/ZxcvbnData/3/female_names.txt`
- role: notes/report/skill
- source_hint: WorldBank/DBnomics/FRED
- owner_hint: Claude/Claude handoff or backup
- size: 26708 bytes; modified: 2020-06-02T15:10:56
- keyword_hits: fred; gold; omo

### `.bds-headless-chrome/ZxcvbnData/3/male_names.txt`
- role: notes/report/skill
- source_hint: WorldBank/DBnomics/FRED
- owner_hint: Claude/Claude handoff or backup
- size: 6672 bytes; modified: 2020-06-02T15:10:58
- keyword_hits: brent; fred; omo

### `.bds-headless-chrome/ZxcvbnData/3/passwords.txt`
- role: notes/report/skill
- source_hint: WorldBank/DBnomics/FRED
- owner_hint: workspace
- size: 241951 bytes; modified: 2020-06-02T15:10:58
- keyword_hits: bond; fred; gold; omo

### `.bds-browser-profile/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9285_0/txt/typosquat.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 840512 bytes; modified: 2026-05-25T19:05:04
- keyword_hits: cpi; fx; pmi

### `.bds-headless-chrome/Default/Extensions/fheoggkfdfchfphceeifdbepaooicaho/8.1.0.9204_0/txt/typosquat.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 840512 bytes; modified: 2026-05-19T09:13:30
- keyword_hits: cpi; fx; pmi

### `.bds-headless-chrome/ZxcvbnData/3/surnames.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 76077 bytes; modified: 2020-06-02T15:11:00
- keyword_hits: bond; gold; omo

### `.bds-headless-chrome/ZxcvbnData/3/us_tv_and_film.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 164290 bytes; modified: 2020-06-02T15:11:02
- keyword_hits: credit; omo

### `MWG_model_notes.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 5686 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: lãi suất

### `QH/page_16_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1327 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_20_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1439 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_22_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1472 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_27_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1459 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_29_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1417 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_33_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1580 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_35_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1564 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_39_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1421 bytes; modified: 2026-05-19T09:13:35
- description: Macro-related file detected by keywords
- keyword_hits: omo; vĩ

### `QH/page_42_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1422 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_47_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1458 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_48_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1519 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_50_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1312 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_52_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1395 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_53_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1255 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_54_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1506 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_56_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1377 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `QH/page_58_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1400 bytes; modified: 2026-05-19T09:13:35
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `QH/page_60_screenshot.png.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 1226 bytes; modified: 2026-05-19T09:13:35
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/pptx/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 10329 bytes; modified: 2026-06-03T16:18:43
- keyword_hits: cycle; gold

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/pptx/editing.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 6881 bytes; modified: 2026-06-03T16:18:43
- keyword_hits: yield

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/schedule/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 2253 bytes; modified: 2026-06-03T16:33:39
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/setup-cowork/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7421 bytes; modified: 2026-06-03T16:33:39
- keyword_hits: omo

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/skill-creator/agents/grader.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 9049 bytes; modified: 2026-06-03T16:18:43
- keyword_hits: credit

### `backups/claude-before-reinstall-20260603-163449/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/xlsx/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 11679 bytes; modified: 2026-06-03T16:18:43
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/pptx/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 10329 bytes; modified: 2026-06-03T15:57:29
- keyword_hits: cycle; gold

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/pptx/editing.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 6881 bytes; modified: 2026-06-03T15:57:29
- keyword_hits: yield

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/schedule/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 2253 bytes; modified: 2026-06-03T16:10:58
- keyword_hits: omo

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/setup-cowork/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7421 bytes; modified: 2026-06-03T16:10:58
- keyword_hits: omo

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/skill-creator/agents/grader.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 9049 bytes; modified: 2026-06-03T15:57:29
- keyword_hits: credit

### `backups/claude-reset-20260603-161427/Claude/local-agent-mode-sessions/skills-plugin/de02162d-3c69-412e-9024-f5352028d7fc/c4b54126-16ad-4de8-8704-3ec86690a87f/skills/xlsx/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 11679 bytes; modified: 2026-06-03T15:57:30
- description: Macro-related file detected by keywords
- keyword_hits: macro

### `memory/2026-05-05.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw memory notes
- size: 17306 bytes; modified: 2026-05-05T17:10:32
- description: Macro-related file detected by keywords
- keyword_hits: vi-mo; vĩ

### `memory/2026-05-09.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw memory notes
- size: 7937 bytes; modified: 2026-05-09T20:30:32
- keyword_hits: cycle

### `memory/2026-05-14.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw memory notes
- size: 7054 bytes; modified: 2026-05-14T15:39:19
- description: Macro-related file detected by keywords
- keyword_hits: vĩ; yield

### `memory/2026-05-27.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 12349 bytes; modified: 2026-05-27T16:38:51
- keyword_hits: gold

### `memory/2026-05-28.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5488 bytes; modified: 2026-05-28T20:41:05
- keyword_hits: omo

### `memory/2026-05-30.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 8891 bytes; modified: 2026-05-30T21:05:50
- keyword_hits: omo

### `memory/2026-06-01.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 34358 bytes; modified: 2026-06-01T20:17:39
- keyword_hits: omo

### `reports/MIT_18_642_Chuong_05_Derivatives_BlackScholes_CW_VI.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3760 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity; lãi suất

### `reports/MIT_18_642_finance_lessons_vi.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 46091 bytes; modified: 2026-06-04T14:54:32
- keyword_hits: bond; lãi suất

### `reports/MIT_18_642_transcript_source_audit.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3502 bytes; modified: 2026-06-04T16:02:22
- keyword_hits: bond

### `skills/fixing-motion-performance/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 5716 bytes; modified: 2026-06-04T14:07:06
- keyword_hits: omo

### `skills/frontend-craft-skill/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 10373 bytes; modified: 2026-06-04T14:07:14
- keyword_hits: cycle

### `skills/frontend-craft-skill/references/accessibility-checklist.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 9854 bytes; modified: 2026-06-04T14:07:14
- keyword_hits: cycle

### `skills/frontend-craft-skill/references/animation-motion.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 6699 bytes; modified: 2026-06-04T14:07:14
- keyword_hits: cycle

### `skills/frontend-craft-skill/references/design-philosophy.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 11173 bytes; modified: 2026-06-04T14:07:14
- keyword_hits: gold

### `skills/frontend-design-engineer/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 12309 bytes; modified: 2026-06-04T14:07:09
- keyword_hits: omo

### `skills/lh-investment-firebase-final-deploy/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 6381 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: gold

### `skills/mit-finance-quant-strategy/references/chapter-05-derivatives-blackscholes-cw-vi.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 3760 bytes; modified: 2026-06-04T15:13:50
- keyword_hits: liquidity; lãi suất

### `skills/mit-finance-quant-strategy/references/playlist-lessons-auto-vi.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 46091 bytes; modified: 2026-06-04T14:54:32
- keyword_hits: bond; lãi suất

### `skills/mit18642-trainer/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 20155 bytes; modified: 2026-06-05T08:58:22
- keyword_hits: bond; credit; fx; liquidity; lãi suất; omo; vix; yield

### `skills/neej-frontend-craft/references/component-patterns.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 21508 bytes; modified: 2026-06-04T14:07:11
- keyword_hits: cycle

### `skills/neej-frontend-craft/references/inspiration-sites.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 5121 bytes; modified: 2026-06-04T14:07:11
- keyword_hits: gold

### `skills/ui-arsenal/REFERENCE-VAULT.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 7451 bytes; modified: 2026-06-04T14:07:12
- keyword_hits: gold

### `skills/video-to-pdf-trainer/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 10731 bytes; modified: 2026-06-05T01:49:04
- keyword_hits: gold

### `skills/vn-equity-research/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 5403 bytes; modified: 2026-06-05T02:03:46
- description: Macro-related file detected by keywords
- keyword_hits: lãi suất; vĩ

### `skills/vn-equity-research/references/phan-tich-co-ban.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 4374 bytes; modified: 2026-06-05T02:04:28
- description: Macro-related file detected by keywords
- keyword_hits: cpi; cycle; gdp; lãi suất; vĩ; yield

### `skills/vn-equity-research/references/phan-tich-ky-thuat.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 3485 bytes; modified: 2026-06-05T02:05:02
- keyword_hits: gold

### `skills/vn-equity-research/references/trinh-bay-bao-cao.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: OpenClaw skill
- size: 3000 bytes; modified: 2026-06-05T02:06:10
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `stock-news-backend/MAIN_SITE_LOCK.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 964 bytes; modified: 2026-06-04T08:31:01
- keyword_hits: omo

### `stock-news-backend/firebase_public/reports/news_report_latest.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 10991 bytes; modified: 2026-06-05T13:54:31
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `stock-news-backend/pattern_engine/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7180 bytes; modified: 2026-06-04T08:31:02
- keyword_hits: gold

### `stock-news-backend/pattern_engine_v2/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 7023 bytes; modified: 2026-06-02T14:30:25
- keyword_hits: gold

### `tmp_claude_pattern_pack/stock-news-backend/pattern_engine/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 5325 bytes; modified: 2026-06-02T07:18:46
- keyword_hits: gold

### `tmp_claude_pattern_pack_v2/stock-news-backend/pattern_engine/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7023 bytes; modified: 2026-06-02T14:30:25
- keyword_hits: gold

### `tmp_claude_v1_src/stock-news-backend/pattern_engine/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 7023 bytes; modified: 2026-06-02T07:30:26
- keyword_hits: gold

### `tmp_data_KQKD_GetListReportData.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 250152 bytes; modified: 2026-05-31T19:06:19
- keyword_hits: vix

### `tmp_data_KQKD_GetListReportData_v2.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 250152 bytes; modified: 2026-05-31T19:12:54
- keyword_hits: fx

### `tmp_mit18642_trainer_zip/video-to-pdf/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 10731 bytes; modified: 2026-06-05T01:49:04
- keyword_hits: gold

### `tmp_mwg_docx_text.txt`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 62375 bytes; modified: 2026-05-31T18:35:35
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `tmp_vn_equity_skill_zip/vn-equity-research/SKILL.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 5403 bytes; modified: 2026-06-05T02:03:46
- description: Macro-related file detected by keywords
- keyword_hits: lãi suất; vĩ

### `tmp_vn_equity_skill_zip/vn-equity-research/references/phan-tich-co-ban.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 4374 bytes; modified: 2026-06-05T02:04:28
- description: Macro-related file detected by keywords
- keyword_hits: cpi; cycle; gdp; lãi suất; vĩ; yield

### `tmp_vn_equity_skill_zip/vn-equity-research/references/phan-tich-ky-thuat.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3485 bytes; modified: 2026-06-05T02:05:02
- keyword_hits: gold

### `tmp_vn_equity_skill_zip/vn-equity-research/references/trinh-bay-bao-cao.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 3000 bytes; modified: 2026-06-05T02:06:10
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `vendor_audit/TradingAgents/README.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 16820 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: liquidity; macro

### `vnstock/LICENSE.md`
- role: notes/report/skill
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 8442 bytes; modified: 2026-04-23T14:16:09
- keyword_hits: omo

### `exports/github_chart_patterns_libraries_research_20260602.md`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 20135 bytes; modified: 2026-06-02T11:38:11
- keyword_hits: yfinance

### `vendor_audit/TRADINGAGENTS_LH_AUDIT.md`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 3742 bytes; modified: 2026-06-04T08:44:37
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/CHANGELOG.md`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: Claude/Claude handoff or backup
- size: 17552 bytes; modified: 2026-06-04T08:43:43
- description: Macro-related file detected by keywords
- keyword_hits: fx; macro; yfinance

### `vendor_audit/TradingAgents/lh_test_outputs/memory.md`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 547 bytes; modified: 2026-06-04T09:08:08
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/lh_test_outputs/mwg_tradingagents_mock_report.md`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 917 bytes; modified: 2026-06-04T09:08:08
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tradingagents.egg-info/SOURCES.txt`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 3922 bytes; modified: 2026-06-04T08:47:43
- keyword_hits: yfinance

### `vendor_audit/TradingAgents/tradingagents.egg-info/requires.txt`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 421 bytes; modified: 2026-06-04T08:47:43
- keyword_hits: yfinance

### `vendor_audit/tradingagents_file_inventory.txt`
- role: notes/report/skill
- source_hint: yfinance/Yahoo
- owner_hint: workspace
- size: 2798 bytes; modified: 2026-06-04T08:44:14
- keyword_hits: yfinance

### `reports/MIT_18_642_Bai_Giang_Chuyen_Nghiep_Cho_Nha_Dau_Tu.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: workspace
- size: 34709 bytes; modified: 2026-06-04T16:46:11
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_Comprehensive_Transcript_Notes_VI.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: workspace
- size: 183601 bytes; modified: 2026-06-04T16:41:41
- keyword_hits: bond; lãi suất; yield

### `reports/MIT_18_642_Giao_Trinh_Day_Du_Chinh_Chu_VI.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: workspace
- size: 128177 bytes; modified: 2026-06-04T22:44:36
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_Khoa_Hoc_Nha_Dau_Tu_22_Video_FULL.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: workspace
- size: 33790 bytes; modified: 2026-06-04T16:32:18
- keyword_hits: bond; lãi suất; yield

### `reports/MIT_18_642_Training_Guide_LH_Investment_DESIGN.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: workspace
- size: 27525 bytes; modified: 2026-06-04T16:26:35
- description: Macro-related file detected by keywords
- keyword_hits: bond; liquidity; macro; yield

### `stock-news-backend/local_internal_redesign_safe/index.html`
- role: preview/html
- source_hint: Internal macro score
- owner_hint: LH Investment backend/OpenClaw
- size: 10767 bytes; modified: 2026-06-05T09:26:30
- keyword_hits: gold

### `stock-news-backend/local_preview/macro.html`
- role: preview/html
- source_hint: Pinetree
- owner_hint: LH Investment backend/OpenClaw
- size: 5356 bytes; modified: 2026-05-19T09:13:37
- description: Macro-related file detected by keywords
- keyword_hits: brent; fx; liquidity; liên nh; lãi suất; macro; pinetree; vix; vĩ

### `hoa_f319_bulk_archive/lpb-payback-time-chuyen-tau-phuc-thu-ve-dich-expansion-pack.1817673/lpb-payback-time-chuyen-tau-phuc-thu-ve-dich-expansion-pack.1817673.html`
- role: preview/html
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 2991674 bytes; modified: 2026-06-02T11:24:38
- keyword_hits: cpi; lãi suất; sbv

### `offline_f319_toa_son_thuong_tra_html_fast/page_0432.html`
- role: preview/html
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 85160 bytes; modified: 2026-06-01T20:01:30
- keyword_hits: nhnn; sbv

### `reports/dynamic_tradingagents_reports/MWG_APIFREE_mobile_style_macro_report.html`
- role: preview/html
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 68661 bytes; modified: 2026-06-04T10:32:31
- description: Macro-related file detected by keywords
- keyword_hits: breadth; brent; cpi; dxy; fred; gold; lãi suất; macro; pmi; sbv; vĩ; worldbank

### `reports/dynamic_tradingagents_reports/MWG_APIFREE_mobile_style_macro_report_fixed.html`
- role: preview/html
- source_hint: SBV/NHNN
- owner_hint: workspace
- size: 72960 bytes; modified: 2026-06-04T10:44:19
- description: Macro-related file detected by keywords
- keyword_hits: breadth; brent; cpi; credit; dxy; fred; gold; interbank; lãi suất; macro; pmi; sbv; vix; vĩ; worldbank; yield

### `backups/claude-before-reinstall-20260603-163449/AnthropicClaude/app-1.10628.0/resources/ion-dist/index.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 3804 bytes; modified: 2026-06-03T15:52:46
- keyword_hits: fx

### `hoa_f319_bulk_archive/techcombank-tcb-co-phieu-an-tet.1518523/techcombank-tcb-co-phieu-an-tet.1518523.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 65215 bytes; modified: 2026-06-02T12:30:18
- keyword_hits: fx

### `offline_f319_toa_son_thuong_tra_html_fast/page_0056.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 96162 bytes; modified: 2026-06-01T19:54:26
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `offline_f319_toa_son_thuong_tra_html_fast/page_0117.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 91247 bytes; modified: 2026-06-01T19:55:33
- keyword_hits: lãi suất

### `offline_f319_toa_son_thuong_tra_html_fast/page_0160.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 90706 bytes; modified: 2026-06-01T19:56:19
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `offline_f319_toa_son_thuong_tra_html_fast/page_0229.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 85932 bytes; modified: 2026-06-01T19:57:43
- keyword_hits: lãi suất

### `offline_f319_toa_son_thuong_tra_html_fast/page_0328.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 89309 bytes; modified: 2026-06-01T20:00:29
- keyword_hits: cpi

### `offline_f319_toa_son_thuong_tra_html_fast/page_0363.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 90380 bytes; modified: 2026-06-01T20:00:35
- keyword_hits: omo

### `offline_f319_toa_son_thuong_tra_html_fast/page_0446.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 89744 bytes; modified: 2026-06-01T20:01:39
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `offline_f319_toa_son_thuong_tra_html_fast/page_0448.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 90742 bytes; modified: 2026-06-01T20:01:40
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `reports/MIT18642_Trainer_50_Slide_Deck.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 37674 bytes; modified: 2026-06-05T09:02:00
- keyword_hits: bond; fx; yield

### `reports/MIT_18_642_22_Video_44_Trang_Giang_Day.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 56027 bytes; modified: 2026-06-04T16:36:49
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_50_Trang_ChatGPT_Original_Quality.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: Claude/Claude handoff or backup
- size: 57782 bytes; modified: 2026-06-04T22:39:48
- keyword_hits: bond; liquidity; lãi suất; yield

### `reports/MIT_18_642_Training_Guide_50_Trang_CHATGPT_FIX.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 31907 bytes; modified: 2026-06-04T22:31:23
- keyword_hits: bond; liquidity; lãi suất; yield

### `stock-news-backend/firebase_public/reports/news_report_latest.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: LH Investment backend/OpenClaw
- size: 12011 bytes; modified: 2026-06-05T13:54:31
- description: Macro-related file detected by keywords
- keyword_hits: vĩ

### `tmp_https_www_mwg_vn_cong_ty_gioi_thieu_chung.html`
- role: preview/html
- source_hint: unknown/mixed
- owner_hint: workspace
- size: 33545 bytes; modified: 2026-05-31T21:59:59
- keyword_hits: omo
