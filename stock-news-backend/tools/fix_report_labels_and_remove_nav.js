const fs=require('fs'),path=require('path');
const f=path.resolve(__dirname,'..','firebase_public','stock-report.html');
let s=fs.readFileSync(f,'utf8');
// User requested the entire pill navigation removed from this report page.
s=s.replace(/\s*<nav class="main-tabs"[\s\S]*?<\/nav>/,'');
// Backend historical job labels are mojibake. Render canonical Vietnamese labels by stable section key.
const old="function node(s){return `<div class=\"node ${cls(s.status)}\"><div style=\"display:flex;justify-content:space-between;gap:8px\"><div><div class=\"name\">${clean(s.name||s.key)}</div>";
const neu="const sectionLabels={news:'Tin tức & tác động',technical:'Chỉ báo LHInvestment / PTKT',fundamental:'Cơ bản & vĩ mô',scenario:'Kịch bản đầu tư',bull_bear:'Tăng giá / Giảm giá / Chất xúc tác',risk:'Rủi ro & quan điểm',followup:'Kế hoạch theo dõi',quick_summary:'Tóm tắt điều hành',word:'Xuất Word',notebooklm:'NotebookLM / PDF online'};\nfunction node(s){return `<div class=\"node ${cls(s.status)}\"><div style=\"display:flex;justify-content:space-between;gap:8px\"><div><div class=\"name\">${sectionLabels[s.key]||clean(s.name||s.key)}</div>";
if(!s.includes(old))throw new Error('node renderer marker not found');
s=s.replace(old,neu);
fs.writeFileSync(f,s,'utf8');
console.log('Removed report nav and canonicalized Vietnamese section labels');
