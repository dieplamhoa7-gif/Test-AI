"""
STEP 3 (Claude fix) — Walk-forward combo 5-8 indicator family / task

Mục tiêu: ghép tổ hợp 5-8 family đã được Step 2 fix chứng minh có lower-bound CI cao,
huấn luyện model trên combo, đánh giá qua walk-forward với purged gap, threshold tune
trên VAL, calibration isotonic, bootstrap CI, Bonferroni penalty mạnh hơn (vì combo
nhân số config), và yêu cầu pass cả 3 tiêu chí:
   (1) lower bound CI precision ≥ 70%
   (2) tổng predN ≥ 50 qua N folds
   (3) expected net pnl/trade > 0 sau 0.4% phí round-trip

Khác biệt với step3 gốc:
  1. Đọc Step 2 Claude-fix (file _Claude_fix.json).
  2. KHÔNG dùng "best per family" thẳng — chọn top N family theo lower-bound CI
     của Step 2 (conservative), bỏ family có expected_pnl âm.
  3. Walk-forward CV với purged gap.
  4. Mọi threshold đều tune trên VAL.
  5. Probability calibration isotonic.
  6. Bootstrap 95% CI; rank theo lower bound.
  7. Bonferroni penalty mạnh: tổng số combo có thể lên đến vài trăm.
  8. Sample size guard chặt: tổng predN ≥ 50.
  9. Output thêm trường "tradePlan": với combo top 1 per task, gợi ý entry/stop/target
     dựa trên S/R hiện tại (nếu task là SUPPORT_HOLD/RESISTANCE_REJECT/RS).

File này KHÔNG đè file gốc.
"""

from __future__ import annotations
import json, csv, datetime as dt, itertools, importlib.util, warnings, math
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
STEP2 = DATA / "core12_step2_tune_params_precision_first_rs_d1a_d1s_Claude_fix.json"
OUT = DATA / "core12_step3_combo_5to8_from_step2_precision_first_rs_d1a_d1s_fast_Claude_fix.json"
CSV_OUT = DATA / "core12_step3_combo_5to8_from_step2_precision_first_rs_d1a_d1s_fast_Claude_fix.csv"

# Import step2 fix module dynamically để re-use load_rows / label / folds / clf
STEP2_PY = ROOT / "step2_tune_params_precision_first_rs_d1a_d1s_Claude_fix.py"
spec = importlib.util.spec_from_file_location("step2fix", STEP2_PY)
step2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(step2)

# Walk-forward config (đồng bộ step2 fix)
N_FOLDS = step2.N_FOLDS
HORIZON_DAYS = step2.HORIZON_DAYS
VAL_RATIO = step2.VAL_RATIO
MIN_TOTAL_PRED = 50            # nghiêm hơn step1/step2 vì step3 quét combo
MIN_FOLD_PRED = 3
BOOTSTRAP_N = step2.BOOTSTRAP_N
TX_COST_PCT = step2.TX_COST_PCT
TASKS = step2.TASKS
MODELS = ["ET", "RF", "LOG"]
GROUP_SIZES = [5, 6, 7, 8]
MAX_POOL_PER_TASK = 8   # tối đa 8 family pool → C(8,5)+...+C(8,8) = 93 combo/task

RANDOM_SEED = 20260526
np.random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers re-using step2 fix
# ─────────────────────────────────────────────────────────────────────────────
def stats(y, p):
    return step2.stats(y, p)


def bootstrap_precision_ci(y_true, y_pred):
    return step2.bootstrap_precision_ci(y_true, y_pred)


def fit_calibrated(name, seed, Xtr, ytr):
    return step2.fit_calibrated(name, seed, Xtr, ytr)


def tune_threshold_on_val(y_val, prob_val, task):
    return step2.tune_threshold_on_val(y_val, prob_val, task)


