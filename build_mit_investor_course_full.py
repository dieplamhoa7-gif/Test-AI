from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_HTML=Path('reports/MIT_18_642_Khoa_Hoc_Nha_Dau_Tu_22_Video_FULL.html')
OUT_PDF=Path('reports/MIT_18_642_Khoa_Hoc_Nha_Dau_Tu_22_Video_FULL.pdf')
OUT_MD=Path('reports/MIT_18_642_Khoa_Hoc_Nha_Dau_Tu_22_Video_FULL.md')
OUT_HTML.parent.mkdir(exist_ok=True)

modules = [
{
'n':'01','title':'Tổng quan khóa học & cách tư duy tài chính định lượng','lect':'Lecture 1 Parts I–II','color':'#2563eb',
'learn':['Tài chính không phải là đoán giá, mà là ra quyết định dưới bất định.','Một tài sản là quyền hưởng dòng tiền hoặc payoff trong tương lai.','Nhà đầu tư phải luôn hỏi: lợi nhuận kỳ vọng là gì, rủi ro là gì, xác suất bao nhiêu, sai khi nào?'],
'explain':'MIT 18.642 bắt đầu bằng việc đặt nền cho tư duy định lượng. Thị trường tài chính gồm cổ phiếu, trái phiếu, phái sinh, quỹ, hàng hóa, tiền tệ và nhiều sản phẩm lai. Điểm chung của tất cả sản phẩm là chúng có payoff trong tương lai và payoff đó bất định. Vì vậy, tài chính định lượng không tìm một câu trả lời chắc chắn, mà xây khung để định giá, đo xác suất, đo rủi ro và chọn quyết định có kỳ vọng tốt nhất.',
'formula':'Expected Value = P(win) × AvgWin - P(loss) × AvgLoss - Cost',
'investor':'Là nhà đầu tư chứng khoán, anh không nên chỉ hỏi “MWG có tăng không?”. Câu hỏi đúng là: nếu mua MWG hôm nay, trong 20 phiên tới xác suất lời >6% là bao nhiêu, xác suất lỗ >5% là bao nhiêu, mức lời/lỗ trung bình ra sao, và điều kiện nào làm kèo này sai?',
'mistakes':['Nhầm tín hiệu kỹ thuật với sự chắc chắn.','Chỉ nhìn upside mà bỏ qua drawdown và thanh khoản.','Không phân biệt trade ngắn hạn với đầu tư dài hạn.'],
'exercise':['Chọn 3 mã anh đang quan tâm và viết ra: lý do mua, điểm sai, target, stop, horizon.','Với mỗi mã, ước lượng nếu đúng lời bao nhiêu %, nếu sai lỗ bao nhiêu %.']
},
{
'n':'02','title':'Bond Math — Lãi suất, chiết khấu, duration, convexity','lect':'Lecture 1 Part III','color':'#7c3aed',
'learn':['Tiền hôm nay đáng giá hơn tiền tương lai.','Lãi suất tăng làm giảm present value.','Duration đo độ nhạy của giá với lãi suất.','Convexity giúp hiểu sai lệch khi lãi suất biến động lớn.'],
'explain':'Bond Math là nền móng định giá tài sản. Một dòng tiền trong tương lai phải được chiết khấu về hiện tại. Trái phiếu có coupon và principal, giá là tổng present value của các dòng tiền đó. Khi yield tăng, mẫu số chiết khấu tăng nên giá trái phiếu giảm. Duration cho biết giá nhạy thế nào với yield. Tư duy này cũng áp dụng cho cổ phiếu: cổ phiếu tăng trưởng có dòng tiền xa tương lai nên giống tài sản duration dài, rất nhạy với lãi suất.',
'formula':'PV = CF/(1+r)^t\nBond Price = Σ Coupon_t/(1+y)^t + Face/(1+y)^T\n%ΔPrice ≈ -Duration × ΔYield',
'investor':'Khi lãi suất/tiền gửi tăng, cổ phiếu P/E cao, câu chuyện tăng trưởng xa tương lai dễ bị nén định giá. Ngược lại khi lãi suất giảm, dòng tiền rẻ hơn và risk appetite có thể cải thiện. Nhà đầu tư Việt Nam nên nhìn lãi suất huy động, tín dụng, tỷ giá như bối cảnh nền cho thị trường.',
'mistakes':['Nghĩ cổ phiếu không liên quan lãi suất.','Chỉ nhìn lợi nhuận doanh nghiệp mà quên P/E có thể bị nén.','Mua CW dài/short time decay mà không hiểu time value.'],
'exercise':['So sánh một cổ phiếu growth P/E cao và một cổ phiếu dividend/cashflow ổn định khi lãi suất tăng.','Ghi lại 3 ngành nhạy lãi suất: ngân hàng, BĐS, chứng khoán/growth.']
},
{
'n':'03','title':'Linear Algebra — Vector, matrix, factor và danh mục','lect':'Lecture 2 + Lecture 4','color':'#0891b2',
'learn':['Mỗi cổ phiếu/ngày là một vector đặc trưng.','Nhiều cổ phiếu nhiều ngày tạo thành ma trận dữ liệu.','Covariance/correlation đo mức đi cùng nhau.','Eigen/PCA giúp tìm factor chính.'],
'explain':'Linear algebra biến dữ liệu thị trường thành dạng máy có thể học. Ví dụ MWG ngày hôm nay có vector: return 20 ngày, RSI, MACD, volume ratio, ATR%, khoảng cách tới hỗ trợ, khoảng cách tới kháng cự, pattern score. Nếu làm cho 120 mã trong 800 ngày, ta có ma trận hàng chục nghìn dòng. Từ ma trận này có thể chạy regression, PCA, ML, portfolio optimization.',
'formula':'x_t = [ret20, RSI, MACD, volumeRatio, ATR%, distSupport, distResistance]\nX = stock-date observations × features',
'investor':'Khi anh nhìn nhiều chỉ báo trên chart, thực chất anh đang nhìn một vector. Vấn đề là nhiều chỉ báo trùng nhau. RSI, Stochastic, Williams %R đều là momentum oscillator. Nếu cả 3 cùng xanh, không có nghĩa là 3 bằng chứng độc lập.',
'mistakes':['Đếm nhiều indicator trùng nhau thành nhiều tín hiệu độc lập.','Không chuẩn hóa dữ liệu trước khi so sánh.','Không có feature matrix nên model chỉ là cảm tính có code.'],
'exercise':['Viết vector 10 feature cho một mã anh đang theo dõi.','Đánh dấu feature nào thuộc trend, momentum, volume, volatility, support/resistance.']
},
{
'n':'04','title':'Xác suất & stochastic process — nghĩ theo phân phối, không nghĩ theo chắc chắn','lect':'Lecture 4 + 5 + 6','color':'#059669',
'learn':['Return tương lai là biến ngẫu nhiên.','Giá là một quá trình theo thời gian, không phải một điểm.','Tín hiệu chỉ làm thay đổi xác suất có điều kiện.','Backtest phải giữ thứ tự thời gian.'],
'explain':'Probability dạy kỳ vọng, phương sai, phân phối, xác suất có điều kiện. Stochastic process dạy rằng giá cổ phiếu là chuỗi biến ngẫu nhiên theo thời gian. Một setup đẹp không đảm bảo thắng; nó chỉ có thể làm xác suất thắng cao hơn hoặc payoff tốt hơn. Vì dữ liệu có thứ tự thời gian, không được random shuffle khi đánh giá chiến lược.',
'formula':'P(hit target | setup present)\nE[R | setup] = Σ p_i × r_i',
'investor':'Thay vì nói “mã này chắc vượt đỉnh”, hãy nói “trong quá khứ, setup tương tự có 54% xác suất đạt +6% trong 20 phiên, avgWin 9%, avgLoss -4%, EV dương”. Cách nói này giúp anh biết có nên đánh và đánh bao nhiêu.',
'mistakes':['Lấy vài ví dụ thắng rồi tin setup.','Không tính sample size.','Dùng dữ liệu tương lai vô tình trong feature.'],
'exercise':['Với một setup anh thích, tìm ít nhất 30 mẫu quá khứ và ghi thắng/thua.','Tính win rate, avg win, avg loss.']
},
{
'n':'05','title':'Regression Analysis — kiểm định feature nào thật sự có edge','lect':'Lecture 6 + 8 + 11','color':'#dc2626',
'learn':['Regression đo quan hệ giữa feature và future return.','Coefficient không ổn định thì không đáng tin.','In-sample đẹp chưa chắc out-of-sample tốt.','Residual và outlier rất quan trọng.'],
'explain':'Regression là công cụ để kiểm xem các feature như RSI, ATR, khoảng cách tới hỗ trợ có liên quan future return không. Nhưng regression trong tài chính rất dễ bị nhiễu, multicollinearity và overfit. Do đó phải xem coefficient ổn định qua thời gian không, top/bottom quintile có khác biệt không, và OOS có giữ được không.',
'formula':'futureReturn20d = a + b1*distSupport + b2*distResistance + b3*ATR + b4*RSI + error',
'investor':'Nếu một indicator được quảng cáo rất hay nhưng khi kiểm định không tạo spread giữa nhóm tốt và nhóm xấu, nó chỉ là trang trí. Feature tốt phải giúp phân biệt nhóm có kỳ vọng tốt hơn.',
'mistakes':['Tin R² cao trong sample nhỏ.','Tối ưu tham số trên toàn bộ lịch sử rồi tưởng là khách quan.','Không kiểm regime.'],
'exercise':['Chia dữ liệu thành 2023-2024 train, 2025 validate, 2026 test.','Kiểm một feature: nhóm top 20% và bottom 20% có future return khác nhau không?']
},
{
'n':'06','title':'PCA trong Finance — bớt ảo giác nhiều tín hiệu','lect':'Lecture 9','color':'#9333ea',
'learn':['PCA tìm hướng biến động chính trong dữ liệu.','Eigenvalue cho biết factor giải thích bao nhiêu variance.','PCA giúp giảm trùng lặp indicator.','Danh mục có thể bị chi phối bởi market factor/sector factor.'],
'explain':'PCA lấy ma trận dữ liệu và tìm các trục chính giải thích biến động. Trong tài chính, PC1 thường giống market factor, các PC sau có thể giống sector/style factor. Với indicator, PCA/correlation giúp thấy RSI/Stoch/Williams cùng một nhóm, ATR/realized vol/Bollinger width cùng một nhóm.',
'formula':'X ≈ PC1 + PC2 + ... + noise',
'investor':'Nếu danh mục có 10 mã nhưng tất cả đều cùng factor chứng khoán/thanh khoản, anh tưởng phân tán nhưng thực ra đang all-in một yếu tố. PCA/correlation giúp nhìn rủi ro ẩn đó.',
'mistakes':['Cộng điểm indicator trùng nhau làm score phình giả.','Không biết portfolio bị một factor chi phối.','Dùng PCA nhưng không hiểu ý nghĩa kinh tế.'],
'exercise':['Nhóm 20 indicator thành 5 nhóm: trend, momentum, volume, volatility, SR.','Trong danh mục hiện tại, đánh dấu mã nào cùng ngành/cùng beta thị trường.']
},
{
'n':'07','title':'Rates Products & Yield Curve — đọc môi trường lãi suất','lect':'Lecture 7','color':'#ca8a04',
'learn':['Yield curve là cấu trúc lãi suất theo kỳ hạn.','Forward rate là kỳ vọng/định giá lãi suất tương lai.','Swaps và hedging dùng để quản trị rate risk.','Rate regime ảnh hưởng sector khác nhau.'],
'explain':'Lecture về rates đi sâu vào sản phẩm lãi suất như SOFR/LIBOR, swaps, curve construction. Với nhà đầu tư cổ phiếu, không cần trade swap, nhưng cần hiểu môi trường lãi suất ảnh hưởng định giá, tín dụng, thanh khoản và khẩu vị rủi ro.',
'formula':'Discount factor = 1/(1+r_t)^t',
'investor':'Ngân hàng có thể hưởng lợi từ NIM trong vài giai đoạn, BĐS chịu áp lực khi tín dụng/lãi suất căng, chứng khoán phụ thuộc thanh khoản. Vì vậy cùng một signal kỹ thuật nhưng hiệu quả khác nhau theo rate regime.',
'mistakes':['Dùng một chiến lược cho mọi macro regime.','Bỏ qua tín dụng và thanh khoản khi phân tích BĐS/chứng khoán.'],
'exercise':['Ghi lại lãi suất tiền gửi 12 tháng, tỷ giá, thanh khoản thị trường hàng tuần.','Đánh dấu sector nào hưởng lợi/bị hại khi rate tăng.']
},
{
'n':'08','title':'Time Series Analysis — horizon, regime shift và stationarity','lect':'Lecture 12','color':'#0f766e',
'learn':['Chuỗi thời gian có autocorrelation và regime shift.','Stationarity là giả định mạnh, thường bị phá vỡ.','Một feature có thể tốt 5 ngày nhưng tệ 60 ngày.','Forecast phải gắn horizon.'],
'explain':'Time series analysis nghiên cứu dữ liệu theo thời gian: AR, MA, ARMA, stationarity, trend, cycle. Trong chứng khoán, thị trường đổi chế độ: bull, bear, sideway, high volatility. Model cố định dễ hỏng khi regime đổi.',
'formula':'R_t = a + b R_{t-1} + error',
'investor':'Anh phải phân biệt trade T+ ngắn hạn, swing 20 phiên, trend 60 phiên. Một setup breakout có thể tốt 10-20 phiên nhưng không nói gì về đầu tư 1 năm.',
'mistakes':['Trộn timeframe trong một score.','Backtest 2023 rồi áp 2026 không kiểm regime.','Không đo time-to-target.'],
'exercise':['Với một chiến lược, tính kết quả 5d, 10d, 20d, 60d riêng.','Kiểm xem chiến lược tốt nhất ở horizon nào.']
},
{
'n':'09','title':'Portfolio Management & Counterparty Risk — chọn mã chưa đủ, phải phân bổ vốn','lect':'Lecture 10 + 13','color':'#0f172a',
'learn':['Danh mục phụ thuộc covariance, không chỉ số lượng mã.','Diversification thật là khác nguồn rủi ro.','Optimization cần constraints thực tế.','Concentration risk có thể giết tài khoản.'],
'explain':'Portfolio management dùng expected return vector và covariance matrix để phân bổ vốn. Counterparty risk optimization dạy tư duy exposure, concentration, dependency. Với cổ phiếu, risk tương tự là tập trung ngành, beta thị trường, thanh khoản và các mã cùng factor.',
'formula':'Portfolio variance = wᵀ Σ w',
'investor':'Mua SSI, VND, HCM, VCI, MBS không phải là 5 kèo độc lập. Đó là một kèo lớn vào ngành chứng khoán/thanh khoản. Position size phải giảm nếu correlation cao.',
'mistakes':['Danh mục nhiều mã nhưng cùng ngành.','Không có sector cap.','Mã volatility cao nhưng size như mã phòng thủ.'],
'exercise':['Tính tỷ trọng danh mục theo ngành.','Đặt rule: không quá X% vào một sector nếu market regime xấu.']
},
{
'n':'10','title':'Volatility Modeling — biến động là risk và cũng là cơ hội','lect':'Lecture 19','color':'#ea580c',
'learn':['Volatility thay đổi và có clustering.','ATR% là thước đo thực dụng cho cổ phiếu.','Vol cao tăng cơ hội hit target nhưng cũng tăng drawdown.','Stop và position size nên theo volatility.'],
'explain':'Volatility modeling dạy rằng biến động không cố định. Sau cú sốc, thị trường thường tiếp tục biến động mạnh. Volatility ảnh hưởng option pricing, stop-loss, sizing và xác suất chạm target/stop.',
'formula':'RealizedVol20 = std(daily returns 20d) × sqrt(252)\nATR% = ATR14 / Close',
'investor':'Không nên dùng stop 5% cho mọi mã. Mã ATR 1.5% và mã ATR 5% khác nhau hoàn toàn. Vol cao có thể trade được nhưng size phải nhỏ hơn và stop/target phải hợp lý.',
'mistakes':['Thấy vol cao là mua vì “sắp chạy”.','Đặt stop quá gần với mã biến động mạnh.','Không tính gap risk.'],
'exercise':['Tính ATR% cho 5 mã anh hay xem.','So sánh target/stop có phù hợp ATR không.']
},
{
'n':'11','title':'Black-Scholes, Options và Chứng quyền CW','lect':'Lecture 21','color':'#be123c',
'learn':['Option/CW phụ thuộc S, K, T, r, σ.','Time decay làm CW mất giá theo thời gian.','Break-even quan trọng hơn leverage đẹp.','Greeks giúp hiểu rủi ro option.'],
'explain':'Black-Scholes cho thấy giá option không chỉ phụ thuộc cổ phiếu cơ sở tăng hay giảm. Nó còn phụ thuộc thời gian còn lại, volatility, lãi suất, strike và moneyness. Risk-neutral valuation là logic định giá không-arbitrage, không phải bảo rằng đời thực không rủi ro.',
'formula':'Call = S N(d1) - K e^{-rT} N(d2)\nInputs: S, K, T, r, σ',
'investor':'Với CW, anh có thể đúng cổ phiếu cơ sở nhưng vẫn không lời nếu CW gần đáo hạn, spread rộng, thanh khoản thấp, break-even xa hoặc theta ăn mòn. Vì vậy CW score phải khác stock score.',
'mistakes':['Chọn CW vì leverage cao nhất.','Không nhìn ngày đáo hạn.','Không tính break-even và spread.'],
'exercise':['Lấy 3 CW cùng underlying, so sánh daysToMaturity, spread, break-even.','Chỉ chọn CW nếu underlying signal đủ mạnh và break-even hợp lý.']
},
{
'n':'12','title':'AI, Machine Learning, Event Markets & Stochastic Calculus','lect':'Lecture 18 + 20 + 23 + 24 + 25','color':'#4f46e5',
'learn':['ML cần dữ liệu sạch, label rõ, OOS nghiêm.','Event markets biến biến cố thành xác suất.','Stochastic calculus là nền cho option/vol/path risk.','Model nên xuất probability, không xuất chắc chắn.'],
'explain':'Các lecture cuối mở rộng sang AI/ML, event contracts và stochastic calculus. ML trong finance dễ overfit vì noise và regime shift. Event market dạy cách nghĩ về biến cố như xác suất. Stochastic calculus/SDE cho hiểu sâu về path, volatility và option pricing.',
'formula':'dS = μSdt + σSdW\nModel output: P(hit target), P(drawdown), Expected Return',
'investor':'ML hữu ích nếu dùng để rank xác suất và giải thích feature. Nó nguy hiểm nếu anh tin nó như hộp đen. Với event như KQKD, chính sách, chia cổ tức, cần eventRiskFlag riêng vì kỹ thuật thường có thể bị phá.',
'mistakes':['Train ML trước khi có feature matrix sạch.','Random split dữ liệu time series.','Không calibration xác suất.'],
'exercise':['Viết label rõ: hit +6% trong 20 phiên hay futureReturn20d?','So sánh model ML với rule baseline đơn giản trước khi tin.']
}
]

