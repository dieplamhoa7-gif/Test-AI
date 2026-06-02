import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
from pathlib import Path
from pattern_engine.core import load_data, add_indicators, find_pivots
from pattern_engine.forecast import forecast, build_scenarios
from pattern_engine.plot import _dedup, _lab, C
from run_mwg_pattern_forecast import detect_all

CSV = sys.argv[1] if len(sys.argv) > 1 else 'MWG.csv'
SYM = sys.argv[2] if len(sys.argv) > 2 else 'MWG'
OUT = Path(sys.argv[3] if len(sys.argv) > 3 else 'exports')
OUT.mkdir(parents=True, exist_ok=True)

df = add_indicators(load_data(CSV))
piv = find_pivots(df, distance=3)
allpats = detect_all(df, piv)
fc = forecast(df, 20, min(60, len(df)))
sc = build_scenarios(df, allpats, fc)
pats = _dedup([p for p in allpats if p['category'] != 'candlestick'])

fig, (ax, axv) = plt.subplots(2, 1, figsize=(17, 10), height_ratios=[3.6, 1], sharex=True)
dts = mdates.date2num(df['date'])
w = 4.2

def D(s): return mdates.date2num(pd.to_datetime(s))

for d, o, h, l, c in zip(dts, df['open'], df['high'], df['low'], df['close']):
    col = '#16a34a' if c >= o else '#dc2626'
    ax.plot([d, d], [l, h], color=col, lw=0.7, zorder=2)
    ax.add_patch(Rectangle((d - w/2, min(o, c)), w, abs(c - o) + 0.01, color=col, zorder=2))
ax.plot(df['date'], df['sma20'], color='#9333ea', lw=1.1, label='SMA20', alpha=0.7, zorder=3)
ax.plot(df['date'], df['sma50'], color='#f97316', lw=1.1, label='SMA50', alpha=0.7, zorder=3)

def lbl(x, y, text, color, va='center', ha='left', weight='bold', fs=9.5, box=True):
    bbox = dict(boxstyle='round,pad=0.25', fc='white', ec=color, alpha=0.85, lw=0.8) if box else None
    ax.annotate(text, (x, y), color=color, fontsize=fs, va=va, ha=ha, weight=weight, bbox=bbox, zorder=10)

for p in pats:
    t = p['type']
    if t in ('support-cluster', 'resistance-cluster'):
        pts = p['lines'][0]['points']; y = pts[0]['value']
        col = C['support'] if 'support' in t else C['resistance']
        ax.plot([D(pts[0]['time']), dts[-1]], [y, y], '--', color=col, lw=1.4, alpha=0.7, zorder=4)
        lbl(dts[-1], y, f"{_lab(t)} {y}", col, ha='left', fs=9)
    elif t in ('support-trendline', 'resistance-trendline'):
        pts = p['lines'][0]['points']
        col = C['trendline_s'] if 'support' in t else C['trendline_r']
        xs = [D(q['time']) for q in pts]; ys = [q['value'] for q in pts]
        ax.plot(xs, ys, '-', color=col, lw=2, zorder=4)
        lbl(xs[-1], ys[-1] + (2 if 'resistance' in t else -2), _lab(t), col, ha='right', fs=9)

for p in pats:
    t = p['type']
    if t.startswith(('double', 'triple')):
        col = C['bull'] if p['direction'] == 'bullish' else C['bear']
        mk = '^' if p['direction'] == 'bullish' else 'v'
        for ln in p['lines']:
            if ln['type'] == 'point':
                q = ln['points'][0]
                ax.scatter([D(q['time'])], [q['value']], marker=mk, s=150, color=col,
                           edgecolors='white', linewidths=1.5, zorder=8)
            elif ln['name'] == 'neckline':
                pts = ln['points']
                ax.plot([D(q['time']) for q in pts], [q['value'] for q in pts], ':',
                        color=C['neckline'], lw=2, zorder=5)
        fp = p['lines'][0]['points'][0]; lv = p.get('levels', {})
        tgt = f" -> {lv['target']}" if lv.get('target') else ''
        lbl(D(fp['time']), fp['value'] - 3, f"{_lab(t)}{tgt}", col, va='top', ha='center')
    elif t in ('head-shoulders', 'inverse-head-shoulders'):
        col = C['bear'] if 'inverse' not in t else C['bull']
        mkmap = {'left_shoulder': ('o', 'Vai T'), 'head': ('*', 'Dau'), 'right_shoulder': ('o', 'Vai P')}
        for ln in p['lines']:
            if ln['type'] == 'point' and ln['name'] in mkmap:
                q = ln['points'][0]; symb, txt = mkmap[ln['name']]
                ax.scatter([D(q['time'])], [q['value']], marker=symb,
                           s=260 if symb == '*' else 120, color=col,
                           edgecolors='white', linewidths=1.5, zorder=8)
                lbl(D(q['time']), q['value'] + 1.5, txt, col, va='bottom', ha='center', fs=8, box=False)
            elif ln['name'] == 'neckline':
                pts = ln['points']
                ax.plot([D(q['time']) for q in pts], [q['value'] for q in pts], ':',
                        color=C['neckline'], lw=2, zorder=5)
        hp = next((ln['points'][0] for ln in p['lines'] if ln['name'] == 'head'), None)
        if hp:
            lbl(D(hp['time']), hp['value'] + 4, _lab(t), col, va='bottom', ha='center')

