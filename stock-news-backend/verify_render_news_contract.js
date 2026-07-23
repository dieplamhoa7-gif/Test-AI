const fs = require('fs');
const p = require('path').join(__dirname, 'render_node_server.js');
const s = fs.readFileSync(p, 'utf8');
const required = [
  'LH_NEWS_FORMAT_V2_LOCKED',
  'summaryBullets',
  'async function refreshNewsCache',
  "url.searchParams.get('refresh')",
  "status: 'render-node-rss-refresh'",
];
const missing = required.filter(x => !s.includes(x));
if (missing.length) {
  console.error('Render news contract FAILED:', missing.join(', '));
  process.exit(1);
}
console.log('Render news contract OK: refresh + locked format');
