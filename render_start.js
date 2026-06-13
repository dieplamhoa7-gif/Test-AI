const fs = require('fs');
const path = require('path');

function firstExisting(candidates) {
  for (const p of candidates) {
    try { if (p && fs.existsSync(p)) return p; } catch (_) {}
  }
  return '';
}

function findPlaywrightChrome() {
  const roots = ['/ms-playwright', path.join(__dirname, 'node_modules', 'playwright-core', '.local-browsers')];
  const candidates = [];
  for (const root of roots) {
    try {
      for (const name of fs.readdirSync(root)) {
        if (/^chromium/.test(name)) candidates.push(path.join(root, name, 'chrome-linux', 'chrome'));
      }
    } catch (_) {}
  }
  candidates.push('/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser');
  return firstExisting(candidates);
}

process.env.NVTC_PROXY_PORT = process.env.PORT || process.env.NVTC_PROXY_PORT || '10000';
process.env.PYTHON = process.env.PYTHON || '/usr/bin/python3';
process.env.PYTHONIOENCODING = process.env.PYTHONIOENCODING || 'utf-8';
process.env.BDS_WEB_MODE = process.env.BDS_WEB_MODE || '1';
process.env.LANG = process.env.LANG || 'C.UTF-8';
process.env.LC_ALL = process.env.LC_ALL || 'C.UTF-8';
process.env.BDS_BROWSER_CDP = process.env.BDS_BROWSER_CDP || 'http://127.0.0.1:18800';
process.env.BDS_BROWSER_PROFILE = process.env.BDS_BROWSER_PROFILE || '/tmp/lh-bds-browser-profile';
process.env.BDS_CHROME_PATH = process.env.BDS_CHROME_PATH || findPlaywrightChrome();

console.log('[render_start] PORT=', process.env.NVTC_PROXY_PORT);
console.log('[render_start] BDS_CHROME_PATH=', process.env.BDS_CHROME_PATH || '(not found)');

require('./LH BDS/backend/nvtc_9router_proxy.js');
