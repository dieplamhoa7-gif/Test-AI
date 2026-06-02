"""
run_mwg_pattern_forecast.py — Orchestrator.

Chạy: python run_mwg_pattern_forecast.py <csv_path> [out_dir]
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

from pattern_engine.core import (load_data, add_indicators, find_pivots, infer_timeframe,
                                 HAS_TALIB, HAS_SCIPY)
from pattern_engine.candlesticks import detect_candlesticks
from pattern_engine import chart_patterns as cp
from pattern_engine import experimental as ex
from pattern_engine.forecast import forecast, build_scenarios
from pattern_engine.plot import make_chart


def detect_all(df, pivots, include_experimental=True):
    patterns = []
    # candlestick
    patterns += detect_candlesticks(df, recent_bars=30)
    # tier 1-2 chart patterns
    patterns += cp.support_resistance(df, pivots)
    patterns += cp.trendlines(df, pivots)
    patterns += cp.double_patterns(df, pivots)
    patterns += cp.head_shoulders(df, pivots)
    patterns += cp.triangle_wedge_channel(df, pivots, lookback=40)
    patterns += cp.darvas_box(df, lookback=30)
    patterns += cp.cup_handle(df, pivots, lookback=60)
    patterns += cp.rounding(df, lookback=40)
    patterns += cp.flags(df)
    patterns += cp.spring_upthrust(df, pivots)
    patterns += cp.gaps(df)
    patterns += cp.vsa_signals(df)
    patterns += cp.indicator_patterns(df, pivots)
    # tier 3 experimental
    if include_experimental:
        patterns += ex.harmonic(df, pivots)
        patterns += ex.elliott(df, pivots)
        patterns += ex.smart_money(df, pivots)
        patterns += ex.wyckoff(df)
    return patterns


def summarize(patterns, df):
    close = df["close"].iloc[-1]
    active = [p for p in patterns if p.get("status") in ("active", "forming", "completed")]
    bull = sorted([p for p in active if p["direction"] == "bullish"], key=lambda x: -x["score"])
    bear = sorted([p for p in active if p["direction"] == "bearish"], key=lambda x: -x["score"])
    bull_w = sum(p["score"] for p in bull)
    bear_w = sum(p["score"] for p in bear)
    if bull_w > bear_w * 1.2:
        bias = "bullish"
    elif bear_w > bull_w * 1.2:
        bias = "bearish"
    else:
        bias = "neutral"
    supports = sorted({round(p["levels"]["support"], 2) for p in patterns
                       if p.get("levels", {}).get("support") and p["levels"]["support"] < close}, reverse=True)
    resist = sorted({round(p["levels"]["resistance"], 2) for p in patterns
                     if p.get("levels", {}).get("resistance") and p["levels"]["resistance"] > close})
    return {
        "bias": bias,
        "bullScore": round(bull_w, 1), "bearScore": round(bear_w, 1),
        "topBullishSignals": [{"type": p["type"], "score": p["score"], "conf": p["confidence"]} for p in bull[:5]],
        "topBearishSignals": [{"type": p["type"], "score": p["score"], "conf": p["confidence"]} for p in bear[:5]],
        "keyLevels": {"supports": supports[:4], "resistances": resist[:4]},
        "note": "Research-only, not financial advice",
    }


def main():
    csv = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("MWG.csv")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("exports")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(csv)
    tf = infer_timeframe(df)
    df = add_indicators(df)
    pivots = find_pivots(df, distance=3)

    print(f"[info] TA-Lib={HAS_TALIB} scipy={HAS_SCIPY} | timeframe={tf} | "
          f"bars={len(df)} | pivots={len(pivots)}")

    patterns = detect_all(df, pivots, include_experimental=True)
    fc = forecast(df, horizon=20, fit_window=min(60, len(df)))
    scenarios = build_scenarios(df, patterns, fc)
    summary = summarize(patterns, df)

    # ---- JSON ----
    out = {
        "symbol": "MWG", "timeframe": tf,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": csv.name, "bars": len(df),
        "lastDate": df["date"].iloc[-1].strftime("%Y-%m-%d"),
        "lastClose": round(float(df["close"].iloc[-1]), 2),
        "engineFlags": {"talib": HAS_TALIB, "scipy": HAS_SCIPY},
        "patterns": [{k: v for k, v in p.items() if not k.startswith("_")} for p in patterns],
        "forecast": {**fc, "scenarios": scenarios},
        "summary": summary,
    }
    out_json = out_dir / "MWG_patterns_forecast.json"
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- HTML chart ----
    out_html = out_dir / "MWG_patterns_forecast.html"
    make_chart(df, patterns, fc, scenarios, "MWG", str(out_html))

    # ---- Markdown ----
    out_md = out_dir / "MWG_pattern_forecast_summary.md"
    out_md.write_text(build_markdown(out, patterns, df), encoding="utf-8")

    print(f"[done] patterns={len(patterns)} | bias={summary['bias']}")
    print(f"  JSON: {out_json}")
    print(f"  HTML: {out_html}")
    print(f"  MD  : {out_md}")
    return out, patterns, df, fc, scenarios


def build_markdown(out, patterns, df):
    fc = out["forecast"]
    s = out["summary"]
    by_tier = {1: [], 2: [], 3: []}
    for p in patterns:
        by_tier.setdefault(p.get("tier", 1), []).append(p)
    lines = []
    A = lines.append
    A(f"# MWG — Pattern & Forecast Summary\n")
    A(f"> **Research-only, not financial advice.** Forecast mang tính xác suất/kịch bản.\n")
    A(f"- Nguồn: `{out['source']}` ({out['timeframe']}, {out['bars']} nến)")
    A(f"- Ngày cuối: **{out['lastDate']}** — Giá cuối: **{out['lastClose']}**")
    A(f"- Engine: TA-Lib={out['engineFlags']['talib']}, scipy={out['engineFlags']['scipy']}")
    A(f"- **Thiên hướng tổng hợp: `{s['bias'].upper()}`** (bull {s['bullScore']} vs bear {s['bearScore']})\n")

    A(f"## Tín hiệu nổi bật")
    A(f"**Tăng:** " + (", ".join(f"{x['type']}({x['score']},{x['conf']})" for x in s["topBullishSignals"]) or "—"))
    A(f"**Giảm:** " + (", ".join(f"{x['type']}({x['score']},{x['conf']})" for x in s["topBearishSignals"]) or "—") + "\n")

    A(f"## Vùng giá quan trọng")
    A(f"- Hỗ trợ: {s['keyLevels']['supports'] or '—'}")
    A(f"- Kháng cự: {s['keyLevels']['resistances'] or '—'}\n")

    A(f"## Dự báo (regression log-close + ATR band)")
    for h in (5, 10, 20):
        if h <= len(fc["points"]):
            pt = fc["points"][h-1]
            A(f"- **{h} phiên**: {pt['value']} (vùng {pt['lower']}–{pt['upper']}) → {pt['time']}")
    A(f"\n**Kịch bản:**")
    for k in ("bullish", "base", "bearish"):
        if k in fc["scenarios"]:
            sc = fc["scenarios"][k]
            A(f"- {k.title()}: **{sc['target']}** — {sc['reason']}")
    A("")

    A(f"## Mẫu hình phát hiện theo tầng tin cậy")
    tier_name = {1: "Tier 1 — tin cậy", 2: "Tier 2 — trung bình", 3: "Tier 3 — experimental (tham khảo)"}
    for t in (1, 2, 3):
        ps = by_tier.get(t, [])
        if not ps:
            continue
        A(f"\n### {tier_name[t]} ({len(ps)})")
        for p in sorted(ps, key=lambda x: -x["score"]):
            lv = p.get("levels", {})
            tgt = f" → target {lv['target']}" if lv.get("target") else ""
            A(f"- **{p['type']}** [{p['direction']}, {p['confidence']}, score {p['score']}, {p['status']}]"
              f"{tgt} — {p.get('evidence',{}).get('notes','')}")

    A(f"\n## Đường đã vẽ trên chart")
    line_types = {}
    for p in patterns:
        for ln in p.get("lines", []):
            line_types[ln["name"]] = line_types.get(ln["name"], 0) + 1
    for name, cnt in sorted(line_types.items(), key=lambda x: -x[1]):
        A(f"- {name}: {cnt}")

    A(f"\n## Chart")
    A(f"Mở file: `MWG_patterns_forecast.html`\n")
    A(f"---")
    A(f"*Disclaimer: Đây là công cụ nghiên cứu kỹ thuật tự động. Không mẫu hình nào đúng 100%. "
      f"Không phải khuyến nghị đầu tư.*")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
