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
      // Keep Chrome visible/non-headless. Guland/Cloudflare blocks headless automation.
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
  if (!r.ok) throw new Error(`KhÃ´ng má»Ÿ Ä‘Æ°á»£c tab Chrome: HTTP ${r.status}`);
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
  if (!tab.webSocketDebuggerUrl) throw new Error('KhÃ´ng cÃ³ browser websocket');
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

function stripHtml(x) {
  return String(x || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim();
}

function summarizeText(text, label) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  if (!t) return { text: `${label}: không đọc được nội dung hiển thị.`, degraded: true };
  return { text: `${label}: ${t.slice(0, 3000)}`, degraded: false };
}

async function readGulandPopupText(lat, lon) {
  // Improved Guland scraper using Playwright + CDP
  const { chromium } = require('playwright');
  await ensureCdpBrowser();
  // Direct ?lat=&lng= can be ignored/redirected and now often hits Cloudflare verification.
  // Older working flow: open HCMC planning page, then force Leaflet map + main_marker to exact coordinate.
  const url = `https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lon}`;
  const browser = await chromium.connectOverCDP(DEFAULT_CDP);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = await context.newPage();
  try {
    console.log(`[Guland] Navigating to ${url}`);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Wait for map to be interactive
    await page.waitForSelector('.leaflet-container, #map, .map', { timeout: 12000 }).catch(() => {});
    await page.waitForTimeout(2500);

    // Force Leaflet/Guland globals to the exact coordinate. Do not create a new L.map(); use page globals only.
    await page.evaluate(async ({ lat, lon }) => {
      const sleep = (ms) => new Promise(r => setTimeout(r, ms));
      const maps=[];
      for (const k of Object.keys(window)) {
        let v;
        try { v = window[k]; } catch (_) { continue; }
        try { if (v && typeof v==='object' && typeof v.setView==='function' && typeof v.getCenter==='function') maps.push(v); } catch (_) {}
      }
      const map = window.map || window.guland_map || window.map_view || window.main_map || maps[0];
      if (map && typeof map.setView === 'function') {
        try { map.setView([lat, lon], 19); } catch(e) {}
      }
      if (window.main_marker && typeof window.main_marker.setLatLng === 'function') {
        try { window.main_marker.setLatLng([lat, lon]); } catch(e) {}
      }
      if (window.main_marker && typeof window.main_marker.fire === 'function') {
        try { window.main_marker.fire('click'); } catch(e) {}
      }
      // Try common app functions if present.
      for (const fn of ['checkPlan','check_planning','showPlanning','getPlanning','loadPlanning']) {
        if (typeof window[fn] === 'function') { try { window[fn](lat, lon); } catch(e){} }
      }
      await sleep(3500);
    }, { lat, lon });

    // Try clicking the marker - try several possible selectors
    const markerSelectors = [
      '.leaflet-marker-icon.leaflet-marker-draggable',
      '.leaflet-marker-icon',
      '.marker, .map-marker, [class*="marker"]',
      'img.leaflet-marker-icon'
    ];

    let clicked = false;
    for (const sel of markerSelectors) {
      const loc = page.locator(sel).first();
      if (await loc.count() > 0) {
        await loc.click({ timeout: 8000, force: true }).catch(() => {});
        clicked = true;
        console.log(`[Guland] Clicked using selector: ${sel}`);
        await page.waitForTimeout(6000);
        break;
      }
    }

    if (!clicked) {
      // Fallback: click near center of map
      const mapEl = page.locator('.leaflet-container').first();
      if (await mapEl.count()) {
        const box = await mapEl.boundingBox();
        if (box) {
          await page.mouse.click(box.x + box.width/2, box.y + box.height/2);
          await page.waitForTimeout(5000);
        }
      }
    }

    // Try to get the most relevant content - prefer popup or side panel
    let text = '';
    const popupSelectors = [
      '.leaflet-popup-content',
      '.popup, .info-popup, .detail-popup',
      '[class*="popup"]',
      '.quyhoach-info, .planning-info, .info-box',
      'body'
    ];

    for (const sel of popupSelectors) {
      const el = page.locator(sel).first();
      if (await el.count() > 0) {
        const t = await el.innerText({ timeout: 5000 }).catch(() => '');
        if (t && t.length > 200) {
          text = t;
          console.log(`[Guland] Extracted using ${sel}, length=${t.length}`);
          break;
        }
      }
    }

    if (!text) {
      text = await page.locator('body').innerText({ timeout: 10000 });
    }

    return {
      text: `Guland popup/browser: ${text.slice(0, 4500)}`,
      degraded: false,
      sourceUrl: url
    };
  } catch (e) {
    console.error('[Guland] Error:', e.message);
    return { text: `Guland error: ${e.message}`, degraded: true };
  } finally {
    // Do not aggressively close when using persistent CDP
    await page.close().catch(() => {});
    // browser.close() commented to keep connection stable for multiple calls
    // await browser.close().catch(() => {});
  }
}
async function readQhVietPopupText(lat, lon, location = {}) {
  // QH Viá»‡t automation must use the persistent logged-in Chrome profile on CDP port 18800.
  // Do NOT use temporary browsers here: HÃ²a's QH Viá»‡t cookies/session live in .bds-browser-profile.
  // Old working flow: selectProvince -> selectWard -> checkparcel.open() -> activeTab=3 -> gpoint -> gapply().
  const { chromium } = require('playwright');
  await ensureCdpBrowser();
  const targetWard = String(location.ward || location.suburb || '').trim();
  const targetCity = String(location.city || location.district || '').trim();
  const targetProvince = String(location.state || location.city || location.district || '').trim();
  const provinceText = `${targetProvince} ${targetCity} ${targetWard}`;
  let url = 'https://qhviet.com/quy-hoach';
  if (/hồ chí minh|ho chi minh|tp\.?\s*hcm|quận|phường nhiêu lộc/i.test(provinceText)) {
    url = 'https://qhviet.com/quy-hoach/thanh-pho-ho-chi-minh-hanh-chinh-2-cap';
  } else if (/bắc ninh|bac ninh|bắc giang|bac giang/i.test(provinceText)) {
    url = 'https://qhviet.com/quy-hoach/tinh-bac-ninh-hanh-chinh-2-cap';
  }
  const browser = await chromium.connectOverCDP(DEFAULT_CDP);
  const context = browser.contexts()[0] || await browser.newContext();
  const page = await context.newPage();
  try {
    await page.setViewportSize({ width: 1440, height: 1000 }).catch(() => {});
    await page.setExtraHTTPHeaders({
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }).catch(() => {});
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForFunction(() => {
      const app = document.querySelector('#app') && document.querySelector('#app').__vue__;
      const map = app && app.$refs && app.$refs['app-map'];
      const lvl = map && map.$refs && map.$refs['province-box'] && map.$refs['province-box'].$refs && map.$refs['province-box'].$refs['province-level-2'];
      return !!(app && map && lvl && Array.isArray(lvl.provinces) && lvl.provinces.length && app.$refs.checkparcel);
    }, { timeout: 45000 }).catch(() => null);
    await page.waitForTimeout(3000);
    const out = await page.evaluate(async ({ lat, lon, targetWard, targetCity, targetProvince }) => {
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      const norm = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/Ä‘/g,'d').replace(/Ä/g,'D').toLowerCase().replace(/\s+/g,' ').trim();
      const app = document.querySelector('#app') && document.querySelector('#app').__vue__;
      const map = app && app.$refs && app.$refs['app-map'];
      const lvl = map && map.$refs && map.$refs['province-box'] && map.$refs['province-box'].$refs && map.$refs['province-box'].$refs['province-level-2'];
      const picker = app && app.$refs && app.$refs.checkparcel;
      if (!app || !map || !lvl || !picker) return { error: 'KhÃ´ng tháº¥y Vue/checkparcel cá»§a QH Viá»‡t', body: document.body?.innerText || '' };
      const provinceNeed = norm(targetProvince).replace(/^(tinh|thanh pho)\s+/, '');
      let province = (lvl.provinces || []).find(p => norm(p.name) === norm(targetProvince))
                  || (lvl.provinces || []).find(p => norm(p.name).replace(/^(tinh|thanh pho)\s+/, '') === provinceNeed)
                  || (lvl.provinces || []).find(p => norm(p.name).includes(provinceNeed) || provinceNeed.includes(norm(p.name).replace(/^(tinh|thanh pho)\s+/, '')));
      if (!province && /bac giang|bac ninh/.test(provinceNeed)) {
        province = (lvl.provinces || []).find(p => /bac ninh|bac giang/i.test(norm(p.name)));
      }
      if (!province) province = (lvl.provinces || []).find(p => /ho chi minh/i.test(norm(p.name))) || (lvl.provinces || [])[0];
      if (!province) return { error: 'Không tìm thấy tỉnh/thành trong QH Việt', body: document.body?.innerText || '' };
      try { lvl.selectProvince(province); } catch (_) {}
      await sleep(7000);
      const wantFull = norm(targetWard);
      const cityFull = norm(targetCity);
      const wantBare = wantFull.replace(/^(phuong|xa)\s+/, '');
      const cityBare = cityFull.replace(/^(phuong|xa|thanh pho|thi xa|huyen)\s+/, '');
      let ward = (lvl.wards || []).find(w => norm(w.name) === wantFull)
              || (lvl.wards || []).find(w => norm(w.name).replace(/^(phuong|xa)\s+/, '') === wantBare)
              || (lvl.wards || []).find(w => norm(w.name).includes(wantBare))
              || (lvl.wards || []).find(w => cityBare && norm(w.name) === 'phuong '+cityBare)
              || (lvl.wards || []).find(w => cityBare && norm(w.name).replace(/^(phuong|xa)\s+/, '') === cityBare)
              || (lvl.wards || []).find(w => cityBare && norm(w.name).includes(cityBare));
      if (!ward) {
        // Some QH Viá»‡t versions keep the full ward list in DOM before Vue wards is hydrated.
        // Try clicking the exact ward text, then reuse selected_ward if Vue sets it.
        const el = [...document.querySelectorAll('a,li,div,span')].find(e => norm(e.textContent) === wantFull);
        if (el) { try { el.click(); await sleep(8000); } catch (_) {} }
        ward = lvl.selected_ward || map.ward || null;
      }
      if (!ward) return { error: `KhÃ´ng tÃ¬m tháº¥y phÆ°á»ng/xÃ£ QH Viá»‡t: ${targetWard}`, wards: (lvl.wards || []).map(w => w.name).slice(0, 220), body: document.body?.innerText || '' };
      try { lvl.selectWard(ward); } catch (_) {}
      await sleep(5000);
      let got = null;
      try {
        picker.open({
          province,
          ward,
          allowCheckParcel: true,
          callback: result => { got = result; window.__qhvietGot = result; }
        });
        await sleep(1000);
        picker.activeTab = 3;
        picker.gpoint = `${lat}, ${lon}`;
        await picker.gapply();
        for (let i = 0; i < 35 && !window.__qhvietGot; i++) await sleep(1000);
        got = window.__qhvietGot || got;
      } catch (e) {
        return { province: province.name, ward: ward.name, ward_id: ward.id, error: `checkparcel.gapply lá»—i: ${e && e.message ? e.message : e}`, body: document.body?.innerText || '' };
      }
      // Important: old/full QH Việt details come from the map polygon/checkPlan flow, not only checkparcel.gapply().
      // findPolygon(point) calls QH Việt's polygon API, draws the parcel, then checkPlan() fills parcel.plan_info.
      try {
        if (map && typeof map.findPolygon === 'function') {
          map.findPolygon({ lat: Number(lat), lng: Number(lon) });
          for (let i = 0; i < 45; i++) {
            await sleep(1000);
            const parcel = map.parcel || {};
            if ((Array.isArray(parcel.plan_info) && parcel.plan_info.length) || (Array.isArray(parcel.properties) && parcel.properties.length >= 3)) break;
          }
        }
      } catch (_) {}

      const rows = [];
      const qhFull = { parcel: {}, planning: [], plan_info: [], plan_detail: [] };
      if (got && got.feature && got.feature.properties) {
        const props = got.feature.properties;
        if (Array.isArray(props.html)) rows.push(...props.html);
        for (const [k,v] of Object.entries(props)) {
          if (k !== 'html' && v != null && typeof v !== 'object') rows.push(`${k}: ${v}`);
        }
      }
      if (map && map.parcel) {
        const parcel = map.parcel;
        if (parcel.geometry) qhFull.geometry = parcel.geometry;
        if (parcel.area) qhFull.parcel.area_m2 = parcel.area;
        if (Array.isArray(parcel.properties)) {
          rows.push(...parcel.properties);
          for (const html of parcel.properties) {
            const tmp = document.createElement('div');
            tmp.innerHTML = String(html || '');
            const label = (tmp.querySelector('.label')?.textContent || '').trim();
            const value = (tmp.querySelector('.value')?.textContent || '').trim();
            const key = norm(label);
            if (/so to/.test(key)) qhFull.parcel.map_sheet = value;
            if (/so thua/.test(key)) qhFull.parcel.parcel_no = value;
            if (/dien tich/.test(key)) qhFull.parcel.area_text = value;
            if (/khu vuc cu/.test(key)) qhFull.old_area_name = value;
            if (/khu vuc moi/.test(key)) qhFull.area_name = value;
          }
        }
        if (Array.isArray(parcel.plan_info)) {
          qhFull.plan_info = parcel.plan_info;
          for (const p of parcel.plan_info) {
            const itemOut = { source: 'QH Việt' };
            if (p.name) { rows.push(`Quy hoạch: ${p.name}`); itemOut.name = p.name; itemOut.land_use = p.name; }
            if (p.str_code) itemOut.str_code = p.str_code;
            if (p.area) itemOut.area_m2 = p.area;
            if (p.area_percent) itemOut.area_percent = p.area_percent;
            if (p.plan_type) itemOut.plan_type = p.plan_type;
            if (Array.isArray(p.info)) {
              for (const info of p.info) {
                const o = typeof info === 'string' ? (() => { try { return JSON.parse(info); } catch (_) { return { label: '', value: info }; } })() : info;
                if (o && o.label) {
                  const label = String(o.label || '').trim();
                  const value = String(o.value ?? '').trim();
                  rows.push(`${label}: ${value}`);
                  const key = norm(label);
                  if (/ky hieu loai dat|loai dat/.test(key)) { itemOut.code = value; qhFull.land_code = value; }
                  else if (/he so su dung/.test(key)) { itemOut.far = value; qhFull.far = value; }
                  else if (/mat do xay dung/.test(key)) { itemOut.density = value; qhFull.density = value; }
                  else if (/tang cao/.test(key)) { itemOut.height = value; qhFull.height = value; }
                  else if (/ten khu chuc nang/.test(key)) { itemOut.functional_area = value; qhFull.functional_area = value; }
                  else if (/mo ta/.test(key)) { itemOut.description = value; qhFull.description = value; }
                }
              }
            }
            qhFull.planning.push(itemOut);
          }
        }
        if (Array.isArray(parcel.plan_detail)) qhFull.plan_detail = parcel.plan_detail;
      }
      return { province: province.name, ward: ward.name, ward_id: ward.id, got, qhFull, rows, body: document.body?.innerText || '' };
    }, { lat, lon, targetWard, targetCity, targetProvince });
    const rowsText = Array.isArray(out && out.rows) ? out.rows.map(stripHtml).filter(Boolean).join('\n') : '';
    const bodyText = String((out && out.body) || '').slice(0, 6000);
    const meta = out && out.error ? `Lá»—i: ${out.error}\n` : `Khu vực: ${out.ward || targetWard}, ${out.province || targetProvince}\n`;
    return summarizeText(`${meta}${rowsText}\n${bodyText}`, 'QH Viá»‡t browser');
  } finally {
    await page.close().catch(() => null);
    // Disconnect only from CDP. Do not close the persistent Chrome profile.
    await browser.close().catch(() => null);
  }
}

module.exports = { readGulandPopupText, readQhVietPopupText };

