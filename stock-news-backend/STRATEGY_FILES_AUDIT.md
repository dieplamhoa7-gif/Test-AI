# Strategy Files Audit

Updated: 2026-05-01

## Chosen strategy set for web Strategy Filter

The web strategy matrix must use only these three strategy IDs:

1. `b4_trend_pullback` — **Trend Pullback Pro**
2. `clean_split_a_bottom` — **Support Rebound Hunter**
3. `shakeout_breakdown_rebound` — **Shakeout Rebound**

Current web signal cache:

- `data/strategy_results_cache.json`
- current source: `data/three_strategies_vn30x_cache_signals.json`
- universe: VN30 excluding VIC/VHM, using available indicator cache.

## Correct source files

### 1. Trend Pullback Pro

Keep:

- `B4_TREND_PULLBACK_SPEC.md`
- `backtest_b4_trend_pullback_locked.py`
- `scan_v3_b4_bullish_divergence_current_signals.py` — older dedicated B4 current scan/reference.
- `scan_three_strategies_vn30x_from_cache.py` — current web scan for VN30 ex-VIC/VHM.
- `scan_three_strategies_vn100_from_cache.py` — broader cache scan reference.

Output/reference:

- `data/b4_trend_pullback_locked_backtest.json`
- `data/v3_b4_bullish_divergence_current_signals.json`
- `data/three_strategies_vn30x_cache_signals.json`

### 2. Support Rebound Hunter

Chosen implementation is the Clean Split A / near-support rebound family.

Keep:

- `backtest_v3_clean_split_rs_action.py`
- `save_v3_clean_split_baseline.py`
- `scan_v3_clean_split_a2_b2_current_signals.py` — older current scan/reference.
- `scan_three_strategies_vn30x_from_cache.py` — current web scan for VN30 ex-VIC/VHM.

Output/reference:

- `data/v3_clean_split_rs_action_backtest.json`
- `data/v3_clean_split_baseline_locked.json`
- `data/v3_clean_split_a2_b2_current_signals.json`
- `data/three_strategies_vn30x_cache_signals.json`

### 3. Shakeout Rebound

Correct implementation is NOT V3 Plus6 Focused. Do not map V3 Plus6 into Shakeout.

Keep:

- `backtest_breakdown_rebound_midcap50_target6.py`
- `scan_shakeout_current_cache.py`
- `scan_three_strategies_vn30x_from_cache.py` — current web scan for VN30 ex-VIC/VHM.

Output/reference:

- `data/breakdown_rebound_midcap50_target6.json`
- `data/midcap_shakeout_strategy_analysis.json`
- `data/shakeout_rebound_current_signals.json` if available.
- `data/three_strategies_vn30x_cache_signals.json`

## Guardrails

- `2_V3_Plus6_Focused` is not a chosen web strategy and must not feed Shakeout Rebound.
- `strategy_results_cache.json` should contain only chosen strategy IDs above.
- Web must read cache only; no heavy live PTKT during render.
- Prefer archive over deletion for old research scripts.
