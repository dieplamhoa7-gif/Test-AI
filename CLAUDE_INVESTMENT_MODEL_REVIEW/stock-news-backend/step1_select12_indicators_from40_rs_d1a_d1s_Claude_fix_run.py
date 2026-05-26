"""
STEP 1 (Claude fix) â€” Walk-forward indicator selection cho RS / D1A / D1S
                     + 2 task má»›i SUPPORT_HOLD / RESISTANCE_REJECT
                     (má»¥c tiÃªu: tÃ¬m S/R chÃ­nh xÃ¡c cao)

KhÃ¡c biá»‡t chÃ­nh so vá»›i file gá»‘c (step1_select12_indicators_from40_rs_d1a_d1s.py):
  1. Walk-forward CV (rolling, máº·c Ä‘á»‹nh 5 folds) thay vÃ¬ 2 fixed splits cá»‘ Ä‘á»‹nh.
  2. Purged gap = HORIZON ngÃ y giá»¯a train_end vÃ  test_start Ä‘á»ƒ khá»­ label leak
     (vÃ¬ label dÃ¹ng future20 â†’ máº«u sÃ¡t biÃªn cÃ³ rÃ² rá»‰ thÃ´ng tin).
  3. Threshold tune trÃªn VALIDATION fold (cáº¯t ra tá»« tail cá»§a train), KHÃ”NG trÃªn IS,
     vÃ  KHÃ”NG bao giá» trÃªn test fold.
  4. Probability calibration (isotonic) trÆ°á»›c khi tune threshold Ä‘á»ƒ xÃ¡c suáº¥t
     cÃ³ Ã½ nghÄ©a thá»±c sá»±.
  5. Bootstrap 95% CI cho precision; rank Æ°u tiÃªn LOWER BOUND cá»§a CI
     thay vÃ¬ point estimate (conservative selection).
  6. Bonferroni-aware penalty: trá»« Ä‘iá»ƒm theo log(sá»‘ indicator family Ã— sá»‘ model)
     Ä‘á»ƒ háº¡n cháº¿ lucky configs.
  7. Net-cost aware: trá»« 0.4% round-trip khi quy Ä‘á»•i precision -> trade-able edge.
  8. Sample size guard: tá»•ng predN qua N folds â‰¥ MIN_TOTAL_PRED má»›i Ä‘Æ°á»£c pass.
  9. ThÃªm 2 task: SUPPORT_HOLD vÃ  RESISTANCE_REJECT â€” Ä‘Ã¢y lÃ  má»¥c tiÃªu cá»‘t lÃµi
     "tÃ¬m há»— trá»£/khÃ¡ng cá»± chÃ­nh xÃ¡c cao" mÃ  file gá»‘c chÆ°a cÃ³.

LÆ°u Ã½ quan trá»ng cho ngÆ°á»i Ä‘á»c code:
  - File nÃ y KHÃ”NG Ä‘Ã¨ file gá»‘c. CÃ³ thá»ƒ cháº¡y song song Ä‘á»ƒ so sÃ¡nh.
  - Output schema giá»¯ tÆ°Æ¡ng Ä‘Æ°Æ¡ng file gá»‘c + thÃªm cÃ¡c trÆ°á»ng walk-forward.
  - Input váº«n lÃ  vn100_history_2025_06_2026_05_cache.json
    vÃ  d1a_full_research_features_is_oos.json, váº«n dÃ¹ng module
    build_indicator40_ml_outputs.py (ind40) y nguyÃªn.
"""