css = '''@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Segoe UI,sans-serif;color:#111827;background:white}.page{width:210mm;min-height:297mm;padding:15mm 15mm;page-break-after:always;position:relative;overflow:hidden}.cover{background:radial-gradient(circle at 20% 10%,#60a5fa 0,transparent 24%),linear-gradient(135deg,#020617,#0f2d5c 48%,#111827);color:white;display:flex;flex-direction:column;justify-content:center}.cover h1{font-size:43px;line-height:1.02;margin:18px 0 8px;letter-spacing:-1.4px}.cover h2{font-weight:400;font-size:21px;opacity:.92;margin:0 0 20px}.badge{display:inline-block;width:max-content;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:7px 12px;font-size:11px;letter-spacing:.08em}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}.box{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:16px;padding:13px}.box b{display:block;color:#93c5fd;margin-bottom:5px}.footer{position:absolute;bottom:9mm;left:15mm;right:15mm;display:flex;justify-content:space-between;font-size:10px;color:#64748b}.cover .footer{color:rgba(255,255,255,.65)}h2{font-size:28px;margin:0 0 8px;color:#0f172a;letter-spacing:-.5px}.toc .item{display:flex;gap:10px;border:1px solid #e5e7eb;border-left:6px solid var(--c);border-radius:14px;padding:10px;margin:7px 0;background:#f8fafc}.toc .num{width:32px;height:32px;background:var(--c);color:white;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;flex-shrink:0}.toc h3{margin:0 0 2px;font-size:13px}.toc p{margin:0;color:#475569;font-size:11px;line-height:1.35}.module{padding-left:18mm}.bar{position:absolute;left:0;top:0;bottom:0;width:10mm;background:var(--c)}.head{border-bottom:2px solid #e5e7eb;padding-bottom:10px;margin-bottom:10px}.kicker{color:var(--c);font-weight:800;font-size:12px;letter-spacing:.06em}.head h2{font-size:25px;margin:4px 0}.learn{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0}.learn div{background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;padding:9px;font-size:11.4px;line-height:1.35}.section{border:1px solid #e5e7eb;border-radius:16px;padding:12px;margin:9px 0;background:white;box-shadow:0 4px 16px rgba(15,23,42,.04)}.section h3{margin:0 0 6px;color:var(--c);font-size:15px}.section p,.section li{font-size:12.1px;line-height:1.55}.formula{white-space:pre-wrap;font-family:Consolas,monospace;background:#020617;color:#bbf7d0;border-radius:12px;padding:10px;font-size:11px;line-height:1.45}.cols{display:grid;grid-template-columns:1fr 1fr;gap:9px}.callout{background:#fffbeb;border:1px solid #fde68a;border-radius:14px;padding:10px;color:#78350f;font-size:12px;line-height:1.45}.road{background:#0f172a;color:white}.road h2{color:white}.road .step{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);border-radius:15px;padding:12px;margin:8px 0}.road b{color:#93c5fd}.road p{color:#dbeafe;font-size:12px;line-height:1.45}'''