for p in pats:
    t = p['type']
    if 'triangle' in t or 'wedge' in t or 'channel' in t:
        col = C['bull'] if p['direction'] == 'bullish' else (C['bear'] if p['direction'] == 'bearish' else C['neutral'])
        for ln in p['lines']:
            pts = ln['points']
            ax.plot([D(q['time']) for q in pts], [q['value'] for q in pts], '-', color=col, lw=1.8, zorder=4)
        up = p['lines'][0]['points'][-1]
        lbl(D(up['time']), up['value'], _lab(t), col, ha='right')

for p in pats:
    if p['type'] == 'darvas-box':
        lv = p['levels']; x0 = D(p['lines'][0]['points'][0]['time'])
        ax.add_patch(Rectangle((x0, lv['support']), dts[-1] - x0, lv['resistance'] - lv['support'],
                     fill=True, fc='#a855f7', alpha=0.08, ec='#a855f7', lw=1.4, ls='--', zorder=3))
        lbl(x0, lv['resistance'] + 1, f"{_lab('darvas-box')} {lv['support']}-{lv['resistance']}", '#7c3aed', va='bottom')

for p in pats:
    t = p['type']
    if t.startswith('fvg'):
        lv = p['levels']; d0 = D(p['time'])
        fc_ = '#16a34a' if 'bull' in t else '#dc2626'
        ax.add_patch(Rectangle((d0, lv.get('gapLow', 0)), dts[-1] - d0, lv.get('gapHigh', 0) - lv.get('gapLow', 0),
                     fill=True, fc=fc_, alpha=0.12, ec='none', zorder=1))
    elif t.startswith('order-block'):
        lv = p['levels']; d0 = D(p['time'])
        fc_ = '#10b981' if 'bull' in t else '#f43f5e'
        ax.add_patch(Rectangle((d0, lv.get('obLow', 0)), dts[-1] - d0, lv.get('obHigh', 0) - lv.get('obLow', 0),
                     fill=True, fc=fc_, alpha=0.15, ec='#94a3b8', lw=0.5, zorder=1))

for p in pats:
    t = p['type']
    if t in ('spring-shakeout', 'upthrust-bull-trap'):
        col = C['bull'] if 'spring' in t else C['bear']
        mk = '^' if 'spring' in t else 'v'
        ax.scatter([D(p['time'])], [p['price']], marker=mk, s=200, color=col, edgecolors='black', linewidths=1, zorder=9)
        lbl(D(p['time']), p['price'] + (-3 if 'spring' in t else 3), _lab(t), col,
            va='top' if 'spring' in t else 'bottom', ha='center')

fd = [D(p['time']) for p in fc['points']]; fv = [p['value'] for p in fc['points']]
fu = [p['upper'] for p in fc['points']]; fl_ = [p['lower'] for p in fc['points']]
last_d = dts[-1]; last_c = df['close'].iloc[-1]
ax.plot([last_d] + fd, [last_c] + fv, ':', color=C['forecast'], lw=2.6, label=f"Du bao {fc['horizonBars']}p", zorder=6)
ax.fill_between([last_d] + fd, [last_c] + fl_, [last_c] + fu, color=C['forecast'], alpha=0.10, zorder=1)
lbl(fd[-1], fv[-1], f"Du bao {fv[-1]}", C['forecast'], ha='left')
for k, col, nm in [('bullish', C['bull'], 'KB tang'), ('base', C['forecast'], 'KB co so'), ('bearish', C['bear'], 'KB giam')]:
    ax.axhline(sc[k]['target'], color=col, ls=':', lw=1, alpha=0.5, zorder=2)
    lbl(fd[-1], sc[k]['target'], f"{nm}:{sc[k]['target']}", col, ha='left', fs=8.5)

ax.set_title(f'{SYM} - Mau hinh ky thuat & Du bao gia  (research-only, khong phai khuyen nghi dau tu)', fontsize=13, weight='bold')
ax.legend(loc='upper left', fontsize=9, ncol=3)
ax.grid(alpha=0.18); ax.set_ylabel('Gia (nghin d)')
ax.set_xlim(dts[0] - 10, fd[-1] + 60)

vcol = ['#16a34a' if c >= o else '#dc2626' for c, o in zip(df['close'], df['open'])]
axv.bar(df['date'], df['volume'], color=vcol, alpha=0.5, width=5)
axv.set_ylabel('KL'); axv.grid(alpha=0.18)
axv.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

plt.tight_layout()
plt.savefig(OUT / f'{SYM}_chart_preview.png', dpi=115, bbox_inches='tight')
print(f'PNG preview OK -> {OUT}/{SYM}_chart_preview.png')