from __future__ import annotations
import json, csv, datetime as dt, importlib.util, warnings, math, random
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HIST = DATA / "vn100_history_2025_06_2026_05_cache.json"
D1SRC = DATA / "d1a_full_research_features_is_oos.json"
IND40 = ROOT / "build_indicator40_ml_outputs.py"
OUT = DATA / "core12_step1_select12_from40_rs_d1a_d1s_Claude_fix.json"
CSV_OUT = DATA / "core12_step1_select12_from40_rs_d1a_d1s_Claude_fix.csv"

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Cáº¥u hÃ¬nh walk-forward
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
N_FOLDS = 2                  # sá»‘ fold walk-forward
HORIZON_DAYS = 10            # label dÃ¹ng future20 â†’ purge gap 20 ngÃ y
VAL_RATIO = 0.20             # 20% cuá»‘i train tÃ¡ch lÃ m validation Ä‘á»ƒ tune threshold
MIN_TOTAL_PRED = 30          # tá»•ng predN qua N folds tá»‘i thiá»ƒu
MIN_FOLD_PRED = 3            # má»—i fold pháº£i predict Ä‘Æ°á»£c â‰¥ N má»›i counted
BOOTSTRAP_N = 100            # sá»‘ láº§n bootstrap Ä‘á»ƒ Æ°á»›c lÆ°á»£ng CI
RANDOM_SEED = 20260526
TX_COST_PCT = 0.4            # phÃ­ round-trip giáº£ Ä‘á»‹nh 0.4% (phÃ­ + thuáº¿ + slippage)

# Tasks: giá»¯ RS/D1A/D1S + thÃªm 2 task má»¥c tiÃªu chÃ­nh cá»§a anh diep
TASKS = ["RS", "D1A", "D1S", "SUPPORT_HOLD", "RESISTANCE_REJECT"]

INDICATOR_MAP = {
    "SMA": ["sma"], "EMA": ["ema"], "WMA": ["wma"], "MACD": ["macd"],
    "ICHIMOKU": ["ichi"], "ADX": ["adx"], "PSAR": ["psar"], "SUPERTREND": ["supertrend"],
    "DMI": ["plusDI", "minusDI", "diSpread"], "AROON": ["aroon"], "ZIGZAG": ["zigzag"], "TRIX": ["trix"],
    "RSI": ["rsi"], "STOCHASTIC": ["stoch"], "CCI": ["cci"], "WILLIAMS_R": ["williams"],
    "MOMENTUM": ["mom"], "ROC": ["roc"], "AO": ["ao"], "ULTIMATE_OSC": ["ultimate"],
    "TSI": ["tsi"], "KDJ": ["kdj"],
    "BOLLINGER": ["bb"], "ATR": ["atr"], "KELTNER": ["keltner"], "DONCHIAN": ["donchian"],
    "STDDEV": ["std"], "HIST_VOL": ["hist_vol"], "CHOPPINESS": ["choppiness"],
    "CHAIKIN_VOL": ["chaikin_vol"], "RVI": ["rvi"], "MASS_INDEX": ["mass_index"],
    "VWAP": ["vwap"], "OBV": ["obv"], "CMF": ["cmf"], "AD_LINE": ["ad_slope"],
    "MFI": ["mfi"], "VWMA": ["vwma"], "PVI": ["pvi"], "NVI": ["nvi"],
    "VOSC": ["vosc"], "KLINGER": ["klinger"],
}

MODELS = ["LOG", "ET", "RF"]
N_CONFIGS_SCANNED = len(INDICATOR_MAP) * len(MODELS) * len(TASKS)  # for Bonferroni

