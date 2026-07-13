#!/usr/bin/env node
/**
 * planning_server.js  (REBUILT 2026-07-11)
 *
 * Backend Quy hoach cho quyhoach.html. File orchestrator cu (planning_browser_popups.js)
 * da bi xoa nham; ban nay viet lai, TAI SU DUNG 2 parser con giu:
 *   backend/guland_popup_parser.js  -> parseGulandPopupText(text)
 *   backend/qhviet_popup_parser.js  -> parseQhVietPopupText(text)
 *
 * Endpoint (khop quyhoach.html):
 *   GET  /health            -> { ok:true, hasPlanning:true }
 *   POST /planning/lookup    { lat, lng, includeQhViet, includeGuland }
 *        -> { ok, location, planning, raw, qhviet, guland }
 *
 * TRANG THAI: location block (geocode) chay that. Guland/QH Viet la best-effort
 * qua Playwright (selector popup tung nam trong file da xoa) -> CAN TEST/tinh chinh
 * tren may that (Chrome + profile dang nhap QH Viet .pw-tvpl-profile). Neu popup
 * chua bat dung, tra ok:false + error ro rang thay vi crash.
 *
 * Chay:  node backend/planning_server.js   (mac dinh PORT=8790)
 * Deps:  npm i express playwright   (Chrome he thong hoac chromium playwright)
 */
const express = require('express');
const path = require('path');
const { parseGulandPopupText } = require('./guland_popup_parser');
const { parseQhVietPopupText } = require('./qhviet_popup_parser');
const { lookupGisXayDung } = require('./gisxaydung_client');

const PORT = process.env.QH_PORT || 8790;
const PW_PROFILE = process.env.QH_BROWSER_PROFILE || path.resolve(__dirname, '..', '.pw-tvpl-profile');
const HEADLESS = process.env.QH_HEADLESS === '1';
const USE_TEMP_PROFILE = process.env.QH_TEMP_PROFILE === '1';

