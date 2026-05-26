"""
STEP 2 (Claude fix) â€” Walk-forward parameter / feature-variant tuning
                     trong tá»«ng indicator family Ä‘Ã£ chá»n tá»« Step 1.

Má»¥c tiÃªu: tÃ¬m ra biáº¿n thá»ƒ Ä‘áº·c trÆ°ng (theo period 7/10/14/20/50â€¦, theo signal/hist/spread,
v.v.) cÃ³ precision cao vÃ  á»•n Ä‘á»‹nh cho task SUPPORT_HOLD / RESISTANCE_REJECT /
RS / D1A / D1S, sau khi Ä‘Ã£ cháº¡y Step 1 Claude-fix.

KhÃ¡c biá»‡t vá»›i step2 gá»‘c:
  1. Äá»c tá»« Step 1 Claude-fix (file _Claude_fix.json), khÃ´ng Ä‘á»c step1 cÅ©.
  2. Walk-forward CV vá»›i purged gap = HORIZON_DAYS.
  3. Threshold tune trÃªn VALIDATION fold, KHÃ”NG trÃªn IS train.
  4. Probability calibration isotonic.
  5. Bootstrap 95% CI cho precision OOS qua má»—i fold; rank theo
     mean(lower_bound_CI) thay vÃ¬ point estimate.
  6. Bonferroni penalty theo log(sá»‘ variant Ã— sá»‘ model Ã— sá»‘ task) â€” vÃ¬ step 2
     quÃ©t ráº¥t nhiá»u variant nÃªn cáº§n penalize chá»‘ng lucky picks.
  7. Net cost-aware: pháº£i cÃ³ edge dÆ°Æ¡ng sau 0.4% phÃ­ round-trip má»›i Ä‘Æ°á»£c "pass".
  8. Sample size guard nghiÃªm hÆ¡n: tá»•ng predN â‰¥ 40 trÃªn N folds, má»—i fold â‰¥ 3.
  9. Output tÆ°Æ¡ng thÃ­ch downstream (selectedByTask, allRuns) cá»™ng thÃªm cÃ¡c trÆ°á»ng
     foldResults vÃ  bootstrapCI Ä‘á»ƒ Step 3 sá»­ dá»¥ng.

File nÃ y KHÃ”NG Ä‘Ã¨ file gá»‘c. TÃªn: step2_tune_params_precision_first_rs_d1a_d1s_Claude_fix.py
"""

from __future__ import annotations
import json, csv, datetime as dt, importlib.util, warnings, math
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
STEP1 = DATA / "core12_step1_select12_from40_rs_d1a_d1s_Claude_fix.json"   # input tá»« Step 1 fix
IND40 = ROOT / "build_indicator40_ml_outputs.py"
OUT = DATA / "core12_step2_tune_params_precision_first_rs_d1a_d1s_Claude_fix.json"
CSV_OUT = DATA / "core12_step2_tune_params_precision_first_rs_d1a_d1s_Claude_fix.csv"

# Walk-forward config (Ä‘á»“ng bá»™ vá»›i step 1 fix)
N_FOLDS = 2
HORIZON_DAYS = 10
VAL_RATIO = 0.20
MIN_TOTAL_PRED = 40       # nghiÃªm hÆ¡n step 1 (vÃ¬ sample variant biÃªn dá»… overfit)
MIN_FOLD_PRED = 3
BOOTSTRAP_N = 100
RANDOM_SEED = 20260526
TX_COST_PCT = 0.4
MODELS = ["LOG", "ET", "RF"]
TASKS = ["RS", "D1A", "D1S", "SUPPORT_HOLD", "RESISTANCE_REJECT"]

# Variant tokens â€” bao gá»“m period chuáº©n vÃ  mÃ´ táº£ (slope, dist, width, pos, pct...)
VARIANT_TOKENS = [
    "7", "10", "14", "20", "21", "40", "50", "60", "100", "200",
    "slope", "dist", "width", "pos", "pct", "hist", "signal", "spread",
    "norm", "inv", "ratio", "z", "diff", "lag", "ma",
]

