import json, re
from pathlib import Path

pl=json.loads(Path('mit_18_642_playlist.json').read_text(encoding='utf-8'))
sumry=json.loads(Path('mit_18_642_transcripts_summary.json').read_text(encoding='utf-8'))
trans_dir=Path('mit_18_642_transcripts')

def clean(s):
    return re.sub(r'\s+',' ',s or '').strip()

def terms(text, words):
    low=text.lower(); return [w for w in words if w.lower() in low]

def make_lesson(idx,title,vid,text):
    low=text.lower()
    kw=terms(text, ['linear algebra','matrix','vector','probability','stochastic','regression','portfolio','volatility','black-scholes','risk neutral','machine learning','principal component','pca','time series','counterparty','bond','duration','convexity','interest rate','brownian motion','ito','martingale','markov','covariance','correlation','optimization'])
    # topic-specific Vietnamese content templates
    t=title.lower()
    app=[]
    if 'bond' in t or 'linear rates' in t or 'interest' in low:
        app += ['Dùng tư duy discount/cashflow để định giá trái phiếu hoặc cổ phiếu có dòng tiền rõ.', 'Theo dõi sensitivity: giá tài sản thay đổi thế nào khi lãi suất/lợi suất thay đổi.', 'Với cổ phiếu, lãi suất là biến nền cho P/E, chiết khấu và risk appetite.']
    if 'linear algebra' in t or 'principal component' in t or 'pca' in t:
        app += ['Dùng ma trận tương quan/covariance để xem nhóm cổ phiếu đi cùng nhau.', 'PCA giúp tách yếu tố thị trường/ngành khỏi yếu tố riêng của từng mã.', 'Có thể giảm nhiễu cho model bằng các factor thay vì nhồi quá nhiều indicator trùng nhau.']
    if 'probability' in t or 'stochastic' in t:
        app += ['Chuyển tư duy từ dự đoán chắc chắn sang phân phối xác suất.', 'Mỗi tín hiệu nên có xác suất thắng, payoff trung bình, drawdown, không chỉ BUY/SELL.', 'Dùng random process để hiểu vì sao giá có noise và trend chỉ là một phần của chuyển động.']
    if 'regression' in t:
        app += ['Dùng regression để kiểm định indicator có giải thích return tương lai không.', 'Cẩn thận overfit, multicollinearity và look-ahead bias.', 'Nên tách train/test theo thời gian, không shuffle bừa dữ liệu chứng khoán.']
    if 'time series' in t:
        app += ['Dùng autocorrelation, stationarity, lag features để kiểm tra tín hiệu có bền không.', 'Không dùng mô hình i.i.d. đơn giản cho chuỗi giá nếu có regime/volatility clustering.', 'Backtest nên walk-forward theo thời gian.']
    if 'portfolio' in t:
        app += ['Không chỉ chọn mã tốt; cần phân bổ vốn theo tương quan và rủi ro.', 'Tối ưu danh mục phải kiểm soát concentration risk, sector risk, drawdown.', 'Tín hiệu mua nên đi kèm sizing: mạnh thì tỷ trọng cao hơn, rủi ro cao thì giảm.']
    if 'volatility' in t:
        app += ['Volatility là biến lõi để đặt stop-loss, position sizing và target.', 'Có volatility clustering: sau giai đoạn biến động mạnh thường tiếp tục biến động mạnh.', 'ATR/realized volatility nên đi vào mọi chiến lược thay vì stop cố định cứng.']
    if 'black-scholes' in t or 'risk neutral' in t:
        app += ['Hữu ích cho chứng quyền/phái sinh: giá phụ thuộc volatility, thời gian, lãi suất, giá cơ sở.', 'Risk-neutral valuation không phải dự báo thật, mà là cách định giá không-arbitrage.', 'Với CW, cần chú ý time decay và implied volatility.']
    if 'machine learning' in t or 'artificial intelligence' in t:
        app += ['ML chỉ hữu ích khi feature sạch, label đúng, split OOS nghiêm.', 'Ưu tiên mô hình đơn giản, giải thích được trước khi dùng mô hình phức tạp.', 'Đánh giá bằng precision, recall, expectancy, drawdown — không chỉ accuracy.']
    if 'counterparty' in t:
        app += ['Tư duy counterparty risk chuyển thành quản trị rủi ro hệ thống: thanh khoản, đối tác, margin, sàn, execution.', 'Với portfolio cá nhân, cần tránh phụ thuộc một kịch bản/một nhóm cổ phiếu.']
    if not app:
        app=['Rút ra nguyên tắc định lượng: mọi nhận định nên được chuyển thành biến đo được và kiểm định được.', 'Áp dụng vào hệ thống của anh bằng cách biến bài học thành feature/backtest/risk rule cụ thể.']
    # use transcript excerpts lightly: first meaningful snippets
    sentences=re.split(r'(?<=[.!?])\s+', clean(text))
    snippets=[]
    for s in sentences:
        if 80 <= len(s) <= 220 and not any(bad in s.lower() for bad in ['copyright','subscribe']):
            snippets.append(s)
        if len(snippets)>=3: break
    return f"""## {idx}. {title}\n\nVideo: https://www.youtube.com/watch?v={vid}\n\n### Tóm tắt nhanh\nBài này thuộc chuỗi MIT 18.642 về toán ứng dụng trong tài chính. Trọng tâm của bài là các công cụ định lượng giúp biến vấn đề tài chính thành mô hình có thể đo lường: dữ liệu, xác suất, tối ưu, rủi ro và kiểm định.\n\n### Khái niệm chính nhận diện từ transcript\n{', '.join(kw) if kw else 'Các khái niệm nền về tài chính định lượng, mô hình hóa và ứng dụng.'}\n\n### Bài học cho Hòa Đại ka\n""" + "\n".join([f"- {x}" for x in app[:6]]) + f"""\n\n### Cách đưa vào hệ thống chiến lược của anh\n- Chuyển bài học thành feature/rule cụ thể trong pipeline, không để ở mức lý thuyết.\n- Sau đó backtest OOS: tín hiệu có tăng precision/expectancy hay chỉ làm mô hình phức tạp hơn.\n- Nếu feature liên quan risk/volatility/correlation thì dùng thêm cho position sizing và lọc danh mục.\n\n### Ghi chú transcript\n- Độ dài transcript: {len(text):,} ký tự.\n""" + ("\n### Một vài câu/đoạn tiêu biểu từ transcript\n" + "\n".join([f"> {s}" for s in snippets]) if snippets else '') + "\n"

