// Minimal browser-popup readers for Guland/QH Viet.
// Goal: avoid dead fallback by reading visible page text via shared Chrome CDP.

const path = require('path');
const { spawn } = require('child_process');

const DEFAULT_CDP = process.env.BDS_BROWSER_CDP || 'http://127.0.0.1:18800';
const DEFAULT_CHROME = process.env.BDS_CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const DEFAULT_PROFILE = process.env.BDS_BROWSER_PROFILE || path.join(__dirname, '.bds-browser-profile');

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }
async function cdpJson(p, options = {}) {
  const res = await fetch(`${DEFAULT_CDP}${p}`, options);
  if (!res.ok) throw new Error(`CDP HTTP ${res.status} ${p}`);
  return res.json();
}
let chromeStartedByBot = false;
async function ensureCdpBrowser() {
  try { await cdpJson('/json/version'); return true; } catch (_) {}
  if (chromeStartedByBot) return false;
  chromeStartedByBot = true;
  try {
    const child = spawn(DEFAULT_CHROME, [
      '--remote-debugging-port=18800',
      `--user-data-dir=${DEFAULT_PROFILE}`,
      '--no-first-run',
      '--disable-popup-blocking',
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      'about:blank',
    ], { detached: true, stdio: 'ignore' });
    child.unref();
    for (let i = 0; i < 20; i++) {
      await wait(500);
      try { await cdpJson('/json/version'); return true; } catch (_) {}
    }
    return false;
  } catch (_) { return false; }
}
async function openTab(url) {
  await ensureCdpBrowser();
  const r = await fetch(`${DEFAULT_CDP}/json/new?${encodeURIComponent(url)}`, { method: 'PUT' });
  if (!r.ok) throw new Error(`Không mở được tab Chrome: HTTP ${r.status}`);
  return r.json();
}
async function closeTab(id) { if (id) await fetch(`${DEFAULT_CDP}/json/close/${id}`).catch(() => null); }
function connectWs(wsUrl) {
  return new Promise((resolve, reject) => {
    const u = new URL(wsUrl);
    const key = Buffer.from(Math.random().toString(36).slice(2) + Date.now()).toString('base64').slice(0, 24);
    const net = require(u.protocol === 'wss:' ? 'tls' : 'net');
    const socket = net.connect({ host: u.hostname, port: Number(u.port) || 80 }, () => {
      socket.write([
        `GET ${u.pathname}${u.search} HTTP/1.1`, `Host: ${u.host}`,
        'Upgrade: websocket', 'Connection: Upgrade', `Sec-WebSocket-Key: ${key}`,
        'Sec-WebSocket-Version: 13', '', ''
      ].join('\r\n'));
    });
    let buf = Buffer.alloc(0), open = false, nextId = 1;
    const pending = new Map();
    function sendFrame(str) {
      const payload = Buffer.from(str); let header;
      if (payload.length < 126) header = Buffer.from([0x81, 0x80 | payload.length]);
      else if (payload.length < 65536) { header = Buffer.alloc(4); header[0]=0x81; header[1]=0x80|126; header.writeUInt16BE(payload.length,2); }
      else { header = Buffer.alloc(10); header[0]=0x81; header[1]=0x80|127; header.writeBigUInt64BE(BigInt(payload.length),2); }
      const mask = Buffer.from([1,2,3,4]); const out = Buffer.alloc(payload.length);
      for (let i=0;i<payload.length;i++) out[i]=payload[i]^mask[i%4];
      socket.write(Buffer.concat([header, mask, out]));
    }
    function parseFrames() {
      while (buf.length >= 2) {
        const b0=buf[0], b1=buf[1]; let len=b1&0x7f, off=2;
        if (len===126) { if (buf.length<4) return; len=buf.readUInt16BE(2); off=4; }
        else if (len===127) { if (buf.length<10) return; len=Number(buf.readBigUInt64BE(2)); off=10; }
        const masked=!!(b1&0x80), maskLen=masked?4:0;
        if (buf.length < off+maskLen+len) return;
        let payload=buf.slice(off+maskLen, off+maskLen+len);
        if (masked) { const m=buf.slice(off,off+4); payload=Buffer.from(payload.map((x,i)=>x^m[i%4])); }
        buf=buf.slice(off+maskLen+len);
        if ((b0&0x0f)===1) {
          let msg; try { msg=JSON.parse(payload.toString('utf8')); } catch { continue; }
          if (msg.id && pending.has(msg.id)) { const e=pending.get(msg.id); pending.delete(msg.id); msg.error?e.reject(new Error(JSON.stringify(msg.error))):e.resolve(msg.result); }
        }
      }
    }
    socket.on('data', d => {
      buf = Buffer.concat([buf, d]);
      if (!open) {
        const s = buf.toString('latin1'); const idx=s.indexOf('\r\n\r\n');
        if (idx >= 0) { open = true; buf = buf.slice(idx+4); resolve({ send(method, params={}) { const id=nextId++; sendFrame(JSON.stringify({id, method, params})); return new Promise((rs,rj)=>pending.set(id,{resolve:rs,reject:rj})); }, close() { socket.end(); } }); parseFrames(); }
      } else parseFrames();
    });
    socket.on('error', reject);
  });
}

