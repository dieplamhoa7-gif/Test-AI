from __future__ import annotations

import json
from pathlib import Path
from app.macro_cycle import build

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / "local_preview"
LOCAL.mkdir(exist_ok=True)


def fmt(v, suffix=""):
    if v is None:
        return "-"
    if isinstance(v, (int, float)):
        return f"{v:,.2f}".rstrip("0").rstrip(".") + suffix
    return str(v)


def metric_card(title, obj, suffix=""):
    return f"""
    <div class="card">
      <span>{title}</span>
      <b>{fmt(obj.get('value'), suffix)}</b>
      <small>1D: {fmt(obj.get('change1d'))} · YTD: {fmt(obj.get('ytd'))}</small>
    </div>"""


def main():
    payload = build()
    data = payload["data"]
    comps = payload["components"]
    html = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>LHInvestment - Yếu tố vĩ mô LOCAL</title>
<style>
body{{margin:0;background:#07111f;color:#eaf1ff;font-family:Inter,Arial,sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:28px}}
.badge{{display:inline-flex;padding:8px 12px;border:1px solid #35506f;border-radius:999px;color:#9fb4d1;background:#0d1a2d}}
h1{{font-size:34px;margin:16px 0 6px}} .muted{{color:#9fb4d1}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0}}
.card{{border:1px solid #22395b;background:linear-gradient(180deg,#101d31,#0b1628);border-radius:18px;padding:16px;box-shadow:0 18px 40px rgba(0,0,0,.25)}}
.card span{{display:block;color:#9fb4d1;font-size:13px}} .card b{{display:block;font-size:26px;margin:8px 0}} .card small{{color:#9fb4d1}}
.score{{font-size:54px;font-weight:900;color:#6ee7b7}} .phase{{font-size:24px;font-weight:800;color:#7dd3fc}}
.comp{{display:flex;justify-content:space-between;gap:10px;border-top:1px solid #22395b;padding:12px 0}}
.bar{{height:8px;background:#16243a;border-radius:999px;overflow:hidden;margin-top:8px}} .fill{{height:100%;background:linear-gradient(90deg,#ef4444,#f59e0b,#22c55e)}}
.note{{padding:14px;border-radius:16px;border:1px dashed #35506f;color:#c9d7ee;background:#0d1a2d}}
</style>
</head>
<body><div class="wrap">
  <div class="badge">LOCAL TEST ONLY · chưa deploy live</div>
  <h1>Yếu tố vĩ mô & chu kỳ thị trường</h1>
  <p class="muted">Nguồn thử nghiệm: Pinetree Morning Brief · ngày {payload['date']} · chỉ dùng local để anh duyệt.</p>
  <div class="grid">
    <div class="card"><span>Macro Score</span><div class="score">{fmt(payload['macroScore'])}</div><small>/100</small></div>
    <div class="card"><span>Giai đoạn chu kỳ</span><div class="phase">{payload['phase']}</div><small>{payload['marketView']}</small></div>
  </div>
  <h2>Thanh khoản - Lãi suất - Tỷ giá</h2>
  <div class="grid">
    {metric_card('Lãi suất liên ngân hàng', data['interbankOvernight'], '%')}
    {metric_card('Lãi suất tiết kiệm 12T', data['deposit12m'], '%')}
    {metric_card('TPCP 5 năm', data['govBond5y'], '%')}
    {metric_card('TPCP 10 năm', data['govBond10y'], '%')}
    {metric_card('USD/VND', data['usdVnd'])}
    {metric_card('CNY/VND', data['cnyVnd'])}
  </div>
  <h2>Quốc tế & dòng tiền thị trường</h2>
  <div class="grid">
    {metric_card('S&P500', data['sp500'])}
    {metric_card('NASDAQ', data['nasdaq'])}
    {metric_card('VIX', data['vix'])}
    {metric_card('Brent', data['brent'])}
    {metric_card('VNINDEX', data['vnindex'])}
    {metric_card('Khối ngoại mua ròng (tỷ)', data['foreignNetBuyBn'])}
    {metric_card('Tổng GTGD (tỷ)', data['marketTurnoverBn'])}
  </div>
  <h2>Điểm thành phần</h2>
  <div class="card">
"""
    for k, c in comps.items():
        notes = "; ".join(c.get("notes") or ["Trung tính"])
        html += f"<div class='comp'><div><b>{k}</b><div class='muted'>{notes}</div><div class='bar'><div class='fill' style='width:{c['score']}%'></div></div></div><strong>{fmt(c['score'])}</strong></div>"
    html += f"""
  </div>
  <p class="note">Nhận định này là lớp macro filter. Khi đưa vào hệ thống thật, nó chỉ điều chỉnh tỷ trọng/risk regime, không thay thế PTKT R/S và chiến lược.</p>
  <p class="muted">Source: <a style="color:#7dd3fc" href="{data['url']}">{data['url']}</a></p>
</div></body></html>"""
    out = LOCAL / "macro.html"
    out.write_text(html, encoding="utf-8")
    print(out.resolve())
    print(json.dumps({"score": payload["macroScore"], "phase": payload["phase"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
