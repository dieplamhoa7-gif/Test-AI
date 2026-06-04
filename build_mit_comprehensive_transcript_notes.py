from pathlib import Path
import json, re, math
from playwright.sync_api import sync_playwright

SUM=json.loads(Path('mit_18_642_transcripts_summary.json').read_text(encoding='utf-8'))
OUT_HTML=Path('reports/MIT_18_642_Comprehensive_Transcript_Notes_VI.html')
OUT_MD=Path('reports/MIT_18_642_Comprehensive_Transcript_Notes_VI.md')
OUT_PDF=Path('reports/MIT_18_642_Comprehensive_Transcript_Notes_VI.pdf')

NOISE={'[SQUEAKING]','[RUSTLING]','[CLICKING]','[APPLAUSE]','[LAUGHTER]','[MUSIC]'}
KEYWORDS={
 'linear algebra':['vector','matrix','linear','eigen','basis','rank','singular','svd','covariance','correlation'],
 'probability':['probability','random','distribution','expectation','variance','conditional','normal','gaussian','martingale'],
 'stochastic processes':['stochastic','process','brownian','wiener','markov','random walk','gambler'],
 'regression':['regression','least squares','ols','residual','coefficient','r squared','factor'],
 'pca':['principal component','pca','eigenvalue','eigenvector','component'],
 'rates/bonds':['bond','yield','interest rate','duration','convexity','coupon','discount','forward','swap','sofr','libor'],
 'portfolio/risk':['portfolio','optimization','risk','var','cvar','covariance','counterparty','exposure','collateral'],
 'volatility':['volatility','garch','arch','variance','implied','realized'],
 'black-scholes/options':['black-scholes','option','call','put','risk neutral','delta','gamma','vega','theta'],
 'machine learning':['machine learning','ai','training','test','classification','neural','model','feature'],
 'event markets':['event','contract','exchange','kalshi','probability'],
 'stochastic calculus':['ito','calculus','sde','differential equation','brownian','lemma']
}

def clean(t):
    t=re.sub(r'\[[A-Z ]+\]',' ',t)
    t=re.sub(r'\s+',' ',t).strip()
    return t

