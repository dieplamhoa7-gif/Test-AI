from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether

OUT = Path('reports/MIT_18_642_Training_Guide_LH_Investment_PREMIUM.pdf')
OUT_MD = Path('reports/MIT_18_642_Training_Guide_LH_Investment_PREMIUM.md')
OUT.parent.mkdir(exist_ok=True)

font = 'Helvetica'
bold = 'Helvetica-Bold'
for fp in [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\calibri.ttf']:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFont', fp)); font = 'VNFont'; break
for fp in [r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\calibrib.ttf']:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFontBold', fp)); bold = 'VNFontBold'; break

NAVY = colors.HexColor('#0B1F3A')
BLUE = colors.HexColor('#1F5EFF')
LIGHT = colors.HexColor('#F3F6FB')
GOLD = colors.HexColor('#C58A1A')
GRAY = colors.HexColor('#4B5563')
GREEN = colors.HexColor('#0F8A5F')
RED = colors.HexColor('#B42318')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('CoverTitle', fontName=bold, fontSize=25, leading=31, alignment=TA_CENTER, textColor=NAVY, spaceAfter=14))
styles.add(ParagraphStyle('CoverSub', fontName=font, fontSize=13, leading=18, alignment=TA_CENTER, textColor=GRAY, spaceAfter=8))
styles.add(ParagraphStyle('TinyCenter', fontName=font, fontSize=8.5, leading=12, alignment=TA_CENTER, textColor=GRAY))
styles.add(ParagraphStyle('H1', fontName=bold, fontSize=16, leading=21, textColor=NAVY, spaceBefore=10, spaceAfter=8))
styles.add(ParagraphStyle('H2', fontName=bold, fontSize=12.5, leading=17, textColor=BLUE, spaceBefore=7, spaceAfter=5))
styles.add(ParagraphStyle('Body', fontName=font, fontSize=9.4, leading=13.5, textColor=colors.HexColor('#111827'), spaceAfter=4))
styles.add(ParagraphStyle('BodySmall', fontName=font, fontSize=8.4, leading=11.8, textColor=colors.HexColor('#111827'), spaceAfter=3))
styles.add(ParagraphStyle('VNBullet', parent=styles['Body'], leftIndent=12, firstLineIndent=-8))
styles.add(ParagraphStyle('Quote', fontName=bold, fontSize=10.2, leading=14, textColor=NAVY, backColor=LIGHT, borderColor=BLUE, borderWidth=0.5, borderPadding=7, spaceBefore=5, spaceAfter=7))
styles.add(ParagraphStyle('VNCodePretty', fontName=font, fontSize=8, leading=10, backColor=colors.HexColor('#F8FAFC'), borderColor=colors.HexColor('#E5E7EB'), borderWidth=0.3, borderPadding=5, spaceAfter=5))

story=[]
md=[]

def P(text, style='Body'):
    story.append(Paragraph(text, styles[style])); md.append(text.replace('<b>','**').replace('</b>','**').replace('<br/>','\n'))

def bullet(text): P('• ' + text, 'VNBullet')
def h1(text): story.append(Paragraph(text, styles['H1'])); md.append('\n# '+text+'\n')
def h2(text): story.append(Paragraph(text, styles['H2'])); md.append('\n## '+text+'\n')

