from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_HTML = Path('reports/MIT_18_642_Training_Guide_LH_Investment_DESIGN.html')
OUT_PDF = Path('reports/MIT_18_642_Training_Guide_LH_Investment_DESIGN.pdf')
OUT_HTML.parent.mkdir(exist_ok=True)

modules = [
('01','GIỚI THIỆU & THỊ TRƯỜNG','Course overview, asset classes, risk/return, arbitrage','Lecture 1 Parts I–III','#2563eb'),
('02','BOND MATH','Discounting, yield, duration, convexity, yield curve','Lecture 1 Part III','#7c3aed'),
('03','LINEAR ALGEBRA','Vectors, matrices, covariance, eigenvectors, feature matrix','Lecture 2 + 4','#0891b2'),
('04','PROBABILITY & STOCHASTIC PROCESS','Conditional probability, expectation, random path, no look-ahead','Lecture 4 + 5 + 6','#059669'),
('05','REGRESSION & PCA','OLS, residuals, factor models, PCA, indicator redundancy','Lecture 6 + 8 + 9 + 11','#dc2626'),
('06','RATES PRODUCTS','Yield curve, forwards, swaps, hedging, rate regimes','Lecture 7','#ca8a04'),
('07','TIME SERIES','AR/MA, stationarity, regime shifts, forecast horizons','Lecture 12','#9333ea'),
('08','PORTFOLIO & RISK','Markowitz, covariance, concentration, counterparty risk','Lecture 10 + 13','#0f766e'),
('09','VOLATILITY MODELING','ATR, realized vol, clustering, GARCH intuition, sizing','Lecture 19','#ea580c'),
('10','BLACK-SCHOLES & CW','Options, Greeks, time decay, moneyness, break-even','Lecture 21','#be123c'),
('11','AI / ML / EVENT MARKETS','ML workflow, calibration, event probability, overfit control','Lecture 18 + 20 + 23','#4f46e5'),
('12','STOCHASTIC CALCULUS & SDE','Brownian motion, Ito, SDE, scenario/path risk','Lecture 14 + 24 + 25','#0f172a'),
]

cards = ''.join([f'''
<div class="module-card" style="--accent:{c}">
  <div class="num">{n}</div>
  <div><h3>{t}</h3><p>{d}</p><span>{lec}</span></div>
</div>''' for n,t,d,lec,c in modules])

