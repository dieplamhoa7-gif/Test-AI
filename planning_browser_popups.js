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
  const url = `https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lon}`;
  const text = await readVisibleText(url, true);
  return summarizeText(text, 'Guland popup/browser');
}

async function readQhVietPopupText(lat, lon) {
  const url = `https://qhviet.com/`; // minimal fallback only
  const text = await readVisibleText(url, false);
  return summarizeText(text, 'QH Việt browser');
}

module.exports = { readGulandPopupText, readQhVietPopupText };