toc = ''.join([f'<div class="item" style="--c:{m["color"]}"><div class="num">{m["n"]}</div><div><h3>{m["title"]}</h3><p>{m["lect"]}</p></div></div>' for m in modules])

pages=[]
md=['# MIT 18.642 — Khóa học cho nhà đầu tư chứng khoán & LH Investment\n']
for m in modules:
    learns=''.join([f'<div>{x}</div>' for x in m['learn']])
    mistakes=''.join([f'<li>{x}</li>' for x in m['mistakes']])
    exercise=''.join([f'<li>{x}</li>' for x in m['exercise']])
    pages.append(f'''<section class="page module" style="--c:{m['color']}"><div class="bar"></div><div class="head"><div class="kicker">{m['lect']}</div><h2>Module {m['n']} — {m['title']}</h2></div><div class="learn">{learns}</div><div class="section"><h3>1. Bài học gốc</h3><p>{m['explain']}</p></div><div class="section"><h3>2. Công thức / mô hình cần nhớ</h3><div class="formula">{m['formula']}</div></div><div class="section"><h3>3. Ý nghĩa cho nhà đầu tư</h3><p>{m['investor']}</p></div><div class="cols"><div class="section"><h3>4. Hiểu sai thường gặp</h3><ul>{mistakes}</ul></div><div class="section"><h3>5. Bài tập nhỏ</h3><ul>{exercise}</ul></div></div><div class="callout"><b>Áp dụng hệ thống:</b> Nội dung module này phải được biến thành feature, rule, risk flag hoặc backtest metric trước khi đưa vào model.</div><div class="footer"><span>MIT 18.642 Investor Course</span><span>Module {m['n']}</span></div></section>''')
    md += [f'\n## Module {m["n"]} — {m["title"]}\n', f'Nguồn: {m["lect"]}\n', '### Bài học chính\n'] + [f'- {x}' for x in m['learn']] + ['\n### Giải thích\n'+m['explain'], '\n### Công thức\n```\n'+m['formula']+'\n```', '\n### Ý nghĩa nhà đầu tư\n'+m['investor'], '\n### Hiểu sai\n'] + [f'- {x}' for x in m['mistakes']] + ['\n### Bài tập\n'] + [f'- {x}' for x in m['exercise']]