sections = []
for n,t,d,lec,c in modules:
    concepts = {
        '01':[('Asset','Claim on future cash flow/state'),('Return vs Risk','Lợi nhuận luôn đi cùng rủi ro'),('Arbitrage','Neo logic định giá'),('Liquidity','Khả năng vào/ra vị thế')],
        '02':[('PV','CF/(1+r)^t'),('Duration','Độ nhạy với yield'),('Convexity','Sửa duration khi yield đổi lớn'),('Yield Curve','Tín hiệu macro/rate')],
        '03':[('Vector','1 mã tại 1 ngày'),('Matrix','VN100 × ngày × feature'),('Covariance','Biến động chung'),('Eigen/PCA','Factor chính')],
        '04':[('Probability','Xác suất thay vì chắc chắn'),('Expectation','Kỳ vọng'),('Variance','Rủi ro phân tán'),('Process','Đường đi theo thời gian')],
        '05':[('OLS','Kiểm định feature'),('Residual','Phần chưa giải thích'),('Multicollinearity','Indicator trùng'),('PCA','Giảm nhiễu/factor')],
        '06':[('Forward Rate','Lãi suất hàm ý'),('Swap','Trao đổi dòng tiền'),('Curve','Cấu trúc kỳ hạn'),('Hedging','Giảm risk')],
        '07':[('AR/MA','Phụ thuộc quá khứ'),('Stationarity','Ổn định thống kê'),('Regime Shift','Đổi luật chơi'),('Horizon','5/10/20/60d')],
        '08':[('Expected Return','Vector lợi nhuận'),('Covariance','Risk danh mục'),('Efficient Frontier','Return/risk tối ưu'),('Concentration','Tập trung ngành/factor')],
        '09':[('ATR%','Biên dao động'),('Realized Vol','Vol thực tế'),('Clustering','Vol cao kéo dài'),('Sizing','Điều chỉnh tỷ trọng')],
        '10':[('S/K/T/r/σ','Input option'),('Delta','Nhạy với underlying'),('Theta','Time decay'),('Break-even','Ngưỡng hòa vốn')],
        '11':[('Label','Mục tiêu train'),('OOS','Ngoài mẫu'),('Calibration','Xác suất đáng tin'),('Overfit','Khớp quá khứ giả')],
        '12':[('Brownian','Nhiễu liên tục'),('Ito','Toán cho process'),('SDE','dS=μSdt+σSdW'),('Scenario','Base/bull/bear/gap')],
    }[n]
    rows=''.join([f'<tr><td>{a}</td><td>{b}</td></tr>' for a,b in concepts])
    app = {
        '01':'Output recommendation phải có horizon, why, wrongIf, risk và probability — không chỉ BUY/WATCH.',
        '02':'Thêm rateSensitiveScore, valuationDurationRisk, macroRateRegime; đặc biệt quan trọng với cổ phiếu growth và CW.',
        '03':'Chuẩn hóa research_feature_matrix_vn100.json: mỗi stock-date là một vector feature sạch.',
        '04':'Tạo pHitTarget20d, pLossMoreThan5Pct20d; validation chronological, không random shuffle.',
        '05':'Chạy correlation/top-bottom quintile/OOS; gom indicator trùng bằng PCA/correlation.',
        '06':'Dùng rate/macro regime làm filter cho sector ngân hàng, BĐS, growth, leverage cao.',
        '07':'Mọi score phải gắn horizon 5d/10d/20d/60d, tránh trộn timeframe mơ hồ.',
        '08':'Thêm positionSizeHint, sectorCapWarning, correlationWarning và portfolio risk layer.',
        '09':'Vol cao dùng để sizing/stop/risk; không đơn giản mua/bỏ theo volatility.',
        '10':'CW score cần underlying signal + maturity + moneyness + break-even + spread + liquidity + theta.',
        '11':'ML đầu tiên nên logistic/GBM nhẹ, calibrated probability, explainable, so với baseline.',
        '12':'Dùng scenario/path-risk: max drawdown, time underwater, gap risk, bull/base/bear case.',
    }[n]
    sections.append(f'''
<section class="page module-page" style="--accent:{c}">
  <div class="stripe"></div>
  <div class="module-head"><div class="big-num">{n}</div><div><div class="kicker">{lec}</div><h2>{t}</h2><p>{d}</p></div></div>
  <div class="two-col">
    <div class="panel"><h4>Bài học gốc</h4><p>{d}. MIT dùng phần này để xây nền toán/tài chính cho quyết định dưới bất định. Điểm quan trọng là hiểu assumption, xác suất, thời gian và risk thay vì tìm câu trả lời chắc chắn.</p></div>
    <div class="panel accent"><h4>Áp dụng vào LH Investment</h4><p>{app}</p></div>
  </div>
  <table><thead><tr><th>Khái niệm</th><th>Ý nghĩa</th></tr></thead><tbody>{rows}</tbody></table>
  <div class="callout"><b>Checklist training:</b> feature phải đo được · có label tương lai riêng · kiểm OOS · báo EV/avgWin/avgLoss/sampleSize · giải thích why/wrongIf.</div>
</section>''')

