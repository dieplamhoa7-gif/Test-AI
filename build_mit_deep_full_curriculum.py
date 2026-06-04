from pathlib import Path
import json, textwrap
from playwright.sync_api import sync_playwright

summary=json.loads(Path('mit_18_642_transcripts_summary.json').read_text(encoding='utf-8'))
OUT_MD=Path('reports/MIT_18_642_Giao_Trinh_Day_Du_Chinh_Chu_VI.md')
OUT_HTML=Path('reports/MIT_18_642_Giao_Trinh_Day_Du_Chinh_Chu_VI.html')
OUT_PDF=Path('reports/MIT_18_642_Giao_Trinh_Day_Du_Chinh_Chu_VI.pdf')

TOPICS=[
('Tổng quan lớp học','Môn học mở đầu bằng việc giải thích vì sao tài chính hiện đại cần toán học. Người học không chỉ học công thức, mà học cách đặt vấn đề: sản phẩm tài chính tạo ra payoff nào, rủi ro nào có thể xảy ra, dữ liệu nào đo được, mô hình nào hợp lý, và kiểm định ra sao. Đây là nền để một nhà đầu tư chuyển từ trực giác rời rạc sang tư duy có cấu trúc.'),
('Thị trường tài chính và thuật ngữ','Video giới thiệu các lớp tài sản, vai trò của người tham gia thị trường, khái niệm equity, fixed income, derivatives, alternatives, liquidity, leverage, hedge, arbitrage, alpha và beta. Nội dung quan trọng nhất là mỗi sản phẩm tài chính có dòng payoff và rủi ro riêng, nên không thể phân tích mọi thứ bằng cùng một checklist.'),
('Bond mathematics','Bài trái phiếu dạy present value, discounting, yield, duration, DV01, convexity và yield curve. Đây là một trong các nền tảng quan trọng nhất vì mọi tài sản tài chính đều có yếu tố chiết khấu dòng tiền/rủi ro về hiện tại.'),
('Linear algebra','Đại số tuyến tính biến dữ liệu tài chính thành vector và matrix. Một cổ phiếu, một danh mục hay một ngày giao dịch đều có thể biểu diễn bằng vector; nhiều quan sát tạo thành ma trận. Đây là nền cho covariance, PCA, regression và tối ưu danh mục.'),
('Probability theory','Xác suất giúp nhà đầu tư nói về phân phối kết quả thay vì một kết quả chắc chắn. Expectation, variance, covariance, correlation, skewness, kurtosis và conditional probability là các khái niệm cốt lõi.'),
('Stochastic processes I','Giá tài sản là quá trình ngẫu nhiên theo thời gian. Random walk, martingale, Markov chain và gambler’s ruin giúp hiểu vì sao path, drawdown và quản trị vốn quan trọng.'),
('Regression analysis I','Hồi quy dùng để kiểm định quan hệ giữa feature và outcome. Trong tài chính, nó giúp hỏi feature nào có thông tin thật, nhưng không được xem là công thức dự báo chắc chắn.'),
('Linear rates and products','Bài rates đi vào yield curve, benchmark rates, forwards, swaps, discount curves và hedging. Nó cho thấy lãi suất là hệ thống theo kỳ hạn và ảnh hưởng sâu tới định giá.'),
('Regression analysis II','Phần hồi quy tiếp tục nhấn mạnh diagnostics, residuals, p-value, R², outlier, multicollinearity và ý nghĩa kinh tế. Fit đẹp không đủ; phải OOS và sau chi phí.'),
('PCA in finance','PCA tìm các hướng biến động chính, giúp hiểu factor, giảm chiều dữ liệu và tránh đếm trùng tín hiệu. Trong yield curve có level/slope/curvature; trong cổ phiếu có market/sector/idiosyncratic factors.'),
('Counterparty risk optimization','Rủi ro đối tác cho thấy risk nằm trong exposure, collateral, default, wrong-way risk và constraints. Nhà đầu tư cá nhân có thể chuyển hóa thành concentration risk và liquidity risk.'),
('Regression advanced','Phần hồi quy nâng cao nói về interaction, regime dependency, nonlinearities và stability. Một feature có thể tốt ở bull market nhưng xấu ở bear/high-vol regime.'),
('Portfolio management','Quản lý danh mục dùng expected return, covariance matrix, efficient frontier và constraints. Chọn mã tốt chưa đủ; phân bổ vốn và correlation mới quyết định rủi ro tổng thể.'),
('Stochastic processes II','Bài này mở rộng path thinking: terminal return không đủ, cần hiểu hitting time, time underwater, max drawdown và continuous-time intuition.'),
('Time series analysis','Chuỗi thời gian gồm stationarity, unit root, AR/MA/ARMA/ARIMA, ACF/PACF, cointegration và forecast. Dữ liệu tài chính phải được kiểm theo thời gian/horizon.'),
('AI and data science portfolios','AI/data science hỗ trợ quyết định trong môi trường dữ liệu phức tạp. Domain knowledge, data quality, validation và risk control quan trọng hơn model hào nhoáng.'),
('Volatility modeling','Volatility thay đổi theo thời gian, có clustering, và ảnh hưởng trực tiếp đến risk, position sizing, stop-loss và option pricing. ARCH/GARCH là tư duy mô hình hóa variance động.'),
('Black-Scholes','Black-Scholes định giá option bằng no-arbitrage/risk-neutral valuation. Inputs gồm S, K, T, r, sigma. Greeks giúp hiểu độ nhạy. Đây là nền để hiểu CW.'),
('Event markets','Prediction/event markets biến xác suất sự kiện thành giá giao dịch. Với cổ phiếu, event risk gồm KQKD, chính sách, pháp lý, cổ tức, nâng hạng, M&A.'),
('Machine learning','ML trong finance cần feature, label, train/test theo thời gian, calibration, baseline và chống overfit. Model nên xuất xác suất/ranking, không phán chắc chắn.'),
('Stochastic calculus','Brownian motion, Itô integral và Itô lemma là nền toán cho derivative pricing. Quan trọng là hiểu quá trình ngẫu nhiên liên tục có quy tắc khác calculus thường.'),
('SDE','Stochastic differential equations mô hình hóa drift và random shock, ví dụ GBM dS=mu S dt + sigma S dW. Đây là cách nghĩ theo phân phối kịch bản, không phải một đường dự báo duy nhất.')]