const app = express();
app.use(express.json({ limit: '1mb' }));
app.use((req, res, next) => {
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Headers', 'content-type');
  res.set('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  if (req.method === 'OPTIONS') return res.status(204).end();
  next();
});

app.get('/health', (_req, res) => res.json({ ok: true, service: 'lh_planning', hasPlanning: true, time: Date.now() }));

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36';
const km = (a, b, c, d) => {
  const R = 6371, r = Math.PI / 180;
  const x = Math.sin((c - a) * r / 2) ** 2 + Math.cos(a * r) * Math.cos(c * r) * Math.sin((d - b) * r / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
};

async function geocode(lat, lng) {
  const loc = { display_name: '', road: '', ward: '', suburb: '', district: '', city: '', nearest_pois: [] };
  try {
    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=jsonv2&zoom=18&addressdetails=1`,
      { headers: { 'User-Agent': 'LHRealEstate-RnD/1.0', 'Accept-Language': 'vi' } });
    if (r.ok) {
      const j = await r.json(); const a = j.address || {};
      loc.display_name = j.display_name || '';
      loc.road = a.road || a.pedestrian || a.residential || '';
      loc.ward = a.suburb || a.quarter || a.ward || a.village || '';
      loc.suburb = loc.ward;
      loc.district = a.city_district || a.county || a.district || '';
      loc.city = a.city || a.state || a.town || '';
    }
  } catch (e) { /* keep going */ }
  try {
    const q = `[out:json][timeout:15];(way(around:350,${lat},${lng})[highway][name];node(around:350,${lat},${lng})[amenity][name];);out center 30;`;
    const r = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', headers: { 'User-Agent': UA }, body: 'data=' + encodeURIComponent(q) });
    if (r.ok) {
      const els = (await r.json()).elements || []; const roads = [], pois = [];
      for (const el of els) {
        const name = el.tags && el.tags.name; if (!name) continue;
        const p = el.center || el; if (p.lat == null) continue;
        const d = km(lat, lng, p.lat, p.lon) * 1000;
        if (el.tags.highway) roads.push({ name, highway: el.tags.highway, distance_m: d });
        else if (el.tags.amenity) pois.push({ name, amenity: el.tags.amenity, distance_m: d });
      }
      roads.sort((x, y) => x.distance_m - y.distance_m); pois.sort((x, y) => x.distance_m - y.distance_m);
      if (roads[0]) { loc.nearest_road = roads[0]; if (!loc.road) loc.road = roads[0].name; }
      loc.nearest_pois = pois.slice(0, 5);
    }
  } catch (e) { /* keep going */ }
  return loc;
}

async function grabQhVietPointText(lat, lng) {
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch { throw new Error('Chua cai playwright (npm i playwright)'); }
  const launchOptions = { headless: HEADLESS, viewport: { width: 1366, height: 900 }, args: ['--disable-blink-features=AutomationControlled', '--no-first-run'] };
  let ctx;
  try { ctx = USE_TEMP_PROFILE ? await chromium.launchPersistentContext('', launchOptions) : await chromium.launchPersistentContext(PW_PROFILE, launchOptions); }
  catch (e) { if (USE_TEMP_PROFILE) throw e; ctx = await chromium.launchPersistentContext('', launchOptions); }
  try {
    const page = ctx.pages()[0] || await ctx.newPage();
    await page.goto('https://qhviet.com/quy-hoach/thanh-pho-ho-chi-minh-hanh-chinh-2-cap', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(7000);
    const out = await page.evaluate(async ({ lat, lng }) => {
      const sleep = ms => new Promise(r => setTimeout(r, ms));
      const app = document.querySelector('#app')?.__vue__;
      const map = app?.$refs?.['app-map'];
      const lvl = map?.$refs?.['province-box']?.$refs?.['province-level-2'];
      const picker = app?.$refs?.checkparcel;
      if (!app || !lvl || !picker) return { error: 'missing qhviet vue refs', body: document.body.innerText.slice(0, 4000) };
      const norm = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
      let hcm = (lvl.provinces || []).find(p => /ho chi minh/.test(norm(p.name)));
      if (hcm) { try { lvl.selectProvince(hcm); await sleep(5000); } catch { } }
      let ward = null;
      const body = document.body.innerText || '';
      if (/Phú Thuận|Phu Thuan/i.test(body)) ward = (lvl.wards || []).find(w => /phu thuan/.test(norm(w.name)));
      if (ward) { try { lvl.selectWard(ward); await sleep(3000); } catch { } }
      let got = null;
      try {
        picker.open({ province: hcm || lvl.selected_province || map?.province, ward: ward || lvl.selected_ward || map?.ward, allowCheckParcel: true, callback: result => { window.__qhvietGot = result; got = result; } });
        await sleep(1000);
        picker.activeTab = 3;
        picker.gpoint = `${lat}, ${lng}`;
        await picker.gapply();
        for (let i = 0; i < 25 && !window.__qhvietGot; i++) await sleep(1000);
        got = window.__qhvietGot || got;
      } catch (e) { return { error: String(e && e.message || e), body: document.body.innerText.slice(0, 8000) }; }
      const parts = [];
      if (got) parts.push(typeof got === 'string' ? got : JSON.stringify(got));
      parts.push(document.body.innerText.slice(0, 8000));
      return { text: parts.filter(Boolean).join('\n') };
    }, { lat, lng });
    if (out.error) throw new Error(out.error + ': ' + (out.body || '').slice(0, 300));
    return out.text || '';
  } finally { await ctx.close(); }
}

// Best-effort: mo trang soi quy hoach, click giua map de bung popup, doc text lon nhat.
async function grabPopupText(url) {
  let chromium;
  try { ({ chromium } = require('playwright')); }
  catch { throw new Error('Chua cai playwright (npm i playwright)'); }
  const launchOptions = {
    headless: HEADLESS, viewport: { width: 1366, height: 900 },
    args: ['--disable-blink-features=AutomationControlled', '--no-first-run'],
  };
  let ctx;
  try {
    ctx = USE_TEMP_PROFILE
      ? await chromium.launchPersistentContext('', launchOptions)
      : await chromium.launchPersistentContext(PW_PROFILE, launchOptions);
  } catch (e) {
    // Playwright/Chrome can refuse an old or locked persistent profile
    // (common after Chrome version upgrades: ShaderCache/Snapshots access denied).
    // Fall back to an ephemeral profile instead of failing the whole lookup.
    if (USE_TEMP_PROFILE) throw e;
    ctx = await chromium.launchPersistentContext('', launchOptions);
  }
  try {
    const page = ctx.pages()[0] || await ctx.newPage();
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(6000);
    try { const b = await page.locator('body').boundingBox(); if (b) await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2); } catch { }
    await page.waitForTimeout(4000);
    // Lay khoi text hien thi dai nhat (popup thuong la khoi lon nhat sau khi click).
    const text = await page.evaluate(() => {
      let best = '';
      for (const el of Array.from(document.querySelectorAll('div,section,aside,li'))) {
        if (el.offsetParent === null) continue;
        const t = (el.innerText || '').replace(/\s+/g, ' ').trim();
        if (t.length > best.length && t.length < 4000) best = t;
      }
      return best;
    });
    return text || '';
  } finally { await ctx.close(); }
}

app.post('/planning/lookup', async (req, res) => {
  const lat = Number(req.body.lat), lng = Number(req.body.lng ?? req.body.lon);
  if (!isFinite(lat) || !isFinite(lng)) return res.status(400).json({ ok: false, error: 'lat/lng khong hop le' });

  const location = await geocode(lat, lng);

  // NOTE: nguon chinh thong (thongtinquyhoach HCM official_lots) do orchestrator cu
  // dam nhan da bi xoa. Tra khung rong + confidence de UI hien thi trung thuc.
  const planning = {
    planning_project: {},
    exact_indicators: {},
    confidence: { location: location.display_name ? 'Da xac dinh vi tri' : 'Chua chac vi tri', district_planning: 'Chua co nguon chinh thong (can rebuild)', exact_indicators: 'Chua co chi tieu o dat' },
  };
  const raw = { official_lots: { details: [], lots: [] } };

  let qhviet = { ok: false, error: 'Bo qua (includeQhViet=false)' };
  let guland = { ok: false, error: 'Bo qua (includeGuland=false)' };
  let gisxaydung = { ok: false, error: 'Chua query GIS Xay dung' };

  try {
    gisxaydung = await lookupGisXayDung(lat, lng);
    if (gisxaydung.ok) {
      const gp = gisxaydung.planning || {};
      planning.exact_indicators = {
        chuc_nang_dat: gp.land_use || null,
        ma_quy_uoc: gp.land_code || null,
        tang_cao: gp.height || null,
        mat_do_xay_dung: gp.density,
        he_so_su_dung_dat: gp.far,
        dan_so_lo_o_pho: gp.population || null,
        dien_tich: gp.area_m2,
      };
      planning.confidence.district_planning = 'Da query GIS Xay dung TP.HCM';
      planning.confidence.exact_indicators = 'GIS Xay dung TP.HCM';
      raw.official_lots.details = [{ detail: {
        chucnangsdd: gp.land_use || null,
        maquyuoc: gp.land_code || null,
        tangcao: gp.height || null,
        matdo: gp.density,
        hesosdd: gp.far,
        danso: gp.population || null,
        dientich: gp.area_m2,
      } }];
      raw.official_lots.lots = [{
        chucnang: gp.land_use || null,
        maso: gp.land_code || null,
        dientich: gp.area_m2,
      }];
    }
  } catch (e) { gisxaydung = { ok: false, error: 'GIS Xay dung loi: ' + e.message }; }

  if (req.body.includeGuland) {
    try {
      const txt = await grabPopupText(`https://guland.vn/soi-quy-hoach?lat=${lat}&lng=${lng}`);
      const parsed = parseGulandPopupText(txt);
      guland = { ok: !!txt, error: txt ? '' : 'Khong bat duoc popup Guland (can tinh chinh selector)', parsed, raw_text: txt.slice(0, 1200) };
    } catch (e) { guland = { ok: false, error: 'Guland loi: ' + e.message }; }
  }
  if (req.body.includeQhViet) {
    try {
      const txt = await grabQhVietPointText(lat, lng);
      const parsed = parseQhVietPopupText(txt);
      qhviet = { ok: !!txt, error: txt ? '' : 'Khong bat duoc popup QH Viet (can dang nhap/tinh chinh selector)', parsed, raw_text: txt.slice(0, 1200) };
    } catch (e) { qhviet = { ok: false, error: 'QH Viet loi: ' + e.message }; }
  }

  res.json({ ok: true, location, planning, raw, qhviet, guland, gisxaydung });
});

app.listen(PORT, () => console.log(`[planning_server] listening on http://localhost:${PORT}`));
