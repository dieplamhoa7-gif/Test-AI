from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_HTML=Path('reports/MIT18642_Trainer_50_Slide_Deck.html')
OUT_PDF=Path('reports/MIT18642_Trainer_50_Slide_Deck.pdf')
OUT_MD=Path('reports/MIT18642_Trainer_50_Slide_Deck.md')

modules=[
('01','Giới thiệu & thị trường tài chính','Tư duy tài chính định lượng, cấu trúc thị trường, buy-side/sell-side, sản phẩm cơ bản','Equity · Fixed Income · Derivatives · FX · Commodities','Nhà đầu tư VN cần phân biệt payoff của cổ phiếu, trái phiếu và CW trước khi dùng model.'),
('02','Bond Math — Toán học trái phiếu','Time value of money, present value, YTM, duration, DV01, convexity, yield curve','P=Σ C/(1+y)^t + M/(1+y)^n\nD_mod=D_mac/(1+y)\nDV01=D_mod*P*0.0001','Dùng yield curve/WACC để hiểu định giá cổ phiếu, nhất là ngân hàng, BĐS, cổ phiếu growth.'),
('03','Đại số tuyến tính trong tài chính','Vector trọng số, covariance matrix, eigenvalues, SVD, no-arbitrage, risk-neutral measure','R_p=w^T R\nσ_p²=w^T Σ w\nΣv=λv','Danh mục VN30 là vector trọng số; covariance cho biết mua nhiều mã có thật sự giảm rủi ro không.'),
('04','Xác suất & quá trình ngẫu nhiên I','Không gian xác suất, moments, fat tails, martingale, gambler’s ruin, Markov chains','E[X], Var(X), Skewness, Kurtosis\nE[X_{t+1}|F_t]=X_t','Một setup cổ phiếu chỉ làm thay đổi xác suất, không tạo chắc chắn. Quản trị vốn tránh gambler’s ruin.'),
('05','Regression Analysis & PCA','OLS, Gauss-Markov, CAPM, Fama-French, Ridge/Lasso, PCA, factor loading','β_hat=(X^T X)^-1 X^T Y\nR_i-R_f=α+β(R_m-R_f)+ε','Kiểm indicator bằng OOS, IC, alpha, không chỉ nhìn chart đẹp. PCA giúp gom indicator trùng.'),
('06','Lãi suất tuyến tính & fixed income','LIBOR→SOFR, FRA, IRS, bootstrapping yield curve, DV01 hedge, electronic trading','N_hedge=-DV01_portfolio/DV01_instrument','Rate regime ảnh hưởng mạnh đến bank, BĐS, chứng khoán, cổ phiếu vay nợ cao.'),
('07','Time Series Analysis','Stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration, pairs trading','AR(1): X_t=φX_{t-1}+ε_t\nHalf-life=ln(2)/|ln(1+φ)|','Không random split dữ liệu cổ phiếu. Mọi tín hiệu phải ghi horizon 5/10/20/60 phiên.'),
('08','Portfolio & Risk Management','Markowitz, efficient frontier, VaR, CVaR, Kelly, Black-Litterman, counterparty risk','IR=IC*sqrt(N)\nKelly f*=μ/σ²\nCVaR=E[Loss|Loss>VaR]','Không all-in nhiều mã cùng ngành. Cần sector cap, correlation cap, position sizing.'),
('09','Stochastic Calculus','Wiener process, quadratic variation, Itô integral, Itô lemma, GBM, SDE, Monte Carlo','dS=μSdt+σSdW\nS_T=S_0 exp[(μ-σ²/2)T+σW_T]','Dùng scenario distribution cho CW/options; không tin một đường forecast duy nhất.'),
('10','Black-Scholes & Option/CW','BS PDE, risk-neutral valuation, Greeks, put-call parity, implied vol, smile/skew','C=S*N(d1)-K*e^{-rT}*N(d2)\nC-P=S-Ke^{-rT}','Chọn CW phải xét maturity, break-even, spread, liquidity, theta, IV — không chỉ leverage.'),
('11','Volatility Modeling, ML & AI','GARCH, volatility clustering, ML pipeline, walk-forward, lookahead bias, AMH','σ_t²=ω+αε_{t-1}²+βσ_{t-1}²\nIC=Corr(signal,return)','ML trong finance phải OOS/walk-forward, calibration, kiểm phí giao dịch và regime shift.'),
('12','Systematic Trading & Prediction Markets','Factor investing, momentum/value/quality/low-vol, prediction markets, breadth, risk limits','Information Ratio = IC * sqrt(Breadth)','Xây hệ thống đầu tư: signal → validation → sizing → risk limits → review định kỳ.')]

