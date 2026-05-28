from pathlib import Path
p=Path('firebase_public/stocks-claude.html')
s=p.read_text(encoding='utf-8')
old="const loadOverlayData = async (frame) => { const urls = [`/data/charts/${encodeURIComponent(symbol)}_auto_chart_${encodeURIComponent(frame)}.json?ts=${Date.now()}`, `/data/charts/${encodeURIComponent(symbol)}_${encodeURIComponent(frame)}.json?ts=${Date.now()}`]; for (const url of urls) { try { const res = await fetch(url, { cache:'no-store' }); if (!res.ok) continue; return await res.json(); } catch(_) {} } return null; };"
new="const loadOverlayData = async (frame) => { const sym = String(symbol || '').toUpperCase(); const urls = (sym === 'MWG' && frame === 'day') ? [`/data/charts/MWG_auto_chart_day_longterm.json?ts=${Date.now()}`, `/data/charts/${encodeURIComponent(sym)}_auto_chart_${encodeURIComponent(frame)}.json?ts=${Date.now()}`, `/data/charts/${encodeURIComponent(sym)}_${encodeURIComponent(frame)}.json?ts=${Date.now()}`] : [`/data/charts/${encodeURIComponent(sym)}_auto_chart_${encodeURIComponent(frame)}.json?ts=${Date.now()}`, `/data/charts/${encodeURIComponent(sym)}_${encodeURIComponent(frame)}.json?ts=${Date.now()}`]; for (const url of urls) { try { const res = await fetch(url, { cache:'no-store' }); if (!res.ok) continue; return await res.json(); } catch(_) {} } return null; };"
s=s.replace(old,new,1)
p.write_text(s, encoding='utf-8')
print('done')
