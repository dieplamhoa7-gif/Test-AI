const fs = require('fs');
const path = require('path');
const file = path.resolve(__dirname, '..', 'firebase_public', 'stock-report.html');
let s = fs.readFileSync(file, 'utf8');
const styleNeedle = '    .report-hero,.card,.out{';
const headerCss = `    /* Shared LH Investment header: aligned with /stocks */
    .topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border:1px solid var(--line);background:rgba(9,14,24,.85);border-radius:24px;box-shadow:var(--shadow);backdrop-filter:blur(18px);position:sticky;top:10px;z-index:20}.brand-wrap{display:flex;align-items:center;gap:14px;min-width:0}.brand-icon{width:56px;height:56px;flex:0 0 56px;border-radius:16px;overflow:hidden;background:#0f1522;border:1px solid rgba(100,181,255,.22);box-shadow:0 10px 24px rgba(100,181,255,.25)}.brand-icon img{width:100%;height:100%;object-fit:cover}.brand-text h1{margin:0;font-size:26px;letter-spacing:.04em;line-height:1.1}.brand-text p{margin:5px 0 0;color:var(--muted);font-size:12px;letter-spacing:.16em;font-weight:800}.top-actions{display:flex;align-items:center;gap:10px;flex-wrap:wrap;justify-content:flex-end}.lang-toggle{display:flex;gap:4px;padding:3px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.04)}.lang-btn{border:0;border-radius:999px;min-height:0;padding:6px 9px;background:transparent;color:var(--muted);font-weight:900;font-size:12px;cursor:pointer}.lang-btn.active{background:linear-gradient(135deg,var(--accent),#7a74ff);color:#06111f}.theme-toggle{display:inline-flex;align-items:center;gap:8px;min-height:0;border:1px solid var(--line);background:rgba(18,26,43,.92);color:var(--text);border-radius:999px;padding:10px 13px;font-size:13px;font-weight:800;cursor:pointer}.status-pill{border:1px solid rgba(78,240,192,.18);background:rgba(78,240,192,.08);color:var(--accent2);padding:10px 14px;border-radius:999px;font-size:13px;font-weight:800;white-space:nowrap}.breadcrumb{display:flex;gap:8px;align-items:center;margin-top:14px;color:var(--muted);font-size:13px}.breadcrumb a{color:#cfe0ff}.breadcrumb b{color:var(--accent2)}body.light-theme{--bg:#f4f7fb;--panel:#ffffff;--panel2:#eef3f9;--text:#132033;--muted:#607087;--line:rgba(38,61,99,.14);background:linear-gradient(180deg,#f7faff,#eef4fb)}body.light-theme .topbar{background:rgba(255,255,255,.88)}body.light-theme .theme-toggle,body.light-theme .lang-toggle{background:#fff}body.light-theme .report-hero,body.light-theme .card,body.light-theme .out{background:#fff}body.light-theme input{background:#fff;color:#132033}body.light-theme .logs pre,body.light-theme .metric,body.light-theme .agent,body.light-theme .node,body.light-theme .phase,body.light-theme .scope{background:#f5f8fc;color:#132033}@media(max-width:980px){.topbar{position:static}.top-actions{margin-top:12px;justify-content:flex-start}}@media(max-width:640px){.shell{width:min(100% - 16px,1360px)}.topbar{padding:12px;border-radius:18px}.brand-text h1{font-size:21px}.brand-text p{font-size:10px;letter-spacing:.12em}.brand-icon{width:46px;height:46px;flex-basis:46px}.status-pill{padding:8px 10px;font-size:12px}.theme-toggle{padding:8px 10px;font-size:12px}}
`;
if (!s.includes(headerCss.trim())) s = s.replace(styleNeedle, headerCss + styleNeedle);
const headerStart = s.indexOf('  <header class="topbar">');
const headerEnd = s.indexOf('  </header>', headerStart) + '  </header>'.length;
if (headerStart < 0 || headerEnd < 0) throw new Error('Existing header not found');
const header = `  <header class="topbar">
    <a class="brand-wrap" href="/stocks" aria-label="LH Investment - Trang chứng khoán">
      <div class="brand-icon"><img src="/assets/lh-logo.jpg" alt="LHInvestment logo" /></div>
      <div class="brand-text"><h1>LH INVESTMENT</h1><p>INVESTMENT INFORMATION</p></div>
    </a>
    <div class="top-actions">
      <div class="lang-toggle" aria-label="Ngôn ngữ"><button class="lang-btn active" id="langViBtn" type="button">VI</button><button class="lang-btn" id="langEnBtn" type="button">EN</button></div>
      <button class="theme-toggle" id="themeToggle" type="button" aria-label="Đổi giao diện">◐ Tối</button>
      <div class="status-pill" id="apiStatus">Online</div>
    </div>
  </header>`;
s = s.slice(0, headerStart) + header + s.slice(headerEnd);
const breadcrumb = `  <div class="breadcrumb"><a href="/stocks">Chứng khoán</a><span>/</span><b>Model3 Report</b></div>\n`;
if (!s.includes('class="breadcrumb"')) s = s.replace('  <div class="ticker">', breadcrumb + '  <div class="ticker">');
const scriptNeedle = "const BUILD='20260720-lhinvt-header-log-cleaner';";
const scriptAdd = `${scriptNeedle}
function applyTheme(theme){const light=theme==='light';document.body.classList.toggle('light-theme',light);const b=document.getElementById('themeToggle');if(b)b.textContent=light?'☼ Sáng':'◐ Tối';try{localStorage.setItem('hoa.theme',theme)}catch(_){}}
document.getElementById('themeToggle')?.addEventListener('click',()=>applyTheme(document.body.classList.contains('light-theme')?'dark':'light'));
try{applyTheme(localStorage.getItem('hoa.theme')||'dark')}catch(_){applyTheme('dark')}
document.getElementById('langViBtn')?.addEventListener('click',()=>{document.getElementById('langViBtn').classList.add('active');document.getElementById('langEnBtn').classList.remove('active')});
document.getElementById('langEnBtn')?.addEventListener('click',()=>{document.getElementById('langEnBtn').classList.add('active');document.getElementById('langViBtn').classList.remove('active')});`;
if (!s.includes('function applyTheme(theme)')) s = s.replace(scriptNeedle, scriptAdd);
fs.writeFileSync(file, s, 'utf8');
console.log('Updated shared-style header:', file);
