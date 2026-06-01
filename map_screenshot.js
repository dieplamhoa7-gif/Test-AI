// Capture a multi-pin satellite map screenshot using Chrome CDP (port 18800).
// Strategy: build a self-contained Leaflet+Esri HTML page, open via data: URL in Chrome,
// fitBounds with 15% padding (→ bounding box 70% of viewport), Page.captureScreenshot.
// Pin accuracy is guaranteed because Leaflet's latLngToContainerPoint() computes pixel
// position exactly from the lat/lng we pass.

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const DEFAULT_CDP = process.env.BDS_BROWSER_CDP || 'http://127.0.0.1:18800';
const CHROME_PATH_CANDIDATES = [
  process.env.BDS_CHROME_PATH,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
].filter(Boolean);
const DEFAULT_PROFILE = process.env.BDS_BROWSER_PROFILE || path.join(__dirname, '.bds-browser-profile');

function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

function firstExistingChromePath() {
  for (const p of CHROME_PATH_CANDIDATES) {
    try { if (fs.existsSync(p)) return p; } catch (_) {}
  }
  return null;
}

async function cdpJson(p, options = {}) {
  const res = await fetch(DEFAULT_CDP + p, options);
  if (!res.ok) throw new Error('CDP HTTP ' + res.status + ' ' + p);
  return res.json();
}

let chromeLaunchInFlight = false;
let lastLaunchAt = 0;

async function ensureCdpBrowser() {
  try { await cdpJson('/json/version'); return true; } catch (_) {}
  if (chromeLaunchInFlight) return false;
  if (Date.now() - lastLaunchAt < 30000) return false;
  chromeLaunchInFlight = true;
  lastLaunchAt = Date.now();
  try {
    const exe = firstExistingChromePath();
    if (!exe) { console.error('[map] Chrome/Edge not found in any default path. Set BDS_CHROME_PATH.'); return false; }
    const child = spawn(exe, [
      '--remote-debugging-port=18800',
      '--user-data-dir=' + DEFAULT_PROFILE,
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-popup-blocking',
      'about:blank',
    ], { detached: true, stdio: 'ignore' });
    child.on('error', err => console.error('[map] Chrome spawn error:', err && err.message || err));
    child.unref();
    for (let i = 0; i < 30; i++) {
      await wait(500);
      try { await cdpJson('/json/version'); return true; } catch (_) {}
    }
    return false;
  } catch (e) {
    console.error('[map] ensureCdpBrowser error:', e && e.message || e);
    return false;
  } finally { chromeLaunchInFlight = false; }
}

async function openTab(url) {
  const ok = await ensureCdpBrowser();
  if (!ok) throw new Error('Chrome CDP khong khoi dong duoc');
  const r = await fetch(DEFAULT_CDP + '/json/new?' + encodeURIComponent(url), { method: 'PUT' });
  if (!r.ok) throw new Error('Khong mo duoc tab Chrome: HTTP ' + r.status);
  return r.json();
}

async function closeTab(id) {
  if (!id) return;
  await fetch(DEFAULT_CDP + '/json/close/' + id).catch(() => null);
}

function connectWs(wsUrl) {
  return new Promise((resolve, reject) => {
    const u = new URL(wsUrl);
    const key = Buffer.from(Math.random().toString(36).slice(2) + Date.now()).toString('base64').slice(0, 24);
    const net = require(u.protocol === 'wss:' ? 'tls' : 'net');
    const socket = net.connect({ host: u.hostname, port: Number(u.port) || 80 }, () => {
      socket.write([
        'GET ' + u.pathname + u.search + ' HTTP/1.1',
        'Host: ' + u.host,
        'Upgrade: websocket',
        'Connection: Upgrade',
        'Sec-WebSocket-Key: ' + key,
        'Sec-WebSocket-Version: 13', '', ''
      ].join('\r\n'));
    });
    let buf = Buffer.alloc(0), open = false, nextId = 1;
    const pending = new Map();
    function sendFrame(str) {
      const payload = Buffer.from(str);
      let header;
      if (payload.length < 126) header = Buffer.from([0x81, 0x80 | payload.length]);
      else if (payload.length < 65536) { header = Buffer.alloc(4); header[0]=0x81; header[1]=0x80|126; header.writeUInt16BE(payload.length,2); }
      else { const h = Buffer.alloc(10); h[0]=0x81; h[1]=0x80|127; h.writeBigUInt64BE(BigInt(payload.length),2); header=h; }
      const mask = Buffer.from([1,2,3,4]);
      const out = Buffer.alloc(payload.length);
      for (let i=0;i<payload.length;i++) out[i]=payload[i]^mask[i%4];
      socket.write(Buffer.concat([header, mask, out]));
    }
    function parseFrames() {
      while (buf.length >= 2) {
        const b0=buf[0], b1=buf[1]; let len=b1&0x7f, off=2;
        if (len===126) { if (buf.length<4) return; len=buf.readUInt16BE(2); off=4; }
        else if (len===127) { if (buf.length<10) return; len=Number(buf.readBigUInt64BE(2)); off=10; }
        const masked=!!(b1&0x80); const maskLen=masked?4:0;
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
        if (idx >= 0) {
          open = true; buf = buf.slice(idx+4);
          resolve({
            send(method, params) { const id=nextId++; sendFrame(JSON.stringify({id, method, params: params||{}})); return new Promise((rs,rj)=>pending.set(id,{resolve:rs,reject:rj})); },
            close() { socket.end(); }
          });
          parseFrames();
        }
      } else parseFrames();
    });
    socket.on('error', reject);
  });
}