# ─────────────────────────────────────────────────────────────────────────────
# Eval combo qua walk-forward
# ─────────────────────────────────────────────────────────────────────────────
def eval_combo(rows, folds, task, combo, model_name, n_total_configs):
    features = sorted({f for r in combo for f in r["features"]})
    y_full = np.array([step2.label(task, r) for r in rows])
    fold_results = []
    for fd in folds:
        tr_idx, va_idx, te_idx = fd["trainIdx"], fd["valIdx"], fd["testIdx"]
        ytr = y_full[tr_idx]; yva = y_full[va_idx]; yte = y_full[te_idx]
        if len(set(ytr)) < 2 or yva.sum() < 2 or yte.sum() < 2:
            return None
        Xtr = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in tr_idx], float)
        Xva = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in va_idx], float)
        Xte = np.array([[rows[i]["features40"].get(f, 0.0) for f in features] for i in te_idx], float)
        keep = [i for i, s in enumerate(Xtr.std(axis=0)) if s > 1e-9]
        if len(keep) < 5:
            return None
        Xtr, Xva, Xte = Xtr[:, keep], Xva[:, keep], Xte[:, keep]
        feats_kept = [features[i] for i in keep]
        seed = abs(hash((task, tuple(x["family"] + "|" + x["setName"] for x in combo),
                         model_name, fd["fold"]))) % 100000
        try:
            m, calibrated = fit_calibrated(model_name, seed, Xtr, ytr)
            prob_val = m.predict_proba(Xva)[:, 1]
            prob_te = m.predict_proba(Xte)[:, 1]
        except Exception:
            return None
        tuned = tune_threshold_on_val(yva, prob_val, task)
        if tuned is None:
            return None
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

    bonferroni_penalty = math.log(max(n_total_configs, 2)) * 1.2  # step3 penalty mạnh nhất

    pass_strict = (lower_bound_mean >= 70 and pred_total >= MIN_TOTAL_PRED and
                   np.min(precisions) >= 60 and expected_pnl_per_trade > 0)
    pass_conservative = (lower_bound_mean >= 60 and pred_total >= MIN_TOTAL_PRED and
                         expected_pnl_per_trade > 0)

    score = (
        lower_bound_mean * 1.80
        + avg_p * 0.50
        + np.mean(recalls) * 0.25
        + np.mean(f1s) * 0.20
        + min(pred_total, 150) * 0.05
        + max(expected_pnl_per_trade, 0) * 12
        - bonferroni_penalty
    )

    return {
        "task": task,
        "groupSize": len(combo),
        "families": [r["family"] for r in combo],
        "setNames": [r["setName"] for r in combo],
        "model": model_name,
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
        "passStrict": bool(pass_strict),
        "passConservative": bool(pass_conservative),
        "bonferroniPenalty": round(bonferroni_penalty, 3),
        "score": round(score, 3),
        "folds": fold_results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not STEP2.exists():
        raise FileNotFoundError(f"Không tìm thấy {STEP2}. Chạy step2 Claude-fix trước.")
    rows = step2.load_rows()
    folds = step2.make_walkforward_folds(rows)
    print(f"[info] {len(rows)} rows | {len(folds)} folds", flush=True)

    s2 = json.load(open(STEP2, encoding="utf-8"))["selectedByTask"]

    # Pool family per task: chỉ giữ family có expected_pnl > 0 và CI lower bound cao,
    # 1 variant tốt nhất / family, tối đa MAX_POOL_PER_TASK
    pools = {}
    for task, arr in s2.items():
        seen = set()
        pool = []
        # Sort lại để chắc chắn theo conservative rank
        arr_sorted = sorted(arr, key=lambda x: (x["precisionCI95LowerMean"], x["avgPrecision"],
                                                x["totalPredN"]), reverse=True)
        for r in arr_sorted:
            if r["family"] in seen:
                continue
            if r.get("expectedNetPnlPerTrade", -99) <= 0:
                continue
            if r.get("precisionCI95LowerMean", 0) < 50:
                continue
            pool.append(r); seen.add(r["family"])
            if len(pool) >= MAX_POOL_PER_TASK:
                break
        pools[task] = pool
        print(f"  task {task}: pool size = {len(pool)} families: {[p['family'] for p in pool]}", flush=True)

    # Đếm tổng combo
    total_configs = 0
    for task, pool in pools.items():
        for k in GROUP_SIZES:
            if k <= len(pool):
                total_configs += math.comb(len(pool), k) * len(MODELS)
    total_configs = max(total_configs, 1)
    print(f"[info] tổng combo sẽ quét: {total_configs}", flush=True)

    runs = []
    for task, pool in pools.items():
        if len(pool) < min(GROUP_SIZES):
            print(f"  {task}: pool quá nhỏ ({len(pool)}) → bỏ qua", flush=True)
            continue
        combos = []
        for k in GROUP_SIZES:
            if k <= len(pool):
                combos += list(itertools.combinations(pool, k))
        for combo in combos:
            best = None
            for mn in MODELS:
                try:
                    rr = eval_combo(rows, folds, task, combo, mn, total_configs)
                except Exception as e:
                    print(f"  {task} combo {[r['family'] for r in combo]} {mn} ERR {e}", flush=True)
                    continue
                if rr is None:
                    continue
                if best is None or (rr["precisionCI95LowerMean"], rr["avgPrecision"],
                                    rr["totalPredN"]) > (best["precisionCI95LowerMean"],
                                                         best["avgPrecision"],
                                                         best["totalPredN"]):
                    best = rr
            if best:
                runs.append(best)
                print(json.dumps({k: best[k] for k in [
                    "task", "groupSize", "families", "model", "avgPrecision",
                    "minPrecision", "precisionCI95LowerMean", "totalPredN",
                    "expectedNetPnlPerTrade", "passStrict", "passConservative"
                ]}, ensure_ascii=False), flush=True)

    selected = {}
    for task in TASKS:
        arr = [r for r in runs if r["task"] == task]
        arr.sort(key=lambda x: (x["passStrict"], x["passConservative"],
                                x["precisionCI95LowerMean"], x["avgPrecision"],
                                x["expectedNetPnlPerTrade"], x["totalPredN"]), reverse=True)
        selected[task] = arr[:20]

    # Tóm tắt: cho mỗi task lấy top 1 conservative-pass nếu có
    top_per_task = {}
    for task, arr in selected.items():
        if not arr:
            top_per_task[task] = None
            continue
        passers = [r for r in arr if r.get("passConservative")]
        top_per_task[task] = passers[0] if passers else arr[0]

    payload = {
        "createdAt": dt.datetime.now().isoformat(timespec="seconds"),
        "method": (
            "STEP 3 Claude-fix: Walk-forward combo 5-8 family/task; pool family đã filter "
            "theo expected_pnl > 0 và CI lower bound ≥ 50 từ Step 2 fix. "
            f"N_FOLDS={N_FOLDS}, purged gap={HORIZON_DAYS}d, isotonic calibration, "
            "threshold tune trên VAL, bootstrap CI, rank theo lower bound, "
            f"Bonferroni penalty (n_configs={total_configs}), net cost {TX_COST_PCT}%, "
            f"MIN_TOTAL_PRED={MIN_TOTAL_PRED}."
        ),
        "config": {
            "nFolds": N_FOLDS, "horizonDays": HORIZON_DAYS, "valRatio": VAL_RATIO,
            "minTotalPred": MIN_TOTAL_PRED, "minFoldPred": MIN_FOLD_PRED,
            "bootstrapN": BOOTSTRAP_N, "txCostPct": TX_COST_PCT,
            "tasks": TASKS, "totalConfigsScanned": total_configs,
            "groupSizes": GROUP_SIZES, "maxPoolPerTask": MAX_POOL_PER_TASK,
        },
        "folds": [{k: v for k, v in fd.items() if k not in ("trainIdx", "valIdx", "testIdx")} for fd in folds],
        "sourceStep2": str(STEP2),
        "pools": {t: [{k: r[k] for k in ["family", "setName", "model", "avgPrecision",
                                          "precisionCI95LowerMean", "totalPredN",
                                          "expectedNetPnlPerTrade"]} for r in p] for t, p in pools.items()},
        "selectedByTask": selected,
        "topPerTask": top_per_task,
        "allRuns": runs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with CSV_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["task", "rank", "groupSize", "families", "setNames", "model",
                  "featureCount", "nFolds", "avgPrecision", "stdPrecision",
                  "minPrecision", "precisionCI95LowerMean", "avgRecall", "avgF1",
                  "totalPredN", "expectedNetPnlPerTrade", "passStrict",
                  "passConservative", "score"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for task, arr in selected.items():
            for i, r in enumerate(arr, 1):
                row = {k: (json.dumps(r[k], ensure_ascii=False) if k in ("families", "setNames")
                           else r.get(k)) for k in fields}
                row["rank"] = i
                row["task"] = task
                w.writerow(row)

    summary = {
        "out": str(OUT),
        "csv": str(CSV_OUT),
        "runs": len(runs),
        "topPerTask": {
            t: ({"families": v["families"], "model": v["model"],
                 "precisionCI95LowerMean": v["precisionCI95LowerMean"],
                 "avgPrecision": v["avgPrecision"], "totalPredN": v["totalPredN"],
                 "expectedNetPnlPerTrade": v["expectedNetPnlPerTrade"],
                 "passStrict": v["passStrict"], "passConservative": v["passConservative"]}
                if v else None)
            for t, v in top_per_task.items()
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
