from pathlib import Path
import re
p = Path('firebase_public/stock-report.html')
s = p.read_text(encoding='utf-8', errors='replace')
# Ensure nav CSS exists (matches stock page pill header in screenshot)
css = ".main-tabs{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap}.chip-btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;border:1px solid var(--line);background:rgba(18,26,43,.92);color:var(--text);border-radius:999px;padding:11px 14px;font-size:13px;font-weight:700;cursor:pointer;transition:transform .14s ease,border-color .14s ease}.chip-btn:hover{transform:translateY(-1px);border-color:rgba(100,181,255,.38)}.chip-btn.active{background:linear-gradient(135deg,var(--accent),#7a74ff);border-color:transparent;color:#06111f}body.light-theme .chip-btn{background:#fff}body.light-theme .chip-btn.active{background:linear-gradient(135deg,var(--accent),#7a74ff)}"
if '.main-tabs{' not in s:
    s = s.replace('/* Shared LH Investment header: aligned with /stocks */', css + '\n    /* Shared LH Investment header: aligned with /stocks */')
header = '''<header class="topbar"><a class="brand-wrap" href="/stocks"><div class="brand-icon"><img src="/assets/lh-logo.jpg" alt="LHInvestment logo" /></div><div class="brand-text"><h1>LH INVESTMENT</h1><p>INVESTMENT INFORMATION</p></div></a><nav class="main-tabs" aria-label="Điều hướng chính"><a class="chip-btn" href="/stocks">Chứng Khoán</a><a class="chip-btn" href="/macro">Vĩ mô</a><a class="chip-btn" href="/cw">Chứng Quyền</a><a class="chip-btn" href="/news-page">Tin Tức</a><a class="chip-btn active" href="/stock-report" aria-current="page">Báo cáo cổ phiếu</a><a class="chip-btn" href="/account">Account</a></nav><div class="top-actions"><div class="lang-toggle"><button class="lang-btn active" id="langViBtn" type="button">VI</button><button class="lang-btn" id="langEnBtn" type="button">EN</button></div><button class="theme-toggle" id="themeToggle" type="button">🌙 Tối</button><div class="status-pill" id="apiStatus">Online</div></div></header>'''
# Replace current header and remove any standalone nav immediately after it.
s = re.sub(r'<header class="topbar".*?</header>\s*(?:<nav class="main-tabs".*?</nav>\s*)?', header + '\n', s, count=1, flags=re.S)
# Layout adjustment: screenshot has logo, nav, controls on one row; allow nav in header center.
extra = '.topbar .main-tabs{margin-top:0;flex:1;justify-content:flex-end}.topbar .chip-btn{min-height:40px;padding:9px 13px}.topbar .top-actions{flex:0 0 auto}@media(max-width:1180px){.topbar{flex-wrap:wrap}.topbar .main-tabs{order:3;flex-basis:100%;justify-content:flex-start}}'
if '.topbar .main-tabs{margin-top:0' not in s:
    s = s.replace('</style>', extra + '\n  </style>')
p.write_text(s, encoding='utf-8')
