# LHINVT Final Strategy Files

Only the final LH strategy files below should stay in the deploy repository. Do not re-add old research/backtest variants unless Hòa Đại ka explicitly asks.

## Live final strategy contract

- `LH1_FINAL`
- `LH2_FINAL`
- `LH3_FINAL`
- `LH4_FINAL`

## Final source / evidence files to keep

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

## Cleanup rule

Old/non-final files matching broad research names such as `backtest_a4_*`, `backtest_b4_*` variants, `v3_target*`, `v3_two_strategies*`, non-H60 `wave_entry*`, old archive folders, `tmp_*`, and research PPT/audit files were removed from git to prevent future rollback/confusion.