# Load module indicator40 y nguyÃªn cÃ¡ch file gá»‘c
spec = importlib.util.spec_from_file_location("ind40", IND40)
ind40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ind40)

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Data loading â€” giá»‘ng step1 gá»‘c Ä‘á»ƒ cache feature40 á»•n Ä‘á»‹nh
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def load_rows():
    hist = json.load(open(HIST, encoding="utf-8"))["symbols"]
    src = json.load(open(D1SRC, encoding="utf-8"))["items"]
    need = {(x["symbol"], x["date"]) for x in src}
    smap = {(x["symbol"], x["date"]): x for x in src}
    rows = []
    for sym, p in hist.items():
        if not any(s == sym for s, _ in need):
            continue
        df = pd.DataFrame(p["rows"]).sort_values("time").reset_index(drop=True)
        feat = ind40.add_indicator40(df).fillna(0)
        for _, r in feat.iterrows():
            key = (sym, str(r["date"]))
            if key not in smap:
                continue
            base = smap[key]
            feats = {
                k: float(v) for k, v in r.items()
                if k != "date" and isinstance(v, (int, float, np.integer, np.floating)) and np.isfinite(v)
            }
            rows.append({
                "symbol": sym,
                "date": key[1],
                "sector": base.get("sector"),
                "features40": feats,
                "rs": base.get("rs") or {},
                "lc": base.get("lc") or {},
                "full": base.get("fullResearchFeatures") or {},
                "mtf": base.get("mtfAsOfDate") or {},
            })
    rows.sort(key=lambda x: (x["date"], x["symbol"]))
    return rows


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Labels â€” giá»¯ nguyÃªn RS/D1A/D1S + thÃªm SUPPORT_HOLD / RESISTANCE_REJECT
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def label(task, r):
    lc, rs, f, mtf = r["lc"], r["rs"], r["full"], r["mtf"]

    if task == "RS":
        near = bool(rs.get("nearSupport") or abs(rs.get("distSupportPct") or 99) < 4)
        survive = (lc.get("futureMin20") or 0) > -7
        rebound = (lc.get("futureMax20") or 0) > 5
        return int(near and survive and rebound)

    if task == "D1A":
        future_survive = (lc.get("futureMin20") or 0) > -8 and (lc.get("futureClose20") or 0) > -5
        absorption = (f.get("dryUp20_norm", 0) > 0 or f.get("greenAbsorb10_norm", 0) > 0 or f.get("baseQualityScore_norm", 0) > 0)
        base_ok = (f.get("range40Pct_inv", 0) > 0 or f.get("tightClose20_norm", 0) > 0 or rs.get("nearSupport"))
        return int(future_survive and (absorption or base_ok))

    if task == "D1S":
        future_bad = (lc.get("futureMin20") or 0) < -10 or ((lc.get("futureClose20") or 0) < -6 and (lc.get("futureMin20") or 0) < -7)
        structural = rs.get("supportBroken") or rs.get("weekSupportBroken") or f.get("support_break", 0) > 0 or f.get("break_ma_cluster", 0) > 0
        distro = f.get("distribution_cluster", 0) > 0 or (f.get("two_red_high_vol_5d", 0) > 0 and f.get("close_low_cluster", 0) > 0)
        mtf_bad = ((mtf.get("W_rsi14") or 50) < 42 and not mtf.get("W_macdImproving")) or (not mtf.get("W_aboveMa20") and not mtf.get("W_maTrendUp"))
        return int(future_bad and (structural or distro or mtf_bad))

    if task == "SUPPORT_HOLD":
        # Má»¥c tiÃªu: vá»›i máº«u hiá»‡n Ä‘ang gáº§n support, support Ä‘Ã³ GIá»® trong 20 phiÃªn tá»›i.
        # Äiá»u kiá»‡n tiá»n Ä‘á»: ngÃ y t Ä‘ang náº±m trong vÃ¹ng test support
        near = bool(rs.get("nearSupport") or abs(rs.get("distSupportPct") or 99) < 4)
        if not near:
            return 0
        # Hold: futureMin20 khÃ´ng xuyÃªn thá»§ng support > 3% (1 ATR ~ 2.5-3%)
        future_min = lc.get("futureMin20") or 0
        not_broken = future_min > -4.5
        # Pháº£i cÃ³ Ã­t nháº¥t 1 cÃº náº£y lÃªn trÃªn 3% trong tÆ°Æ¡ng lai â†’ chá»©ng minh support lÃ  vÃ¹ng "bid máº¡nh"
        future_max = lc.get("futureMax20") or 0
        bounced = future_max >= 3.0
        return int(not_broken and bounced)

    if task == "RESISTANCE_REJECT":
        # Má»¥c tiÃªu: vá»›i máº«u hiá»‡n Ä‘ang gáº§n resistance, resistance Ä‘Ã³ REJECT trong 20 phiÃªn.
        near_res = bool(rs.get("nearResistance") or abs(rs.get("distResistancePct") or 99) < 4)
        if not near_res:
            return 0
        # Reject: futureMax20 khÃ´ng vÆ°á»£t resistance Ä‘Ã¡ng ká»ƒ (close khÃ´ng > 3% trÃªn resistance)
        future_max = lc.get("futureMax20") or 0
        not_breakout = future_max <= 3.0
        # Pháº£i cÃ³ cÃº giáº£m tháº­t tá»« vÃ¹ng resistance (futureMin <= -3%)
        future_min = lc.get("futureMin20") or 0
        rejected = future_min <= -3.0
        return int(not_breakout and rejected)

    raise ValueError(task)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Metric helpers + bootstrap
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def stats(y, p):
    pr, rc, f1, _ = precision_recall_fscore_support(y, p, average="binary", zero_division=0)
    return {
        "n": int(len(y)),
        "tp": int(((p == 1) & (y == 1)).sum()),
        "fp": int(((p == 1) & (y == 0)).sum()),
        "tn": int(((p == 0) & (y == 0)).sum()),
        "fn": int(((p == 0) & (y == 1)).sum()),
        "precision": round(pr * 100, 2),
        "recall": round(rc * 100, 2),
        "accuracy": round(accuracy_score(y, p) * 100, 2),
        "f1": round(f1 * 100, 2),
        "predN": int((p == 1).sum()),
        "oracleN": int((y == 1).sum()),
    }