road = ''.join([f'<div class="step"><b>{i}. {t}</b><p>{d}</p></div>' for i,(t,d) in enumerate([
('Feature matrix','Mỗi mã/ngày là một vector feature: trend, momentum, volume, volatility, SR, pattern, regime.'),
('No look-ahead','Feature tại ngày t chỉ dùng dữ liệu đến ngày t. Future return là label riêng.'),
('Feature validation','Kiểm top/bottom quintile, Spearman, sample size, regime, drawdown.'),
('Backtest EV','Tính precision, avgWin, avgLoss, EV, profitFactor, max drawdown.'),
('Portfolio risk','Tính sector/correlation/volatility/liquidity concentration.'),
('ML nhẹ','Chỉ train logistic/GBM sau khi rule baseline ổn và OOS sạch.')],1)])
html=f'''<!doctype html><html><head><meta charset="utf-8"><title>MIT 18.642 Investor Course</title><style>{css}</style></head><body><section class="page cover"><div class="badge">MIT 18.642 · 22 PUBLIC VIDEO TRANSCRIPTS · INVESTOR COURSE</div><h1>Khóa học Toán Tài chính<br/>cho Nhà đầu tư Chứng khoán</h1><h2>Bản dạy chi tiết cho Hòa Đại ka — học kiến thức trước, áp dụng LH Investment sau</h2><div class="grid"><div class="box"><b>Không chỉ layout</b>Bản này giải thích bài học, công thức, ví dụ đầu tư, lỗi thường gặp và bài tập nhỏ.</div><div class="box"><b>Ứng dụng thực chiến</b>Mỗi module đều gắn với feature/backtest/risk/model/CW.</div><div class="box"><b>Nguyên tắc</b>No look-ahead · OOS · Expected Value · Regime · Risk-first.</div><div class="box"><b>Nguồn</b>22 transcript public của MIT 18.642 Fall 2024.</div></div><div class="footer"><span>Prepared by Tiểu đệ</span><span>Full Teaching Edition</span></div></section><section class="page toc"><h2>Mục lục 12 module học</h2>{toc}<div class="footer"><span>Mục lục</span><span>Trang 2</span></div></section>{''.join(pages)}<section class="page road"><h2>Roadmap áp dụng vào model LH Investment</h2><p>Sau khi học 22 video, pipeline training đúng phải đi theo thứ tự này.</p>{road}<div class="footer"><span>LH Investment Training SOP</span><span>Final</span></div></section></body></html>'''
OUT_HTML.write_text(html,encoding='utf-8')
OUT_MD.write_text('\n'.join(md),encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={"width":1240,"height":1754})
    page.goto(OUT_HTML.resolve().as_uri(),wait_until='networkidle')
    page.pdf(path=str(OUT_PDF),format='A4',print_background=True,margin={"top":"0","right":"0","bottom":"0","left":"0"})
    browser.close()
print(OUT_HTML, OUT_HTML.stat().st_size)
print(OUT_MD, OUT_MD.stat().st_size)
print(OUT_PDF, OUT_PDF.stat().st_size)