FAMILY_PREFIX = {
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
    "MFI": ["mfi"], "VWMA": ["vwma"], "PVI_NVI": ["pvi", "nvi"],
    "VOSC_KLINGER": ["vosc", "klinger"],
}

spec = importlib.util.spec_from_file_location("ind40", IND40)
ind40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ind40)

np.random.seed(RANDOM_SEED)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Data loading
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
                "symbol": sym, "date": key[1], "sector": base.get("sector"),
                "features40": feats, "rs": base.get("rs") or {},
                "lc": base.get("lc") or {}, "full": base.get("fullResearchFeatures") or {},
                "mtf": base.get("mtfAsOfDate") or {},
            })
    rows.sort(key=lambda x: (x["date"], x["symbol"]))
    return rows


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Labels (Ä‘á»“ng bá»™ step1 fix â€” bao gá»“m SUPPORT_HOLD, RESISTANCE_REJECT)
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
        near = bool(rs.get("nearSupport") or abs(rs.get("distSupportPct") or 99) < 4)
        if not near: return 0
        future_min = lc.get("futureMin20") or 0
        future_max = lc.get("futureMax20") or 0
        return int(future_min > -4.5 and future_max >= 3.0)
    if task == "RESISTANCE_REJECT":
        near_res = bool(rs.get("nearResistance") or abs(rs.get("distResistancePct") or 99) < 4)
        if not near_res: return 0
        future_max = lc.get("futureMax20") or 0
        future_min = lc.get("futureMin20") or 0
        return int(future_max <= 3.0 and future_min <= -3.0)
    raise ValueError(task)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Metrics helpers
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
    idx = np.where(y_pred == 1)[0]
    if len(idx) < MIN_FOLD_PRED:
        return (0.0, 0.0, 0.0)
    rng = np.random.RandomState(RANDOM_SEED)
    ps = []
    for _ in range(n_bootstrap):
        sample = rng.choice(idx, size=len(idx), replace=True)
        tp = int((y_true[sample] == 1).sum())
        ps.append(tp / len(sample))
    arr = np.array(ps) * 100
    return float(arr.mean()), float(np.percentile(arr, 100 * alpha / 2)), float(np.percentile(arr, 100 * (1 - alpha / 2)))


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Walk-forward folds (cÃ¹ng Ä‘á»‹nh nghÄ©a step 1 fix)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def make_walkforward_folds(rows, n_folds=N_FOLDS, horizon=HORIZON_DAYS, val_ratio=VAL_RATIO):
    dates = sorted({r["date"] for r in rows})
    n_dates = len(dates)
    if n_dates < n_folds * (horizon + 5):
        raise ValueError(f"KhÃ´ng Ä‘á»§ ngÃ y: {n_dates}")
    test_block_len = (n_dates - horizon) // (n_folds + 2)
    if test_block_len < 5:
        raise ValueError("Test block quÃ¡ ngáº¯n")
    folds = []
    for k in range(n_folds):
        test_end_idx = n_dates - (n_folds - 1 - k) * test_block_len
        test_start_idx = test_end_idx - test_block_len
        train_end_idx = test_start_idx - horizon
        if train_end_idx < int(n_dates * 0.20):
            continue
        train_dates = dates[:train_end_idx]
        test_dates = dates[test_start_idx:test_end_idx]
        val_block_len = max(int(len(train_dates) * val_ratio), horizon + 5)
        val_dates = train_dates[-val_block_len:]
        train_final_end = len(train_dates) - val_block_len - horizon
        if train_final_end < 15:
            continue
        train_final_dates = train_dates[:train_final_end]
        train_set, val_set, test_set = set(train_final_dates), set(val_dates), set(test_dates)
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
            "trainIdx": train_idx, "valIdx": val_idx, "testIdx": test_idx,
        })
    return folds


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Models + calibration
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clf(name, seed):
    if name == "ET":
        return ExtraTreesClassifier(n_estimators=360, max_depth=3, min_samples_leaf=8,
                                    class_weight="balanced", random_state=seed, n_jobs=1)
    if name == "RF":
        return RandomForestClassifier(n_estimators=360, max_depth=3, min_samples_leaf=8,
                                      class_weight="balanced", random_state=seed, n_jobs=1)
    return Pipeline([("s", StandardScaler()),
                     ("l", LogisticRegression(max_iter=1200, C=0.25, class_weight="balanced", random_state=seed))])