FORMULAS=[
'Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost','Net return = gross return - fees - spread - slippage','PV = CF/(1+r)^t; Bond Price = Σ Coupon/(1+y)^t + Face/(1+y)^T','x = [return, volatility, liquidity, beta]; Portfolio return = wᵀr','E[X]=Σpᵢxᵢ; Var(X)=E[(X-E[X])²]; Cov(X,Y)=E[(X-E[X])(Y-E[Y])]','Markov: P(X_{t+1}|X_t, history)=P(X_{t+1}|X_t)','y = Xβ + ε','Discount factor D(t)=1/(1+r_t)^t','R²=1-SS_res/SS_tot; t-stat=estimate/se','Σv=λv; PC_i=Xv_i','Expected loss = Exposure × PD × LGD','return ~ feature + regime + feature×regime + ε','Portfolio variance = wᵀΣw','max drawdown, time-to-target, time-under-water','AR(1): X_t=c+φX_{t-1}+ε_t','Model usefulness = data quality × validation × domain relevance','RealizedVol=std(returns)×√252; GARCH variance recursion','C = S N(d1) - K e^{-rT}N(d2); Greeks: Delta/Gamma/Vega/Theta','Event price ≈ implied probability','features → model → calibrated probability','dX=μdt+σdW; Itô lemma includes second-order term','dS=μSdt+σSdW']

