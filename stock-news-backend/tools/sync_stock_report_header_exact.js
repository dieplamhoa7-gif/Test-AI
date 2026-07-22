const fs=require('fs'),path=require('path');
const f=path.resolve(__dirname,'..','firebase_public','stock-report.html');
let s=fs.readFileSync(f,'utf8');
// Add the exact stock-page navigation row and remove report-only breadcrumb/ticker variants.
s=s.replace(/\s*<div class="breadcrumb">[\s\S]*?<\/div>\s*<div class="ticker">[\s\S]*?<\/div><\/div>\s*/,
`\n  <nav class="main-tabs" aria-label="Điều hướng chính">
    <a class="chip-btn" href="/stocks">Chứng Khoán</a>
    <a class="chip-btn" href="/macro">Vĩ mô</a>
    <a class="chip-btn" href="/cw">Chứng Quyền</a>
    <a class="chip-btn" href="/news-page">Tin Tức</a>
    <a class="chip-btn active" href="/stock-report" aria-current="page">Báo cáo cổ phiếu</a>
    <a class="chip-btn" href="/account">Account</a>
  </nav>\n\n`);
const needle='    /* Shared LH Investment header: aligned with /stocks */';
const css=`    .main-tabs{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap}.chip-btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;border:1px solid var(--line);background:rgba(18,26,43,.92);color:var(--text);border-radius:999px;padding:11px 14px;font-size:13px;font-weight:700;cursor:pointer;transition:transform .14s ease,border-color .14s ease}.chip-btn:hover{transform:translateY(-1px);border-color:rgba(100,181,255,.38)}.chip-btn.active{background:linear-gradient(135deg,var(--accent),#7a74ff);border-color:transparent;color:#06111f}body.light-theme .chip-btn{background:#fff}body.light-theme .chip-btn.active{background:linear-gradient(135deg,var(--accent),#7a74ff)}\n`;
if(!s.includes('.main-tabs{display:flex'))s=s.replace(needle,css+needle);
// Match stock page content width exactly.
s=s.replace(/\.shell\{width:min\(1360px,calc\(100% - 24px\)\)/g,'.shell{width:min(1180px,calc(100% - 24px))');
fs.writeFileSync(f,s,'utf8');
console.log('Exact stock header/nav synchronized');
