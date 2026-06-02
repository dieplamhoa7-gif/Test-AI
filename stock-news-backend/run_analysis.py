"""
run_analysis.py — Đầu vào tự động: 1 mã hoặc CẢ THƯ MỤC nhiều mã.

Dùng:
    # 1 file:
    python run_analysis.py data/MWG.csv
    python run_analysis.py data/MWG.csv MWG exports

    # cả thư mục (mỗi file *.csv/*.json là 1 mã, tên file = mã):
    python run_analysis.py data/ --batch
    python run_analysis.py data/ --batch exports

Output mỗi mã: <SYM>_analysis.json, <SYM>_summary.md, <SYM>_chart.html
Batch còn xuất thêm: _portfolio_overview.json (xếp hạng toàn bộ mã theo bias).
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

from pattern_engine.analyze import analyze
from pattern_engine.plot import make_chart


def analyze_one(path, symbol, out_dir, write_chart=True):
    r = analyze(str(path), symbol)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    # JSON (bỏ các khóa _internal)
    clean = {k: v for k, v in r.items() if not k.startswith("_")}
    (out_dir / f"{symbol}_analysis.json").write_text(
        json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown
    (out_dir / f"{symbol}_summary.md").write_text(_md(r), encoding="utf-8")

    # HTML chart
    if write_chart:
        make_chart(r["_df"], r["_ranked"], r["_fc"], r["_scenarios"],
                   symbol, str(out_dir / f"{symbol}_chart.html"))
    return r


def analyze_batch(folder, out_dir):
    folder = Path(folder)
    files = sorted([f for f in folder.iterdir()
                    if f.suffix.lower() in (".csv", ".json") and not f.name.startswith("_")])
    if not files:
        print(f"[!] Không tìm thấy file CSV/JSON trong {folder}")
        return
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    overview = []
    print(f"[batch] {len(files)} mã trong {folder}\n")
    for f in files:
        sym = f.stem.upper()
        try:
            r = analyze_one(f, sym, out_dir)
            s = r["summary"]
            prim = s["primarySignals"][0]["type"] if s["primarySignals"] else "—"
            overview.append({
                "symbol": sym, "timeframe": r["timeframe"], "bars": r["bars"],
                "lastClose": round(r["lastClose"], 2), "bias": s["bias"],
                "biasStrength": s["biasStrength"], "bullScore": s["bullScore"],
                "bearScore": s["bearScore"], "topSignal": prim,
                "nConflicts": len(s["conflicts"]),
                "fc20": r["forecast"]["points"][-1]["value"] if r["forecast"]["points"] else None,
            })
            print(f"  ✓ {sym:8} [{r['timeframe']:7}] {r['bars']:4} nến | "
                  f"bias={s['bias']:8}({s['biasStrength']:>4}%) | top: {prim}")
        except Exception as e:
            print(f"  ✗ {sym:8} LỖI: {str(e)[:60]}")
            overview.append({"symbol": sym, "error": str(e)[:120]})

    # xếp hạng: bullish mạnh nhất -> bearish mạnh nhất
    def sort_key(o):
        if "error" in o:
            return (-1, 0)
        sign = 1 if o["bias"] == "bullish" else (-1 if o["bias"] == "bearish" else 0)
        return (sign, o["biasStrength"] * sign if sign else 0)
    overview.sort(key=sort_key, reverse=True)

    port = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "count": len(files), "stocks": overview,
        "note": "Research-only, not financial advice",
    }
    (out_dir / "_portfolio_overview.json").write_text(
        json.dumps(port, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "_portfolio_overview.md").write_text(_md_port(port), encoding="utf-8")
    print(f"\n[done] Tổng quan danh mục: {out_dir}/_portfolio_overview.json (+ .md)")


def _md(r):
    s = r["summary"]; fc = r["forecast"]
    by_tier = {}
    for p in r["patterns"]:
        by_tier.setdefault(p.get("tier", 1), []).append(p)
    L = []; A = L.append
    A(f"# {r['symbol']} — Phân tích mẫu hình tự động\n")
    A(f"> Research-only, không phải khuyến nghị đầu tư.\n")
    A(f"- Khung: **{r['timeframe']}** (tự nhận diện) · {r['bars']} nến · {r['period'][0]} → {r['period'][1]}")
    A(f"- Giá cuối: **{r['lastClose']}**")
    A(f"- **Thiên hướng: `{s['bias'].upper()}`** (độ mạnh {s['biasStrength']}% · bull {s['bullScore']} vs bear {s['bearScore']})")
    if r["config"]["notes"]:
        A(f"- ⚠ {'; '.join(r['config']['notes'])}")
    A("")

    A(f"## Tín hiệu CHÍNH (engine tự xếp ưu tiên)")
    if s["primarySignals"]:
        for x in s["primarySignals"]:
            tgt = f" → mục tiêu {x['target']}" if x.get("target") else ""
            A(f"- **{x['type']}** [{x['direction']}, {x['confidence']}, điểm {x['composite']}, {x['status']}]{tgt}")
            if x["note"]:
                A(f"  - {x['note']}")
    else:
        A("- (không có tín hiệu đủ mạnh)")
    A("")

    if s["supportingSignals"]:
        A(f"## Tín hiệu hỗ trợ")
        for x in s["supportingSignals"]:
            A(f"- {x['type']} [{x['direction']}, {x['confidence']}, điểm {x['composite']}]")
        A("")

    if s["conflicts"]:
        A(f"## ⚠ Mâu thuẫn tín hiệu (engine tự phát hiện)")
        for c in s["conflicts"]:
            A(f"- **{c['bullish']}** (tăng) ⚔ **{c['bearish']}** (giảm) — {c['note']}")
        A("")

    A(f"## Vùng giá quan trọng")
    A(f"- Hỗ trợ: {s['keyLevels']['supports'] or '—'}")
    A(f"- Kháng cự: {s['keyLevels']['resistances'] or '—'}\n")

    A(f"## Dự báo {fc['horizonBars']} phiên (regression damped + ATR)")
    for h in (5, 10, fc["horizonBars"]):
        if h <= len(fc["points"]):
            pt = fc["points"][h - 1]
            A(f"- {h} phiên: {pt['value']} (vùng {pt['lower']}–{pt['upper']})")
    A(f"\n**Kịch bản:** " + " · ".join(
        f"{k}: {fc['scenarios'][k]['target']}" for k in ("bearish", "base", "bullish") if k in fc["scenarios"]))
    A("")

    A(f"## Thống kê nhận dạng")
    A(f"- Tổng pattern: {len(r['patterns'])}")
    for t in sorted(by_tier):
        tn = {1: "Tier 1 tin cậy", 2: "Tier 2 trung bình", 3: "Tier 3 experimental"}[t]
        A(f"- {tn}: {len(by_tier[t])}")
    A(f"\n---\n*Engine tự nhận khung, tự chỉnh tham số, tự phân loại & xếp ưu tiên. Không phải khuyến nghị đầu tư.*")
    return "\n".join(L)


def _md_port(port):
    L = []; A = L.append
    A(f"# Tổng quan danh mục — {port['count']} mã\n")
    A(f"> Research-only, không phải khuyến nghị đầu tư. Xếp từ tăng mạnh nhất → giảm mạnh nhất.\n")
    A(f"| Mã | Khung | Nến | Giá | Bias | Độ mạnh | Tín hiệu chính | Mâu thuẫn | DB cuối |")
    A(f"|---|---|--:|--:|---|--:|---|--:|--:|")
    for o in port["stocks"]:
        if "error" in o:
            A(f"| {o['symbol']} | LỖI | | | | | {o['error'][:30]} | | |"); continue
        A(f"| {o['symbol']} | {o['timeframe']} | {o['bars']} | {o['lastClose']} | "
          f"**{o['bias']}** | {o['biasStrength']}% | {o['topSignal']} | {o['nConflicts']} | {o['fc20']} |")
    A(f"\n*Engine tự động phân tích từng mã.*")
    return "\n".join(L)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Dùng: python run_analysis.py <file.csv | folder/> [symbol|--batch] [out_dir]")
        sys.exit(1)

    target = Path(args[0])
    if "--batch" in args or target.is_dir():
        out = next((a for a in args[1:] if a != "--batch"), "exports")
        analyze_batch(target, out)
    else:
        sym = args[1] if len(args) > 1 and not args[1].startswith("-") else target.stem.upper()
        out = args[2] if len(args) > 2 else "exports"
        r = analyze_one(target, sym, out)
        s = r["summary"]
        print(f"[done] {sym} [{r['timeframe']}] bias={s['bias']} ({s['biasStrength']}%) | "
              f"{len(r['patterns'])} pattern | primary: "
              f"{[x['type'] for x in s['primarySignals']]}")
        print(f"  -> {out}/{sym}_analysis.json | {sym}_summary.md | {sym}_chart.html")
