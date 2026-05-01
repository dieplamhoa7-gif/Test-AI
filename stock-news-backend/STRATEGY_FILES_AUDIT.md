# Strategy Files Audit

Updated: 2026-05-01

## Important correction

`data/strategy_results_cache.json` currently comes from `data/three_strategies_vn30x_cache_signals.json`, which was produced by `scan_three_strategies_vn30x_from_cache.py` using `data/v3_full_indicator_cache_v2.json`.

That scan is a lightweight **cache approximation** for the web, not a direct run of the three original selected strategy scanner files. Therefore, if the user asks for exact/current official strategy output, do not treat `scan_three_strategies_vn30x_from_cache.py` as the canonical strategy implementation.

## Chosen canonical strategy files

The web strategy matrix must use only these three strategy IDs:

1. `b4_trend_pullback` — **Trend Pullback Pro**
2. `clean_split_a_bottom` — **Support Rebound Hunter**
3. `shakeout_breakdown_rebound` — **Shakeout Rebound**

## Canonical source files

### 1. Trend Pullback Pro

Canonical backtest/spec/current scan:

- `B4_TREND_PULLBACK_SPEC.md`
- `backtest_b4_trend_pullback_locked.py`
- `scan_v3_b4_bullish_divergence_current_signals.py`

Outputs:

- `data/b4_trend_pullback_locked_backtest.json`
- `data/v3_b4_bullish_divergence_current_signals.json`

### 2. Support Rebound Hunter

Canonical backtest/current scan:

- `backtest_v3_clean_split_rs_action.py`
- `save_v3_clean_split_baseline.py`
- `scan_v3_clean_split_a2_b2_current_signals.py`

Outputs:

- `data/v3_clean_split_rs_action_backtest.json`
- `data/v3_clean_split_baseline_locked.json`
- `data/v3_clean_split_a2_b2_current_signals.json`

### 3. Shakeout Rebound

Canonical backtest/current scan:

- `backtest_breakdown_rebound_midcap50_target6.py`
- `scan_shakeout_current_cache.py`

Outputs:

- `data/breakdown_rebound_midcap50_target6.json`
- `data/midcap_shakeout_strategy_analysis.json`
- `data/shakeout_rebound_current_signals.json` if generated.

## Non-canonical helper files

These files are helper/cache scanners only; they should not be described as the canonical selected strategy files:

- `scan_three_strategies_vn30x_from_cache.py`
- `scan_three_strategies_vn100_from_cache.py`
- `scan_three_strategies_vn100_current.py`
- `tmp_update_strategy_results_cache_vn30x.py`

They may be used only to build a fast web cache from precomputed indicators, with a clear note that this is an approximation/cache scan.

## Guardrails

- `2_V3_Plus6_Focused` is not a chosen web strategy and must not feed Shakeout Rebound.
- `strategy_results_cache.json` should contain only chosen strategy IDs above.
- Web must read cache only; no heavy live PTKT during render.
- Prefer archive over deletion for old research scripts.
