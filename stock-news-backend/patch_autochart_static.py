from pathlib import Path
import re

root = Path(__file__).parent
files = [root/'firebase_public'/'stocks.html']

for p in files:
    s = p.read_text(encoding='utf-8')
    s = s.replace(".analysis-switch { display:grid; grid-template-columns: repeat(2, minmax(0,1fr));", ".analysis-switch { display:grid; grid-template-columns: repeat(3, minmax(0,1fr));")
    s = s.replace(".technical-panel, .fundamental-panel { border:1px solid rgba(92,110,148,.20);", ".technical-panel, .fundamental-panel, .autochart-panel { border:1px solid rgba(92,110,148,.20);")
    s = s.replace("body.light-theme .technical-panel, body.light-theme .fundamental-panel { background:#fff; border-color:rgba(38,61,99,.12); }", "body.light-theme .technical-panel, body.light-theme .fundamental-panel, body.light-theme .autochart-panel { background:#fff; border-color:rgba(38,61,99,.12); }")
    s = s.replace("    .fundamental-panel { border-color:rgba(78,240,192,.18); background:linear-gradient(180deg, rgba(78,240,192,.055), rgba(100,181,255,.025)); }\n", "    .fundamental-panel { border-color:rgba(78,240,192,.18); background:linear-gradient(180deg, rgba(78,240,192,.055), rgba(100,181,255,.025)); }\n    .autochart-panel { border-color:rgba(100,181,255,.22); background:linear-gradient(180deg, rgba(100,181,255,.06), rgba(122,116,255,.03)); }\n")
    s = s.replace("    .fundamental-tool span { display:block; color:var(--muted); font-size:11px; margin-bottom:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }\n", "    .fundamental-tool span { display:block; color:var(--muted); font-size:11px; margin-bottom:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }\n    .autochart-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:8px; margin-top:12px; }\n    .autochart-card { border:1px solid rgba(92,110,148,.18); border-radius:14px; padding:12px; background:rgba(255,255,255,.03); }\n    body.light-theme .autochart-card { background:#f8fbff; border-color:rgba(38,61,99,.12); }\n    .autochart-card span { display:block; color:var(--muted); font-size:12px; margin-bottom:4px; }\n    .autochart-card b { font-size:18px; color:var(--text); }\n    .autochart-note { color:var(--muted); font-size:12px; line-height:1.6; margin-top:12px; }\n    .autochart-links { display:flex; gap:10px; flex-wrap:wrap; margin-top:14px; }\n    .autochart-links a { color:var(--accent); font-weight:700; }\n")
    s = re.sub(r"const APP_CACHE_VERSION = '[^']+';", "const APP_CACHE_VERSION = '2026-05-28-autochart-static-v1';", s, count=1)
    s = s.replace("const DETAIL_CACHE_MS = 180000; const chartRangeState = new Map();", "const DETAIL_CACHE_MS = 180000; const chartRangeState = new Map(); const autoChartCache = new Map();")
    insert_after = "async function loadFundamentalAverage(symbol) { try { const res = await fetch(`/data/fundamental_top_upside.json?ts=${Date.now()}`, { cache: 'no-store' }); if (!res.ok) return null; const payload = await res.json(); return (payload.items || []).find(x => String(x.symbol || '').toUpperCase() === String(symbol || '').toUpperCase()) || null; } catch (_) { return null; } }\n"
    auto_fn = """    async function loadAutoChart(symbol, timeframe = 'week') { const sym = String(symbol || '').trim().toUpperCase(); const key = `${sym}:${timeframe}`; if (autoChartCache.has(key)) return autoChartCache.get(key); try { const res = await fetch(`/data/charts/${encodeURIComponent(sym)}_${encodeURIComponent(timeframe)}.json?ts=${Date.now()}`, { cache: 'no-store' }); if (!res.ok) throw new Error('autochart'); const payload = await res.json(); autoChartCache.set(key, payload); return payload; } catch (_) { return null; } }
    function renderAutoChartPanel(symbol, payload, timeframe = 'week') { const sym = String(symbol || '').toUpperCase(); if (!payload) return `<div class="autochart-panel"><div class="empty error">Không tải được Auto-chart cho ${escapeHtml(sym)}.</div></div>`; const trendlines = Array.isArray(payload?.trendlines) ? payload.trendlines.length : 0; const patterns = Array.isArray(payload?.patterns) ? payload.patterns.length : 0; const rows = Array.isArray(payload?.rows) ? payload.rows : []; const last = rows.length ? rows[rows.length - 1] : null; const bias = payload?.trendline?.trend || payload?.srZones?.status || 'neutral'; const biasCls = /tăng|bull|up/i.test(String(bias)) ? 'market-up' : (/giảm|bear|down/i.test(String(bias)) ? 'market-down' : 'market-flat'); const support = payload?.trendline?.support || payload?.srZones?.support || null; const resistance = payload?.trendline?.resistance || payload?.srZones?.resistance || null; const jsonUrl = `/data/charts/${encodeURIComponent(sym)}_${encodeURIComponent(timeframe)}.json`; return `<div class="autochart-panel"><div class="analysis-title"><div><h4>Auto-chart ${escapeHtml(sym)} (${escapeHtml(timeframe)})</h4><p>Đọc trực tiếp từ JSON static trên lhinvestment.web.app</p></div></div><div class="detail-table"><div class="detail-row"><span>Bias / trạng thái</span><b class="${biasCls}">${escapeHtml(String(bias || '-'))}</b></div><div class="detail-row"><span>Giá đóng gần nhất</span><b>${escapeHtml(formatNumber(last?.close || 0))}</b></div><div class="detail-row"><span>Support gần nhất</span><b>${support ? escapeHtml(formatNumber(support)) : '-'}</b></div><div class="detail-row"><span>Resistance gần nhất</span><b>${resistance ? escapeHtml(formatNumber(resistance)) : '-'}</b></div></div><div class="autochart-grid"><div class="autochart-card"><span>Nến dữ liệu</span><b>${escapeHtml(String(rows.length || 0))}</b></div><div class="autochart-card"><span>Trendlines</span><b>${escapeHtml(String(trendlines))}</b></div><div class="autochart-card"><span>Patterns</span><b>${escapeHtml(String(patterns))}</b></div><div class="autochart-card"><span>MA20 points</span><b>${escapeHtml(String((payload?.ma20 || []).length || 0))}</b></div><div class="autochart-card"><span>MA50 points</span><b>${escapeHtml(String((payload?.ma50 || []).length || 0))}</b></div><div class="autochart-card"><span>RSI points</span><b>${escapeHtml(String((payload?.rsi || []).length || 0))}</b></div></div><div class="autochart-links"><a href="${escapeHtml(jsonUrl)}" target="_blank" rel="noreferrer">Mở JSON Auto-chart</a></div><div class="autochart-note">Tab này chạy độc lập trên Firebase Hosting, không cần web cũ/OnRender. Bước sau có thể vẽ hẳn line trend/SR/pattern trực tiếp lên chart.</div></div>`; }
"""
    if 'function renderAutoChartPanel' not in s:
        s = s.replace(insert_after, insert_after + auto_fn)
    s = s.replace("        let fundamentalLoaded = false;\n", "        let fundamentalLoaded = false;\n        let autoChartLoaded = false;\n")
    s = re.sub(r"(<div class=\"analysis-switch\">\s*<button[^>]+data-analysis-tab=\"technical\"[\s\S]*?</button>)\s*(<button[^>]+data-analysis-tab=\"fundamental\"[\s\S]*?</button>)\s*</div>", r"\1\n            <button type=\"button\" class=\"analysis-tab-btn\" data-analysis-tab=\"autochart\"><strong>Auto-chart</strong><span>JSON static độc lập</span></button>\n            \2\n          </div>", s, count=1)
    s = s.replace("            <div class=\"analysis-pane active\" data-analysis-pane=\"technical\"></div>\n            <div class=\"analysis-pane\" data-analysis-pane=\"fundamental\"", "            <div class=\"analysis-pane active\" data-analysis-pane=\"technical\"></div>\n            <div class=\"analysis-pane\" data-analysis-pane=\"autochart\" id=\"autochartDetailPane\"><div class=\"autochart-panel\"><div class=\"empty\">Đang tải Auto-chart...</div></div></div>\n            <div class=\"analysis-pane\" data-analysis-pane=\"fundamental\"", 1)
    s = s.replace("          if (tab === 'fundamental' && !fundamentalLoaded) loadFundamentalForDetail();\n", "          if (tab === 'autochart' && !autoChartLoaded) loadAutoChartForDetail();\n          if (tab === 'fundamental' && !fundamentalLoaded) loadFundamentalForDetail();\n", 1)
    marker = "        const loadFundamentalForDetail = () => {\n"
    auto_loader = """        const loadAutoChartForDetail = () => {
          autoChartLoaded = true;
          loadAutoChart(item.ticker, 'week').then(payload => {
            if (activeDetailTicker !== item.ticker) return;
            const pane = document.getElementById('autochartDetailPane');
            if (pane) pane.innerHTML = renderAutoChartPanel(item.ticker, payload, 'week');
          }).catch(() => { const pane = document.getElementById('autochartDetailPane'); if (pane) pane.innerHTML = `<div class="autochart-panel"><div class="empty error">Không tải được Auto-chart cho ${escapeHtml(item.ticker)}.</div></div>`; });
        };
"""
    if 'const loadAutoChartForDetail' not in s:
        s = s.replace(marker, auto_loader + marker, 1)
    s = s.replace("        renderTechnicalFrame('day');\n", "        renderTechnicalFrame('day');\n        loadAutoChartForDetail();\n", 1)
    p.write_text(s, encoding='utf-8')

# keep common entry pages identical for Firebase rewrites
src = (root/'firebase_public'/'stocks.html').read_text(encoding='utf-8')
for name in ['index.html','news-page.html','warrants.html']:
    (root/'firebase_public'/name).write_text(src, encoding='utf-8')

fj = root/'firebase.json'
fs = fj.read_text(encoding='utf-8')
fs = fs.replace(' https://hoa-investment.onrender.com', '')
fs = fs.replace('https://hoa-investment.onrender.com ', '')
fj.write_text(fs, encoding='utf-8')
print('patched autochart static firebase pages')