slides=[]
md=['# MIT 18.642 Trainer — 50 slide deck\n']
def slide(title, body, badge='', formula='', app='', take=''):
    slides.append((title, body, badge, formula, app, take))
    md.append(f'\n## {title}\n{body}\n')
    if formula: md.append(f'```\n{formula}\n```')
    if app: md.append(f'Ứng dụng: {app}\n')
    if take: md.append(f'Takeaway: {take}\n')

slide('MIT 18.642 Finance Trainer','Slide deck 50 trang dành cho nhà đầu tư chứng khoán Việt Nam. Mục tiêu: học có hệ thống các khái niệm toán tài chính MIT 18.642 và biết cách áp dụng vào HOSE/HNX/VN30.', 'Cover', app='Học để xây hệ thống quyết định đầu tư dựa trên dữ liệu, không dựa vào cảm tính.', take='Lý thuyết phải đi kèm ví dụ số và ứng dụng đầu tư.')
slide('Cách học theo skill','Mỗi topic được học theo 6 bước: tại sao cần biết, khái niệm, công thức, ví dụ số, ứng dụng đầu tư, câu hỏi kiểm tra.', 'Learning Protocol', take='Không học công thức rời rạc; học để ra quyết định tốt hơn.')
slide('Bản đồ 12 modules','12 modules bao phủ toàn bộ 22 video: markets, bond math, linear algebra, probability, regression/PCA, rates, time series, portfolio risk, stochastic calculus, Black-Scholes, volatility/ML, systematic trading.', 'Course Map')

for i,(num,title,concept,formula,app) in enumerate(modules,1):
    slide(f'Module {num} — {title}: Tại sao cần biết?', f'{concept}. Đây là mảnh ghép giúp nhà đầu tư chuyển từ nhận định cảm tính sang mô hình có dữ liệu, giả định và kiểm định.', f'Module {num}', app=app, take='Trước khi dùng vào đầu tư, phải hiểu vấn đề tài chính mà module này giải quyết.')
    slide(f'Module {num} — Khái niệm cốt lõi', f'Khái niệm chính của module: {concept}. Khi học, hãy ghi rõ từng biến đại diện cho điều gì, giả định nào đang dùng, và lỗi phổ biến khi áp dụng.', f'Module {num}', formula=formula, take='Công thức chỉ hữu ích khi hiểu ý nghĩa kinh tế của từng ký hiệu.')
    slide(f'Module {num} — Ví dụ đầu tư Việt Nam', f'Ví dụ áp dụng: {app} Nếu chuyển thành hệ thống, cần định nghĩa dữ liệu đầu vào, cách tính, horizon, và cách kiểm định ngoài mẫu.', f'Module {num}', app=app, take='Ứng dụng tốt phải đo được và backtest được.')

slide('Bảng công thức phải thuộc — phần 1','Nhóm định giá và lãi suất: present value, bond price, duration, DV01, convexity, yield curve. Đây là nền để hiểu WACC, DCF, lãi suất và định giá tài sản.', 'Formula Summary', formula='PV=CF/(1+r)^t\nP=Σ C/(1+y)^t + M/(1+y)^n\nDV01=D_mod*P*0.0001')
slide('Bảng công thức phải thuộc — phần 2','Nhóm xác suất, regression và portfolio: expectation, variance, covariance, OLS, CAPM, portfolio variance.', 'Formula Summary', formula='E[X]=Σp_i x_i\nβ_hat=(X^T X)^-1X^TY\nσ_p²=w^TΣw')
slide('Bảng công thức phải thuộc — phần 3','Nhóm time series, volatility, option và stochastic calculus: AR(1), GARCH, Black-Scholes, GBM.', 'Formula Summary', formula='X_t=φX_{t-1}+ε_t\nσ_t²=ω+αε²_{t-1}+βσ²_{t-1}\nC=S*N(d1)-K*e^{-rT}*N(d2)\ndS=μSdt+σSdW')
slide('Checklist dùng cho cổ phiếu VN','Khi áp dụng vào HOSE/HNX: xác định horizon, tính liquidity/slippage, kiểm market regime, tránh lookahead bias, đo EV, kiểm drawdown, sau đó mới sizing.', 'VN Application', take='Một signal tốt phải có xác suất, payoff, rủi ro và điều kiện sai.')
slide('Checklist dùng cho CW/chứng quyền','Với CW: không chỉ nhìn underlying tăng. Cần days to maturity, moneyness, break-even, spread, liquidity, implied volatility, theta/time decay.', 'CW Application', take='Đúng hướng cổ phiếu cơ sở chưa đủ để lời CW.')
slide('Bài tập thực hành 1 — Bond Math','Tính giá trái phiếu coupon 7%, face 1,000,000 VND, maturity 5 năm, yield 7.5%. Sau đó tính duration và tác động khi yield tăng 50 bps.', 'Exercise')
slide('Bài tập thực hành 2 — Portfolio','Với VCB/HPG/FPT, hãy lập expected return vector, volatility, correlation matrix, tính variance equal-weight và tìm danh mục Sharpe tốt hơn.', 'Exercise')
slide('Bài tập thực hành 3 — Regression/PCA','Chạy CAPM regression cho HPG với VN-Index. Sau đó lấy 20 indicator kỹ thuật, tính correlation/PCA để xem indicator nào trùng thông tin.', 'Exercise')
slide('Bài tập thực hành 4 — Time Series','Chọn một cặp cổ phiếu cùng ngành, kiểm cointegration, tính spread z-score và backtest pairs trading với rule ±2σ.', 'Exercise')
slide('Roadmap học 4 tuần','Tuần 1: markets, bond math, linear algebra. Tuần 2: probability, stochastic process, regression. Tuần 3: PCA, rates, time series, portfolio. Tuần 4: volatility, Black-Scholes, ML, systematic trading.', 'Study Plan')
slide('Kết luận','MIT 18.642 không cho một công thức thần kỳ. Giá trị của khóa học là khung tư duy: xác suất, định giá, kiểm định, rủi ro, danh mục và kỷ luật hệ thống.', 'Final', take='Đầu tư tốt = hiểu payoff + đo xác suất + quản trị downside + kiểm định liên tục.')