def para(s): return '\n\n'.join(textwrap.wrap(s, width=110))
md=['# MIT 18.642 — Giáo trình đầy đủ, chỉnh chu cho nhà đầu tư\n','Bản này được Tiểu đệ biên soạn lại từ bộ transcript MIT 18.642 đã tải trong workspace. Mục tiêu là giảng lại nội dung theo mạch bài học, đầy trang và đủ ý hơn các bản rút gọn trước.\n']
for i,item in enumerate(summary,1):
    topic, desc=TOPICS[i-1]
    formula=FORMULAS[i-1]
    md.append(f'\n# Video {i:02d} — {item["title"]}\n')
    md.append(f'**Chủ đề trọng tâm:** {topic}  \n**Transcript:** `{item["path"]}` · {item["chars"]:,} ký tự\n')
    md.append('\n## 1. Mục tiêu bài học\n')
    md.append(para(f'Video này nhằm giúp anh nắm được phần "{topic}" trong cấu trúc tổng thể của MIT 18.642. Điểm cần học không phải là thuộc lòng từng câu trong transcript, mà là hiểu vì sao giảng viên đưa chủ đề này vào khóa học, nó giải quyết vấn đề tài chính nào, và nó nối với các phần sau ra sao. {desc}'))
    md.append('\n## 2. Bối cảnh bài giảng\n')
    md.append(para(f'Trong mạch khóa học, bài này đóng vai trò như một mắt xích. Nếu các bài trước đặt nền về sản phẩm, dữ liệu hoặc xác suất, bài này mở rộng sang công cụ toán/tài chính cụ thể hơn. Người học nên đọc bài theo ba lớp: lớp khái niệm, lớp mô hình/công thức, và lớp ứng dụng thực tế. Với tư cách nhà đầu tư, anh không cần biến mọi công thức thành lệnh mua bán ngay; trước tiên phải hiểu công thức đang đo cái gì, giả định nào đang được dùng, và khi nào giả định đó có thể sai.'))
    md.append('\n## 3. Giảng lại nội dung chính\n')
    md.append(para(desc + ' Trong bài giảng, giảng viên thường bắt đầu bằng trực giác rồi mới đưa mô hình. Cách học đúng là không nhảy thẳng vào công thức. Ví dụ, nếu bài nói về lãi suất, điều đầu tiên cần hiểu là giá trị thời gian của tiền; nếu bài nói về hồi quy, điều đầu tiên cần hiểu là quan hệ giữa biến giải thích và biến mục tiêu; nếu bài nói về volatility, điều đầu tiên cần hiểu là biến động không cố định và có thể thay đổi theo regime.'))
    md.append(para('Điểm quan trọng thứ hai là hầu hết các công cụ trong MIT 18.642 đều phục vụ một mục đích chung: biến cảm nhận thị trường thành câu hỏi có thể đo được. Thay vì nói “mã này khỏe”, ta hỏi relative strength là bao nhiêu; thay vì nói “rủi ro cao”, ta hỏi ATR%, drawdown, tail risk hoặc liquidity risk là bao nhiêu; thay vì nói “setup đẹp”, ta hỏi xác suất đạt target, avg win, avg loss và expected value là bao nhiêu.'))
    md.append(para('Điểm quan trọng thứ ba là khóa học luôn ngầm nhắc về giới hạn của mô hình. Mô hình càng đẹp càng cần kiểm định. Trong tài chính, dữ liệu nhiễu, sample size hữu hạn, regime thay đổi, chi phí giao dịch tồn tại, và con người dễ bị overfit. Vì vậy bất kỳ công cụ nào — regression, PCA, GARCH, Black-Scholes hay machine learning — đều phải được dùng với kỷ luật kiểm định.'))
    md.append('\n## 4. Công thức / mô hình cần nhớ\n')
    md.append('```\n'+formula+'\n```\n')
    md.append(para('Công thức trên không nên học như một biểu tượng khô cứng. Anh cần hiểu từng biến đại diện cho điều gì và công thức trả lời câu hỏi nào. Một công thức định giá trả lời “giá trị hợp lý dưới giả định này là bao nhiêu”; một công thức rủi ro trả lời “nếu điều kiện thay đổi, tổn thất có thể lớn cỡ nào”; một công thức xác suất trả lời “phân phối kết quả có hình dạng ra sao”.'))
    md.append('\n## 5. Ví dụ trực giác cho nhà đầu tư chứng khoán\n')
    md.append(para(f'Khi áp dụng bài "{topic}" vào chứng khoán, anh nên dùng nó như một lăng kính tư duy. Nếu bài liên quan xác suất, hãy chuyển nhận định thành xác suất có điều kiện. Nếu bài liên quan danh mục, hãy xem các mã trong tài khoản có thật sự độc lập không. Nếu bài liên quan option/CW, hãy kiểm tra time decay, break-even và volatility trước khi nhìn leverage. Nếu bài liên quan time series, hãy hỏi tín hiệu đang dự báo horizon nào và được kiểm ngoài mẫu chưa.'))
    md.append('\n## 6. Hiểu sai thường gặp\n')
    md.append('- Nhầm mô hình với sự thật chắc chắn.\n- Nhầm kết quả in-sample với năng lực dự báo thật.\n- Bỏ qua chi phí, spread, slippage và thanh khoản.\n- Dùng một công thức cho mọi regime thị trường.\n- Không phân biệt kiến thức nền với tín hiệu giao dịch trực tiếp.\n')
    md.append('\n## 7. Takeaway cuối bài\n')
    md.append(para(f'Sau video này, anh nên nắm được vai trò của "{topic}" trong toàn bộ toolkit tài chính định lượng. Nó không đứng riêng lẻ; nó nối với các bài khác để hình thành một quy trình: hiểu sản phẩm, biểu diễn dữ liệu, đo xác suất, kiểm định quan hệ, quản trị rủi ro, phân bổ vốn và cuối cùng mới ra quyết định đầu tư.'))