def tbl(data, widths=None, header=True):
    table = Table([[Paragraph(str(c), styles['BodySmall']) for c in row] for row in data], colWidths=widths, hAlign='LEFT')
    ts=[('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#D8DEE9')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if header:
        ts += [('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),bold)]
    table.setStyle(TableStyle(ts)); story.append(table); story.append(Spacer(1,6))
    for row in data: md.append(' | '.join(map(str,row)))

# Cover
story.append(Spacer(1, 2.2*cm))
P('MIT 18.642', 'CoverTitle')
P('Topics in Mathematics with Applications in Finance', 'CoverTitle')
P('Training Guide dành cho Nhà đầu tư Chứng khoán & hệ thống LH Investment', 'CoverSub')
P('Fall 2024 · Massachusetts Institute of Technology · 22 public video transcripts processed', 'CoverSub')
story.append(Spacer(1, 0.7*cm))
tbl([
    ['Nguồn', 'MIT 18.642 Fall 2024 public playlist transcripts'],
    ['Mục tiêu', 'Biến kiến thức toán tài chính thành feature, backtest, risk rule, portfolio logic và CW scoring'],
    ['Cách đọc', 'Bài học gốc trước → ý nghĩa đầu tư → áp dụng vào LH Investment'],
    ['Nguyên tắc đỏ', 'No look-ahead · OOS/walk-forward · Expected Value · Regime-aware · Risk-first']
], [4.0*cm, 11.5*cm], header=False)
story.append(Spacer(1, 1.0*cm))
P('Prepared by Tiểu đệ for Hòa Đại ka', 'TinyCenter')
story.append(PageBreak())

# TOC
h1('MỤC LỤC TỔNG QUAN')
modules = [
('Module 1', 'Giới thiệu khóa học & thị trường tài chính', 'Lecture 1 Parts I–III'),
('Module 2', 'Bond Math — lãi suất, chiết khấu, duration, convexity', 'Lecture 1 Part III'),
('Module 3', 'Linear Algebra trong tài chính', 'Lecture 2 + 4'),
('Module 4', 'Probability & Stochastic Processes I', 'Lecture 4 + 5 + 6'),
('Module 5', 'Regression Analysis & PCA', 'Lecture 6 + 8 + 9 + 11'),
('Module 6', 'Rates products & fixed income models', 'Lecture 7'),
('Module 7', 'Time Series Analysis', 'Lecture 12'),
('Module 8', 'Portfolio, Counterparty Risk & Risk Optimization', 'Lecture 10 + 13'),
('Module 9', 'Volatility Modeling', 'Lecture 19'),
('Module 10', 'Black-Scholes, Options & CW', 'Lecture 21'),
('Module 11', 'AI, Machine Learning & Event Markets', 'Lecture 18 + 20 + 23'),
('Module 12', 'Stochastic Calculus & SDE', 'Lecture 14 + 24 + 25'),
('Module 13', 'Roadmap training model LH Investment', 'Ứng dụng tổng hợp')]
tbl([['Module','Nội dung','Lecture']] + modules, [2.2*cm, 9.4*cm, 4.0*cm])
story.append(PageBreak())

# Executive summary
h1('EXECUTIVE SUMMARY — ANH CẦN NHỚ GÌ?')
P('<b>MIT 18.642 không dạy đi tìm một chỉ báo thần kỳ.</b> Khóa học dạy cách biến thị trường thành bài toán xác suất, dòng tiền, thời gian, rủi ro, danh mục và kiểm định định lượng.')
P('Với LH Investment, bài học cốt lõi là chuyển từ “indicator + cảm tính” sang “feature matrix + probability + expected value + regime + risk-adjusted ranking”.', 'Quote')
for x in ['Mọi tín hiệu phải có horizon: 5d/10d/20d/60d.', 'Mọi backtest phải tránh look-ahead bias.', 'Win rate không đủ; phải có expected value, avgWin, avgLoss.', 'Model phải biết nó sai khi nào: wrongIf/invalidation.', 'Không dùng ML phức tạp trước khi feature/backtest cơ bản sạch.']:
    bullet(x)

# Module definitions
module_text = [
('MODULE 1 — GIỚI THIỆU KHÓA HỌC & THỊ TRƯỜNG TÀI CHÍNH', 'Lecture 1 Parts I–II–III',
 'Khóa học đặt nền: tài chính là hệ thống các tài sản, dòng tiền, rủi ro, xác suất và định giá. Investor không nên hỏi “mã này chắc tăng không”, mà hỏi xác suất, payoff, drawdown, thanh khoản, chi phí và bối cảnh thị trường.',
 [('Tài sản', 'claim trên dòng tiền/trạng thái tương lai'), ('Return', 'lợi nhuận phải đi cùng risk'), ('Arbitrage', 'neo logic định giá'), ('Market structure', 'thanh khoản/chi phí/slippage quan trọng')],
 ['Thêm liquidityScore, marketRegime, sectorRegime, slippageRisk.', 'Output khuyến nghị phải có why/wrongIf/horizon/risk.', 'Không chỉ hiển thị indicator; phải hỗ trợ quyết định.']),
('MODULE 2 — BOND MATH: LÃI SUẤT, CHIẾT KHẤU, DURATION', 'Lecture 1 Part III — Vasily Strela',
 'Bond math dạy quy đổi dòng tiền tương lai về hiện tại. Lãi suất là trọng lực của tài chính: rate tăng thì present value giảm, đặc biệt với tài sản duration dài như cổ phiếu tăng trưởng.',
 [('PV', 'CF/(1+r)^t'), ('Bond Price', 'PV coupons + PV principal'), ('Duration', 'độ nhạy giá với yield'), ('Convexity', 'sửa sai số duration khi yield đổi lớn')],
 ['Thêm rateSensitiveScore, valuationDurationRisk, peCompressionRisk.', 'Cổ phiếu growth/P/E cao cần cảnh báo khi rate regime xấu.', 'CW/option phải tính time value và discounting.']),
('MODULE 3 — LINEAR ALGEBRA TRONG TÀI CHÍNH', 'Lecture 2 + 4',
 'Linear algebra là ngôn ngữ của dữ liệu nhiều chiều: mỗi cổ phiếu/ngày là một vector feature; toàn bộ VN100 theo thời gian là matrix để regression, PCA, ML và portfolio optimization.',
 [('Vector', 'hồ sơ 1 mã tại 1 ngày'), ('Matrix', 'stock-date × features'), ('Covariance', 'biến động chung'), ('Eigen/PCA', 'factor chính trong dữ liệu')],
 ['Duy trì research_feature_matrix_vn100.json.', 'Chuẩn hóa feature groups: trend/momentum/volume/volatility/SR/pattern/regime.', 'Không training ML từ các cache rời rạc thiếu schema.']),
('MODULE 4 — PROBABILITY & STOCHASTIC PROCESSES', 'Lecture 4 + 5 + 6',
 'Giá cổ phiếu là quá trình ngẫu nhiên theo thời gian, không phải điểm dự báo đơn lẻ. Tín hiệu chỉ làm thay đổi xác suất có điều kiện, không bảo đảm kết quả.',
 [('Conditional Probability', 'P(kết quả | setup)'), ('Expectation', 'lợi nhuận kỳ vọng'), ('Variance', 'rủi ro/phân tán'), ('Stochastic Process', 'chuỗi biến ngẫu nhiên theo thời gian')],
 ['Mỗi setup phải có pHitTarget20d, pLossMoreThan5Pct20d.', 'Validation phải chronological/walk-forward, không random shuffle.', 'Feature tại t chỉ dùng dữ liệu <= t.']),
('MODULE 5 — REGRESSION ANALYSIS & PCA', 'Lecture 6 + 8 + 9 + 11',
 'Regression kiểm định feature nào thực sự liên quan future return. PCA/correlation giúp loại chỉ báo trùng thông tin và tìm factor thật.',
 [('OLS', 'ước lượng quan hệ tuyến tính'), ('Residual', 'phần model không giải thích'), ('Multicollinearity', 'feature trùng gây méo hệ số'), ('PCA', 'giảm chiều/tìm factor')],
 ['Chạy Spearman/top-bottom quintile/OOS.', 'Tạo feature_correlation_report và indicator_factor_groups.', 'Pattern score chỉ là overlay nếu chưa chứng minh OOS.']),
('MODULE 6 — LINEAR RATES, PRODUCTS & MODELS', 'Lecture 7 — Mizuho/Rates',
 'Rates products và yield curve cho thấy định giá phụ thuộc toàn bộ đường cong lãi suất, không chỉ một con số rate.',
 [('Yield curve', 'cấu trúc lãi suất theo kỳ hạn'), ('Forward rate', 'lãi suất hàm ý tương lai'), ('Swap', 'trao đổi dòng tiền lãi suất'), ('Hedging', 'giảm rủi ro thay vì đoán hướng')],
 ['Thêm macroRateRegime/yieldCurveProxy khi có data.', 'Sector ngân hàng/BĐS/growth cần phản ứng khác nhau với rate.', 'Dùng regime macro làm filter, không làm tín hiệu đơn độc.']),
('MODULE 7 — TIME SERIES ANALYSIS', 'Lecture 12',
 'Time series nhấn mạnh autocorrelation, stationarity, trend, regime shift. Một feature có thể đúng horizon 5d nhưng sai horizon 60d.',
 [('AR/MA/ARMA', 'mô hình phụ thuộc quá khứ'), ('Stationarity', 'tính ổn định thống kê'), ('Regime shift', 'thị trường đổi luật chơi'), ('Forecast horizon', 'khung thời gian dự báo')],
 ['Mọi output phải có horizon.', 'Backtest tách 5/10/20/60d.', 'Không gom mọi horizon vào một score mơ hồ.']),
('MODULE 8 — PORTFOLIO & COUNTERPARTY/RISK OPTIMIZATION', 'Lecture 10 + 13',
 'Danh mục không chỉ là chọn mã tốt. Risk phụ thuộc covariance, correlation, sector exposure, liquidity và constraints.',
 [('Expected return vector', 'lợi nhuận kỳ vọng từng tài sản'), ('Covariance matrix', 'mức độ đi cùng nhau'), ('Efficient frontier', 'return/risk tối ưu'), ('Concentration risk', 'rủi ro tập trung')],
 ['Thêm positionSizeHint, sectorCapWarning, correlationWarning.', 'Mua 5 mã cùng ngành không phải diversification.', 'Size = confidence × volatility × regime × liquidity.']),
('MODULE 9 — VOLATILITY MODELING', 'Lecture 19',
 'Volatility thay đổi theo thời gian và có clustering. Vol cao vừa là cơ hội vừa là nguy hiểm.',
 [('Realized volatility', 'biến động thực tế'), ('ATR%', 'biên dao động thực dụng'), ('Vol clustering', 'vol cao thường kéo dài'), ('GARCH intuition', 'vol động theo shock quá khứ')],
 ['Dùng atrPct/realizedVol20/bbWidth20.', 'Vol cao không tự động xấu; dùng cho sizing/stop/risk.', 'Backtest phải báo maxDrawdownAfterEntry.']),
('MODULE 10 — BLACK-SCHOLES, OPTIONS & CW', 'Lecture 21',
 'Option/CW phụ thuộc underlying, strike, time, rate, volatility. Cổ phiếu cơ sở tăng chưa chắc CW tốt nếu time decay/spread/break-even xấu.',
 [('S', 'giá tài sản cơ sở'), ('K', 'giá thực hiện'), ('T', 'thời gian còn lại'), ('σ', 'volatility'), ('Greeks', 'Delta/Gamma/Vega/Theta')],
 ['CW score = underlyingSignal + maturity + moneyness + breakEven + spread + liquidity + theta.', 'Không rank CW theo leverage đơn thuần.', 'Cảnh báo CW gần đáo hạn/spread rộng.']),
('MODULE 11 — AI, MACHINE LEARNING & EVENT MARKETS', 'Lecture 18 + 20 + 23',
 'ML chỉ tốt khi dữ liệu/label/validation tốt. Event markets nhắc ta quy đổi biến cố thành xác suất.',
 [('Label', 'mục tiêu training'), ('OOS', 'kiểm ngoài mẫu'), ('Calibration', 'xác suất có đáng tin không'), ('Event probability', 'giá/xác suất biến cố')],
 ['ML đầu tiên: logistic regression/GBM nhẹ.', 'Output pHitTarget và pLoss, không phán chắc.', 'Tin/event cần eventRiskFlag riêng.']),
('MODULE 12 — STOCHASTIC CALCULUS & SDE', 'Lecture 14 + 24 + 25',
 'Stochastic calculus là nền cho option/volatility/path modeling. Với stock ranking hằng ngày, dùng như tư duy scenario và risk path.',
 [('Brownian motion', 'nhiễu liên tục'), ('Ito lemma', 'đạo hàm cho quá trình ngẫu nhiên'), ('SDE', 'dS = μSdt + σSdW'), ('Path risk', 'đường đi quan trọng không kém điểm cuối')],
 ['Thêm scenario: bull/base/bear/stop/gap.', 'Tính timeToTarget/timeUnderWater nếu backtest.', 'Không ép SDE phức tạp vào model nếu chưa cần.'])]

for title, lec, summary, concepts, apps in module_text:
    story.append(PageBreak()); h1(title); P(f'<b>Nguồn:</b> {lec}', 'Body')
    h2('1. Bài học gốc')
    P(summary)
    h2('2. Khái niệm cần nhớ')
    tbl([['Khái niệm','Ý nghĩa']] + concepts, [4.2*cm, 11.4*cm])
    h2('3. Áp dụng vào LH Investment')
    for a in apps: bullet(a)

# Roadmap
story.append(PageBreak()); h1('MODULE 13 — ROADMAP TRAINING MODEL LH INVESTMENT')
P('Khi Hòa Đại ka bảo “em tự training model đi”, Tiểu đệ phải làm theo pipeline này, không nhảy thẳng vào ML.')
road=[['Phase','Việc làm','Output'],['1. Data','Cập nhật OHLCV, market/sector, pattern, SR','raw cache sạch'],['2. Feature Matrix','Tạo feature tại từng stock-date, past-only','research_feature_matrix_vn100.json'],['3. Leakage Audit','Kiểm rolling windows, label tách riêng','leakage_audit.md'],['4. Feature Report','Correlation, top/bottom quintile, regime','research_feature_training_report.json'],['5. Strategy Backtest','Rule rõ ràng, chronological OOS','EV/avgWin/avgLoss/profitFactor'],['6. Risk Layer','ATR stop, position sizing, sector/correlation','risk_adjusted_recommendations.json'],['7. ML nhẹ','Logistic/GBM, calibrated probability','pHitTarget/pLoss/modelConfidence'],['8. Production','Chỉ deploy khi anh cho phép','Firebase/cache update']]
tbl(road,[2.6*cm,7.3*cm,5.7*cm])

h2('Bảng output bắt buộc cho recommendation')
P('''{
  "symbol": "MWG",
  "horizon": "20d",
  "setup": "near_support_room_to_resistance",
  "pHitTarget6Pct": 0.0,
  "pLossMoreThan5Pct": 0.0,
  "expectedValue": 0.0,
  "avgWin": 0.0,
  "avgLoss": 0.0,
  "profitFactor": 0.0,
  "sampleSize": 0,
  "marketRegime": "",
  "volRegime": "",
  "positionSizeHint": "",
  "why": "",
  "wrongIf": ""
}'''.replace('\n','<br/>'), 'VNCodePretty')

h2('Kết luận thực chiến')
P('Bước đáng làm nhất hiện tại: <b>build rolling support/resistance features lịch sử</b>, sau đó backtest setup gần hỗ trợ + còn room tới kháng cự + volatility filter + market regime filter.', 'Quote')

OUT_MD.write_text('\n'.join(md), encoding='utf-8')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(font, 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.25*cm, 0.75*cm, 'MIT 18.642 Training Guide for LH Investment')
    canvas.drawRightString(19.7*cm, 0.75*cm, f'Trang {doc.page}')
    canvas.restoreState()

SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.2*cm, leftMargin=1.2*cm, topMargin=1.25*cm, bottomMargin=1.1*cm).build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT, OUT.stat().st_size)
print(OUT_MD, OUT_MD.stat().st_size)