# ensure 50
assert len(slides)==50, len(slides)

css='''@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Segoe UI,sans-serif;color:#111827}.slide{width:210mm;height:297mm;padding:17mm 18mm;page-break-after:always;position:relative;overflow:hidden;background:linear-gradient(180deg,#fff,#f4f6fa)}.cover{background:radial-gradient(circle at 18% 12%,#60a5fa,transparent 25%),linear-gradient(135deg,#020617,#1B2B4B 50%,#111827);color:white}.badge{display:inline-block;background:#C49A1B;color:#111827;border-radius:999px;padding:7px 12px;font-size:11px;font-weight:800;letter-spacing:.06em}.top{border-top:8px solid #A31F34;padding-top:12px}.kicker{font-size:11px;color:#C49A1B;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.title{font-size:30px;line-height:1.08;font-weight:900;color:#1B2B4B;margin:8px 0 14px}.cover .title{color:white;font-size:42px}.body{font-size:18px;line-height:1.5;background:white;border:1px solid #d8dee9;border-radius:18px;padding:18px;box-shadow:0 10px 28px rgba(15,23,42,.08)}.formula{white-space:pre-wrap;margin-top:14px;background:#1B2B4B;color:#bbf7d0;border-radius:14px;padding:14px;font-family:Consolas,monospace;font-size:16px;line-height:1.45}.app{margin-top:14px;background:#F0FFF4;border:2px solid #1B5E20;border-left:8px solid #1B5E20;border-radius:14px;padding:14px;color:#123b18;font-size:16px;line-height:1.45}.take{position:absolute;left:18mm;right:18mm;bottom:22mm;background:#FFFDE7;border:2px solid #C49A1B;border-left:8px solid #C49A1B;border-radius:14px;padding:12px;color:#5b3a00;font-size:15px}.footer{position:absolute;bottom:8mm;left:18mm;right:18mm;display:flex;justify-content:space-between;color:#8A8B8C;font-size:10px}.cover .footer{color:#d4e1f7}'''
html=['<!doctype html><html><head><meta charset="utf-8"><title>MIT18642 50 Slide Deck</title><style>'+css+'</style></head><body>']
for idx,(title,body,badge,formula,app,take) in enumerate(slides,1):
    cls='slide cover' if idx==1 else 'slide'
    html.append(f'<section class="{cls}"><div class="top"><div class="badge">{badge or "MIT 18.642 TRAINER"}</div><div class="title">{title}</div></div><div class="body">{body}</div>')
    if formula: html.append(f'<div class="formula">{formula}</div>')
    if app: html.append(f'<div class="app"><b>Ứng dụng đầu tư:</b> {app}</div>')
    if take: html.append(f'<div class="take"><b>Takeaway:</b> {take}</div>')
    html.append(f'<div class="footer"><span>MIT 18.642 Finance Trainer</span><span>Trang {idx}/50</span></div></section>')
html.append('</body></html>')
OUT_HTML.write_text('\n'.join(html),encoding='utf-8')
OUT_MD.write_text('\n'.join(md),encoding='utf-8')
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_page(viewport={"width":1240,"height":1754})
    page.goto(OUT_HTML.resolve().as_uri(),wait_until='networkidle')
    page.pdf(path=str(OUT_PDF),format='A4',print_background=True,margin={"top":"0","right":"0","bottom":"0","left":"0"})
    b.close()
print(OUT_HTML, OUT_HTML.stat().st_size)
print(OUT_MD, OUT_MD.stat().st_size)
print(OUT_PDF, OUT_PDF.stat().st_size)