async function readVisibleText(url, clickCenter = false) {
  const tab = await openTab(url);
  if (!tab.webSocketDebuggerUrl) throw new Error('Không có browser websocket');
  const cdp = await connectWs(tab.webSocketDebuggerUrl);
  try {
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Page.navigate', { url });
    await wait(7000);
    if (clickCenter) {
      try {
        await cdp.send('Input.dispatchMouseEvent', { type: 'mousePressed', x: 640, y: 360, button: 'left', clickCount: 1 });
        await cdp.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: 640, y: 360, button: 'left', clickCount: 1 });
        await wait(3000);
      } catch (_) {}
    }
    const expr = `(() => {
      const body = (document.body && document.body.innerText) ? document.body.innerText : '';
      return body.slice(0, 12000);
    })()`;
    const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true });
    return String(res.result?.value || '');
  } finally {
    cdp.close();
    await closeTab(tab.id).catch(() => null);
  }
}

function summarizeText(text, label) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  if (!t) return { text: `${label}: không đọc được nội dung hiển thị.`, degraded: true };
  return { text: `${label}: ${t.slice(0, 3000)}`, degraded: false };
}

async function readGulandPopupText(lat, lon) {
  // Guland needs a real browser click on the Leaflet marker; passive body text is mostly listings.
  const { chromium } = require('playwright');
  await ensureCdpBrowser();
  const url = `https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lon}`;
  const browser = await chromium.connectOverCDP(DEFAULT_CDP);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(12000);
    await page.evaluate(async ({ lat, lon }) => {
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      const map = window.map || (typeof window.get_map === 'function' ? window.get_map() : null);
      if (map && map.setView) {
        map.setView([lat, lon], 19);
        await sleep(2500);
        if (window.main_marker && window.main_marker.setLatLng) window.main_marker.setLatLng([lat, lon]);
        await sleep(1000);
        try { if (window.main_marker && window.main_marker.fire) window.main_marker.fire('click'); } catch (_) {}
        await sleep(5000);
      }
    }, { lat, lon });
    const marker = page.locator('.leaflet-marker-icon.leaflet-marker-draggable').first();
    if (await marker.count()) {
      await marker.click({ timeout: 10000, force: true }).catch(() => null);
      await page.waitForTimeout(5000);
    }
    const text = await page.locator('body').innerText({ timeout: 10000 });
    return summarizeText(text, 'Guland popup/browser');
  } finally {
    await page.close().catch(() => null);
    await browser.close().catch(() => null);
  }
}

function slugVi(s) {
  return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
}

