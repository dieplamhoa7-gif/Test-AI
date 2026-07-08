"""
build_report.py — VN Macro Analysis Report Generator
=====================================================
Tạo báo cáo HTML động từ dữ liệu macro đã thu thập.
Bản này tập trung dữ liệu Việt Nam; giữ DXY vì là biến vĩ mô/tỷ giá ảnh hưởng USD/VND.

Usage:
  py -3 build_report.py
  py -3 build_report.py --date 2026-06-05
  py -3 build_report.py --out reports/vn_macro_report.html
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
ARCHIVE_CSV = DATA_DIR / "pinetree_archive" / "pinetree_macro_timeline.csv"
SBV_LATEST = DATA_DIR / "sbv_liquidity" / "latest.json"
HISTORY_DIR = DATA_DIR / "history"
MACRO_HUB_LATEST = DATA_DIR / "macro_data_hub" / "latest.json"
CURATED_GLOB = "curated_vietnam_macro_minimal*.json"


def _load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else default


def _latest_file(directory: Path, pattern: str):
    files = sorted(directory.glob(pattern), reverse=True) if directory.exists() else []
    return files[0] if files else None


def load_data(report_date: str | None = None):
    if ARCHIVE_CSV.exists():
        df = pd.read_csv(ARCHIVE_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["date"])
        if report_date:
            df = df[df["date"] <= pd.to_datetime(report_date)]
        wide = df.pivot_table(index="date", columns="indicator", values="value", aggfunc="first").sort_index()
    else:
        # Newer daily pipeline stores snapshots in data/history/*.json even when
        # the old pinetree_macro_timeline.csv is absent. Build a compact wide
        # frame from those snapshots so the report still renders from the DB.
        records = []
        for p in sorted(HISTORY_DIR.glob("????-??-??.json")):
            if report_date and p.stem > report_date:
                continue
            snap_i = _load_json(p)
            pt = snap_i.get("mergedPinetree") or snap_i.get("pinetree") or {}
            row = {"date": pd.to_datetime(snap_i.get("date") or p.stem, errors="coerce")}
            for key in ["interbankOvernight", "deposit12m", "govBond5y", "govBond10y", "usdVnd", "eurVnd", "cnyVnd", "vnindex", "hnx", "vn30", "upcom", "foreignNetBuyBn", "marketTurnoverBn"]:
                v = pt.get(key)
                row[key] = v.get("value") if isinstance(v, dict) else v
            records.append(row)
        wide = pd.DataFrame(records).dropna(subset=["date"]).set_index("date").sort_index() if records else pd.DataFrame()
    if "usdVnd" in wide.columns:
        wide["usdVnd"] = wide["usdVnd"].where(wide["usdVnd"] < 30000, np.nan)

    sbv = _load_json(SBV_LATEST)

    curated = {}
    curated_files = sorted(DATA_DIR.glob(CURATED_GLOB), reverse=True)
    if curated_files:
        curated = _load_json(curated_files[0])

    snap = {}
    hist_file = _latest_file(HISTORY_DIR, "*.json")
    if hist_file:
        snap = _load_json(hist_file)

    hub = _load_json(MACRO_HUB_LATEST)

    return wide, sbv, curated, snap, hub


def _ts(series: pd.Series, label: str):
    s = series.dropna() if series is not None else pd.Series(dtype=float)
    return {
        "label": label,
        "dates": [str(d.date()) for d in s.index],
        "values": [round(float(v), 4) if pd.notna(v) else None for v in s.values],
    }


def _col(wide: pd.DataFrame, name: str) -> pd.Series:
    return wide[name] if name in wide.columns else pd.Series(index=wide.index, dtype=float)


def prepare_charts(wide: pd.DataFrame, sbv: dict, snap: dict):
    monthly = pd.DataFrame(index=wide.resample("ME").mean(numeric_only=True).index)
    for name, agg in {
        "interbankOvernight": "mean",
        "usdVnd": "mean",
        "foreignNetBuyBn": "sum",
        "vnindex": "last",
        "govBond10y": "mean",
        "deposit12m": "mean",
        "marketTurnoverBn": "mean",
    }.items():
        if name in wide.columns:
            monthly[name] = wide[name].resample("ME").agg(agg)

    since22m = monthly[monthly.index >= "2022-01-01"]
    since23d = wide[wide.index >= "2023-01-01"]

    cd = {
        "vnindex_monthly": _ts(since22m.get("vnindex"), "VNINDEX"),
        "interbank_monthly": _ts(since22m.get("interbankOvernight"), "Liên NH ON avg tháng"),
        "deposit_monthly": _ts(since22m.get("deposit12m"), "Tiết kiệm 12T"),
        "usdvnd_monthly": _ts(since22m.get("usdVnd"), "USD/VND"),
        "foreign_monthly": _ts(since22m.get("foreignNetBuyBn"), "NĐTNN tổng tháng"),
        "bond10y_monthly": _ts(since22m.get("govBond10y"), "TPCP 10Y"),
        "turnover_monthly": _ts(since22m.get("marketTurnoverBn"), "Thanh khoản TB"),
        "interbank_daily": _ts(_col(since23d, "interbankOvernight"), "Liên NH ON"),
        "interbank_ma20": _ts(_col(since23d, "interbankOvernight").rolling(20).mean(), "Liên NH MA20"),
        "usdvnd_daily": _ts(_col(since23d, "usdVnd"), "USD/VND"),
        "foreign_daily": _ts(_col(since23d, "foreignNetBuyBn"), "NĐTNN mua ròng"),
    }

    # DXY latest only from history/global. We keep it as macro FX-pressure variable, not a stock market chart.
    dxy_val = (((snap.get("global") or {}).get("dxy") or {}).get("value"))
    cd["dxy_latest"] = dxy_val

    fnb = _col(wide, "foreignNetBuyBn").dropna()
    recent = wide.tail(40)
    fnb_r = _col(recent, "foreignNetBuyBn").dropna().tail(20)
    ib_r = _col(recent, "interbankOvernight").dropna().tail(20)
    cd["recent_fnb_bar"] = {
        "dates": [str(d.date()) for d in fnb_r.index],
        "values": [round(float(v), 2) for v in fnb_r.values],
        "colors": ["rgba(220,53,69,0.85)" if v < 0 else "rgba(40,167,69,0.85)" for v in fnb_r.values],
    }
    cd["recent_ib_line"] = {
        "dates": [str(d.date()) for d in ib_r.index],
        "values": [round(float(v), 2) for v in ib_r.values],
    }

    cumul_by_year = {}
    for y in sorted(set(fnb.index.year)):
        if y < 2022:
            continue
        s = fnb[fnb.index.year == y]
        if len(s):
            cs = s.cumsum()
            cumul_by_year[str(y)] = {
                "dates": [str(d.date()) for d in cs.index],
                "values": [round(float(v), 2) for v in cs.values],
            }
    cd["cumul_by_year"] = cumul_by_year

    sc = monthly[[c for c in ["interbankOvernight", "usdVnd", "foreignNetBuyBn"] if c in monthly.columns]].dropna()
    if {"interbankOvernight", "foreignNetBuyBn"}.issubset(sc.columns):
        cd["scatter_ib_fnb"] = {
            "x": [round(float(v), 2) for v in sc["interbankOvernight"].values],
            "y": [round(float(v), 0) for v in sc["foreignNetBuyBn"].values],
            "dates": [str(d.date()) for d in sc.index],
        }
    else:
        cd["scatter_ib_fnb"] = {"x": [], "y": [], "dates": []}

    if {"usdVnd", "foreignNetBuyBn"}.issubset(sc.columns):
        cd["scatter_fx_fnb"] = {
            "x": [round(float(v), 0) for v in sc["usdVnd"].values],
            "y": [round(float(v), 0) for v in sc["foreignNetBuyBn"].values],
            "dates": [str(d.date()) for d in sc.index],
        }
    else:
        cd["scatter_fx_fnb"] = {"x": [], "y": [], "dates": []}

    return cd


def _last(wide: pd.DataFrame, col: str):
    s = _col(wide, col).dropna()
    return None if s.empty else float(s.iloc[-1])


def _fmt(v, digits=2, suffix=""):
    if v is None or pd.isna(v):
        return "N/A"
    return f"{float(v):,.{digits}f}{suffix}"


def _fmt0(v, suffix=""):
    if v is None or pd.isna(v):
        return "N/A"
    return f"{float(v):,.0f}{suffix}"


def compute_stats(wide: pd.DataFrame, sbv: dict, snap: dict, hub: dict | None = None):
    today_year = date.today().year
    fnb = _col(wide, "foreignNetBuyBn").dropna()
    vn = _col(wide, "vnindex").dropna()
    ytd = vn[vn.index.year == today_year]

    omo = sbv.get("omo", {})
    summary = sbv.get("summary", {})
    net = summary.get("reverseRepoNetBn", omo.get("reverseRepoNetBn", 0)) or 0

    hub = hub or {}
    s = {
        "report_date": date.today().strftime("%d/%m/%Y"),
        "hub_date": hub.get("date") or "N/A",
        "hub_datasets": hub.get("datasets") or 0,
        "hub_indicators": hub.get("indicators") or 0,
        "vnindex": _fmt(vn.iloc[-1] if len(vn) else None, 2),
        "vnindex_ytd": "N/A" if ytd.empty else f"{(vn.iloc[-1] / ytd.iloc[0] - 1) * 100:+.1f}%",
        "interbank": _fmt(_last(wide, "interbankOvernight"), 2, "%"),
        "deposit12m": _fmt(_last(wide, "deposit12m"), 2, "%"),
        "bond10y": _fmt(_last(wide, "govBond10y"), 2, "%"),
        "usdvnd": _fmt0(_last(wide, "usdVnd")),
        "fnb_today": _fmt(_last(wide, "foreignNetBuyBn"), 2, " tỷ"),
        "fnb_ytd": _fmt0(fnb[fnb.index.year == today_year].sum() if len(fnb) else None, " tỷ"),
        "fnb_2025": _fmt0(fnb[fnb.index.year == 2025].sum() if len(fnb) else None, " tỷ"),
        "turnover": _fmt(_last(wide, "marketTurnoverBn"), 2, " tỷ"),
        "omo_net": f"{net:+,.0f} tỷ {'(bơm ròng)' if net > 0 else '(hút ròng)' if net < 0 else '(trung tính)'}",
        "omo_rate": _fmt(summary.get("omoRate", omo.get("omoRate")), 2, "%"),
        "omo_date": summary.get("date") or omo.get("date") or "N/A",
        "dxy": _fmt(((snap.get("global") or {}).get("dxy") or {}).get("value"), 2),
    }

    # Simple VN-only macro score.
    score = 50
    ib = _last(wide, "interbankOvernight")
    usd = _last(wide, "usdVnd")
    fnb_today = _last(wide, "foreignNetBuyBn")
    if ib is not None:
        score += 8 if ib < 5 else 0 if ib < 6 else -12
    if net:
        score += 5 if net > 0 else -6
    if usd is not None:
        score += -8 if usd > 26600 else 2 if usd < 26200 else 0
    if fnb_today is not None:
        score += 5 if fnb_today > 0 else -7 if fnb_today < -1000 else -2
    score = max(0, min(100, round(score)))
    phase = "Risk-on / thuận lợi" if score >= 65 else "Trung tính có chọn lọc" if score >= 50 else "Phòng thủ / thận trọng"
    s["macro_score"] = str(score)
    s["macro_phase"] = phase

    monthly = wide.resample("ME").agg({
        "interbankOvernight": "mean" if "interbankOvernight" in wide.columns else "first",
        "foreignNetBuyBn": "sum" if "foreignNetBuyBn" in wide.columns else "first",
    }).dropna()
    if len(monthly) >= 4 and "interbankOvernight" in monthly.columns and "foreignNetBuyBn" in monthly.columns:
        q75 = monthly["interbankOvernight"].quantile(0.75)
        q25 = monthly["interbankOvernight"].quantile(0.25)
        s["ib_hi_threshold"] = f"{q75:.1f}%"
        s["ib_lo_threshold"] = f"{q25:.1f}%"
        s["fnb_when_ib_hi"] = f"{monthly[monthly['interbankOvernight'] >= q75]['foreignNetBuyBn'].mean():,.0f} tỷ/tháng"
        s["fnb_when_ib_lo"] = f"{monthly[monthly['interbankOvernight'] <= q25]['foreignNetBuyBn'].mean():,.0f} tỷ/tháng"
    else:
        s.update({"ib_hi_threshold": "N/A", "ib_lo_threshold": "N/A", "fnb_when_ib_hi": "N/A", "fnb_when_ib_lo": "N/A"})

    return s


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>VN Macro Report — {report_date}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root { --bg:#0d1117; --surface:#161b22; --surface2:#1c2330; --border:#30363d; --text:#c9d1d9; --text2:#8b949e; --blue:#58a6ff; --green:#3fb950; --red:#f85149; --orange:#d29922; --cyan:#79c0ff; }
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:Segoe UI,system-ui,sans-serif;font-size:14px;line-height:1.55}.container{max-width:1380px;margin:0 auto;padding:24px 20px}.header{background:linear-gradient(135deg,#1a237e,#0d47a1,#01579b);border-radius:14px;padding:28px 32px;margin-bottom:22px}.header-title{font-size:28px;font-weight:800;color:#fff}.header-sub{color:rgba(255,255,255,.75);margin-top:4px}.header-meta{display:flex;gap:14px;flex-wrap:wrap;margin-top:18px}.stat{background:rgba(255,255,255,.1);border-radius:10px;padding:10px 14px;min-width:150px}.stat-l{font-size:11px;text-transform:uppercase;color:rgba(255,255,255,.65)}.stat-v{font-size:21px;font-weight:800;color:#fff}.badge{display:inline-block;margin-top:16px;padding:7px 16px;border-radius:20px;background:rgba(255,193,7,.14);border:1px solid rgba(255,193,7,.4);color:#ffc107;font-weight:700}.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:24px}.kpi-card,.chart-card,.insight{background:var(--surface);border:1px solid var(--border);border-radius:11px;padding:16px}.kpi-label{font-size:11px;color:var(--text2);text-transform:uppercase;letter-spacing:.5px}.kpi-val{font-size:22px;font-weight:800}.pos{color:var(--green)}.neg{color:var(--red)}.warn{color:var(--orange)}.neutral{color:var(--cyan)}.section{margin-bottom:30px}.section-title{font-size:19px;font-weight:800;color:var(--blue);border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:16px}.chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}.chart-title{font-size:12px;color:var(--text2);font-weight:700;text-transform:uppercase;margin-bottom:12px}.chart-wrap{height:270px;position:relative}.insight-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:12px;margin-top:14px}.insight{border-left:4px solid var(--blue);background:var(--surface2)}.insight.warn{border-left-color:var(--orange)}.insight.danger{border-left-color:var(--red)}.insight.pos{border-left-color:var(--green)}.insight-title{font-weight:800;margin-bottom:6px}.footer{text-align:center;color:var(--text2);font-size:12px;border-top:1px solid var(--border);padding:18px;margin-top:32px}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <div class="header-title">📊 Phân tích vĩ mô Việt Nam — Dynamic HTML</div>
  <div class="header-sub">Chính sách tiền tệ · Tỷ giá · Dòng tiền nước ngoài · VNINDEX · DXY</div>
  <div class="header-meta">
    <div class="stat"><div class="stat-l">VNINDEX</div><div class="stat-v">{vnindex}</div><div class="pos">{vnindex_ytd} YTD</div></div>
    <div class="stat"><div class="stat-l">Liên NH ON</div><div class="stat-v">{interbank}</div></div>
    <div class="stat"><div class="stat-l">NĐTNN hôm nay</div><div class="stat-v" style="color:#f85149">{fnb_today}</div></div>
    <div class="stat"><div class="stat-l">USD/VND</div><div class="stat-v">{usdvnd}</div></div>
    <div class="stat"><div class="stat-l">DXY</div><div class="stat-v">{dxy}</div></div>
    <div class="stat"><div class="stat-l">OMO</div><div class="stat-v">{omo_net}</div><div>@ {omo_rate}</div></div>
  </div>
  <div class="badge">Macro Regime: {macro_phase} | Score: {macro_score}/100 | Cập nhật {report_date}</div>
</div>

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-label">Tiết kiệm 12T</div><div class="kpi-val warn">{deposit12m}</div></div>
  <div class="kpi-card"><div class="kpi-label">TPCP 10Y</div><div class="kpi-val warn">{bond10y}</div></div>
  <div class="kpi-card"><div class="kpi-label">NĐTNN YTD</div><div class="kpi-val neg">{fnb_ytd}</div></div>
  <div class="kpi-card"><div class="kpi-label">NĐTNN 2025</div><div class="kpi-val neg">{fnb_2025}</div></div>
  <div class="kpi-card"><div class="kpi-label">Thanh khoản</div><div class="kpi-val neutral">{turnover}</div></div>
</div>

<div class="section">
  <div class="section-title">🏦 I. Chính sách tiền tệ & thanh khoản</div>
  <div class="chart-grid">
    <div class="chart-card"><div class="chart-title">Liên NH ON daily & MA20</div><div class="chart-wrap"><canvas id="chartIbDaily"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">Liên NH vs Huy động 12T vs TPCP 10Y</div><div class="chart-wrap"><canvas id="chartRates"></canvas></div></div>
  </div>
  <div class="insight-grid">
    <div class="insight warn"><div class="insight-title">Luận điểm</div>Liên NH ON và huy động 12T là cảm biến chính của thanh khoản. Khi liên NH duy trì cao, thị trường khó risk-on bền.</div>
    <div class="insight pos"><div class="insight-title">Tín hiệu NHNN</div>OMO hiện tại: {omo_net}, lãi suất {omo_rate}, ngày {omo_date}. Dương nghĩa là NHNN đang hỗ trợ thanh khoản.</div>
  </div>
</div>

<div class="section">
  <div class="section-title">💱 II. Tỷ giá & DXY</div>
  <div class="chart-grid">
    <div class="chart-card"><div class="chart-title">USD/VND daily</div><div class="chart-wrap"><canvas id="chartFx"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">Scatter USD/VND vs NĐTNN mua ròng tháng</div><div class="chart-wrap"><canvas id="chartScatterFx"></canvas></div></div>
  </div>
  <div class="insight-grid">
    <div class="insight"><div class="insight-title">DXY giữ lại vì sao?</div>DXY = {dxy}. Đây là biến vĩ mô/tỷ giá quan trọng ảnh hưởng trực tiếp USD/VND và dư địa chính sách của NHNN, không phải chỉ số chứng khoán quốc tế.</div>
    <div class="insight warn"><div class="insight-title">Ràng buộc chính sách</div>Nếu USD/VND và DXY tăng mạnh, NHNN khó bơm thanh khoản mạnh vì phải ưu tiên ổn định tỷ giá.</div>
  </div>
</div>

<div class="section">
  <div class="section-title">🌏 III. Dòng tiền nước ngoài</div>
  <div class="chart-grid">
    <div class="chart-card"><div class="chart-title">NĐTNN mua/bán ròng 20 phiên gần nhất</div><div class="chart-wrap"><canvas id="chartFnbRecent"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">NĐTNN lũy kế theo năm</div><div class="chart-wrap"><canvas id="chartFnbYearly"></canvas></div></div>
  </div>
  <div class="insight-grid">
    <div class="insight danger"><div class="insight-title">Cảnh báo</div>Khối ngoại hôm nay: {fnb_today}. Nếu bán ròng lớn kéo dài, đây là lực cản trực tiếp cho VNINDEX dù dòng tiền nội còn tốt.</div>
    <div class="insight"><div class="insight-title">Thống kê theo lãi suất</div>Khi liên NH cao ≥ {ib_hi_threshold}, NĐTNN bình quân {fnb_when_ib_hi}; khi liên NH thấp ≤ {ib_lo_threshold}, NĐTNN bình quân {fnb_when_ib_lo}.</div>
  </div>
</div>

<div class="section">
  <div class="section-title">📈 IV. VNINDEX & thanh khoản thị trường</div>
  <div class="chart-grid">
    <div class="chart-card"><div class="chart-title">VNINDEX monthly</div><div class="chart-wrap"><canvas id="chartVnindex"></canvas></div></div>
    <div class="chart-card"><div class="chart-title">Thanh khoản thị trường TB tháng</div><div class="chart-wrap"><canvas id="chartTurnover"></canvas></div></div>
  </div>
</div>

<div class="section">
  <div class="section-title">🗄️ V. Macro Data Hub</div>
  <div class="insight-grid">
    <div class="insight pos"><div class="insight-title">Database tổng hợp</div>Báo cáo đã nối với Macro Data Hub ngày {hub_date}: {hub_datasets} nhóm dữ liệu / {hub_indicators} chỉ tiêu. File nguồn: <code>FA/data/macro_data_hub/latest.json</code> và <code>latest.csv</code>.</div>
    <div class="insight warn"><div class="insight-title">SBV status</div>SBV OMO đã vào hub; liên ngân hàng chính thức PDF nếu bị chặn sẽ fallback sang Pinetree snapshot để không làm đứt database.</div>
  </div>
</div>

<div class="footer">Nguồn: Macro Data Hub · Pinetree archive · SBV liquidity · VCB FX · TradingEconomics visible · WorldBank · yfinance DXY · LH Investment macro pipeline. Không phải lời khuyên đầu tư cá nhân hóa.</div>
</div>

<script>
const CD = __CHART_DATA__;
Chart.defaults.color = '#8b949e'; Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
const ctx = id => document.getElementById(id).getContext('2d');
function line(id, seriesList){
  const labels = seriesList[0]?.dates || [];
  return new Chart(ctx(id), {
    type:'line',
    data:{
      labels,
      datasets: seriesList.map(s => ({
        label:s.label,
        data:s.values,
        borderColor:s.color,
        backgroundColor:s.color+'22',
        fill:false,
        borderWidth:2,
        tension:.25,
        pointRadius:0,
        pointHoverRadius:4
      }))
    },
    options:{
      responsive:true,
      maintainAspectRatio:false,
      interaction:{intersect:false,mode:'index'},
      plugins:{legend:{position:'top'}},
      scales:{
        x:{grid:{color:'rgba(255,255,255,0.06)'},ticks:{maxTicksLimit:12}},
        y:{grid:{color:'rgba(255,255,255,0.06)'}}
      }
    }
  });
}
function ts(d, color, label){ return {label, dates:d.dates || [], values:d.values || [], color}; }
line('chartIbDaily',[ts(CD.interbank_daily,'#d29922','Liên NH ON'),ts(CD.interbank_ma20,'#58a6ff','MA20')]);
line('chartRates',[ts(CD.interbank_monthly,'#d29922','Liên NH'),ts(CD.deposit_monthly,'#79c0ff','Huy động 12T'),ts(CD.bond10y_monthly,'#bc8cff','TPCP 10Y')]);
line('chartFx',[ts(CD.usdvnd_daily,'#3fb950','USD/VND')]);
new Chart(ctx('chartScatterFx'),{type:'scatter',data:{datasets:[{label:'USD/VND vs NĐTNN',data:CD.scatter_fx_fnb.x.map((x,i)=>({x:x,y:CD.scatter_fx_fnb.y[i]})),backgroundColor:'rgba(248,81,73,.65)'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'USD/VND'}},y:{title:{display:true,text:'NĐTNN tỷ'}}}}});
new Chart(ctx('chartFnbRecent'),{type:'bar',data:{labels:CD.recent_fnb_bar.dates,datasets:[{label:'NĐTNN mua/bán ròng',data:CD.recent_fnb_bar.values,backgroundColor:CD.recent_fnb_bar.colors}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{maxTicksLimit:10}},y:{grid:{color:'rgba(255,255,255,0.06)'}}}}});
const yearColors={'2022':'#3fb950','2023':'#58a6ff','2024':'#79c0ff','2025':'#f85149','2026':'#d29922'};
const yearly = Object.entries(CD.cumul_by_year).map(([y,d])=>({label:y,dates:d.dates.map(x=>x.slice(5)),values:d.values,color:yearColors[y]||'#58a6ff'}));
line('chartFnbYearly', yearly.length ? yearly : [{label:'N/A',dates:[],values:[],color:'#58a6ff'}]);
line('chartVnindex',[ts(CD.vnindex_monthly,'#58a6ff','VNINDEX')]);
line('chartTurnover',[ts(CD.turnover_monthly,'#79c0ff','Thanh khoản')]);
</script>
</body></html>"""


def build(report_date: str | None = None, output_path: str | None = None) -> str:
    wide, sbv, curated, snap, hub = load_data(report_date)
    cd = prepare_charts(wide, sbv, snap)
    stats = compute_stats(wide, sbv, snap, hub)
    html = HTML_TEMPLATE.replace("__CHART_DATA__", json.dumps(cd, ensure_ascii=False))
    for k, v in stats.items():
        html = html.replace("{" + k + "}", str(v))
    out = Path(output_path) if output_path else BASE / "reports" / f"vn_macro_report_{date.today():%Y%m%d}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="Report date YYYY-MM-DD")
    ap.add_argument("--out", help="Output HTML path")
    args = ap.parse_args()
    out = build(args.date, args.out)
    print(f"✓ Report saved: {out}")
