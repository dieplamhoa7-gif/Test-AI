from pathlib import Path
p=Path('app/dashboard_template.py')
s=p.read_text(encoding='utf-8')
old=s[s.index('    function renderStrategyMatrix(matrix) {'):s.index('    async function renderTechnicalFilters(payload) {')]
new=r'''    function strategyVisualSvg(style='primary') {
      const color = style === 'danger' ? '#ff7d7d' : (style === 'warning' ? '#ffb454' : (style === 'research' ? '#a68bff' : '#4ef0c0'));
      return `<svg viewBox="0 0 240 46" preserveAspectRatio="none" aria-hidden="true"><path d="M0 36 C35 31 48 22 72 25 C94 28 108 12 132 17 C154 21 164 8 188 11 C210 14 222 7 240 5" fill="none" stroke="${color}" stroke-width="3"/><path d="M0 40 L240 40" stroke="rgba(151,170,214,.22)" stroke-dasharray="5 5"/><circle cx="188" cy="11" r="4" fill="${color}"/></svg>`;
    }

    function renderStrategyTooltip(col) {
      const v = col.validation || {};
      const indicators = col.indicators || col.outputIndicators || 'RSI, MACD, Bollinger/MA, Volume, R/S cache, Ichimoku khi có.';
      const validation = v.combined || v.multiWindow || v.current180 || v.oos || '-';
      return `<span class="strategy-help" tabindex="0">? <span class="strategy-tooltip"><div><b>Chiến lược:</b><br>${escapeHtml(col.summary || col.name || '')}</div><div><b>Chỉ báo dùng:</b><br>${escapeHtml(indicators)}</div><div><b>Kiểm định:</b><br>${escapeHtml(validation)}</div></span></span>`;
    }

    function compactSymbols(items, max=6) {
      const rows = Array.isArray(items) ? items : [];
      if (!rows.length) return '<span class="strategy-empty">-</span>';
      return rows.slice(0,max).map(x => {
        const symbol = escapeHtml(x.symbol || x.ticker || '');
        const action = escapeHtml(x.action || '');
        const entry = x.entryPrice ?? x.entry ?? x.price ?? x.lastClose ?? '';
        const rank = x.rankScore ?? x.rank ?? '';
        const title = escapeHtml([x.reason || '', entry ? `Giá/vùng: ${entry}` : '', rank !== '' ? `Rank: ${rank}` : ''].filter(Boolean).join(' | '));
        return `<button class="strategy-symbol-chip" data-filter-symbol="${symbol}" title="${title}"><b>${symbol}</b>${action ? `<small>${action}</small>` : ''}</button>`;
      }).join('') + (rows.length > max ? `<span class="strategy-more">+${rows.length-max}</span>` : '');
    }

    function getStrategyBucket(col, signalMap, state) {
      const sig = signalMap[col.id] || signalMap[col.signalKey] || {};
      if (state === 'buy') return sig.buy || sig.items || [];
      if (state === 'watch') return sig.watch || sig.watchlist || [];
      return sig.avoid || sig.reject || sig.rejects || [];
    }

    function renderStrategyMatrix(matrix, signalMap = {}) {
      const columns = Array.isArray(matrix?.columns) ? matrix.columns : [];
      if (!columns.length) return '';
      const rows = [{ id: 'buy', label: 'MUA' }, { id: 'watch', label: 'THEO DÕI' }, { id: 'avoid', label: 'LOẠI TRỪ' }];
      const heads = columns.map(col => `<th><div class="strategy-th"><span>${escapeHtml(col.shortName || col.name || '')}</span>${renderStrategyTooltip(col)}</div><div class="strategy-curve small">${strategyVisualSvg(col.style || 'primary')}</div></th>`).join('');
      const body = rows.map(row => `<tr class="strategy-row-${row.id}"><th>${escapeHtml(row.label)}</th>${columns.map(col => `<td>${compactSymbols(getStrategyBucket(col, signalMap, row.id), row.id === 'avoid' ? 4 : 7)}</td>`).join('')}</tr>`).join('');
      const mobile = `<div class="strategy-mobile-matrix">${columns.map(col => `<div class="strategy-mobile-block"><h5>${escapeHtml(col.shortName || col.name || '')} ${renderStrategyTooltip(col)}</h5>${rows.map(row => `<div class="strategy-mobile-row"><b>${escapeHtml(row.label)}</b><span>${compactSymbols(getStrategyBucket(col, signalMap, row.id), 6)}</span></div>`).join('')}</div>`).join('')}</div>`;
      return `<div class="strategy-card" style="grid-column:1/-1;"><div class="strategy-title"><div><h4>Ma trận chiến lược PTKT</h4><div class="strategy-desc">Mã khuyến nghị nằm trực tiếp trong ma trận. Dọc: Mua / Theo dõi / Loại trừ. Dấu ? là chú thích.</div></div><span class="strategy-pill">Cache only</span></div><div class="strategy-table-wrap"><table class="strategy-matrix-table"><thead><tr><th>Trạng thái</th>${heads}</tr></thead><tbody>${body}</tbody></table>${mobile}</div></div>`;
    }

    function buildSignalMap(cache) {
      const map = {};
      const normalize = (s='') => String(s).toLowerCase();
      const put = (id, bucket, arr) => { if (!map[id]) map[id] = { buy: [], watch: [], avoid: [] }; map[id][bucket].push(...(Array.isArray(arr) ? arr : [])); };
      (cache.strategies || []).forEach(st => {
        const id = st.id || '';
        const name = normalize(st.name || id);
        let key = id;
        if (name.includes('pullback') || name.includes('b4')) key = 'b4_trend_pullback';
        else if (name.includes('shakeout') || name.includes('rũ')) key = 'shakeout_breakdown_rebound';
        else if (name.includes('split') || name.includes('hỗ trợ') || name.includes('support')) key = 'clean_split_a_bottom';
        put(key, 'buy', st.buy || []);
        put(key, 'watch', st.watchlist || st.watch || st.items || []);
        put(key, 'avoid', st.rejects || st.reject || st.avoid || []);
      });
      const raw = cache.strategies && !Array.isArray(cache.strategies) ? cache.strategies : null;
      if (raw) Object.entries(raw).forEach(([name, st]) => {
        let key = name.includes('B4') ? 'b4_trend_pullback' : (name.includes('Clean') ? 'clean_split_a_bottom' : (name.includes('V3') ? 'shakeout_breakdown_rebound' : name));
        put(key, 'buy', st.buy || []); put(key, 'watch', st.watchlist || st.watch || []); put(key, 'avoid', st.rejects || st.reject || []);
      });
      return map;
    }

'''
p.write_text(s.replace(old,new), encoding='utf-8')
print('patched matrix renderer')
