from pathlib import Path
p=Path('app/dashboard_template.py')
s=p.read_text(encoding='utf-8')
css='''
    .strategy-illustrated-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; margin-bottom:12px; }
    .strategy-visual-card { position:relative; min-height:170px; border:1px solid rgba(92,110,148,.18); border-radius:20px; padding:14px; overflow:visible; background:linear-gradient(160deg, rgba(100,181,255,.12), rgba(78,240,192,.05)); box-shadow:0 12px 26px rgba(0,0,0,.12); }
    .strategy-visual-card.primary { border-color:rgba(78,240,192,.34); background:linear-gradient(160deg, rgba(78,240,192,.18), rgba(100,181,255,.08)); }
    .strategy-visual-card.warning { border-color:rgba(255,180,84,.32); background:linear-gradient(160deg, rgba(255,180,84,.16), rgba(100,181,255,.06)); }
    .strategy-visual-card.danger { border-color:rgba(255,125,125,.32); background:linear-gradient(160deg, rgba(255,125,125,.15), rgba(100,181,255,.05)); }
    .strategy-visual-card.research { border-color:rgba(166,139,255,.34); background:linear-gradient(160deg, rgba(166,139,255,.16), rgba(78,240,192,.05)); }
    body.light-theme .strategy-visual-card { background:#fff; box-shadow:0 12px 24px rgba(24,39,75,.07); }
    .strategy-visual-head { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; margin-bottom:10px; }
    .strategy-visual-head h4 { margin:0; font-size:16px; line-height:1.25; }
    .strategy-help { position:relative; display:inline-grid; place-items:center; width:22px; height:22px; border-radius:999px; border:1px solid rgba(100,181,255,.38); background:rgba(100,181,255,.12); color:var(--accent); font-weight:900; font-size:12px; cursor:help; flex:0 0 auto; }
    .strategy-tooltip { display:none; position:absolute; right:0; top:28px; width:min(320px, calc(100vw - 34px)); z-index:60; border:1px solid rgba(92,110,148,.28); border-radius:16px; padding:12px; background:#07101f; color:#dbe7ff; box-shadow:0 18px 45px rgba(0,0,0,.36); text-align:left; line-height:1.45; font-size:12px; }
    body.light-theme .strategy-tooltip { background:#fff; color:#132033; box-shadow:0 18px 45px rgba(24,39,75,.16); }
    .strategy-help:hover .strategy-tooltip, .strategy-help:focus .strategy-tooltip, .strategy-help:active .strategy-tooltip { display:block; }
    .strategy-tooltip b { color:var(--accent-2); }
    .strategy-tooltip div { margin-top:7px; }
    .strategy-curve { height:54px; border-radius:14px; margin:10px 0 12px; background:linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.015)); border:1px solid rgba(92,110,148,.12); position:relative; overflow:hidden; }
    .strategy-curve svg { width:100%; height:100%; display:block; }
    .strategy-state { display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }
    .strategy-state div { border-radius:12px; padding:7px 6px; background:rgba(0,0,0,.12); border:1px solid rgba(92,110,148,.10); min-height:54px; }
    body.light-theme .strategy-state div { background:#f8fbff; }
    .strategy-state span { display:block; font-size:10px; font-weight:900; letter-spacing:.04em; }
    .strategy-state small { display:block; color:var(--muted); font-size:10px; line-height:1.3; margin-top:3px; }
    .state-buy span { color:#23c77a; } .state-watch span { color:#ffb454; } .state-avoid span { color:#ff7d7d; }
'''
s=s.replace('    .strategy-matrix-table { width:100%; border-collapse:separate; border-spacing:0; min-width:760px; }', css+'    .strategy-matrix-table { width:100%; border-collapse:separate; border-spacing:0; min-width:760px; }')
old=s[s.index('    function renderStrategyMatrix(matrix) {'):s.index('    async function renderTechnicalFilters(payload) {')]
new=r'''    function strategyVisualSvg(style='primary') {
      const color = style === 'danger' ? '#ff7d7d' : (style === 'warning' ? '#ffb454' : (style === 'research' ? '#a68bff' : '#4ef0c0'));
      return `<svg viewBox="0 0 240 54" preserveAspectRatio="none" aria-hidden="true"><path d="M0 42 C35 36 44 28 68 31 C92 34 105 17 126 21 C150 25 160 9 184 13 C208 16 216 8 240 6" fill="none" stroke="${color}" stroke-width="3"/><path d="M0 47 L240 47" stroke="rgba(151,170,214,.22)" stroke-dasharray="5 5"/><circle cx="184" cy="13" r="4" fill="${color}"/><circle cx="126" cy="21" r="3" fill="${color}" opacity=".8"/></svg>`;
    }

    function renderStrategyTooltip(col) {
      const v = col.validation || {};
      const indicators = col.indicators || col.outputIndicators || 'RSI, MACD, Bollinger/MA, Volume, R/S cache, Ichimoku khi có.';
      const validation = v.combined || v.multiWindow || v.current180 || v.oos || '-';
      return `<span class="strategy-help" tabindex="0">? <span class="strategy-tooltip"><div><b>Chiến lược:</b><br>${escapeHtml(col.summary || col.name || '')}</div><div><b>Chỉ báo dùng:</b><br>${escapeHtml(indicators)}</div><div><b>Kiểm định:</b><br>${escapeHtml(validation)}</div></span></span>`;
    }

    function renderStrategyMatrix(matrix) {
      const columns = Array.isArray(matrix?.columns) ? matrix.columns : [];
      if (!columns.length) return '';
      const rows = [{ id: 'buy', label: 'MUA' }, { id: 'watch', label: 'XEM XÉT' }, { id: 'avoid', label: 'TRÁNH XA' }];
      const visualCards = columns.map(col => {
        const style = col.style || 'primary';
        const v = col.validation || {};
        const m = col.matrix || {};
        return `<div class="strategy-visual-card ${escapeHtml(style)}"><div class="strategy-visual-head"><div><h4>${escapeHtml(col.name || '')}</h4><div class="strategy-desc">${escapeHtml(v.status || col.shortName || '')}</div></div>${renderStrategyTooltip(col)}</div><div class="strategy-curve">${strategyVisualSvg(style)}</div><div class="strategy-state"><div class="state-buy"><span>MUA</span><small>${escapeHtml(m.buy || 'Theo cache')}</small></div><div class="state-watch"><span>XEM XÉT</span><small>${escapeHtml(m.watch || 'Chờ xác nhận')}</small></div><div class="state-avoid"><span>TRÁNH</span><small>${escapeHtml(m.avoid || 'Không đạt')}</small></div></div><div class="strategy-rule"><b>KQ:</b> ${escapeHtml(v.current180 || v.oos || v.combined || '-')}</div></div>`;
      }).join('');
      return `<div class="strategy-card" style="grid-column:1/-1;"><div class="strategy-title"><div><h4>Chiến lược PTKT</h4><div class="strategy-desc">Dạng minh họa output-only. Bấm/hover dấu ? để xem chú thích.</div></div><span class="strategy-pill">Cache only</span></div><div class="strategy-illustrated-grid">${visualCards}</div></div>`;
    }

'''
p.write_text(s.replace(old,new), encoding='utf-8')
print('patched')