html = f'''<!doctype html><html><head><meta charset="utf-8"><title>MIT 18.642 Training Guide LH Investment</title>
<style>
@page {{ size:A4; margin:0; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family: Arial, Segoe UI, sans-serif; color:#111827; background:#fff; }}
.page {{ width:210mm; min-height:297mm; padding:18mm 16mm; position:relative; overflow:hidden; page-break-after:always; }}
.cover {{ background: radial-gradient(circle at 15% 15%, #3b82f6 0, transparent 25%), linear-gradient(135deg,#07152f 0%,#0f2d5c 45%,#111827 100%); color:white; display:flex; flex-direction:column; justify-content:center; }}
.badge {{ display:inline-block; border:1px solid rgba(255,255,255,.35); border-radius:999px; padding:7px 12px; font-size:12px; letter-spacing:.08em; width:max-content; }}
.cover h1 {{ font-size:44px; line-height:1.05; margin:24px 0 10px; letter-spacing:-1.5px; }}
.cover h2 {{ font-size:22px; font-weight:500; opacity:.9; margin:0 0 28px; }}
.cover .meta {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:24px; }}
.meta div {{ background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.18); padding:14px; border-radius:16px; backdrop-filter: blur(6px); }}
.meta b {{ display:block; color:#93c5fd; margin-bottom:5px; }}
.footer {{ position:absolute; bottom:12mm; left:16mm; right:16mm; font-size:11px; opacity:.65; display:flex; justify-content:space-between; }}
.toc h2, .summary h2 {{ font-size:30px; color:#0f172a; margin:0 0 12px; }}
.subtitle {{ color:#64748b; font-size:14px; margin-bottom:18px; }}
.module-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:9px; }}
.module-card {{ border:1px solid #e5e7eb; border-left:6px solid var(--accent); border-radius:15px; padding:11px; display:flex; gap:10px; background:linear-gradient(180deg,#fff,#f8fafc); min-height:82px; }}
.num {{ width:34px; height:34px; border-radius:11px; background:var(--accent); color:white; font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
.module-card h3 {{ margin:0 0 3px; font-size:12.5px; color:#0f172a; }}
.module-card p {{ margin:0; font-size:10.5px; color:#475569; line-height:1.35; }}
.module-card span {{ display:block; margin-top:4px; color:var(--accent); font-size:10px; font-weight:700; }}
.summary .hero {{ background:#f1f5f9; border-radius:22px; padding:20px; border:1px solid #e2e8f0; }}
.summary h3 {{ font-size:20px; margin:0 0 10px; color:#0f172a; }}
.pill-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
.pill {{ background:white; border:1px solid #cbd5e1; border-radius:999px; padding:8px 11px; font-size:12px; font-weight:700; color:#1e293b; }}
.module-page {{ padding-top:14mm; }}
.stripe {{ position:absolute; left:0; top:0; bottom:0; width:8mm; background:var(--accent); }}
.module-head {{ display:flex; gap:18px; align-items:center; border-bottom:2px solid #e5e7eb; padding-bottom:14px; margin-bottom:16px; }}
.big-num {{ font-size:54px; font-weight:900; color:var(--accent); line-height:1; }}
.kicker {{ color:var(--accent); font-size:12px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }}
.module-head h2 {{ font-size:27px; margin:4px 0 5px; color:#0f172a; letter-spacing:-.6px; }}
.module-head p {{ margin:0; color:#475569; font-size:13px; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:14px 0; }}
.panel {{ border:1px solid #e5e7eb; border-radius:18px; padding:14px; background:#fff; box-shadow:0 8px 22px rgba(15,23,42,.06); }}
.panel.accent {{ background:linear-gradient(135deg, color-mix(in srgb, var(--accent) 12%, white), #fff); border-color:color-mix(in srgb, var(--accent) 25%, white); }}
.panel h4 {{ margin:0 0 7px; color:#0f172a; font-size:15px; }}
.panel p {{ margin:0; font-size:12px; line-height:1.55; color:#334155; }}
table {{ width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border-radius:16px; border:1px solid #e5e7eb; margin-top:12px; }}
th {{ background:#0f172a; color:white; text-align:left; font-size:12px; padding:9px; }}
td {{ padding:9px; border-top:1px solid #e5e7eb; font-size:12px; vertical-align:top; }}
td:first-child {{ font-weight:800; color:var(--accent); width:32%; }}
.callout {{ margin-top:14px; border-radius:16px; padding:13px 15px; background:#fffbeb; border:1px solid #fde68a; color:#78350f; font-size:12.5px; line-height:1.45; }}
.roadmap {{ background:#0f172a; color:white; }}
.roadmap h2 {{ font-size:32px; margin:0 0 8px; }}
.steps {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px; }}
.step {{ background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.15); border-radius:18px; padding:13px; }}
.step b {{ color:#93c5fd; }}
.step p {{ margin:6px 0 0; color:#dbeafe; font-size:12px; line-height:1.45; }}
.codebox {{ margin-top:16px; background:#020617; border:1px solid #334155; border-radius:18px; padding:14px; font-family:Consolas,monospace; font-size:11px; line-height:1.45; color:#bbf7d0; white-space:pre-wrap; }}
</style></head><body>
<section class="page cover">
  <div class="badge">MIT 18.642 · FALL 2024 · 22 PUBLIC TRANSCRIPTS</div>
  <h1>Training Guide<br/>for LH Investment</h1>
  <h2>Toán tài chính ứng dụng cho nhà đầu tư chứng khoán, model cổ phiếu và CW</h2>
  <div class="meta"><div><b>Mục tiêu</b>Biến bài học MIT thành feature, backtest, risk rule, portfolio logic và ML roadmap.</div><div><b>Nguyên tắc</b>No look-ahead · Expected Value · OOS · Regime-aware · Risk-first.</div><div><b>Nguồn</b>MIT 18.642 public YouTube transcript set, 22/22 videos captured.</div><div><b>Người dùng</b>Chuẩn bị riêng cho Hòa Đại ka và hệ thống LH Investment.</div></div>
  <div class="footer"><span>Prepared by Tiểu đệ</span><span>Premium Design Edition</span></div>
</section>
<section class="page toc"><h2>Mục lục dạng module</h2><div class="subtitle">Học bài gốc trước, sau đó mới áp dụng vào hệ thống LH Investment.</div><div class="module-grid">{cards}</div><div class="footer"><span>MIT 18.642 Training Guide</span><span>Trang 2</span></div></section>
<section class="page summary"><h2>Executive Summary</h2><div class="hero"><h3>Không tìm “indicator thần kỳ”. Xây hệ thống xác suất.</h3><p>MIT 18.642 dạy cách nhìn tài chính như một bài toán về dữ liệu, dòng tiền, xác suất, thời gian, volatility, danh mục và rủi ro. Với LH Investment, điều này có nghĩa là mọi tín hiệu phải có horizon, xác suất, expected value, drawdown, regime và lời giải thích sai khi nào.</p><div class="pill-row"><span class="pill">Feature Matrix</span><span class="pill">No Look-Ahead</span><span class="pill">Walk-forward OOS</span><span class="pill">Expected Value</span><span class="pill">Portfolio Risk</span><span class="pill">CW Time Decay</span><span class="pill">ML Calibration</span></div></div><div class="footer"><span>Core thesis</span><span>Trang 3</span></div></section>
{''.join(sections)}
<section class="page roadmap"><h2>Roadmap training model LH Investment</h2><p>Không nhảy thẳng vào ML. Training đúng bắt đầu từ dữ liệu sạch, feature matrix, leakage audit, backtest EV, rồi mới đến model xác suất.</p><div class="steps">
<div class="step"><b>1. Data & Feature Matrix</b><p>OHLCV, market/sector, rolling support/resistance, pattern, volatility, labels 5/10/20/60d.</p></div>
<div class="step"><b>2. Leakage Audit</b><p>Feature tại ngày t chỉ dùng dữ liệu <= t. Future return chỉ là label.</p></div>
<div class="step"><b>3. Feature Report</b><p>Correlation, quintile spread, hit target, drawdown, regime summary.</p></div>
<div class="step"><b>4. Strategy Backtest</b><p>Near support + room to resistance + volatility filter + market regime filter.</p></div>
<div class="step"><b>5. Expected Value</b><p>precision, avgWin, avgLoss, EV, profitFactor, sampleSize.</p></div>
<div class="step"><b>6. ML nhẹ</b><p>Logistic/GBM, probability calibration, explainability, compare baseline.</p></div>
</div><div class="codebox">recommendation = feature matrix + probability + expected value + regime + risk-adjusted position sizing + explanation</div><div class="footer"><span>LH Investment Roadmap</span><span>Final</span></div></section>
</body></html>'''

OUT_HTML.write_text(html, encoding='utf-8')
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1240, "height": 1754})
    page.goto(OUT_HTML.resolve().as_uri(), wait_until='networkidle')
    page.pdf(path=str(OUT_PDF), format='A4', print_background=True, margin={"top":"0","right":"0","bottom":"0","left":"0"})
    browser.close()
print(OUT_HTML, OUT_HTML.stat().st_size)
print(OUT_PDF, OUT_PDF.stat().st_size)
