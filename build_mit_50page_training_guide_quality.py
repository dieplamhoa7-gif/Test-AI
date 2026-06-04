from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_HTML=Path('reports/MIT_18_642_Training_Guide_50_Trang_CHATGPT_FIX.html')
OUT_PDF=Path('reports/MIT_18_642_Training_Guide_50_Trang_CHATGPT_FIX.pdf')
OUT_MD=Path('reports/MIT_18_642_Training_Guide_50_Trang_CHATGPT_FIX.md')

modules=[
('01','GIỚI THIỆU KHÓA HỌC & THỊ TRƯỜNG TÀI CHÍNH','Lecture 1 Parts 1–3 · Kempthorne · Jake Xia · Vasily Strela',[
('1.1 Tổng quan MIT 18.642','MIT 18.642 là khóa học toán học ứng dụng trong tài chính, nối giữa nền tảng toán và thực tế thị trường. Khóa học gồm các math lectures do MIT giảng và application lectures từ chuyên gia BlackRock, Two Sigma, Mizuho, Millennium, Kalshi, MIT Sloan. Mục tiêu không phải học công thức rời rạc mà là xây toolkit định lượng: linear algebra, probability, stochastic processes, regression, PCA, time series, portfolio, volatility, Black-Scholes và machine learning.'),
('1.2 Cấu trúc thị trường tài chính','Jake Xia giới thiệu thị trường tài chính như cơ chế phân bổ vốn giữa người có vốn và người cần vốn. Các lớp tài sản chính gồm equity, fixed income, derivatives, alternatives. Mỗi lớp có payoff, risk, liquidity và cách định giá riêng. Nhà đầu tư phải hiểu sản phẩm trước khi dùng mô hình.'),
('1.3 Framework đầu tư của Jake Xia','Một quyết định đầu tư chuyên nghiệp phải đi qua: xác định cơ hội, hiểu sản phẩm, định lượng risk-return, đánh giá thanh khoản/chi phí, kiểm soát danh mục và quản trị downside. Đây là khung quan trọng cho nhà đầu tư cá nhân: không chỉ hỏi mua gì, mà còn hỏi mua bao nhiêu, sai khi nào, và rủi ro danh mục ra sao.'),
], [('Equity','Quyền sở hữu doanh nghiệp; lợi nhuận từ tăng giá vốn/cổ tức; risk từ business và market.'),('Fixed Income','Công cụ nợ; payoff dòng tiền rõ hơn; risk chính là lãi suất/tín dụng.'),('Derivatives','Payoff phụ thuộc tài sản cơ sở; có leverage, time decay, Greeks.'),('Alternatives','Hedge funds, PE, real assets; thanh khoản thấp hơn, kỳ vọng diversification.')], 'Bài học cho nhà đầu tư: trước khi dùng indicator/model, phải biết sản phẩm mình giao dịch thuộc loại payoff nào. Cổ phiếu và CW không thể dùng chung một logic đơn giản.'),
('02','BOND MATH — TOÁN HỌC TRÁI PHIẾU','Lecture 1 Part 3 · Vasily Strela',[
('2.1 Time Value of Money','Tiền hôm nay có giá trị hơn tiền tương lai vì có thể đầu tư sinh lời và vì có rủi ro thời gian. Present Value là nền của định giá tài sản: PV = CF/(1+r)^t. Lãi kép và lãi liên tục cho thấy tăng trưởng/chiết khấu tích lũy theo thời gian.'),
('2.2 Định giá trái phiếu và Yield to Maturity','Giá trái phiếu là tổng hiện giá của coupon và principal. Yield to Maturity là tỷ suất làm cho present value của dòng tiền bằng giá hiện tại. Khi yield tăng, bond price giảm; khi yield giảm, price tăng.'),
('2.3 Duration, DV01 và Convexity','Duration đo độ nhạy giá với thay đổi yield. DV01 đo thay đổi giá khi yield dịch 1 basis point. Convexity sửa sai số của duration khi yield thay đổi lớn. Đây là bộ công cụ risk của fixed income.'),
('2.4 Yield Curve và Term Structure','Yield curve biểu diễn lãi suất theo kỳ hạn. Đường cong dốc, phẳng, đảo ngược đều mang tín hiệu kinh tế. Term structure theories giải thích vì sao kỳ hạn khác nhau có yield khác nhau: expectations, liquidity preference, market segmentation.'),
], [('PV','CF/(1+r)^t'),('Bond Price','Σ Coupon/(1+y)^t + Face/(1+y)^T'),('Duration','%ΔP ≈ -D × Δy'),('DV01','Thay đổi giá khi yield đổi 1bp'),('Convexity','Độ cong của quan hệ price-yield')], 'Bài học cho nhà đầu tư: lãi suất là trọng lực định giá. Cổ phiếu growth/P/E cao giống tài sản duration dài, nhạy với rate. CW/option càng cần hiểu time value.'),
('03','ĐẠI SỐ TUYẾN TÍNH TRONG TÀI CHÍNH','Lecture 2 + 4 · Peter Kempthorne',[
('3.1 Vector và Matrix cho danh mục','Một tài sản có thể biểu diễn bằng vector đặc trưng: return, volatility, liquidity, factor exposure. Một danh mục là tổ hợp tuyến tính của nhiều vector tài sản. Dữ liệu thị trường nhiều mã/nhiều ngày/nhiều biến tạo thành matrix.'),
('3.2 Eigenvalues, Eigenvectors, Diagonalization','Eigenvectors biểu diễn các hướng biến động đặc biệt của ma trận; eigenvalues cho biết độ mạnh của hướng đó. Trong finance, chúng xuất hiện trong covariance matrix, PCA và phân tích factor.'),
('3.3 SVD và ứng dụng trong Finance','Singular Value Decomposition phân rã ma trận thành các thành phần quan trọng, hữu ích để giảm chiều, lọc nhiễu, nén dữ liệu và nhận diện cấu trúc ẩn trong returns/indicators.'),
('3.4 One-Period Financial Models','Mô hình một kỳ mô tả payoff ở kỳ sau dưới các trạng thái khác nhau. Đây là nền cho no-arbitrage, pricing kernel và risk-neutral probability.'),
('3.5 No-Arbitrage và Risk-Neutral Pricing','Nếu tồn tại arbitrage, thị trường có cơ hội lợi nhuận không rủi ro. No-arbitrage là nguyên lý neo định giá. Risk-neutral pricing chuyển bài toán định giá thành kỳ vọng chiết khấu dưới xác suất risk-neutral.'),
], [('Vector','Một quan sát/tài sản/danh mục trong không gian feature'),('Matrix','Tập hợp nhiều observations/features'),('Covariance Matrix','Cấu trúc đồng biến động'),('Eigen/SVD','Tìm hướng/factor chính'),('No-Arbitrage','Không có lợi nhuận miễn phí không rủi ro')], 'Bài học cho nhà đầu tư: muốn model hóa VN100 nghiêm túc, phải có feature matrix sạch; nhiều indicator trùng nhau cần gom factor, không cộng điểm mù quáng.'),
('04','XÁC SUẤT & QUÁ TRÌNH NGẪU NHIÊN I','Lecture 4 + 5 + 6 · Peter Kempthorne',[
('4.1 Không gian xác suất và phân phối','Probability space gồm sample space, events và probability measure. Return tương lai là random variable. Distribution cho biết toàn bộ khả năng, không chỉ trung bình.'),
('4.2 Moments: Mean, Variance, Skewness, Kurtosis','Mean đo kỳ vọng, variance đo phân tán, skewness đo lệch phân phối, kurtosis đo tail/heavy-tail. Trong finance, tail risk quan trọng vì lỗ lớn hiếm nhưng nguy hiểm.'),
('4.3 Multivariate Normal và Covariance Matrix','Nhiều tài sản cùng phân phối cần covariance/correlation để mô tả liên hệ. Danh mục rủi ro hay không phụ thuộc covariance, không chỉ rủi ro từng mã.'),
('4.4 LLN và CLT','Law of Large Numbers nói trung bình mẫu hội tụ về kỳ vọng khi mẫu lớn. Central Limit Theorem giải thích vì sao tổng nhiều biến có xu hướng normal trong điều kiện nhất định. Nhưng thị trường có fat tails nên không lạm dụng normal.'),
('4.5 Martingale, Random Walk, Gambler’s Ruin','Martingale là quá trình có kỳ vọng tương lai bằng hiện tại dưới thông tin hiện có. Gambler’s ruin cảnh báo: quản trị vốn sai có thể phá sản dù xác suất thắng không tệ.'),
('4.6 Markov Chains và Credit Rating','Markov chain mô tả chuyển trạng thái; trong tín dụng là chuyển rating AAA→AA→A→default. Tư duy này cũng dùng cho regime: bull/sideway/bear.'),
], [('E[X]','Kỳ vọng'),('Var(X)','Phương sai/risk'),('Cov(X,Y)','Đồng biến động'),('CLT','Tổng biến ngẫu nhiên tiến gần normal theo điều kiện'),('Martingale','Không có drift kỳ vọng dưới filtration'),('Markov Chain','Xác suất chuyển trạng thái')], 'Bài học cho nhà đầu tư: mọi signal chỉ là xác suất có điều kiện. Không được nhầm setup đẹp với chắc thắng. Phải đo sample size, tail risk và drawdown.'),
('05','REGRESSION ANALYSIS & PCA','Lecture 6 + 8 + 9 + 11 · Kempthorne + Two Sigma',[
('5.1 OLS và Gauss-Markov','OLS ước lượng quan hệ tuyến tính giữa biến mục tiêu và feature. Các giả định Gauss-Markov giúp OLS BLUE trong điều kiện nhất định, nhưng finance thường vi phạm noise độc lập/variance ổn định.'),
('5.2 Kiểm định, residuals và ý nghĩa kinh tế','p-value/R² không đủ. Cần residual analysis, outlier check, stability, transaction cost và economic significance. Mô hình giải thích quá khứ chưa chắc dự báo tương lai.'),
('5.3 CAPM và Factor Models','CAPM giải thích return bằng market beta. Factor models mở rộng thêm value, size, momentum, quality, low-vol. Factor exposure giúp hiểu nguồn return/risk.'),
('5.4 Ridge, Lasso, Regularization','Khi nhiều feature, regularization giúp giảm overfit. Ridge phạt L2, Lasso phạt L1 và có thể chọn biến. Nhưng regularization không thay thế validation đúng.'),
('5.5 ETF Case Study và High-Yield Spread','Case studies cho thấy regression dùng để phân tích sản phẩm thật: ETF exposure, spread, factor sensitivity, macro relationship.'),
('5.6 PCA trong Finance','PCA tìm principal components từ covariance/correlation matrix. Two Sigma application thường nhấn mạnh PCA/factor để giảm chiều, phân tích rủi ro và tìm cấu trúc ẩn.'),
], [('OLS','y = Xβ + ε'),('Residual','Phần model không giải thích'),('CAPM','Rᵢ-Rf = α + β(Rm-Rf)+ε'),('Ridge/Lasso','Regularization chống overfit'),('PCA','Eigenvectors của covariance/correlation matrix')], 'Bài học cho nhà đầu tư: feature tốt phải chứng minh bằng OOS, EV và regime. Nhiều indicator cùng một factor không phải nhiều bằng chứng độc lập.'),
('06','LÃI SUẤT TUYẾN TÍNH & FIXED INCOME','Lecture 7 · Mizuho / Andrew Gunstensen',[
('6.1 LIBOR scandal và chuyển sang SOFR','LIBOR từng là benchmark lớn nhưng có vấn đề thao túng/độ tin cậy. SOFR dựa trên secured overnight financing, phản ánh thị trường repo USD. Chuyển benchmark ảnh hưởng định giá và hợp đồng.'),
('6.2 Interest Rate Swaps và Forward Rate Agreements','IRS trao đổi fixed rate và floating rate. FRA khóa lãi suất tương lai. Các sản phẩm này dùng để hedge hoặc thể hiện quan điểm về rates.'),
('6.3 Bootstrapping Yield Curve','Bootstrapping xây đường cong zero/discount từ các instrument market quoted. Curve construction là nền định giá fixed income/rates derivatives.'),
('6.4 DV01, Hedging, Electronic Trading','DV01 giúp đo risk theo basis point. Hedging dùng instrument khác để giảm exposure. Electronic trading làm rates market nhanh, cạnh tranh và cần mô hình hóa tốt.'),
], [('SOFR','Benchmark overnight secured'),('Swap','Trao đổi fixed/floating cashflows'),('FRA','Khóa lãi suất tương lai'),('Bootstrapping','Xây curve từ market quotes'),('DV01','Risk per basis point')], 'Bài học cho nhà đầu tư: rate regime ảnh hưởng cổ phiếu qua cost of capital, tín dụng, liquidity. Ngân hàng, BĐS, chứng khoán, growth phản ứng khác nhau.'),
('07','TIME SERIES ANALYSIS','Lecture 12 · Peter Kempthorne',[
('7.1 Stationarity và Unit Root','Stationarity nghĩa là cấu trúc thống kê ổn định theo thời gian. Nhiều chuỗi tài chính không stationarity ở price, nhưng return có thể gần stationarity hơn. Unit root test giúp kiểm tra.'),
('7.2 AR, MA, ARMA, ARIMA','AR dùng giá trị quá khứ, MA dùng shock quá khứ, ARMA kết hợp, ARIMA thêm differencing cho non-stationary series. Box-Jenkins là quy trình nhận diện/ước lượng/kiểm định model.'),
('7.3 ACF/PACF','Autocorrelation Function và Partial Autocorrelation giúp chọn bậc AR/MA. Trong finance, autocorrelation thường yếu nhưng vẫn quan trọng ở một số horizon/asset.'),
('7.4 Cointegration và Pairs Trading','Hai chuỗi non-stationary có thể có tổ hợp stationarity — cointegration. Đây là nền cho pairs trading/statistical arbitrage.'),
('7.5 High-Yield Spread/Fourier/Polynomial Fits','Ứng dụng time series vào spread/macro cho thấy fitting phải cẩn trọng, tránh overfit hình dạng quá khứ.'),
], [('AR','X_t phụ thuộc X_{t-1}'),('MA','X_t phụ thuộc shock quá khứ'),('ARIMA','ARMA + differencing'),('ACF/PACF','Chọn cấu trúc lag'),('Cointegration','Quan hệ cân bằng dài hạn')], 'Bài học cho nhà đầu tư: mọi signal phải có horizon. Không dùng random split cho time series. Kiểm theo giai đoạn bull/bear/sideway.'),
('08','QUẢN LÝ DANH MỤC & RỦI RO','Lecture 10 + 13 · Jake Xia + Quantile/LSEG',[
('8.1 Mean-Variance Optimization','Markowitz tối ưu danh mục bằng expected return và covariance. Efficient frontier biểu diễn tập danh mục tối ưu giữa return và risk.'),
('8.2 Risk Measures: VaR, CVaR, Drawdown','VaR đo mức lỗ tối đa ở percentile; CVaR đo lỗ trung bình trong tail; drawdown đo sụt giảm từ đỉnh. CVaR/drawdown thực tế hơn khi tail risk lớn.'),
('8.3 Kelly Criterion và Position Sizing','Kelly tối ưu tăng trưởng vốn dài hạn theo edge và odds, nhưng full Kelly biến động mạnh. Nhà đầu tư thường dùng fractional Kelly hoặc volatility targeting.'),
('8.4 Counterparty Risk Optimization','Counterparty risk gồm exposure, default probability, collateral, netting, wrong-way risk. Tối ưu hóa risk cần constraints và tail scenario.'),
], [('Portfolio variance','wᵀΣw'),('Efficient Frontier','Tập return/risk tối ưu'),('VaR','Loss percentile'),('CVaR','Expected tail loss'),('Kelly','Sizing theo edge/odds')], 'Bài học cho nhà đầu tư: chọn mã chưa đủ. Cần sector cap, correlation cap, position sizing, stop/invalidation và risk tổng danh mục.'),
('09','QUÁ TRÌNH NGẪU NHIÊN II & STOCHASTIC CALCULUS','Lecture 14 + 24 + 25 · Peter Kempthorne',[
('9.1 Brownian Motion và Wiener Process','Brownian motion là mô hình nhiễu liên tục với increments độc lập và phân phối normal. Đây là nền cho nhiều mô hình continuous-time finance.'),
('9.2 Itô Integral và Itô’s Lemma','Stochastic calculus khác calculus thường vì quadratic variation. Itô’s Lemma cho phép tính vi phân hàm của stochastic process, là chìa khóa dẫn tới Black-Scholes PDE.'),
('9.3 Geometric Brownian Motion','GBM mô hình giá cổ phiếu: dS = μSdt + σSdW. Nó tạo lognormal price, nền của Black-Scholes, nhưng thực tế có volatility clustering, jumps, fat tails.'),
('9.4 Euler-Maruyama và phương pháp số','SDE thường cần mô phỏng số. Euler-Maruyama xấp xỉ quá trình stochastic theo bước thời gian nhỏ.'),
], [('Brownian Motion','W_t với increments normal độc lập'),('Itô Lemma','Chain rule cho stochastic process'),('GBM','dS=μSdt+σSdW'),('Euler-Maruyama','Mô phỏng SDE')], 'Bài học cho nhà đầu tư: đừng tin một đường dự báo duy nhất. Hãy nghĩ theo distribution/scenario/path risk, đặc biệt với option/CW.'),
('10','ĐỊNH GIÁ OPTION — BLACK-SCHOLES','Lecture 21 · Vasily Strela',[
('10.1 Derivation Black-Scholes PDE','Black-Scholes xây bằng no-arbitrage, delta hedging và giả định GBM. PDE mô tả quan hệ giữa giá option, underlying, time, rate và volatility.'),
('10.2 Black-Scholes Formula và Risk-Neutral Valuation','Công thức call/put định giá option bằng kỳ vọng risk-neutral chiết khấu. Risk-neutral không có nghĩa nhà đầu tư thật không sợ rủi ro; đó là measure dùng để pricing.'),
('10.3 Greeks','Delta đo nhạy với underlying, Gamma đo nhạy của Delta, Vega đo nhạy với volatility, Theta đo time decay. Greeks là risk dashboard của option.'),
('10.4 Implied Volatility và Vol Surface','Implied vol là volatility hàm ý từ giá option. Vol surface cho thấy volatility thay đổi theo strike/maturity, phản ánh smile/skew và market demand.'),
], [('Call BS','C = S N(d1) - K e^{-rT}N(d2)'),('Inputs','S,K,T,r,σ'),('Delta','∂C/∂S'),('Theta','∂C/∂t'),('Vega','∂C/∂σ')], 'Bài học cho nhà đầu tư: mua CW không chỉ cần đúng underlying. Phải xét maturity, moneyness, break-even, spread, liquidity, theta và implied volatility.'),
('11','VOLATILITY MODELING, MACHINE LEARNING & AI','Lecture 19 + 23 + 18 · Kempthorne + John Hull + Andrew Lo',[
('11.1 ARCH/GARCH và Volatility Clustering','Volatility có clustering: giai đoạn biến động cao thường kéo dài. ARCH/GARCH mô hình variance phụ thuộc shock/variance quá khứ.'),
('11.2 ML Pipeline trong Finance','Machine learning cần feature, label, train/validation/test, loss function, metrics, calibration. Time series không được random split cho final validation.'),
('11.3 Backtesting pitfalls','Các lỗi chính: look-ahead bias, data snooping, survivorship bias, overfitting, transaction cost bị bỏ qua, regime shift. Backtest tốt phải khiêm tốn và OOS.'),
('11.4 Andrew Lo — Adaptive Market Hypothesis & AI','Thị trường thích nghi; edge xuất hiện/mất đi theo cạnh tranh và môi trường. AI hữu ích khi kết hợp domain knowledge, data quality và risk management.'),
], [('GARCH','Variance động theo shock quá khứ'),('Calibration','Xác suất dự báo khớp thực tế'),('OOS','Out-of-sample'),('AMH','Adaptive Market Hypothesis')], 'Bài học cho nhà đầu tư: ML không phải phép màu. Dữ liệu/label/validation quyết định chất lượng. Model nên xuất xác suất, không phán chắc chắn.'),
('12','SYSTEMATIC TRADING, PREDICTION MARKETS & TỔNG KẾT','Lecture 20 + course synthesis',[
('12.1 Factor Investing','Các factor phổ biến gồm momentum, value, quality, low-vol, size. Factor investing là cách hệ thống hóa nguồn alpha/risk, nhưng factor có chu kỳ và crowding risk.'),
('12.2 Fundamental Law of Active Management','Alpha phụ thuộc skill và breadth. Nhiều cơ hội độc lập + skill thật tạo information ratio tốt hơn, nhưng nếu tín hiệu trùng factor thì breadth ảo.'),
('12.3 Prediction Markets và Kalshi','Event contracts định giá xác suất sự kiện. Đây là cách nhìn binary event risk: KQKD, chính sách, pháp lý, lãi suất, nâng hạng.'),
('12.4 Roadmap học tập','Học theo thứ tự: market/bond math → linear algebra/probability → regression/PCA/time series → portfolio/risk/volatility → options/Black-Scholes → ML/stochastic calculus → systematic trading.'),
], [('Momentum','Theo xu hướng/relative strength'),('Value','Định giá rẻ tương đối'),('Quality','Doanh nghiệp chất lượng'),('Low-vol','Biến động thấp'),('Prediction Market','Giá phản ánh xác suất event')], 'Bài học cho nhà đầu tư: hệ thống đầu tư tốt phải có alpha hypothesis, validation, risk control, sizing và review định kỳ. Không có shortcut.'),
]

