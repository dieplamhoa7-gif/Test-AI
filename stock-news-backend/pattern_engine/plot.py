"""
plot.py — Vẽ chart Plotly có NHÃN CHỮ rõ ràng cho từng mẫu hình.

- Mỗi pattern có nhãn chữ (tên + giá) đặt ngay tại vị trí trên chart.
- Marker hình học tại pivot: đáy=tam giác lên, đỉnh=tam giác xuống, vai=tròn, head=sao.
- Dedup pattern trùng. Lọc nhiễu. Vẽ box/zone cho darvas, FVG, order block.
"""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

C = {
    "bull": "#16a34a", "bear": "#dc2626", "neutral": "#6b7280",
    "support": "#16a34a", "resistance": "#dc2626", "neckline": "#f59e0b",
    "trendline_s": "#0891b2", "trendline_r": "#db2777",
    "forecast": "#2563eb", "band": "rgba(37,99,235,0.12)",
    "fvg_bull": "rgba(22,163,74,0.18)", "fvg_bear": "rgba(220,38,38,0.18)",
    "ob_bull": "rgba(16,185,129,0.22)", "ob_bear": "rgba(244,63,94,0.22)",
    "box": "rgba(168,85,247,0.10)",
}

LABEL = {
    "support-cluster": "Hỗ trợ", "resistance-cluster": "Kháng cự",
    "support-trendline": "Trendline hỗ trợ", "resistance-trendline": "Trendline kháng cự",
    "double-bottom": "2 Đáy", "double-top": "2 Đỉnh",
    "triple-bottom": "3 Đáy", "triple-top": "3 Đỉnh",
    "head-shoulders": "Vai-Đầu-Vai", "inverse-head-shoulders": "VĐV ngược",
    "ascending-triangle": "Tam giác tăng", "descending-triangle": "Tam giác giảm",
    "symmetrical-triangle": "Tam giác cân", "falling-wedge": "Nêm giảm",
    "rising-wedge": "Nêm tăng", "up-channel": "Kênh tăng", "down-channel": "Kênh giảm",
    "darvas-box": "Hộp Darvas", "cup-handle": "Cốc-Tay cầm",
    "rounding-bottom": "Đáy tròn", "rounding-top": "Đỉnh tròn",
    "bull-flag": "Cờ tăng", "bear-flag": "Cờ giảm",
    "spring-shakeout": "Spring", "upthrust-bull-trap": "Upthrust",
    "fvg-bullish": "FVG tăng", "fvg-bearish": "FVG giảm",
    "order-block-bullish": "OB tăng", "order-block-bearish": "OB giảm",
    "no-demand": "No Demand", "no-supply": "No Supply", "volume-climax": "Climax",
}


def _lab(t):
    return LABEL.get(t, t)


def _dedup(patterns):
    best = {}
    for p in patterns:
        key = (p["type"], p["direction"])
        if key not in best or p["score"] > best[key]["score"]:
            best[key] = p
    return list(best.values())


