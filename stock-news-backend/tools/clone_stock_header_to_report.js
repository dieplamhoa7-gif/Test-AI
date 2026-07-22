const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..', 'firebase_public');
const stockPath = path.join(root, 'stocks.html');
const reportPath = path.join(root, 'stock-report.html');
const stock = fs.readFileSync(stockPath, 'utf8');
let report = fs.readFileSync(reportPath, 'utf8');

function one(re, text, label) {
  const m = text.match(re);
  if (!m) throw new Error(`Cannot extract ${label}`);
  return m[0];
}
// Canonical source: the actual /stocks header and nav in production source.
const canonicalHeader = one(/<header class="topbar">[\s\S]*?<\/header>/, stock, 'stock header');
const canonicalNav = one(/<nav class="main-tabs">[\s\S]*?<\/nav>/, stock, 'stock navigation');
const canonicalBodyClass = one(/<body class="[^"]+">/, stock, 'stock body class');
const canonicalUnifiedCss = one(/\s*<link rel="stylesheet" href="\/assets\/lh-unified-ui\.css">/, stock, 'unified CSS link');

report = report.replace(/<body(?: class="[^"]*")?>/, canonicalBodyClass);
if (!report.includes('/assets/lh-unified-ui.css')) report = report.replace('</head>', `${canonicalUnifiedCss}\n</head>`);
const oldHeader = /<header class="topbar">[\s\S]*?<\/header>/;
if (!oldHeader.test(report)) throw new Error('Report header not found');
report = report.replace(oldHeader, canonicalHeader);
// Remove any prior report navigation/breadcrumb/ticker between header and report hero.
report = report.replace(/<nav class="main-tabs"[\s\S]*?<\/nav>/, canonicalNav);
report = report.replace(/\s*<div class="breadcrumb">[\s\S]*?<\/div>/, '');
report = report.replace(/\s*<div class="ticker">[\s\S]*?<\/div><\/div>/, '');
// Match /stocks shell width; this guarantees the same left/right alignment and header geometry.
report = report.replace(/\.shell\{width:min\(1360px,calc\(100% - 24px\)\)/g, '.shell{width:min(1180px,calc(100% - 24px))');
fs.writeFileSync(reportPath, report, 'utf8');
console.log('Cloned exact /stocks header, nav, unified UI class and CSS link into /stock-report');
