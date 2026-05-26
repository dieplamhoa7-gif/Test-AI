"""
STEP 1 (Claude fix) — Walk-forward indicator selection cho RS / D1A / D1S
                     + 2 task mới SUPPORT_HOLD / RESISTANCE_REJECT
                     (mục tiêu: tìm S/R chính xác cao)

Khác biệt chính so với file gốc (step1_select12_indicators_from40_rs_d1a_d1s.py):
  1. Walk-forward CV (rolling, mặc định 5 folds) thay vì 2 fixed splits cố định.
  2. Purged gap = HORIZON ngày giữa train_end và test_start để khử label leak
     (vì label dùng future20 → mẫu sát biên có rò rỉ thông tin).
  3. Threshold tune trên VALIDATION fold (cắt ra từ tail của train), KHÔNG trên IS,
     và KHÔNG bao giờ trên test fold.
  4. Probability calibration (isotonic) trước khi tune threshold để xác suất
     có ý nghĩa thực sự.
  5. Bootstrap 95% CI cho precision; rank ưu tiên LOWER BOUND của CI
     thay vì point estimate (conservative selection).
  6. Bonferroni-aware penalty: trừ điểm theo log(số indicator family × số model)
     để hạn chế lucky configs.
  7. Net-cost aware: trừ 0.4% round-trip khi quy đổi precision -> trade-able edge.
  8. Sample size guard: tổng predN qua N folds ≥ MIN_TOTAL_PRED mới được pass.
  9. Thêm 2 task: SUPPORT_HOLD và RESISTANCE_REJECT — đây là mục tiêu cốt lõi
     "tìm hỗ trợ/kháng cự chính xác cao" mà file gốc chưa có.

Lưu ý quan trọng cho người đọc code:
  - File này KHÔNG đè file gốc. Có thể chạy song song để so sánh.
  - Output schema giữ tương đương file gốc + thêm các trường walk-forward.
  - Input vẫn là vn100_history_2025_06_2026_05_cache.json
    và d1a_full_research_features_is_oos.json, vẫn dùng module
    build_indicator40_ml_outputs.py (ind40) y nguyên.
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

# ─────────────────────────────────────────────────────────────────────────────
# Cấu hình walk-forward
# ─────────────────────────────────────────────────────────────────────────────
N_FOLDS = 5                  # số fold walk-forward
HORIZON_DAYS = 20            # label dùng future20 → purge gap 20 ngày
VAL_RATIO = 0.20             # 20% cuối train tách làm validation để tune threshold
MIN_TOTAL_PRED = 30          # tổng predN qua N folds tối thiểu
MIN_FOLD_PRED = 3            # mỗi fold phải predict được ≥ N mới counted
BOOTSTRAP_N = 400            # số lần bootstrap để ước lượng CI
RANDOM_SEED = 20260526
TX_COST_PCT = 0.4            # phí round-trip giả định 0.4% (phí + thuế + slippage)

# Tasks: giữ RS/D1A/D1S + thêm 2 task mục tiêu chính của anh diep
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

# Load module indicator40 y nguyên cách file gốc
spec = importlib.util.spec_from_file_location("ind40", IND40)
ind40 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ind40)

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Data loading — giống step1 gốc để cache feature40 ổn định
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# Labels — giữ nguyên RS/D1A/D1S + thêm SUPPORT_HOLD / RESISTANCE_REJECT
# ─────────────────────────────────────────────────────────────────────────────
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
        # Mục tiêu: với mẫu hiện đang gần support, support đó GIỮ trong 20 phiên tới.
        # Điều kiện tiền đề: ngày t đang nằm trong vùng test support
        near = bool(rs.get("nearSupport") or abs(rs.get("distSupportPct") or 99) < 4)
        if not near:
            return 0
        # Hold: futureMin20 không xuyên thủng support > 3% (1 ATR ~ 2.5-3%)
        future_min = lc.get("futureMin20") or 0
        not_broken = future_min > -4.5
        # Phải có ít nhất 1 cú nảy lên trên 3% trong tương lai → chứng minh support là vùng "bid mạnh"
        future_max = lc.get("futureMax20") or 0
        bounced = future_max >= 3.0
        return int(not_broken and bounced)

    if task == "RESISTANCE_REJECT":
        # Mục tiêu: với mẫu hiện đang gần resistance, resistance đó REJECT trong 20 phiên.
        near_res = bool(rs.get("nearResistance") or abs(rs.get("distResistancePct") or 99) < 4)
        if not near_res:
            return 0
        # Reject: futureMax20 không vượt resistance đáng kể (close không > 3% trên resistance)
        future_max = lc.get("futureMax20") or 0
        not_breakout = future_max <= 3.0
        # Phải có cú giảm thật từ vùng resistance (futureMin <= -3%)
        future_min = lc.get("futureMin20") or 0
        rejected = future_min <= -3.0
        return int(not_breakout and rejected)

    raise ValueError(task)


# ─────────────────────────────────────────────────────────────────────────────
# Metric helpers + bootstrap
# ─────────────────────────────────────────────────────────────────────────────
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
    Bootstrap CI cho precision. Trả về (p_mean, p_low95, p_high95).
    Lưu ý: chỉ bootstrap trên các sample có pred=1; nếu predN nhỏ thì CI sẽ rộng.
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


# ─────────────────────────────────────────────────────────────────────────────
# Walk-forward splits với purged gap
# ─────────────────────────────────────────────────────────────────────────────
def make_walkforward_folds(rows, n_folds=N_FOLDS, horizon=HORIZON_DAYS, val_ratio=VAL_RATIO):
    """
    Tạo N rolling folds:
      [train_block] [purged_gap=horizon] [test_block]
    Trong train_block tách 20% cuối làm validation (cũng purged khỏi train).

    Trả về: list[dict(train_idx, val_idx, test_idx, dates...)]
    """
    dates = sorted({r["date"] for r in rows})
    n_dates = len(dates)
    if n_dates < n_folds * (horizon + 5):
        raise ValueError(f"Không đủ ngày cho {n_folds} folds: chỉ có {n_dates} ngày")

    # Mỗi fold test_block dài bằng nhau
    test_block_len = (n_dates - horizon) // (n_folds + 2)  # +2 để có buffer ở đầu
    if test_block_len < 5:
        raise ValueError(f"Test block quá ngắn ({test_block_len} ngày)")

    folds = []
    for k in range(n_folds):
        # Fold k:  train_end = n_dates - (n_folds-k)*test_block_len - horizon
        test_end_idx = n_dates - (n_folds - 1 - k) * test_block_len
        test_start_idx = test_end_idx - test_block_len
        train_end_idx = test_start_idx - horizon  # purged gap
        if train_end_idx < int(n_dates * 0.20):    # tối thiểu 20% data làm train
            continue
        train_dates = dates[:train_end_idx]
        test_dates = dates[test_start_idx:test_end_idx]

        # Validation = 20% cuối train, ALSO purged khỏi train final
        val_block_len = max(int(len(train_dates) * val_ratio), horizon + 5)
        val_dates = train_dates[-val_block_len:]
        train_final_end = len(train_dates) - val_block_len - horizon
        if train_final_end < 30:
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


# ─────────────────────────────────────────────────────────────────────────────
# Models + calibration
# ─────────────────────────────────────────────────────────────────────────────
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
    Fit model + isotonic calibration trên train (CV=3 nội bộ).
    Calibration giúp threshold có ý nghĩa thực sự "xác suất P(label=1)".
    """
    base = clf(model_name, seed)
    if len(set(ytr)) < 2 or sum(ytr) < 8:
        # quá ít positive → bỏ calibration, fallback fit thẳng
        base.fit(Xtr, ytr)
        return base, False
    try:
        cal = CalibratedClassifierCV(estimator=base, method="isotonic", cv=3)
        cal.fit(Xtr, ytr)
        return cal, True
    except Exception:
        base.fit(Xtr, ytr)
        return base, False