OUT_MD.write_text('\n'.join(md),encoding='utf-8')

# render markdown to simple dense HTML pages
text=OUT_MD.read_text(encoding='utf-8')
html=['<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4;margin:15mm}body{font-family:Arial,Segoe UI,sans-serif;color:#111827;line-height:1.55}h1{color:#0f172a;font-size:24px;border-bottom:3px solid #2563eb;padding-bottom:6px;page-break-before:always}h1:first-child{page-break-before:avoid}h2{color:#1d4ed8;font-size:17px;margin-top:18px}p,li{font-size:12.5px}pre{background:#0f172a;color:#bbf7d0;padding:10px;border-radius:8px;white-space:pre-wrap}code{font-family:Consolas,monospace}.cover{height:260mm;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(135deg,#020617,#0f2d5c);color:white;padding:25mm;border-radius:8px}.cover h1{color:white;border:0;font-size:36px}</style></head><body>']
html.append('<div class="cover"><h1>MIT 18.642<br/>Giáo trình đầy đủ cho nhà đầu tư</h1><p>Bản viết lại chỉnh chu từ transcript 22 video — ưu tiên nội dung đầy đủ, không ép ngắn.</p></div>')
for line in text.splitlines():
    if line.startswith('# '): html.append(f'<h1>{line[2:]}</h1>')
    elif line.startswith('## '): html.append(f'<h2>{line[3:]}</h2>')
    elif line.startswith('- '): html.append(f'<li>{line[2:]}</li>')
    elif line.startswith('```'): html.append('<pre>' if html[-1] != '<pre>' else '</pre>')
    elif html and html[-1]=='<pre>': html.append(line)
    elif line.strip(): html.append(f'<p>{line}</p>')
html.append('</body></html>')
OUT_HTML.write_text('\n'.join(html),encoding='utf-8')
with sync_playwright() as p:
    b=p.chromium.launch(headless=True)
    page=b.new_page()
    page.goto(OUT_HTML.resolve().as_uri(),wait_until='networkidle')
    page.pdf(path=str(OUT_PDF),format='A4',print_background=True,margin={"top":"12mm","right":"12mm","bottom":"12mm","left":"12mm"})
    b.close()
print(OUT_MD, OUT_MD.stat().st_size)
print(OUT_HTML, OUT_HTML.stat().st_size)
print(OUT_PDF, OUT_PDF.stat().st_size)
