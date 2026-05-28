from pathlib import Path
src = Path('firebase_public/stocks.html').read_text(encoding='utf-8')
s = src
s = s.replace('<title>LH INVESTMENT</title>', '<title>LH INVESTMENT - Candle Trendline Experimental</title>', 1)
s = s.replace('https://lhinvestment.web.app/stocks.html', 'https://lhinvestment.web.app/stocks-candle.html')
marker = "const goodChannels = (items = [], minScore = 70, max = 3) => topByScore((Array.isArray(items) ? items : []).filter(x => Number(x?.score || 0) >= minScore), max);"
insert = r'''
        const detectCandleTrendlinesExperimental = (rows = []) => {
          const arr = Array.isArray(rows) ? rows : [];
          if (arr.length < 40) return [];
          const pivotsHigh = [];
          const pivotsLow = [];
          const winSmall = 3;
          const winMajor = 8;
          const isPivotHigh = (i, w) => {
            const h = Number(arr[i]?.high || 0);
            for (let j = i - w; j <= i + w; j += 1) {
              if (j < 0 || j >= arr.length || j === i) continue;
              if (Number(arr[j]?.high || 0) > h) return false;
            }
            return true;
          };
          const isPivotLow = (i, w) => {
            const l = Number(arr[i]?.low || 0);
            for (let j = i - w; j <= i + w; j += 1) {
              if (j < 0 || j >= arr.length || j === i) continue;
              if (Number(arr[j]?.low || 0) < l) return false;
            }
            return true;
          };
          for (let i = winMajor; i < arr.length - winMajor; i += 1) {
            if (isPivotHigh(i, winSmall)) pivotsHigh.push({ idx:i, time:arr[i].time, price:Number(arr[i].high), major:isPivotHigh(i, winMajor) });
            if (isPivotLow(i, winSmall)) pivotsLow.push({ idx:i, time:arr[i].time, price:Number(arr[i].low), major:isPivotLow(i, winMajor) });
          }
          const avgRange = arr.reduce((sum, r) => sum + Math.abs(Number(r.high||0) - Number(r.low||0)), 0) / Math.max(1, arr.length);
          const bodyTop = r => Math.max(Number(r.open||0), Number(r.close||0));
          const bodyBot = r => Math.min(Number(r.open||0), Number(r.close||0));
          const buildLine = (a, b, kind) => {
            if (!a || !b || b.idx - a.idx < 25) return null;
            const slope = (b.price - a.price) / (b.idx - a.idx);
            const tol = Math.max(avgRange * 0.45, 0.12);
            let touches = 0;
            let bodyBreaks = 0;
            const touchPoints = [];
            for (let i = a.idx; i < arr.length; i += 1) {
              const y = a.price + slope * (i - a.idx);
              const row = arr[i];
              const hi = Number(row.high||0), lo = Number(row.low||0);
              const top = bodyTop(row), bot = bodyBot(row);
              if (kind === 'uptrend') {
                if (Math.abs(lo - y) <= tol) { touches += 1; touchPoints.push({ idx:i, time:row.time, price:lo }); }
                if (y > bot + tol && i > b.idx) bodyBreaks += 1;
              } else {
                if (Math.abs(hi - y) <= tol) { touches += 1; touchPoints.push({ idx:i, time:row.time, price:hi }); }
                if (y < top - tol && i > b.idx) bodyBreaks += 1;
              }
            }
            const lastIdx = arr.length - 1;
            const lastVal = a.price + slope * (lastIdx - a.idx);
            const majorBonus = (a.major ? 1 : 0) + (b.major ? 1 : 0);
            const score = touches * 20 + (b.idx - a.idx) * 0.35 + majorBonus * 25 - bodyBreaks * 22;
            if (touches < 3 || bodyBreaks > 3) return null;
            return {
              id: `${kind}_${a.idx}_${b.idx}`,
              type: kind,
              points: [{ time:a.time, value:Number(a.price.toFixed(2)) }, { time:arr[lastIdx].time, value:Number(lastVal.toFixed(2)) }],
              slopePerBar: Number(slope.toFixed(5)),
              touches,
              lengthBars: lastIdx - a.idx,
              rSquared: 0.8,
              valid: bodyBreaks <= 1,
              score: Number(score.toFixed(2)),
              touchPoints: touchPoints.slice(0, 12),
              reversalConfirmed: touches >= 4,
              source: 'candle-experimental'
            };
          };
          const candidates = [];
          for (let i = 0; i < pivotsLow.length; i += 1) {
            for (let j = i + 1; j < pivotsLow.length; j += 1) {
              if (pivotsLow[j].price <= pivotsLow[i].price) continue;
              const line = buildLine(pivotsLow[i], pivotsLow[j], 'uptrend');
              if (line) candidates.push(line);
            }
          }
          for (let i = 0; i < pivotsHigh.length; i += 1) {
            for (let j = i + 1; j < pivotsHigh.length; j += 1) {
              if (pivotsHigh[j].price >= pivotsHigh[i].price) continue;
              const line = buildLine(pivotsHigh[i], pivotsHigh[j], 'downtrend');
              if (line) candidates.push(line);
            }
          }
          const dedupe = (items, max=8) => items.sort((a,b)=>Number(a.points?.[1]?.value||0)-Number(b.points?.[1]?.value||0)).reduce((acc, line) => {
            const last = Number(line.points?.[1]?.value || 0);
            const found = acc.find(x => Math.abs((Number(x.points?.[1]?.value||0) / Math.max(0.0001,last)) - 1) <= 0.02 && Math.abs(Number(x.slopePerBar||0) - Number(line.slopePerBar||0)) <= 0.03 && x.type === line.type);
            if (!found) acc.push(line);
            else if (Number(line.score||0) > Number(found.score||0)) Object.assign(found, line);
            return acc;
          }, []).sort((a,b)=>Number(b.score||0)-Number(a.score||0)).slice(0,max);
          return dedupe(candidates, 10);
        };
'''
s = s.replace(marker, insert + '\n        ' + marker, 1)
old = "let trendLines = dedupeTrendLines(overlayData.trendlines, 6); if (!trendLines.length && Array.isArray(overlayData.trendlines)) trendLines = overlayData.trendlines.filter(x => fallbackTrendLine(x)).slice(0, 9);"
new = "let trendLines = (String(symbol || '').toUpperCase() === 'MWG' && activeFrame === 'day') ? detectCandleTrendlinesExperimental(rows) : dedupeTrendLines(overlayData.trendlines, 6); if (!trendLines.length && Array.isArray(overlayData.trendlines)) trendLines = overlayData.trendlines.filter(x => fallbackTrendLine(x)).slice(0, 9);"
s = s.replace(old, new, 1)
s = s.replace('SR: gom cụm ~2% bất kể support/resistance, giữ mốc mạnh nhất', 'Candle test: trendline bám trực tiếp theo swing nến', 1)
s = s.replace('DBG ${escapeHtml(String(symbol || \'\').toUpperCase())} ${escapeHtml(String(activeFrame || \'day\').toUpperCase())}', 'DBG CANDLE ${escapeHtml(String(symbol || \'\').toUpperCase())} ${escapeHtml(String(activeFrame || \'day\').toUpperCase())}', 1)
badge = '<div style="margin:10px 0 0; display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; border:1px solid rgba(78,240,192,.35); background:rgba(78,240,192,.12); color:#aef7e6; font-size:12px; font-weight:800;">Candle-based Trendline Experimental</div>'
s = s.replace('<div class="chart-legend" id="stockChartLegend"></div>', badge + '<div class="chart-legend" id="stockChartLegend"></div>', 1)
Path('firebase_public/stocks-candle.html').write_text(s, encoding='utf-8')
print('done')