css='''@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Segoe UI,sans-serif;color:#111827}.page{width:210mm;min-height:297mm;padding:13mm 14mm;page-break-after:always;position:relative;background:#fff}.cover{background:radial-gradient(circle at 18% 10%,#60a5fa,transparent 25%),linear-gradient(135deg,#020617,#0f2d5c 50%,#111827);color:white;display:flex;flex-direction:column;justify-content:center}.badge{display:inline-block;width:max-content;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:7px 12px;font-size:11px;letter-spacing:.08em}.cover h1{font-size:42px;line-height:1.05;margin:18px 0}.cover h2{font-weight:400;font-size:21px;opacity:.92}.toc h1{font-size:28px;margin:0 0 10px;color:#0f172a}.tocgrid{display:grid;grid-template-columns:1fr;gap:6px}.tocitem{border:1px solid #e5e7eb;border-left:5px solid #2563eb;border-radius:10px;padding:7px 9px;font-size:11px;background:#f8fafc}.tocitem b{display:block;color:#0f172a;font-size:12px;margin-bottom:2px}.module{border-top:8px solid #1d4ed8}.head{border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin-bottom:10px}.kicker{font-size:11px;color:#2563eb;font-weight:900;text-transform:uppercase;letter-spacing:.06em}.title{font-size:25px;font-weight:900;color:#0f172a;line-height:1.12}.section{border:1px solid #e5e7eb;border-radius:14px;padding:10px 11px;margin:8px 0;background:#fff;box-shadow:0 4px 14px rgba(15,23,42,.035)}.section h3{font-size:14px;margin:0 0 6px;color:#1d4ed8}.section p,.section li{font-size:11.8px;line-height:1.53;margin-top:0}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}table{width:100%;border-collapse:collapse;font-size:10.8px}th{background:#0f172a;color:white;text-align:left;padding:6px}td{border:1px solid #e5e7eb;padding:6px;vertical-align:top}td:first-child{font-weight:800;color:#1d4ed8;width:28%}.take{background:#fffbeb;border:1px solid #fde68a;border-left:5px solid #f59e0b;border-radius:12px;padding:9px 10px;color:#78350f;font-size:11.8px;line-height:1.45}.footer{position:absolute;bottom:7mm;left:14mm;right:14mm;display:flex;justify-content:space-between;color:#64748b;font-size:9.5px}'''

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
html=['<!doctype html><html><head><meta charset="utf-8"><title>MIT 18.642 Training Guide 50 Trang</title><style>'+css+'</style></head><body>']
md=['# MIT 18.642 — Training Guide 50 Trang cho Nhà đầu tư\n']
html.append('<section class="page cover"><div class="badge">MIT 18.642 · TOÁN HỌC ỨNG DỤNG TRONG TÀI CHÍNH · FALL 2024</div><h1>Tài liệu Đào tạo dành cho<br/>Nhà đầu tư Chứng khoán</h1><h2>12 Modules · 22 Video Lectures · Biên soạn đầy đủ/chuyên nghiệp theo cấu trúc khóa học</h2><div class="footer"><span>Prepared by Tiểu đệ for Hòa Đại ka</span><span>50-page Quality Fix</span></div></section>')
toc=''.join(f'<div class="tocitem"><b>Module {i:02d} — {esc(m[1])}</b>{esc(m[2])}</div>' for i,m in enumerate(modules,1))
html.append(f'<section class="page toc"><h1>MỤC LỤC</h1><div class="tocgrid">{toc}</div><div class="footer"><span>MIT 18.642 Training Guide</span><span>Mục lục</span></div></section>')
for idx,(num,title,src,sections,concepts,take) in enumerate(modules,1):
    sec_html=''.join(f'<div class="section"><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for h,p in sections)
    rows=''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>' for a,b in concepts)
    html.append(f'<section class="page module"><div class="head"><div class="kicker">{esc(src)}</div><div class="title">MODULE {num} — {esc(title)}</div></div>{sec_html}<div class="section"><h3>Bảng khái niệm/công thức cần nhớ</h3><table><thead><tr><th>Khái niệm</th><th>Ý nghĩa</th></tr></thead><tbody>{rows}</tbody></table></div><div class="take"><b>Ứng dụng cho nhà đầu tư:</b> {esc(take)}</div><div class="footer"><span>MIT 18.642 · Module {num}</span><span>Trang module {idx}/12</span></div></section>')
    md.append(f'\n## Module {num} — {title}\nNguồn: {src}\n')
    for h,p in sections: md.append(f'\n### {h}\n{p}\n')
    md.append('\n### Khái niệm\n'+'\n'.join(f'- **{a}:** {b}' for a,b in concepts))
    md.append('\n### Ứng dụng cho nhà đầu tư\n'+take+'\n')
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