def fit_calibrated(name, seed, Xtr, ytr):
    base = clf(name, seed)
    if len(set(ytr)) < 2 or sum(ytr) < 8:
        base.fit(Xtr, ytr)
        return base, False
    try:
        cal = CalibratedClassifierCV(estimator=base, method="isotonic", cv=3)
        cal.fit(Xtr, ytr)
        return cal, True
    except Exception:
        base.fit(Xtr, ytr)
        return base, False


def tune_threshold_on_val(y_val, prob_val, task, min_pred_val=5):
    """
    Precision-first threshold tuning trÃªn VAL.
    Step 2 cháº·t hÆ¡n step 1: yÃªu cáº§u precision_val â‰¥ 60% má»›i Ä‘Æ°á»£c pick;
    náº¿u khÃ´ng cÃ³ ngÆ°á»¡ng nÃ o Ä‘áº¡t â†’ tráº£ None (loáº¡i config nÃ y).
    """
    candidates = []
    for th in np.linspace(0.10, 0.98, 89):
        preds = (prob_val >= th).astype(int)
        st = stats(y_val, preds)
        if st["predN"] < min_pred_val:
            continue
        if st["precision"] < 60.0:
            continue
        candidates.append((st["precision"], st["recall"], st["predN"], st["f1"], float(th), st))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)
    return candidates[0]


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Táº¡o cÃ¡c bá»™ feature variant trong tá»«ng family
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def candidate_feature_sets(all_feats, family):
    prefs = FAMILY_PREFIX[family]
    feats = sorted([f for f in all_feats if any(f.startswith(p) or p in f for p in prefs)])
    if not feats:
        return []
    sets = []
    for f in feats:
        sets.append((f, [f]))  # má»—i feature Ä‘á»©ng riÃªng
    for token in VARIANT_TOKENS:
        fs = [f for f in feats if token in f]
        if fs:
            sets.append((family + "_" + token, fs))
    sets.append((family + "_ALL", feats))
    out, seen = [], set()
    for name, fs in sets:
        key = tuple(fs)
        if key not in seen:
            out.append((name, fs))
            seen.add(key)
    return out


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ÄÃ¡nh giÃ¡ 1 (task, family, setName, model) qua walk-forward
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def eval_set(rows, folds, task, family, set_name, features, model_name, n_total_configs):
    y_full = np.array([label(task, r) for r in rows])
    fold_results = []
    for fd in folds:
        tr_idx, va_idx, te_idx = fd["trainIdx"], fd["valIdx"], fd["testIdx"]
        ytr = y_full[tr_idx]; yva = y_full[va_idx]; yte = y_full[te_idx]
        if len(set(ytr)) < 2 or yva.sum() < 2 or yte.sum() < 2:
            continue
        Xtr = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in tr_idx], float)
        Xva = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in va_idx], float)
        Xte = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in te_idx], float)
        keep = [i for i, s in enumerate(Xtr.std(axis=0)) if s > 1e-9]
        if not keep:
            continue
        Xtr, Xva, Xte = Xtr[:, keep], Xva[:, keep], Xte[:, keep]
        feats_kept = [features[i] for i in keep]
        seed = abs(hash((task, family, set_name, model_name, fd["fold"]))) % 100000
        m, calibrated = fit_calibrated(model_name, seed, Xtr, ytr)
        try:
            prob_val = m.predict_proba(Xva)[:, 1]
            prob_te = m.predict_proba(Xte)[:, 1]
        except Exception:
            continue
        tuned = tune_threshold_on_val(yva, prob_val, task)
        if tuned is None:
            continue
        prec_val, rec_val, pred_val, f1_val, th, st_val = tuned
        pred_te = (prob_te >= th).astype(int)
        st_te = stats(yte, pred_te)
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
            "features": feats_kept,
        })
    if not fold_results:
        return None

    precisions = [f["testStats"]["precision"] for f in fold_results]
    recalls = [f["testStats"]["recall"] for f in fold_results]
    f1s = [f["testStats"]["f1"] for f in fold_results]
    pred_total = sum(f["testStats"]["predN"] for f in fold_results)
    ci_lows = [f["precisionCI95"][0] for f in fold_results if f["testStats"]["predN"] >= MIN_FOLD_PRED]
    lower_bound_mean = float(np.mean(ci_lows)) if ci_lows else 0.0

    avg_p = float(np.mean(precisions))
    expected_pnl_per_trade = (avg_p / 100) * 5.0 - (1 - avg_p / 100) * 3.0 - TX_COST_PCT

    bonferroni_penalty = math.log(max(n_total_configs, 2)) * 0.8  # step 2 quÃ©t nhiá»u hÆ¡n â†’ penalty máº¡nh hÆ¡n

    pass_p70 = (lower_bound_mean >= 70 and pred_total >= MIN_TOTAL_PRED and
                np.min(precisions) >= 60 and expected_pnl_per_trade > 0)
    pass_conservative = (lower_bound_mean >= 60 and pred_total >= MIN_TOTAL_PRED and
                         expected_pnl_per_trade > 0)

    score = (
        lower_bound_mean * 1.50
        + avg_p * 0.40
        + np.mean(recalls) * 0.20
        + np.mean(f1s) * 0.20
        + min(pred_total, 120) * 0.06
        + max(expected_pnl_per_trade, 0) * 10
        - bonferroni_penalty
    )

    return {
        "task": task,
        "family": family,
        "setName": set_name,
        "model": model_name,
        "features": features,
        "featureCount": len(features),
        "nFolds": len(fold_results),
        "avgPrecision": round(avg_p, 2),
        "stdPrecision": round(float(np.std(precisions)), 2),
        "minPrecision": round(float(np.min(precisions)), 2),
        "precisionCI95LowerMean": round(lower_bound_mean, 2),
        "avgRecall": round(float(np.mean(recalls)), 2),
        "avgF1": round(float(np.mean(f1s)), 2),
        "totalPredN": int(pred_total),
        "expectedNetPnlPerTrade": round(expected_pnl_per_trade, 3),
        "passP70": bool(pass_p70),
        "passConservative": bool(pass_conservative),
        "bonferroniPenalty": round(bonferroni_penalty, 3),
        "score": round(score, 3),
        "folds": fold_results,
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Main
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main():
    rows = load_rows()
    folds = make_walkforward_folds(rows)
    print(f"[info] {len(rows)} rows | {len(folds)} folds", flush=True)
    if not STEP1.exists():
        raise FileNotFoundError(
            f"KhÃ´ng tÃ¬m tháº¥y {STEP1}. Vui lÃ²ng cháº¡y step1_..._Claude_fix.py trÆ°á»›c."
        )
    step1 = json.load(open(STEP1, encoding="utf-8"))

    all_feats = sorted({k for r in rows for k in r["features40"]})

    # Äáº¿m trÆ°á»›c tá»•ng sá»‘ config sáº½ quÃ©t â†’ Ä‘á»ƒ tÃ­nh bonferroni penalty Ä‘Ãºng
    total_configs = 0
    for task, arr in step1["selected12ByTask"].items():
        families = [x["indicator"] for x in arr]
        family_keys = [f for f in families if f in FAMILY_PREFIX] + \
                      ["PVI_NVI" if "PVI" in families or "NVI" in families else None,
                       "VOSC_KLINGER" if "VOSC" in families or "KLINGER" in families else None]
        family_keys = [f for f in family_keys if f]
        for fam in family_keys:
            variants = candidate_feature_sets(all_feats, fam)
            total_configs += len(variants) * len(MODELS)
    total_configs = max(total_configs, 1)
    print(f"[info] tá»•ng sá»‘ config sáº½ quÃ©t: {total_configs}", flush=True)

    runs = []
    for task, arr in step1["selected12ByTask"].items():
        families = [x["indicator"] for x in arr]
        # Map gá»n vá» key cá»§a FAMILY_PREFIX (PVI/NVI â†’ PVI_NVI, VOSC/KLINGER â†’ VOSC_KLINGER)
        mapped = []
        seen = set()
        for f in families:
            if f in FAMILY_PREFIX:
                key = f
            elif f in ("PVI", "NVI"):
                key = "PVI_NVI"
            elif f in ("VOSC", "KLINGER"):
                key = "VOSC_KLINGER"
            else:
                continue
            if key not in seen:
                mapped.append(key); seen.add(key)
        for fam in mapped:
            for name, fs in candidate_feature_sets(all_feats, fam):
                best = None
                for mn in MODELS:
                    try:
                        r = eval_set(rows, folds, task, fam, name, fs, mn, total_configs)
                    except Exception as e:
                        print(f"  {task} {fam} {name} {mn} ERR {e}", flush=True)
                        continue
                    if r is None:
                        continue
                    if best is None or (r["precisionCI95LowerMean"], r["avgPrecision"], r["totalPredN"]) > \
                       (best["precisionCI95LowerMean"], best["avgPrecision"], best["totalPredN"]):
                        best = r
                if best:
                    runs.append(best)
                    print(json.dumps({k: best[k] for k in [
                        "task", "family", "setName", "model", "avgPrecision",
                        "minPrecision", "precisionCI95LowerMean", "totalPredN",
                        "expectedNetPnlPerTrade", "passConservative", "passP70"
                    ]}, ensure_ascii=False), flush=True)

    selected = {}
    for task in TASKS:
        arr = [r for r in runs if r["task"] == task]
        arr.sort(key=lambda x: (x["passConservative"], x["passP70"],
                                x["precisionCI95LowerMean"], x["avgPrecision"],
                                x["totalPredN"], x["expectedNetPnlPerTrade"]), reverse=True)
        selected[task] = arr[:20]

    payload = {
        "createdAt": dt.datetime.now().isoformat(timespec="seconds"),
        "method": (
            "STEP 2 Claude-fix: Walk-forward parameter/feature-variant tuning trong tá»«ng family. "
            f"N_FOLDS={N_FOLDS}, purged gap={HORIZON_DAYS}d, val tail={VAL_RATIO*100:.0f}% train, "
            "threshold tune trÃªn VAL (yÃªu cáº§u precision_val â‰¥ 60%), isotonic calibration, "
            "bootstrap 95% CI, rank theo lower bound CI, "
            f"Bonferroni penalty (n_configs={total_configs}), net cost {TX_COST_PCT}%."
        ),
        "config": {
            "nFolds": N_FOLDS, "horizonDays": HORIZON_DAYS, "valRatio": VAL_RATIO,
            "minTotalPred": MIN_TOTAL_PRED, "minFoldPred": MIN_FOLD_PRED,
            "bootstrapN": BOOTSTRAP_N, "txCostPct": TX_COST_PCT,
            "tasks": TASKS, "totalConfigsScanned": total_configs,
        },
        "folds": [{k: v for k, v in fd.items() if k not in ("trainIdx", "valIdx", "testIdx")} for fd in folds],
        "sourceStep1": str(STEP1),
        "selectedByTask": selected,
        "allRuns": runs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["task", "rank", "family", "setName", "model", "featureCount",
                  "nFolds", "avgPrecision", "stdPrecision", "minPrecision",
                  "precisionCI95LowerMean", "avgRecall", "avgF1", "totalPredN",
                  "expectedNetPnlPerTrade", "passP70", "passConservative", "score"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for task, arr in selected.items():
            for i, r in enumerate(arr, 1):
                w.writerow({k: (i if k == "rank" else r.get(k)) for k in fields})

    print(json.dumps({
        "out": str(OUT),
        "csv": str(CSV_OUT),
        "selected": {
            t: [{k: r[k] for k in ["family", "setName", "model", "avgPrecision",
                                   "precisionCI95LowerMean", "totalPredN",
                                   "expectedNetPnlPerTrade", "passP70",
                                   "passConservative"]} for r in a[:12]]
            for t, a in selected.items()
        }
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