def make_chart(df, patterns, fc, scenarios, symbol="MWG", out_html=None):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.8, 0.2], vertical_spacing=0.04,
                        subplot_titles=(None, "Khối lượng"))

    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        name=symbol, increasing_line_color="#16a34a", decreasing_line_color="#dc2626",
        increasing_fillcolor="#16a34a", decreasing_fillcolor="#dc2626", line_width=1),
        row=1, col=1)

    for ma, col, nm in [("sma20", "#9333ea", "SMA20"), ("sma50", "#f97316", "SMA50")]:
        if ma in df:
            fig.add_trace(go.Scatter(x=df["date"], y=df[ma], name=nm,
                                     line=dict(width=1.2, color=col), opacity=0.65), row=1, col=1)

    vcol = ["#16a34a" if c >= o else "#dc2626" for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], name="Vol",
                         marker_color=vcol, opacity=0.45, showlegend=False), row=2, col=1)

    pats = _dedup([p for p in patterns if p["category"] != "candlestick"])
    last_date = df["date"].iloc[-1]
    ann = []

    def label(x, y, text, color, **kw):
        d = dict(x=x, y=y, xref="x", yref="y", text=text, showarrow=False,
                 font=dict(size=kw.pop("size", 10), color=color,
                           family=kw.pop("family", "Arial")),
                 bgcolor="rgba(255,255,255,0.78)", borderpad=1)
        d.update(kw); ann.append(d)

    # ---- S/R + trendline ----
    for p in pats:
        t = p["type"]
        if t in ("support-cluster", "resistance-cluster"):
            pts = p["lines"][0]["points"]; y = pts[0]["value"]
            col = C["support"] if "support" in t else C["resistance"]
            fig.add_trace(go.Scatter(x=[pd.to_datetime(pts[0]["time"]), last_date], y=[y, y],
                mode="lines", line=dict(color=col, width=1.5, dash="dash"), opacity=0.7,
                name=f"{_lab(t)} {y}", hovertemplate=f"{_lab(t)}: {y}<extra></extra>"), row=1, col=1)
            label(last_date, y, f"{_lab(t)} {y}", col, xanchor="left", xshift=6)
        elif t in ("support-trendline", "resistance-trendline"):
            pts = p["lines"][0]["points"]
            col = C["trendline_s"] if "support" in t else C["trendline_r"]
            xs = [pd.to_datetime(q["time"]) for q in pts]; ys = [q["value"] for q in pts]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=col, width=2),
                name=_lab(t), hovertemplate=f"{_lab(t)}<extra></extra>"), row=1, col=1)
            label(xs[-1], ys[-1], _lab(t), col, xanchor="right",
                  yshift=12 if "resistance" in t else -12, family="Arial Black")

    # ---- double/triple + H&S ----
    for p in pats:
        t = p["type"]
        if t.startswith(("double", "triple")):
            col = C["bull"] if p["direction"] == "bullish" else C["bear"]
            sym = "triangle-up" if p["direction"] == "bullish" else "triangle-down"
            for ln in p["lines"]:
                if ln["type"] == "point":
                    q = ln["points"][0]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"])], y=[q["value"]],
                        mode="markers", marker=dict(symbol=sym, size=13, color=col,
                        line=dict(width=1.5, color="white")), showlegend=False,
                        hovertemplate=f"{_lab(t)}: {q['value']}<extra></extra>"), row=1, col=1)
                elif ln["name"] == "neckline":
                    pts = ln["points"]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"]) for q in pts],
                        y=[q["value"] for q in pts], mode="lines",
                        line=dict(color=C["neckline"], width=2, dash="dot"),
                        name=f"Neckline {_lab(t)}",
                        hovertemplate=f"Neckline: {pts[0]['value']}<extra></extra>"), row=1, col=1)
            fp = p["lines"][0]["points"][0]; lv = p.get("levels", {})
            tgt = f" → {lv['target']}" if lv.get("target") else ""
            ann.append(dict(x=pd.to_datetime(fp["time"]), y=fp["value"], xref="x", yref="y",
                text=f"{_lab(t)}{tgt}", showarrow=True, arrowhead=2, arrowsize=0.9,
                arrowcolor=col, ax=0, ay=32, font=dict(size=11, color=col, family="Arial Black"),
                bgcolor="rgba(255,255,255,0.88)", bordercolor=col, borderwidth=1, borderpad=2))
        elif t in ("head-shoulders", "inverse-head-shoulders"):
            col = C["bear"] if "inverse" not in t else C["bull"]
            mk = {"left_shoulder": ("circle", "Vai T"), "head": ("star", "Đầu"),
                  "right_shoulder": ("circle", "Vai P")}
            for ln in p["lines"]:
                if ln["type"] == "point" and ln["name"] in mk:
                    q = ln["points"][0]; symb, lb = mk[ln["name"]]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"])], y=[q["value"]],
                        mode="markers+text", marker=dict(symbol=symb,
                        size=15 if symb == "star" else 12, color=col,
                        line=dict(width=1.5, color="white")), text=[lb],
                        textposition="top center", textfont=dict(size=9, color=col),
                        showlegend=False, hovertemplate=f"{lb}: {q['value']}<extra></extra>"), row=1, col=1)
                elif ln["name"] == "neckline":
                    pts = ln["points"]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"]) for q in pts],
                        y=[q["value"] for q in pts], mode="lines",
                        line=dict(color=C["neckline"], width=2, dash="dot"),
                        name=f"Neckline {_lab(t)}"), row=1, col=1)
            hp = next((ln["points"][0] for ln in p["lines"] if ln["name"] == "head"), None)
            if hp:
                ann.append(dict(x=pd.to_datetime(hp["time"]), y=hp["value"], xref="x", yref="y",
                    text=_lab(t), showarrow=True, arrowhead=2, arrowcolor=col, ax=0, ay=-30,
                    font=dict(size=11, color=col, family="Arial Black"),
                    bgcolor="rgba(255,255,255,0.88)", bordercolor=col, borderwidth=1, borderpad=2))

    # ---- triangle/wedge/channel ----
    for p in pats:
        t = p["type"]
        if "triangle" in t or "wedge" in t or "channel" in t:
            col = C["bull"] if p["direction"] == "bullish" else (C["bear"] if p["direction"] == "bearish" else C["neutral"])
            for ln in p["lines"]:
                pts = ln["points"]
                fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"]) for q in pts],
                    y=[q["value"] for q in pts], mode="lines", line=dict(color=col, width=1.8),
                    showlegend=False, hovertemplate=f"{_lab(t)}<extra></extra>"), row=1, col=1)
            up = p["lines"][0]["points"][-1]
            label(pd.to_datetime(up["time"]), up["value"], _lab(t), col,
                  xanchor="right", family="Arial Black")

    # ---- darvas box ----
    for p in pats:
        if p["type"] == "darvas-box":
            lv = p["levels"]; x0 = p["lines"][0]["points"][0]["time"]
            fig.add_shape(type="rect", x0=pd.to_datetime(x0), x1=last_date,
                y0=lv["support"], y1=lv["resistance"], fillcolor=C["box"],
                line=dict(color="#a855f7", width=1.5, dash="dash"), row=1, col=1)
            label(pd.to_datetime(x0), lv["resistance"],
                  f"{_lab('darvas-box')} {lv['support']}-{lv['resistance']}", "#7c3aed",
                  xanchor="left", yshift=10, family="Arial Black")

    # ---- cup&handle ----
    for p in pats:
        if p["type"] == "cup-handle":
            col = C["bull"]
            for ln in p["lines"]:
                if ln["type"] == "point":
                    q = ln["points"][0]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"])], y=[q["value"]],
                        mode="markers+text", marker=dict(symbol="diamond", size=11, color=col),
                        text=[ln["name"]], textposition="top center",
                        textfont=dict(size=8, color=col), showlegend=False), row=1, col=1)
                elif ln["name"] == "neckline":
                    pts = ln["points"]
                    fig.add_trace(go.Scatter(x=[pd.to_datetime(q["time"]) for q in pts],
                        y=[q["value"] for q in pts], mode="lines",
                        line=dict(color=col, width=1.8, dash="dot"), showlegend=False), row=1, col=1)

    # ---- FVG / order block zones ----
    for p in pats:
        t = p["type"]
        if t.startswith("fvg"):
            lv = p["levels"]; d0 = pd.to_datetime(p["time"])
            fig.add_shape(type="rect", x0=d0, x1=last_date, y0=lv.get("gapLow", 0),
                y1=lv.get("gapHigh", 0), fillcolor=C["fvg_bull"] if "bull" in t else C["fvg_bear"],
                line_width=0, row=1, col=1)
        elif t.startswith("order-block"):
            lv = p["levels"]; d0 = pd.to_datetime(p["time"])
            fig.add_shape(type="rect", x0=d0, x1=last_date, y0=lv.get("obLow", 0),
                y1=lv.get("obHigh", 0), fillcolor=C["ob_bull"] if "bull" in t else C["ob_bear"],
                line=dict(width=0.5, color="#94a3b8"), row=1, col=1)

    # ---- spring/upthrust markers ----
    for p in pats:
        t = p["type"]
        if t in ("spring-shakeout", "upthrust-bull-trap"):
            col = C["bull"] if "spring" in t else C["bear"]
            symb = "arrow-up" if "spring" in t else "arrow-down"
            fig.add_trace(go.Scatter(x=[pd.to_datetime(p["time"])], y=[p["price"]],
                mode="markers+text", marker=dict(symbol=symb, size=16, color=col),
                text=[_lab(t)], textposition="bottom center" if "spring" in t else "top center",
                textfont=dict(size=10, color=col, family="Arial Black"), showlegend=False), row=1, col=1)

    # ---- forecast + band ----
    fdates = [pd.to_datetime(pt["time"]) for pt in fc["points"]]
    fvals = [pt["value"] for pt in fc["points"]]
    upper = [pt["upper"] for pt in fc["points"]]
    lower = [pt["lower"] for pt in fc["points"]]
    last_c = float(df["close"].iloc[-1])

    fig.add_trace(go.Scatter(x=[last_date] + fdates, y=[last_c] + upper, mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=[last_date] + fdates, y=[last_c] + lower, mode="lines",
        line=dict(width=0), fill="tonexty", fillcolor=C["band"], name="Dải tin cậy",
        hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=[last_date] + fdates, y=[last_c] + fvals, mode="lines+markers",
        name=f"Dự báo {fc['horizonBars']} phiên", line=dict(color=C["forecast"], width=2.5, dash="dot"),
        marker=dict(size=4), hovertemplate="Dự báo: %{y}<extra></extra>"), row=1, col=1)
    label(fdates[-1], fvals[-1], f"Dự báo {fvals[-1]}", C["forecast"],
          xanchor="left", xshift=4, family="Arial Black")

    for key, col, nm in [("bullish", C["bull"], "KB tăng"), ("base", C["forecast"], "KB cơ sở"),
                         ("bearish", C["bear"], "KB giảm")]:
        if key in scenarios:
            y = scenarios[key]["target"]
            fig.add_hline(y=y, line=dict(color=col, width=1, dash="dot"), opacity=0.5, row=1, col=1)
            label(fdates[-1], y, f"{nm}: {y}", col, xanchor="left", xshift=4, size=9)

    fig.update_layout(
        template="plotly_white", height=860, hovermode="x unified",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=10)),
        title=dict(text=f"<b>{symbol}</b> — Mẫu hình kỹ thuật & Dự báo giá  "
                        f"<span style='font-size:11px;color:#888'>(research-only, không phải khuyến nghị đầu tư)</span>",
                   font=dict(size=16), x=0.01),
        annotations=ann, margin=dict(l=50, r=150, t=110, b=30))
    fig.update_yaxes(title_text="Giá (nghìn đ)", row=1, col=1)
    fig.update_yaxes(title_text="KL", row=2, col=1)
    fig.update_xaxes(range=[df["date"].iloc[0], fdates[-1] + pd.Timedelta(days=40)], row=1, col=1)

    if out_html:
        fig.write_html(out_html, include_plotlyjs="cdn")
    return fig
