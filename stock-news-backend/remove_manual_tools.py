from pathlib import Path
p=Path('firebase_public/stocks.html')
s=p.read_text(encoding='utf-8')
s=s.replace(" frameButtons.forEach(x => x.classList.toggle('active', x.dataset.chartFrame === activeFrame)); data = await loadFrameData(activeFrame); overlayData = await loadOverlayData(activeFrame); rows = data.rows || []; manualDraftPoints = []; manualLines = loadManualLines(); draw(!changedFrame); });", " frameButtons.forEach(x => x.classList.toggle('active', x.dataset.chartFrame === activeFrame)); data = await loadFrameData(activeFrame); overlayData = await loadOverlayData(activeFrame); rows = data.rows || []; draw(!changedFrame); });")
start=s.find("        const manualDrawToggle = document.getElementById('manualDrawToggle');")
end=s.find("        const parsePeriods =", start)
if start!=-1 and end!=-1:
    s=s[:start]+s[end:]
start=s.find("        const manualLineStorageKey = () =>")
end=s.find("        const draw =", start)
if start!=-1 and end!=-1:
    repl="""        const rangeStorageKey = () => `lh.stockChart.range.${rangeKey()}`;\n        const loadStoredRange = () => { try { const r = JSON.parse(localStorage.getItem(rangeStorageKey()) || 'null'); return r && Number.isFinite(r.from) && Number.isFinite(r.to) ? r : null; } catch(_) { return null; } };\n        const isRangeUsable = (r) => r && Number.isFinite(r.from) && Number.isFinite(r.to) && r.to > r.from;\n        const saveRange = (r) => { if (isRangeUsable(r)) { const clean = { from:r.from, to:r.to }; chartRangeState.set(rangeKey(), clean); try { localStorage.setItem(rangeStorageKey(), JSON.stringify(clean)); } catch(_) {} } };\n        const currentRange = () => { try { const live = box._lhChart?.timeScale().getVisibleLogicalRange(); return isRangeUsable(live) ? live : (chartRangeState.get(rangeKey()) || loadStoredRange() || null); } catch(_) { return chartRangeState.get(rangeKey()) || loadStoredRange() || null; } };\n"""
    s=s[:start]+repl+s[end:]
# remove manual render lines
for old in [
"          manualLines.forEach((points, idx) => addOverlayLine(chart, { points, lineStyle:{ color:'#ffd54f', lineWidth:2, lineStyle:0 } }));\n",
"          if (manualDraftPoints.length === 1) legendItems.push('<span style=\"color:#ffd54f\">Chọn điểm thứ 2 để vẽ line</span>');\n",
"          if (manualLines.length) legendItems.push(`<span style=\"color:#ffd54f\">Line tự vẽ ${manualLines.length}</span>`);\n",
"          if (measureState.active && measureState.start && measureState.end) renderMeasure();\n",
]:
    s=s.replace(old,'')
# remove subscribeClick block
start=s.find("          if (chart.subscribeClick) {")
end=s.find("          resizeChartWhenVisible(chart, box, true);", start)
if start!=-1 and end!=-1:
    s=s[:start]+s[end:]
# simplify syncPills
s=s.replace("        const syncPills = () => { Object.keys(state).forEach(k => document.querySelector(`[data-indicator-wrap=\"${k}\"]`)?.classList.toggle('off', !state[k])); if (volSlider) { volSlider.value = String(Math.max(6, Math.min(35, Number(settings.volume) || 14))); volSlider.disabled = !state.volume; volSlider.style.opacity = state.volume ? '1' : '.45'; } if (manualDrawToggle) manualDrawToggle.classList.toggle('active', manualDrawEnabled); };", "        const syncPills = () => { Object.keys(state).forEach(k => document.querySelector(`[data-indicator-wrap=\"${k}\"]`)?.classList.toggle('off', !state[k])); if (volSlider) { volSlider.value = String(Math.max(6, Math.min(35, Number(settings.volume) || 14))); volSlider.disabled = !state.volume; volSlider.style.opacity = state.volume ? '1' : '.45'; } };")
start=s.find("        manualDrawToggle?.addEventListener('click'")
end=s.find("        window.addEventListener('resize'", start)
if start!=-1 and end!=-1:
    s=s[:start]+"        syncPills();\n        draw(true);\n"+s[end:]
p.write_text(s, encoding='utf-8')
print('done')