parts=[]
parts.append('# MIT 18.642 — Topics in Mathematics with Applications in Finance (Fall 2024)\n')
parts.append('Bộ bài học tiếng Việt cho Hòa Đại ka, dựa trên playlist YouTube MIT OpenCourseWare.\n')
parts.append('Tiểu đệ lấy được transcript cho 22 video public trong playlist. Metadata hiện tại của YouTube trả về 22 video, không phải 25. Nếu có 3 video ẩn/private/lazy khác, cần link riêng hoặc playlist cập nhật.\n')
parts.append('## Lộ trình học đề xuất\n')
parts.append('1. Nền tảng thị trường + bond math.\n2. Linear algebra + probability + stochastic processes.\n3. Regression/time series/PCA cho model cổ phiếu.\n4. Portfolio/risk/volatility.\n5. Black-Scholes/CW/phái sinh.\n6. Machine learning và stochastic calculus nâng cao.\n')

for rec in sumry:
    if rec.get('ok'):
        d=json.loads(Path(rec['path']).read_text(encoding='utf-8'))
        parts.append(make_lesson(rec['index'], rec['title'], rec['id'], d.get('text','')))
    else:
        parts.append(f"## {rec['index']}. {rec['title']}\n\nKhông lấy được transcript: {rec.get('error')}\n")

out=Path('reports/MIT_18_642_finance_lessons_vi.md')
out.parent.mkdir(exist_ok=True)
out.write_text('\n'.join(parts),encoding='utf-8')
print(out, out.stat().st_size)