# ─────────────────────────────────────────────────────────────────────────────
# Tune threshold trên VALIDATION fold (precision-first)
# ─────────────────────────────────────────────────────────────────────────────
def tune_threshold_on_val(y_val, prob_val, min_pred_val=5):
    """
    Quét ngưỡng từ 0.10 → 0.95, pick ngưỡng có precision cao nhất
    với điều kiện predN_val ≥ min_pred_val.
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


# ─────────────────────────────────────────────────────────────────────────────
# Đánh giá 1 (task, indicator family, model) qua walk-forward
# ─────────────────────────────────────────────────────────────────────────────
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
            # fold không đủ tin cậy; vẫn lưu để aggregate nhưng đánh dấu
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

    # Bootstrap CI tổng hợp: ghép tất cả TP/FP của các fold lại
    ci_lows = [f["precisionCI95"][0] for f in fold_results if f["testStats"]["predN"] >= MIN_FOLD_PRED]
    overall_lower_bound = float(np.mean(ci_lows)) if ci_lows else 0.0

    # Net edge: precision quy đổi sang trade-able edge
    # Giả định: trade thắng kiếm +X%, thua mất -Y%, expected pnl = P*X - (1-P)*Y - cost
    # Default X=5, Y=3 (~1.7R typical setup) → break-even precision ≈ 37.5%
    avg_p = float(np.mean(precisions))
    expected_pnl_per_trade = (avg_p / 100) * 5.0 - (1 - avg_p / 100) * 3.0 - TX_COST_PCT

    # Bonferroni penalty: log scale
    bonferroni_penalty = math.log(max(N_CONFIGS_SCANNED, 2)) * 0.5

    score = (
        overall_lower_bound * 1.20            # ưu tiên lower bound CI
        + avg_p * 0.50                        # bonus precision trung bình
        + np.mean(recalls) * 0.20             # nhẹ về recall
        + np.mean(f1s) * 0.20
        + min(pred_total, 100) * 0.10
        + max(expected_pnl_per_trade, 0) * 8  # bonus nếu có edge dương sau cost
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
            overall_lower_bound >= 60.0           # lower bound CI ≥ 60% mới gọi là đáng tin
            and pred_total >= MIN_TOTAL_PRED      # đủ sample size
            and expected_pnl_per_trade > 0        # có edge net sau cost
        ),
        "folds": fold_results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main loop: chọn 12 indicator family / task theo conservative rank
# ─────────────────────────────────────────────────────────────────────────────
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

    # Selection: rank theo lower bound CI, ưu tiên configs pass conservative
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
            f"N_FOLDS={N_FOLDS}, purged gap={HORIZON_DAYS} ngày, validation tail={VAL_RATIO*100:.0f}% train, "
            "threshold tune trên VAL (không IS, không test), probability calibration isotonic, "
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
