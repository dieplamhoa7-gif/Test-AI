from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT/'firebase_public/index.html', ROOT/'firebase_public/stocks.html', ROOT/'app/dashboard_template.py']
old = """    async function refreshWarrantDetails(codes = []) {
      const list = [...new Set(codes.map(x => String(x || '').toUpperCase().replace(/[^A-Z0-9]/g,'')).filter(Boolean))].slice(0, 80);
      if (!list.length) return;
"""
new = """    async function refreshWarrantDetails(codes = []) {
      const list = [...new Set(codes.map(x => String(x || '').toUpperCase().replace(/[^A-Z0-9]/g,'')).filter(Boolean))].slice(0, 120);
      if (!list.length) return;
"""
anchor = """    async function openWarrantDetail(code) {
"""
insert = """    let warrantRealtimeTimer = null;
    function currentWarrantRealtimeCodes() {
      const visible = [...document.querySelectorAll('[data-warrant]')].map(el => el.dataset.warrant);
      return [...new Set([...(warrantWatchSymbols || []), activeWarrantCode, selectedWarrant, ...visible].map(x => String(x || '').toUpperCase().replace(/[^A-Z0-9]/g,'')).filter(Boolean))].slice(0, 120);
    }
    async function refreshWarrantRealtimeOverlay() {
      if (pageToTab() !== 'warrants') return;
      const codes = currentWarrantRealtimeCodes();
      if (!codes.length) return;
      await refreshWarrantDetails(codes);
      if (elements.apiStatus) elements.apiStatus.textContent = 'CW realtime 15s';
      if (elements.warrantStatus && !/đăng nhập|login|trống|empty/i.test(elements.warrantStatus.textContent || '')) {
        elements.warrantStatus.textContent = `${warrantTextViEn('CW realtime VPS','CW realtime VPS')} • ${new Date().toLocaleTimeString('vi-VN')}`;
      }
    }
    function startWarrantRealtimeOverlay() {
      if (warrantRealtimeTimer) return;
      refreshWarrantRealtimeOverlay().catch(() => {});
      warrantRealtimeTimer = setInterval(() => refreshWarrantRealtimeOverlay().catch(() => {}), 15000);
    }

"""
old_load = """if (tab === 'warrants') { await loadWarrants(); elements.apiStatus.textContent = warrantItems.length ? 'Online' : 'Offline'; return; }"""
new_load = """if (tab === 'warrants') { await loadWarrants(); startWarrantRealtimeOverlay(); elements.apiStatus.textContent = warrantItems.length ? 'CW realtime 15s' : 'Offline'; return; }"""
old_bottom = """loadData(); loadWarrants(); setTimeout(loadIndexOverview, 300);"""
new_bottom = """loadData(); loadWarrants(); if (pageToTab() === 'warrants') startWarrantRealtimeOverlay(); setTimeout(loadIndexOverview, 300);"""
for p in FILES:
    s = p.read_text(encoding='utf-8')
    if old in s: s = s.replace(old, new, 1)
    if insert.strip() not in s:
        if anchor not in s: raise SystemExit(f'missing open anchor {p}')
        s = s.replace(anchor, insert + anchor, 1)
    if old_load in s: s = s.replace(old_load, new_load, 1)
    else: print('load anchor not found', p)
    if old_bottom in s: s = s.replace(old_bottom, new_bottom, 1)
    else: print('bottom anchor not found', p)
    p.write_text(s, encoding='utf-8')
    print('patched', p.relative_to(ROOT))