def mmss(sec):
    m=int(sec//60); s=int(sec%60); return f'{m:02d}:{s:02d}'

def chunks(rows, target_words=420):
    out=[]; cur=[]; start=None; words=0
    for r in rows:
        tx=clean(r.get('text',''))
        if not tx: continue
        if start is None: start=float(r.get('start',0))
        cur.append(tx); words += len(tx.split())
        if words>=target_words:
            out.append((start, ' '.join(cur)))
            cur=[]; start=None; words=0
    if cur: out.append((start or 0,' '.join(cur)))
    return out

def pick_topics(text):
    low=text.lower(); scores=[]
    for topic, kws in KEYWORDS.items():
        sc=sum(low.count(k) for k in kws)
        if sc: scores.append((sc,topic))
    return [t for _,t in sorted(scores, reverse=True)[:5]]

def representative_sentences(text, max_n=12):
    sents=re.split(r'(?<=[.!?])\s+', text)
    scored=[]
    for s in sents:
        ss=s.strip()
        if len(ss)<45 or len(ss)>260: continue
        low=ss.lower()
        score=0
        for kws in KEYWORDS.values():
            score += sum(1 for k in kws if k in low)
        score += 1 if any(x in low for x in ['so ', 'therefore', 'for example', 'important', 'model', 'finance']) else 0
        if score>0: scored.append((score,ss))
    seen=[]
    for _,s in sorted(scored, reverse=True):
        if s not in seen: seen.append(s)
        if len(seen)>=max_n: break
    return seen

def vi_explain(title, topics):
    base='Bài này trong MIT 18.642 tập trung vào việc xây một mảnh ghép của tư duy toán tài chính. Khi đọc transcript, nên chú ý cách giảng viên đi từ khái niệm nền, đặt giả định, rồi dùng mô hình để giải thích sản phẩm hoặc hiện tượng tài chính.'
    add=[]
    if 'rates/bonds' in topics: add.append('Trọng tâm liên quan lãi suất/trái phiếu: chiết khấu, yield, đường cong lãi suất, duration hoặc sản phẩm rates. Đây là nền cho định giá dòng tiền và hiểu môi trường lãi suất.')
    if 'linear algebra' in topics: add.append('Phần đại số tuyến tính giúp biểu diễn tài sản/danh mục/dữ liệu bằng vector và ma trận, là nền cho PCA, covariance và tối ưu danh mục.')
    if 'probability' in topics: add.append('Phần xác suất nhắc rằng kết quả tài chính là phân phối khả năng, không phải một con số chắc chắn.')
    if 'stochastic processes' in topics: add.append('Phần quá trình ngẫu nhiên xem giá là đường đi theo thời gian, nên drawdown, hitting time và thứ tự dữ liệu rất quan trọng.')
    if 'regression' in topics: add.append('Phần hồi quy dùng để kiểm định quan hệ giữa biến giải thích và kết quả, nhưng phải cảnh giác overfit và in-sample bias.')
    if 'pca' in topics: add.append('PCA giúp tìm factor chính và giảm trùng lặp dữ liệu, rất hữu ích khi nhiều indicator kể cùng một câu chuyện.')
    if 'portfolio/risk' in topics: add.append('Phần danh mục/risk nhấn mạnh rằng chọn mã tốt chưa đủ; correlation, concentration và sizing quyết định rủi ro thực tế.')
    if 'volatility' in topics: add.append('Volatility modeling cho thấy biến động thay đổi theo thời gian và ảnh hưởng trực tiếp đến risk, sizing và option/CW.')
    if 'black-scholes/options' in topics: add.append('Black-Scholes và risk-neutral valuation là nền để hiểu option/CW: thời gian, volatility và moneyness quan trọng không kém hướng đi của underlying.')
    if 'machine learning' in topics: add.append('ML chỉ nên dùng sau khi feature, label và validation sạch; trong tài chính, overfit là rủi ro trung tâm.')
    return ' '.join([base]+add)

css='''@page{size:A4;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Arial,Segoe UI,sans-serif;color:#111827}.page{width:210mm;min-height:297mm;padding:15mm 16mm;page-break-after:always;position:relative}.cover{min-height:297mm;background:radial-gradient(circle at 20% 12%,#60a5fa,transparent 26%),linear-gradient(135deg,#020617,#0f2d5c 50%,#111827);color:white;display:flex;flex-direction:column;justify-content:center}.cover h1{font-size:40px;line-height:1.05;margin:18px 0}.cover h2{font-size:21px;font-weight:400;opacity:.9}.badge{display:inline-block;width:max-content;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:7px 12px;font-size:11px;letter-spacing:.08em}.video{border-top:8px solid #2563eb}.head{border-bottom:2px solid #e5e7eb;padding-bottom:9px;margin-bottom:12px}.kicker{font-size:11px;color:#2563eb;font-weight:900;letter-spacing:.06em}.title{font-size:24px;font-weight:900;color:#0f172a;line-height:1.12}.meta{color:#64748b;font-size:11px;margin-top:4px}.box{border:1px solid #e5e7eb;border-radius:15px;padding:11px 12px;margin:10px 0;background:white;box-shadow:0 4px 14px rgba(15,23,42,.04)}h3{margin:0 0 7px;color:#1d4ed8;font-size:15px}p,li{font-size:12.5px;line-height:1.58}.topics span{display:inline-block;background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af;border-radius:999px;padding:5px 8px;margin:3px;font-size:10.5px;font-weight:700}.quote{background:#f8fafc;border-left:4px solid #64748b;padding:8px 10px;border-radius:10px;margin:6px 0;font-size:11.7px;color:#334155}.time{color:#2563eb;font-weight:800}.chunk{border-left:3px solid #93c5fd;padding-left:10px;margin:8px 0}.footer{position:absolute;bottom:8mm;left:16mm;right:16mm;display:flex;justify-content:space-between;color:#64748b;font-size:10px}.tocgrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.tocitem{border:1px solid #e5e7eb;border-radius:12px;padding:8px;font-size:11px}.tocitem b{display:block;color:#0f172a;margin-bottom:3px}'''

html=['<!doctype html><html><head><meta charset="utf-8"><title>MIT Comprehensive Notes</title><style>'+css+'</style></head><body>']
md=['# MIT 18.642 — Comprehensive Transcript Notes tiếng Việt\n']
html.append('<section class="page cover"><div class="badge">MIT 18.642 · 22 VIDEO TRANSCRIPTS · COMPREHENSIVE NOTES</div><h1>Ghi chú đầy đủ theo transcript<br/>cho Hòa Đại ka</h1><h2>Bám sát thứ tự nội dung video: mục tiêu, chủ đề, diễn giải, timeline, câu transcript tiêu biểu, điểm cần nhớ.</h2><div class="footer"><span>Prepared by Tiểu đệ</span><span>Comprehensive Transcript Notes</span></div></section>')
toc=''.join(f'<div class="tocitem"><b>{i:02d}. {x["title"]}</b>{x["chars"]:,} ký tự transcript</div>' for i,x in enumerate(SUM,1))
html.append(f'<section class="page"><h1>Mục lục 22 video</h1><div class="tocgrid">{toc}</div><div class="footer"><span>Mục lục</span><span>22 videos</span></div></section>')

for i,item in enumerate(SUM,1):
    data=json.loads(Path(item['path']).read_text(encoding='utf-8'))
    rows=data['rows']
    full=' '.join(clean(r.get('text','')) for r in rows if clean(r.get('text','')))
    topics=pick_topics(full)
    reps=representative_sentences(full, 10)
    ch=chunks(rows, 520)
    # limit very long videos but keep substantial timeline
    timeline=[]
    step=max(1, math.ceil(len(ch)/10))
    for idx,(st,txt) in enumerate(ch[::step][:10],1):
        words=txt.split()
        excerpt=' '.join(words[:85]) + ('...' if len(words)>85 else '')
        timeline.append((st, excerpt))
    topic_html=''.join(f'<span>{t}</span>' for t in topics)
    reps_html=''.join(f'<div class="quote">“{q}”</div>' for q in reps[:8])
    time_html=''.join(f'<div class="chunk"><span class="time">{mmss(st)}</span> — {ex}</div>' for st,ex in timeline)
    explain=vi_explain(item['title'], topics)
    html.append(f'''<section class="page video"><div class="head"><div class="kicker">VIDEO {i:02d} · {item['id']} · {item['chars']:,} transcript chars</div><div class="title">{item['title']}</div><div class="meta">Source transcript: {item['path']}</div></div><div class="box"><h3>1. Chủ đề nhận diện trong video</h3><div class="topics">{topic_html}</div></div><div class="box"><h3>2. Giảng lại đầy đủ ý chính</h3><p>{explain}</p><p>Đọc video này nên theo mạch: giảng viên giới thiệu vấn đề, xây khái niệm, đưa công cụ toán hoặc mô hình, rồi nối sang ứng dụng tài chính. Các ví dụ và thuật ngữ trong transcript được giữ theo đúng tinh thần bài giảng thay vì biến thành khuyến nghị đầu tư.</p></div><div class="box"><h3>3. Timeline nội dung theo transcript</h3>{time_html}</div><div class="box"><h3>4. Câu/ý tiêu biểu từ transcript</h3>{reps_html}</div><div class="box"><h3>5. Điểm cần ghi nhớ</h3><ul><li>Hiểu khái niệm và giả định trước khi dùng công thức.</li><li>Phân biệt mô hình giải thích quá khứ với mô hình dự báo tương lai.</li><li>Trong tài chính, phải luôn hỏi rủi ro, xác suất, chi phí và điều kiện mô hình sai.</li></ul></div><div class="footer"><span>MIT 18.642 Comprehensive Notes</span><span>Video {i:02d}</span></div></section>''')
    md.append(f'\n## Video {i:02d} — {item["title"]}\n')
    md.append(f'- Transcript: `{item["path"]}` ({item["chars"]:,} chars)')
    md.append('\n### Chủ đề\n'+'; '.join(topics))
    md.append('\n### Giảng lại\n'+explain)
    md.append('\n### Timeline\n'+'\n'.join(f'- {mmss(st)} — {ex}' for st,ex in timeline))
    md.append('\n### Câu tiêu biểu\n'+'\n'.join(f'> {q}' for q in reps[:8]))

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