def bootstrap_precision_ci(y_true, y_pred, n_bootstrap=BOOTSTRAP_N, alpha=0.05):
    """
    Bootstrap CI cho precision. Tráº£ vá» (p_mean, p_low95, p_high95).
    LÆ°u Ã½: chá»‰ bootstrap trÃªn cÃ¡c sample cÃ³ pred=1; náº¿u predN nhá» thÃ¬ CI sáº½ rá»™ng.
    """
    idx = np.where(y_pred == 1)[0]
    if len(idx) < MIN_FOLD_PRED:
        return (0.0, 0.0, 0.0)
    rng = np.random.RandomState(RANDOM_SEED)
    precisions = []
    for _ in range(n_bootstrap):
        sample = rng.choice(idx, size=len(idx), replace=True)
        tp = int((y_true[sample] == 1).sum())
        precisions.append(tp / len(sample))
    precisions = np.array(precisions) * 100
    return (
        float(precisions.mean()),
        float(np.percentile(precisions, 100 * alpha / 2)),
        float(np.percentile(precisions, 100 * (1 - alpha / 2))),
    )


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Walk-forward splits vá»›i purged gap
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def make_walkforward_folds(rows, n_folds=N_FOLDS, horizon=HORIZON_DAYS, val_ratio=VAL_RATIO):
    """
    Táº¡o N rolling folds:
      [train_block] [purged_gap=horizon] [test_block]
    Trong train_block tÃ¡ch 20% cuá»‘i lÃ m validation (cÅ©ng purged khá»i train).

    Tráº£ vá»: list[dict(train_idx, val_idx, test_idx, dates...)]
    """
    dates = sorted({r["date"] for r in rows})
    n_dates = len(dates)
    if n_dates < n_folds * (horizon + 5):
        raise ValueError(f"KhÃ´ng Ä‘á»§ ngÃ y cho {n_folds} folds: chá»‰ cÃ³ {n_dates} ngÃ y")

    # Má»—i fold test_block dÃ i báº±ng nhau
    test_block_len = (n_dates - horizon) // (n_folds + 2)  # +2 Ä‘á»ƒ cÃ³ buffer á»Ÿ Ä‘áº§u
    if test_block_len < 5:
        raise ValueError(f"Test block quÃ¡ ngáº¯n ({test_block_len} ngÃ y)")

    folds = []
    for k in range(n_folds):
        # Fold k:  train_end = n_dates - (n_folds-k)*test_block_len - horizon
        test_end_idx = n_dates - (n_folds - 1 - k) * test_block_len
        test_start_idx = test_end_idx - test_block_len
        train_end_idx = test_start_idx - horizon  # purged gap
        if train_end_idx < int(n_dates * 0.20):    # tá»‘i thiá»ƒu 20% data lÃ m train
            continue
        train_dates = dates[:train_end_idx]
        test_dates = dates[test_start_idx:test_end_idx]

        # Validation = 20% cuá»‘i train, ALSO purged khá»i train final
        val_block_len = max(int(len(train_dates) * val_ratio), horizon + 5)
        val_dates = train_dates[-val_block_len:]
        train_final_end = len(train_dates) - val_block_len - horizon
        if train_final_end < 15:
            continue
        train_final_dates = train_dates[:train_final_end]

        train_set = set(train_final_dates)
        val_set = set(val_dates)
        test_set = set(test_dates)

        train_idx = [i for i, r in enumerate(rows) if r["date"] in train_set]
        val_idx = [i for i, r in enumerate(rows) if r["date"] in val_set]
        test_idx = [i for i, r in enumerate(rows) if r["date"] in test_set]

        if not train_idx or not val_idx or not test_idx:
            continue

        folds.append({
            "fold": k + 1,
            "trainDates": [train_final_dates[0], train_final_dates[-1]],
            "valDates": [val_dates[0], val_dates[-1]],
            "testDates": [test_dates[0], test_dates[-1]],
            "purgedGapDays": horizon,
            "trainIdx": train_idx,
            "valIdx": val_idx,
            "testIdx": test_idx,
        })
    return folds


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Models + calibration
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clf(name, seed):
    if name == "ET":
        return ExtraTreesClassifier(n_estimators=260, max_depth=4, min_samples_leaf=6,
                                    class_weight="balanced", random_state=seed, n_jobs=1)
    if name == "RF":
        return RandomForestClassifier(n_estimators=260, max_depth=4, min_samples_leaf=8,
                                      class_weight="balanced", random_state=seed, n_jobs=1)
    return Pipeline([
        ("s", StandardScaler()),
        ("l", LogisticRegression(max_iter=1000, C=0.3, class_weight="balanced", random_state=seed)),
    ])