function stripHtml(html) {
  return String(html || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

async function readQhVietPopupText(lat, lon, location = {}) {
  // QH Việt 2026 uses a Vue single-page map for the new 2-level HCMC admin flow.
  // Playwright drives the logged-in Chrome profile through CDP, then calls the same
  // Vue methods the old Quyhoach bot used: selectProvince -> selectWard -> checkparcel.gapply().
  const { chromium } = require('playwright');
  await ensureCdpBrowser();
  const targetWard = String(location.ward || location.suburb || 'Phường Tân Định').trim();
  const url = 'https://qhviet.com/quy-hoach/thanh-pho-ho-chi-minh-hanh-chinh-2-cap';
  const browser = await chromium.connectOverCDP(DEFAULT_CDP);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(7000);
    const out = await page.evaluate(async ({ lat, lon, targetWard }) => {
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      const app = document.querySelector('#app') && document.querySelector('#app').__vue__;
      const lvl = app && app.$refs && app.$refs['app-map'] && app.$refs['app-map'].$refs['province-box'] && app.$refs['app-map'].$refs['province-box'].$refs['province-level-2'];
      if (!app || !lvl) return { error: 'Không thấy Vue province-level-2 của QH Việt', body: document.body?.innerText || '' };
      const hcm = (lvl.provinces || []).find(p => /Hồ Chí Minh|Ho Chi Minh/i.test(p.name || ''));
      if (!hcm) return { error: 'Không tìm thấy TP.HCM trong QH Việt', body: document.body?.innerText || '' };
      lvl.selectProvince(hcm);
      await sleep(5000);
      const norm = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase();
      const want = norm(targetWard);
      const ward = (lvl.wards || []).find(w => norm(w.name) === want) || (lvl.wards || []).find(w => norm(w.name).includes(want.replace(/^phuong\s+|^xa\s+/, '')));
      if (!ward) return { error: `Không tìm thấy phường/xã QH Việt: ${targetWard}`, wards: (lvl.wards || []).map(w => w.name).slice(0, 220), body: document.body?.innerText || '' };
      lvl.selectWard(ward);
      await sleep(5000);
      // This mirrors the real user action: click the map/point after selecting the new ward.
      // It populates the right-side "Thông tin thửa" panel and app-map.parcel.plan_info.
      lvl.accessPointPosition({ lat, lng: lon });
      await sleep(18000);
      const map = app.$refs && app.$refs['app-map'];
      const parcel = map && map.parcel;
      const rows = [];
      if (parcel && Array.isArray(parcel.properties)) rows.push(...parcel.properties);
      if (parcel && Array.isArray(parcel.plan_info)) {
        for (const p of parcel.plan_info) {
          if (p.name) rows.push(`Quy hoạch: ${p.name}`);
          if (p.num_code) rows.push(`Loại đất: ${p.num_code}`);
          if (Array.isArray(p.info)) {
            for (const item of p.info) {
              try {
                const o = typeof item === 'string' ? JSON.parse(item) : item;
                if (o && o.label) rows.push(`${o.label}: ${o.value ?? ''}`);
              } catch (_) { rows.push(String(item)); }
            }
          }
        }
      }
      return { province: hcm.name, ward: ward.name, ward_id: ward.id, rows, body: document.body?.innerText || '' };
    }, { lat, lon, targetWard });
    const rowsText = Array.isArray(out && out.rows) ? out.rows.map(stripHtml).filter(Boolean).join('\n') : '';
    const bodyText = String((out && out.body) || '').slice(0, 6000);
    const meta = out && out.error ? `Lỗi: ${out.error}\n` : `Khu vực mới: ${out.ward || targetWard}, Thành phố Hồ Chí Minh\n`;
    return summarizeText(`${meta}${rowsText}\n${bodyText}`, 'QH Việt browser');
  } finally {
    await page.close().catch(() => null);
    await browser.close().catch(() => null);
  }
}

module.exports = { readGulandPopupText, readQhVietPopupText };