function buildLeafletHtml(points, opts) {
  const width = opts.width || 1920;
  const height = opts.height || 1080;
  const paddingPct = Number.isFinite(opts.paddingPct) ? opts.paddingPct : 0.15;
  const mode = opts.mode || 'satellite';
  const tilesUrl = mode === 'satellite'
    ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const tilesAttr = mode === 'satellite' ? 'Tiles &copy; Esri' : '&copy; OpenStreetMap';
  const singleZoom = Number.isFinite(opts.zoom) ? opts.zoom : 18;
  const ptsJson = JSON.stringify(points.map((p, i) => ({
    lat: Number(p.lat), lon: Number(p.lon),
    label: String(p.label || (i === 0 ? 'Vị trí thẩm định' : ('Dự án ' + i))).slice(0, 80),
    kind: String(p.kind || p.type || (i === 0 ? 'origin' : 'project')),
    price: p.price ? String(p.price).slice(0, 40) : '',
  })));

  // Build HTML via array.join to avoid giant template-literal parsing issues.
  return [
    '<!doctype html>',
    '<html><head><meta charset="utf-8"><title>Map</title>',
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>',
    '<style>',
    'html,body{margin:0;padding:0;height:100%;background:#1a1a1a;}',
    '#map{width:' + width + 'px;height:' + height + 'px;}',
    '.origin-dot{width:11px;height:11px;border-radius:999px;background:#e60000;border:2px solid #fff;box-shadow:0 0 0 2px rgba(230,0,0,.35),0 2px 7px rgba(0,0,0,.7);}',
    '.project-dot{width:10px;height:10px;border-radius:999px;background:#ffd400;border:2px solid #222;box-shadow:0 0 0 2px rgba(255,212,0,.35),0 2px 7px rgba(0,0,0,.7);}',
    '.pin-wrap{display:flex;align-items:center;justify-content:center;}',
    '.info-panel{position:absolute;right:18px;top:18px;z-index:9999;width:310px;max-height:calc(100% - 36px);overflow:hidden;background:rgba(10,15,20,.82);color:#fff;border:1px solid rgba(255,255,255,.22);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.45);font-family:-apple-system,"Segoe UI",Tahoma,sans-serif;padding:12px 13px;backdrop-filter:blur(3px);}',
    '.info-title{font-weight:800;font-size:15px;margin-bottom:8px;color:#ffd400;}',
    '.info-row{font-size:12px;line-height:1.25;margin:7px 0;padding-bottom:7px;border-bottom:1px solid rgba(255,255,255,.13);}',
    '.info-row:last-child{border-bottom:0;margin-bottom:0;padding-bottom:0;}',
    '.info-name{font-weight:700;color:#fff;}',
    '.info-price{color:#ffd400;font-weight:700;}',
    '.leaflet-control-attribution{font-size:10px;opacity:0.45;}',
    '</style></head><body>',
    '<div id="map"></div><div id="infoPanel" class="info-panel"></div>',
    '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>',
    '<script>',
    '(function(){',
    'var POINTS=' + ptsJson + ';',
    'var PADDING=' + paddingPct + ';',
    'var SINGLE_ZOOM=' + singleZoom + ';',
    'var map=L.map("map",{preferCanvas:false,zoomControl:false,attributionControl:true,fadeAnimation:false,zoomAnimation:false});',
    'L.tileLayer(' + JSON.stringify(tilesUrl) + ',{attribution:' + JSON.stringify(tilesAttr) + ',maxZoom:19,crossOrigin:true}).addTo(map);',
    'var bounds=null;',
    'POINTS.forEach(function(p, idx){',
    '  var ll=L.latLng(p.lat,p.lon);',
    '  var klass=(idx===0||p.kind==="origin")?"origin-dot":"project-dot";',
    '  L.marker(ll,{interactive:false,icon:L.divIcon({className:"pin-wrap",html:"<div class=\""+klass+"\"></div>",iconSize:[16,16],iconAnchor:[8,8]})}).addTo(map);',
    '  bounds=bounds?bounds.extend(ll):L.latLngBounds(ll,ll);',
    '});',
    'if(POINTS.length===1){map.setView([POINTS[0].lat,POINTS[0].lon],SINGLE_ZOOM,{animate:false});}',
    'else{var sz=map.getSize();var padX=Math.round(sz.x*PADDING);var padY=Math.round(sz.y*PADDING);map.fitBounds(bounds,{padding:[padY,padX],animate:false});}',
    'var tilesLoaded=false;',
    'map.eachLayer(function(layer){if(layer instanceof L.TileLayer){layer.on("load",function(){tilesLoaded=true;});}});',
    'setTimeout(function(){tilesLoaded=true;},7000);',
    'var t0=Date.now();',
    'var iv=setInterval(function(){',
    '  if(tilesLoaded||Date.now()-t0>12000){clearInterval(iv);requestAnimationFrame(function(){requestAnimationFrame(function(){window.__mapReady=true;});});}',
    '},200);',
    '})();',
    '</script></body></html>'
  ].join('\n');
}