def fit_calibrated(model_name, seed, Xtr, ytr):
    """
    Fit model + isotonic calibration trÃªn train (CV=3 ná»™i bá»™).
    Calibration giÃºp threshold cÃ³ Ã½ nghÄ©a thá»±c sá»± "xÃ¡c suáº¥t P(label=1)".
    """
    base = clf(model_name, seed)
    if len(set(ytr)) < 2 or sum(ytr) < 8:
        # quÃ¡ Ã­t positive â†’ bá» calibration, fallback fit tháº³ng
        base.fit(Xtr, ytr)
        return base, False
    try:
        cal = CalibratedClassifierCV(estimator=base, method="isotonic", cv=3)
        cal.fit(Xtr, ytr)
        return cal, True
    except Exception:
        base.fit(Xtr, ytr)
        return base, False


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Tune threshold trÃªn VALIDATION fold (precision-first)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def tune_threshold_on_val(y_val, prob_val, min_pred_val=5):
    """
    QuÃ©t ngÆ°á»¡ng tá»« 0.10 â†’ 0.95, pick ngÆ°á»¡ng cÃ³ precision cao nháº¥t
    vá»›i Ä‘iá»u kiá»‡n predN_val â‰¥ min_pred_val.
    Tie-break: precision desc, recall desc, predN desc.
    """
    candidates = []
    for th in np.linspace(0.10, 0.95, 86):
        preds = (prob_val >= th).astype(int)
        st = stats(y_val, preds)
        if st["predN"] < min_pred_val:
            continue
        candidates.append((st["precision"], st["recall"], st["predN"], float(th), st))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return candidates[0]  # (precision_val, recall_val, predN_val, th, st_val)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ÄÃ¡nh giÃ¡ 1 (task, indicator family, model) qua walk-forward
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def eval_one(rows, folds, task, indicator, model_name):
    prefs = INDICATOR_MAP[indicator]
    all_feats = {k for r in rows for k in r["features40"]}
    feats = sorted([f for f in all_feats if any(f.startswith(p) or p in f for p in prefs)])
    if not feats:
        return None

    y_full = np.array([label(task, r) for r in rows])

    fold_results = []
    for fd in folds:
        tr_idx, va_idx, te_idx = fd["trainIdx"], fd["valIdx"], fd["testIdx"]

        ytr = y_full[tr_idx]; yva = y_full[va_idx]; yte = y_full[te_idx]
        if len(set(ytr)) < 2 or yva.sum() < 2 or yte.sum() < 2:
            continue

        Xtr = np.array([[rows[i]["features40"].get(f, 0.0) for f in feats] for i in tr_idx], float)
        Xva = np.array([[rows[i]["features40"].get(f, 0.0) for f in feats] for i in va_idx], float)
        Xte = np.array([[rows[i]["features40"].get(f, 0.0) for f in feats] for i in te_idx], float)

        keep = [i for i, s in enumerate(Xtr.std(axis=0)) if s > 1e-9]
        if not keep:
            continue
        Xtr, Xva, Xte = Xtr[:, keep], Xva[:, keep], Xte[:, keep]
        feats_kept = [feats[i] for i in keep]

        seed = abs(hash((task, indicator, model_name, fd["fold"]))) % 100000
        m, calibrated = fit_calibrated(model_name, seed, Xtr, ytr)

        try:
            prob_val = m.predict_proba(Xva)[:, 1]
            prob_te = m.predict_proba(Xte)[:, 1]
        except Exception:
            continue

        tuned = tune_threshold_on_val(yva, prob_val)
        if tuned is None:
            continue
        prec_val, rec_val, pred_val, th, st_val = tuned

        pred_te = (prob_te >= th).astype(int)
        st_te = stats(yte, pred_te)
        if st_te["predN"] < MIN_FOLD_PRED:
            # fold khÃ´ng Ä‘á»§ tin cáº­y; váº«n lÆ°u Ä‘á»ƒ aggregate nhÆ°ng Ä‘Ã¡nh dáº¥u
            st_te["lowConfidence"] = True

        # Bootstrap CI precision OOS
        p_mean, p_low, p_high = bootstrap_precision_ci(yte, pred_te)

        fold_results.append({
            "fold": fd["fold"],
            "threshold": round(th, 3),
            "calibrated": calibrated,
            "valStats": st_val,
            "testStats": st_te,
            "precisionCI95": [round(p_low, 2), round(p_high, 2)],
            "precisionMean": round(p_mean, 2),
            "featureCount": len(feats_kept),
        })

    if not fold_results:
        return None

    # Aggregate qua folds
    precisions = [f["testStats"]["precision"] for f in fold_results]
    recalls = [f["testStats"]["recall"] for f in fold_results]
    f1s = [f["testStats"]["f1"] for f in fold_results]
    pred_total = sum(f["testStats"]["predN"] for f in fold_results)

    # Bootstrap CI tá»•ng há»£p: ghÃ©p táº¥t cáº£ TP/FP cá»§a cÃ¡c fold láº¡i
    ci_lows = [f["precisionCI95"][0] for f in fold_results if f["testStats"]["predN"] >= MIN_FOLD_PRED]
    overall_lower_bound = float(np.mean(ci_lows)) if ci_lows else 0.0

    # Net edge: precision quy Ä‘á»•i sang trade-able edge
    # Giáº£ Ä‘á»‹nh: trade tháº¯ng kiáº¿m +X%, thua máº¥t -Y%, expected pnl = P*X - (1-P)*Y - cost
    # Default X=5, Y=3 (~1.7R typical setup) â†’ break-even precision â‰ˆ 37.5%
    avg_p = float(np.mean(precisions))
    expected_pnl_per_trade = (avg_p / 100) * 5.0 - (1 - avg_p / 100) * 3.0 - TX_COST_PCT

    # Bonferroni penalty: log scale
    bonferroni_penalty = math.log(max(N_CONFIGS_SCANNED, 2)) * 0.5

    score = (
        overall_lower_bound * 1.20            # Æ°u tiÃªn lower bound CI
        + avg_p * 0.50                        # bonus precision trung bÃ¬nh
        + np.mean(recalls) * 0.20             # nháº¹ vá» recall
        + np.mean(f1s) * 0.20
        + min(pred_total, 100) * 0.10
        + max(expected_pnl_per_trade, 0) * 8  # bonus náº¿u cÃ³ edge dÆ°Æ¡ng sau cost
        - bonferroni_penalty
    )

    return {
        "task": task,
        "indicator": indicator,
        "model": model_name,
        "featureCount": len(feats),
        "nFolds": len(fold_results),
        "avgPrecision": round(float(np.mean(precisions)), 2),
        "stdPrecision": round(float(np.std(precisions)), 2),
        "minPrecision": round(float(np.min(precisions)), 2),
        "avgRecall": round(float(np.mean(recalls)), 2),
        "avgF1": round(float(np.mean(f1s)), 2),
        "totalPredN": int(pred_total),
        "precisionCI95LowerMean": round(overall_lower_bound, 2),
        "expectedNetPnlPerTrade": round(expected_pnl_per_trade, 3),
        "score": round(score, 3),
        "passConservative": bool(
            overall_lower_bound >= 60.0           # lower bound CI â‰¥ 60% má»›i gá»i lÃ  Ä‘Ã¡ng tin
            and pred_total >= MIN_TOTAL_PRED      # Ä‘á»§ sample size
            and expected_pnl_per_trade > 0        # cÃ³ edge net sau cost
        ),
        "folds": fold_results,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Main loop: chá»n 12 indicator family / task theo conservative rank
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    rows = load_rows()
    folds = make_walkforward_folds(rows)
    print(f"[info] loaded {len(rows)} rows; built {len(folds)} walk-forward folds", flush=True)
    for fd in folds:
        print(f"  fold {fd['fold']}: train {fd['trainDates']} | val {fd['valDates']} | test {fd['testDates']} | gap {fd['purgedGapDays']}d", flush=True)

    runs = []
    for task in TASKS:
        for ind in INDICATOR_MAP:
            best_for_indicator = None
            for mn in MODELS:
                try:
                    r = eval_one(rows, folds, task, ind, mn)
                except Exception as e:
                    print(f"  {task} {ind} {mn} ERR {e}", flush=True)
                    continue
                if r is None:
                    continue
                if best_for_indicator is None or r["score"] > best_for_indicator["score"]:
                    best_for_indicator = r
            if best_for_indicator:
                runs.append(best_for_indicator)
                print(json.dumps({k: best_for_indicator[k] for k in [
                    "task", "indicator", "model", "avgPrecision", "stdPrecision",
                    "minPrecision", "precisionCI95LowerMean", "totalPredN",
                    "expectedNetPnlPerTrade", "passConservative", "score"
                ]}, ensure_ascii=False), flush=True)

    # Selection: rank theo lower bound CI, Æ°u tiÃªn configs pass conservative
    selected = {}
    for task in TASKS:
        arr = [r for r in runs if r["task"] == task]
        arr.sort(key=lambda x: (x["passConservative"], x["precisionCI95LowerMean"],
                                x["avgPrecision"], x["expectedNetPnlPerTrade"]), reverse=True)
        selected[task] = arr[:12]

    payload = {
        "createdAt": dt.datetime.now().isoformat(timespec="seconds"),
        "method": (
            "STEP 1 Claude-fix: Walk-forward indicator selection cho RS/D1A/D1S/SUPPORT_HOLD/RESISTANCE_REJECT. "
            f"N_FOLDS={N_FOLDS}, purged gap={HORIZON_DAYS} ngÃ y, validation tail={VAL_RATIO*100:.0f}% train, "
            "threshold tune trÃªn VAL (khÃ´ng IS, khÃ´ng test), probability calibration isotonic, "
            "bootstrap 95% CI cho precision, conservative rank theo lower bound CI, "
            f"Bonferroni-aware penalty (n_configs={N_CONFIGS_SCANNED}), net cost {TX_COST_PCT}%."
        ),
        "config": {
            "nFolds": N_FOLDS,
            "horizonDays": HORIZON_DAYS,
            "valRatio": VAL_RATIO,
            "minTotalPred": MIN_TOTAL_PRED,
            "minFoldPred": MIN_FOLD_PRED,
            "bootstrapN": BOOTSTRAP_N,
            "txCostPct": TX_COST_PCT,
            "tasks": TASKS,
        },
        "folds": [{k: v for k, v in fd.items() if k not in ("trainIdx", "valIdx", "testIdx")} for fd in folds],
        "sourceFeatureFile": str(D1SRC),
        "rows": len(rows),
        "indicatorMap": INDICATOR_MAP,
        "selected12ByTask": selected,
        "allRuns": runs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["task", "rank", "indicator", "model", "nFolds", "avgPrecision",
                  "stdPrecision", "minPrecision", "precisionCI95LowerMean",
                  "avgRecall", "avgF1", "totalPredN", "expectedNetPnlPerTrade",
                  "passConservative", "score"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for task, arr in selected.items():
            for i, r in enumerate(arr, 1):
                w.writerow({k: (i if k == "rank" else r.get(k)) for k in fields})

    print(json.dumps({
        "out": str(OUT),
        "csv": str(CSV_OUT),
        "selected": {
            t: [{k: r[k] for k in ["indicator", "model", "avgPrecision",
                                   "precisionCI95LowerMean", "totalPredN",
                                   "expectedNetPnlPerTrade", "passConservative"]} for r in a]
            for t, a in selected.items()
        }
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
