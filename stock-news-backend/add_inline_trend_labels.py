from pathlib import Path
p=Path('firebase_public/stocks.html')
s=p.read_text(encoding='utf-8')
s=s.replace("    .chart-legend span { display:inline-flex; align-items:center; gap:4px; }\n    .volume-drag-handle { display:none; }", "    .chart-legend span { display:inline-flex; align-items:center; gap:4px; }\n    .trend-inline-label { position:absolute; z-index:6; transform:translate(-50%, -50%); padding:1px 5px; border-radius:999px; font-size:10px; line-height:1.35; font-weight:700; color:#081018; background:rgba(255,255,255,.92); border:1px solid rgba(255,255,255,.35); pointer-events:none; white-space:nowrap; box-shadow:0 3px 10px rgba(0,0,0,.16); }\n    .volume-drag-handle { display:none; }")
s=s.replace("const box = document.getElementById('stockChartBox'); const volBox = document.getElementById('stockVolBox'); const macdBox = document.getElementById('stockMacdBox'); const rsiBox = document.getElementById('stockRsiBox'); if (!box) return; box.innerHTML = '<div class=\"empty\">Đang tải biểu đồ...</div>'; if (volBox) volBox.innerHTML = ''; if (macdBox) macdBox.innerHTML = ''; if (rsiBox) rsiBox.innerHTML = '';", "const box = document.getElementById('stockChartBox'); const volBox = document.getElementById('stockVolBox'); const macdBox = document.getElementById('stockMacdBox'); const rsiBox = document.getElementById('stockRsiBox'); if (!box) return; Array.from(box.querySelectorAll('.trend-inline-label')).forEach(el => el.remove()); box.innerHTML = '<div class=\"empty\">Đang tải biểu đồ...</div>'; if (volBox) volBox.innerHTML = ''; if (macdBox) macdBox.innerHTML = ''; if (rsiBox) rsiBox.innerHTML = '';")
old="""        const addOverlayLine = (chart, line, fallbackStyle = {}) => {
          const points = normalizePoints(line?.points || []);
          if (points.length < 2) return null;
          const style = { ...(line?.lineStyle || {}), ...fallbackStyle };
          const series = chart.addLineSeries({ color: style.color || '#4ef0c0', lineWidth: style.lineWidth || 2, lineStyle: Number(style.lineStyle || 0), priceLineVisible:false, lastValueVisible:false });
          series.setData(points);
          return { series, points, style };
        };
"""
new="""        const addOverlayLine = (chart, line, fallbackStyle = {}) => {
          const points = normalizePoints(line?.points || []);
          if (points.length < 2) return null;
          const style = { ...(line?.lineStyle || {}), ...fallbackStyle };
          const series = chart.addLineSeries({ color: style.color || '#4ef0c0', lineWidth: style.lineWidth || 2, lineStyle: Number(style.lineStyle || 0), priceLineVisible:false, lastValueVisible:false });
          series.setData(points);
          return { series, points, style };
        };
        const addTrendInlineLabel = (linePoints = [], color = '#9fb3d9', text = '') => {
          if (!box || !box._lhChart || !box._lhCandleSeries || !linePoints.length || !text) return;
          const anchor = linePoints[Math.max(0, Math.min(linePoints.length - 1, Math.floor(linePoints.length * 0.7)))];
          try {
            const x = box._lhChart.timeScale()?.timeToCoordinate?.(anchor.time);
            const y = box._lhCandleSeries.priceToCoordinate ? box._lhCandleSeries.priceToCoordinate(anchor.value) : null;
            if (!Number.isFinite(x) || !Number.isFinite(y)) return;
            const label = document.createElement('div');
            label.className = 'trend-inline-label';
            label.textContent = text;
            label.style.left = `${Math.max(28, Math.min(box.clientWidth - 28, x))}px`;
            label.style.top = `${Math.max(16, Math.min(box.clientHeight - 16, y - 10))}px`;
            label.style.borderColor = color;
            label.style.color = color;
            box.appendChild(label);
          } catch(_) {}
        };
"""
s=s.replace(old,new)
s=s.replace("try { candleSeries.createPriceLine({ price, color: style.color || '#9fb3d9', lineWidth: 1, lineStyle: Number(style.lineStyle ?? 2), axisLabelVisible: true, title: `${tag} ${formatNumber(price)}` }); } catch(_) {} };", "try { candleSeries.createPriceLine({ price, color: style.color || '#9fb3d9', lineWidth: 1, lineStyle: Number(style.lineStyle ?? 2), axisLabelVisible: true, title: `${tag} ${formatNumber(price)}` }); } catch(_) {} addTrendInlineLabel(r.points, style.color || '#9fb3d9', formatNumber(price)); };")
p.write_text(s, encoding='utf-8')
print('done')