async function captureMultiPinMapAt(points, opts) {
  opts = opts || {};
  if (!Array.isArray(points) || !points.length) throw new Error('captureMultiPinMapAt: points rong');
  for (const p of points) {
    if (!Number.isFinite(Number(p.lat)) || !Number.isFinite(Number(p.lon))) {
      throw new Error('captureMultiPinMapAt: toa do khong hop le ' + JSON.stringify(p));
    }
  }
  const width = Number(opts.width) || 1920;
  const height = Number(opts.height) || 1080;

  const html = buildLeafletHtml(points, opts);
  const url = 'data:text/html;charset=utf-8;base64,' + Buffer.from(html, 'utf8').toString('base64');

  const tab = await openTab('about:blank');
  if (!tab.webSocketDebuggerUrl) throw new Error('Khong co browser websocket');
  const cdp = await connectWs(tab.webSocketDebuggerUrl);
  try {
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await cdp.send('Page.navigate', { url });
    const deadline = Date.now() + 18000;
    let ready = false;
    while (Date.now() < deadline) {
      await wait(400);
      try {
        const r = await cdp.send('Runtime.evaluate', { expression: 'window.__mapReady === true', returnByValue: true });
        if (r.result && r.result.value === true) { ready = true; break; }
      } catch (_) {}
    }
    if (!ready) console.error('[map] __mapReady not set within 18s, capturing anyway');
    await wait(500);
    const shot = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false, fromSurface: true });
    if (!shot || !shot.data) throw new Error('Page.captureScreenshot tra empty');
    return Buffer.from(shot.data, 'base64');
  } finally {
    try { await cdp.send('Emulation.clearDeviceMetricsOverride'); } catch (_) {}
    cdp.close();
    await closeTab(tab.id).catch(() => null);
  }
}

async function captureGoogleMapsAt(lat, lon, opts) {
  opts = opts || {};
  return captureMultiPinMapAt([{ lat, lon, label: opts.label || '\u{1F4CD}' }], opts);
}

module.exports = { captureMultiPinMapAt, captureGoogleMapsAt, buildLeafletHtml };

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args[0] === 'multi') {
    const outPath = args[1];
    const pts = args.slice(2).map((s, i) => {
      const parts = s.split(',');
      return { lat: Number(parts[0]), lon: Number(parts[1]), label: parts.slice(2).join(',') || ('P' + (i+1)) };
    });
    captureMultiPinMapAt(pts, { width: 1920, height: 1080, paddingPct: 0.15, mode: 'satellite' })
      .then(buf => { fs.writeFileSync(outPath, buf); console.log('Saved ' + outPath + ' (' + buf.length + ' bytes, ' + pts.length + ' pins)'); })
      .catch(err => { console.error('ERR', err.message || err); process.exit(1); });
  } else {
    const lat = args[0], lon = args[1], outPath = args[2];
    if (!lat || !lon) { console.error('Usage:\n  node map_screenshot.js <lat> <lon> [out.png]\n  node map_screenshot.js multi <out.png> <lat,lon,label> ...'); process.exit(2); }
    captureGoogleMapsAt(lat, lon, { width: 1920, height: 1080 })
      .then(buf => { const p = outPath || ('map_' + lat + '_' + lon + '.png'); fs.writeFileSync(p, buf); console.log('Saved ' + p + ' (' + buf.length + ' bytes)'); })
      .catch(err => { console.error('ERR', err.message || err); process.exit(1); });
  }
}
