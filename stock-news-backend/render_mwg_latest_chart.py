#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import math

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)

hist = json.loads((DATA / 'vn100_history_from_2023.json').read_text(encoding='utf-8'))
rows = hist['symbols']['MWG']['rows']
df = pd.DataFrame(rows).rename(columns={'time':'date'})
df['date'] = pd.to_datetime(df['date'])
for c in ['open','high','low','close','volume']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df = df.dropna().sort_values('date').tail(220).copy()
for n in [20,50,200]:
    df[f'MA{n}'] = df['close'].rolling(n).mean()
# latest pattern levels
levels = {'supports': [], 'resistances': []}
patterns = None
pfile = DATA / 'chart_patterns_cache.json'
if pfile.exists():
    patterns = json.loads(pfile.read_text(encoding='utf-8')).get('symbols',{}).get('MWG')
    if patterns:
        levels = (patterns.get('summary') or {}).get('keyLevels') or levels

last = df.iloc[-1]
prev = df.iloc[-2]
change = last['close']/prev['close']-1

plt.rcParams['font.family'] = 'DejaVu Sans'
fig = plt.figure(figsize=(15,9), dpi=160)
gs = fig.add_gridspec(5,1, height_ratios=[3.6,0.05,1.0,0.05,0.75], hspace=0.05)
ax = fig.add_subplot(gs[0])
axv = fig.add_subplot(gs[2], sharex=ax)
axinfo = fig.add_subplot(gs[4])
axinfo.axis('off')

x = mdates.date2num(df['date'])
width = 0.72
for xi, o, h, l, c in zip(x, df['open'], df['high'], df['low'], df['close']):
    color = '#16a34a' if c >= o else '#dc2626'
    ax.vlines(xi, l, h, color=color, linewidth=1.1, alpha=.95)
    body_low = min(o,c); body_h = abs(c-o)
    if body_h < 0.03: body_h = 0.03
    ax.add_patch(Rectangle((xi-width/2, body_low), width, body_h, facecolor=color, edgecolor=color, alpha=.85))

ax.plot(df['date'], df['MA20'], color='#2563eb', linewidth=1.4, label='MA20')
ax.plot(df['date'], df['MA50'], color='#f59e0b', linewidth=1.4, label='MA50')
ax.plot(df['date'], df['MA200'], color='#7c3aed', linewidth=1.4, label='MA200')

# Support/resistance bands
for s in levels.get('supports', [])[:5]:
    try:
        s=float(s); ax.axhline(s, color='#16a34a', linestyle='--', linewidth=1.0, alpha=.65)
        ax.text(df['date'].iloc[2], s, f' Support {s:g}', va='bottom', ha='left', fontsize=8, color='#166534')
    except Exception: pass
for r in levels.get('resistances', [])[:5]:
    try:
        r=float(r); ax.axhline(r, color='#dc2626', linestyle='--', linewidth=1.0, alpha=.65)
        ax.text(df['date'].iloc[2], r, f' Resistance {r:g}', va='bottom', ha='left', fontsize=8, color='#991b1b')
    except Exception: pass

ax.set_title(f"MWG latest technical chart | Last {last['date'].date()} close {last['close']:.2f} ({change:+.2%})", loc='left', fontsize=15, fontweight='bold')
ax.legend(loc='upper left', ncol=3, frameon=False)
ax.grid(True, axis='y', alpha=.25)
ax.set_ylabel('Price')
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax.get_xticklabels(), visible=False)

vol_colors = ['#16a34a' if c>=o else '#dc2626' for o,c in zip(df['open'],df['close'])]
axv.bar(df['date'], df['volume']/1e6, color=vol_colors, alpha=.65, width=0.8)
axv.plot(df['date'], df['volume'].rolling(20).mean()/1e6, color='#334155', linewidth=1.1, label='Vol MA20')
axv.grid(True, axis='y', alpha=.2)
axv.set_ylabel('Vol (M)')
axv.legend(loc='upper left', frameon=False, fontsize=8)
axv.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Info panel
summary = patterns.get('summary') if patterns else {}
top_patterns = patterns.get('topPatterns', [])[:3] if patterns else []
nearest_sup = None; nearest_res = None
close = float(last['close'])
sups = sorted([float(v) for v in levels.get('supports', []) if float(v) < close], reverse=True)
ress = sorted([float(v) for v in levels.get('resistances', []) if float(v) > close])
if sups: nearest_sup = sups[0]
if ress: nearest_res = ress[0]
info = [
    f"Trend: price vs MA20 {close/last['MA20']-1:+.1%} | vs MA50 {close/last['MA50']-1:+.1%}" if not math.isnan(last['MA50']) else '',
    f"Nearest support: {nearest_sup:g} ({close/nearest_sup-1:+.1%} from support)" if nearest_sup else 'Nearest support: n/a',
    f"Nearest resistance: {nearest_res:g} ({nearest_res/close-1:+.1%} room)" if nearest_res else 'Nearest resistance: n/a',
    f"Pattern bias: {summary.get('bias','n/a')} | bull {summary.get('bullScore','n/a')} | bear {summary.get('bearScore','n/a')}",
    "Top patterns: " + ', '.join([f"{p.get('type')}({p.get('direction')}, {p.get('score')})" for p in top_patterns])
]
axinfo.text(0.01, .82, 'MWG decision notes (analysis, not investment advice)', fontsize=11, fontweight='bold', color='#0f172a')
axinfo.text(0.01, .52, '\n'.join([i for i in info if i]), fontsize=9.5, color='#334155', va='top')
axinfo.text(0.66, .52, 'Use this chart as technical context only. Confirm with fundamentals, market regime, liquidity and OOS evidence.', fontsize=9.5, color='#7f1d1d', va='top', wrap=True)

fig.autofmt_xdate()
out = REPORTS / 'MWG_latest_technical_chart.png'
fig.savefig(out, bbox_inches='tight', facecolor='white')
print(out, out.stat().st_size)
print('last', last['date'].date(), last['close'])
