from pathlib import Path

files = [Path('firebase_public/stocks-claude.html'), Path('firebase_public/index-claude.html')]
for path in files:
    s = Path('firebase_public/stocks.html').read_text(encoding='utf-8')
    s = s.replace('<title>LH INVESTMENT</title>', '<title>LH INVESTMENT - Claude Experimental</title>', 1)
    s = s.replace('const dedupeTrendLines = (lines = [], max = 6) => {', 'const dedupeTrendLines = (lines = [], max = 8) => {', 1)
    s = s.replace('return clusterTrendLines(valid, max);', "const grouped = clusterTrendLines(valid, max);\n          const support = grouped.filter(x => Number(x?.slopePerBar || 0) >= 0).slice(0, 4);\n          const resistance = grouped.filter(x => Number(x?.slopePerBar || 0) < 0).slice(0, 4);\n          return [...support, ...resistance];", 1)
    s = s.replace('const trendLines = dedupeTrendLines(overlayData.trendlines, 4);', 'const trendLines = dedupeTrendLines(overlayData.trendlines, 8);', 1)
    s = s.replace("supportLike.forEach((line, i) => drawTrendWithPriceTag(line, { color: i === 0 ? '#00c853' : '#76ff03', lineWidth: i === 0 ? 3 : 2, lineStyle:0 }, 'S')); resistanceLike.forEach((line, i) => drawTrendWithPriceTag(line, { color: i === 0 ? '#ff5252' : '#ff8a80', lineWidth: i === 0 ? 3 : 2, lineStyle:0 }, 'R'));", "supportLike.forEach((line, i) => drawTrendWithPriceTag(line, { color: i < 2 ? '#00c853' : '#76ff03', lineWidth: i === 0 ? 3 : 2, lineStyle:0 }, 'S')); resistanceLike.forEach((line, i) => drawTrendWithPriceTag(line, { color: i < 2 ? '#ff5252' : '#ff8a80', lineWidth: i === 0 ? 3 : 2, lineStyle:0 }, 'R'));", 1)
    s = s.replace("legendItems.push('<span style=\"color:#9fb3d9\">SR: gom cụm ~2% bất kể support/resistance, giữ mốc mạnh nhất</span>');", "legendItems.push('<span style=\"color:#ffcf8b\">Claude thử nghiệm: giữ nhiều trendline hơn để soi cấu trúc</span>');", 1)
    badge = '<div style="margin:10px 0 0; display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; border:1px solid rgba(255,180,84,.35); background:rgba(255,180,84,.12); color:#ffcf8b; font-size:12px; font-weight:800;">Claude Experimental Trendline View</div>'
    s = s.replace('<div class="chart-legend" id="stockChartLegend"></div>', badge + '<div class="chart-legend" id="stockChartLegend"></div>', 1)
    path.write_text(s, encoding='utf-8')
print('done')
