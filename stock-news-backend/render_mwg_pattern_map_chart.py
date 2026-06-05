#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; REPORTS=ROOT/'reports'; REPORTS.mkdir(exist_ok=True)

hist=json.loads((DATA/'vn100_history_from_2023.json').read_text(encoding='utf-8'))
rows=hist['symbols']['MWG']['rows']
df=pd.DataFrame(rows).rename(columns={'time':'date'})
df['date']=pd.to_datetime(df['date'])
for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
df=df.dropna().sort_values('date').copy()
for n in [20,50,200]: df[f'MA{n}']=df['close'].rolling(n).mean()
view=df.tail(300).copy()
patterns=json.loads((DATA/'chart_patterns_cache.json').read_text(encoding='utf-8'))['symbols']['MWG']
summary=patterns['summary']; top=patterns.get('topPatterns',[])[:8]
last=view.iloc[-1]; close=float(last['close']); prev=view.iloc[-2]; chg=close/prev['close']-1

plt.rcParams['font.family']='DejaVu Sans'
plt.rcParams['axes.facecolor']='#0b1220'
plt.rcParams['figure.facecolor']='#0b1220'
fig=plt.figure(figsize=(17,10),dpi=170,facecolor='#0b1220')
gs=fig.add_gridspec(6,5,hspace=.12,wspace=.18)
ax=fig.add_subplot(gs[:4,:4])
axv=fig.add_subplot(gs[4,:4],sharex=ax)
axp=fig.add_subplot(gs[:5,4])
axn=fig.add_subplot(gs[5,:])
for a in [ax,axv,axp,axn]: a.set_facecolor('#0b1220')
axp.axis('off'); axn.axis('off')

x=mdates.date2num(view['date']); width=.72
for xi,o,h,l,c in zip(x,view['open'],view['high'],view['low'],view['close']):
    color='#22c55e' if c>=o else '#ef4444'
    ax.vlines(xi,l,h,color=color,linewidth=1.0,alpha=.9)
    body=max(abs(c-o),.04); low=min(o,c)
    ax.add_patch(Rectangle((xi-width/2,low),width,body,facecolor=color,edgecolor=color,alpha=.9))
for ma,col in [('MA20','#60a5fa'),('MA50','#fbbf24'),('MA200','#a78bfa')]:
    ax.plot(view['date'],view[ma],color=col,linewidth=1.45,label=ma)

# draw pattern lines/zones
start=view['date'].iloc[0]; end=view['date'].iloc[-1]
def dnum(t): return mdates.date2num(pd.to_datetime(t))
for p in top:
    direction=p.get('direction'); col='#22c55e' if direction=='bullish' else '#fb7185'
    lev=p.get('levels') or {}
    if 'zoneLow' in lev and 'zoneHigh' in lev:
        ax.axhspan(float(lev['zoneLow']),float(lev['zoneHigh']),color=col,alpha=.10)
    for key in ['support','resistance','neckline','target','stop']:
        if key in lev and lev[key] is not None:
            style='--' if key in ['support','resistance','neckline'] else ':'
            alpha=.72 if key in ['support','resistance','neckline'] else .5
            ax.axhline(float(lev[key]),color=col,linestyle=style,linewidth=1.1,alpha=alpha)
            ax.text(start,float(lev[key]),f' {p["type"]} {key} {float(lev[key]):.2f}',color=col,fontsize=7.5,va='bottom',alpha=.95)
    for line in p.get('lines',[]):
        pts=line.get('points',[])
        if line.get('type')=='diagonal' and len(pts)>=2:
            xs=[pd.to_datetime(q['time']) for q in pts[:2]]; ys=[float(q['value']) for q in pts[:2]]
            ax.plot(xs,ys,color=col,linewidth=2.0,alpha=.75)
            ax.text(xs[-1],ys[-1],f" {p['type']}",color=col,fontsize=8,va='center')
        elif line.get('type')=='point':
            for q in pts:
                qt=pd.to_datetime(q['time']); qv=float(q['value'])
                if qt>=start:
                    ax.scatter([qt],[qv],s=62,color=col,edgecolor='white',linewidth=.7,zorder=5)
                    ax.text(qt,qv+.7,f"{p['type']}",color=col,fontsize=7,ha='center')

# key levels from summary bold
for s in summary['keyLevels'].get('supports',[]):
    if abs(float(s)-close)/close<.35: ax.axhline(float(s),color='#16a34a',linestyle='-',linewidth=.8,alpha=.35)
for r in summary['keyLevels'].get('resistances',[]):
    if abs(float(r)-close)/close<.35: ax.axhline(float(r),color='#dc2626',linestyle='-',linewidth=.8,alpha=.35)

ax.set_title(f"MWG Pattern Map | {last['date'].date()} close {close:.2f} ({chg:+.2%})",loc='left',fontsize=16,fontweight='bold',color='white')
ax.legend(loc='upper left',ncol=3,frameon=False,labelcolor='white')
ax.grid(True,axis='y',alpha=.14,color='white')
ax.tick_params(colors='#cbd5e1'); ax.set_ylabel('Price',color='#cbd5e1')
plt.setp(ax.get_xticklabels(),visible=False)

vol_colors=['#22c55e' if c>=o else '#ef4444' for o,c in zip(view['open'],view['close'])]
axv.bar(view['date'],view['volume']/1e6,color=vol_colors,width=.8,alpha=.65)
axv.plot(view['date'],view['volume'].rolling(20).mean()/1e6,color='#e2e8f0',linewidth=1.1)
axv.grid(True,axis='y',alpha=.12,color='white'); axv.tick_params(colors='#cbd5e1'); axv.set_ylabel('Vol(M)',color='#cbd5e1')
axv.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# pattern evidence panel
axp.text(.02,.98,'PATTERN EVIDENCE',color='white',fontsize=13,fontweight='bold',va='top')
axp.text(.02,.93,f"Bias: {summary['bias']} | bull {summary['bullScore']:.1f} | bear {summary['bearScore']:.1f}",color='#cbd5e1',fontsize=8.5,va='top')
y=.87
for i,p in enumerate(top[:7],1):
    col='#22c55e' if p.get('direction')=='bullish' else '#fb7185'
    ev=p.get('evidence') or {}; lev=p.get('levels') or {}
    title=f"{i}. {p['type']} · {p['direction']} · {p['confidence']}"
    axp.text(.02,y,title,color=col,fontsize=9,fontweight='bold',va='top')
    y-=.036
    txt=ev.get('notes') or ''
    if lev:
        lv=', '.join([f'{k}:{v}' for k,v in lev.items() if v is not None][:3])
        txt += ' | '+lv
    axp.text(.04,y,txt,color='#cbd5e1',fontsize=7.5,va='top',wrap=True)
    y-=.075

conf=summary.get('conflicts',[])[:2]
axp.text(.02,y-.01,'CONFLICTS',color='#fbbf24',fontsize=10,fontweight='bold',va='top'); y-=.06
for c in conf:
    axp.text(.04,y,f"{c.get('bullish')} vs {c.get('bearish')}",color='#fde68a',fontsize=8,va='top')
    y-=.045
    axp.text(.04,y,c.get('note',''),color='#cbd5e1',fontsize=7.2,va='top',wrap=True); y-=.08

# bottom narrative
sups=sorted([float(v) for v in summary['keyLevels'].get('supports',[]) if float(v)<close],reverse=True)
ress=sorted([float(v) for v in summary['keyLevels'].get('resistances',[]) if float(v)>close])
notes=[
    f"Nearest support: {sups[0]:.2f} ({close/sups[0]-1:+.1%})" if sups else 'Nearest support: n/a',
    f"Nearest resistance: {ress[0]:.2f} ({ress[0]/close-1:+.1%} room)" if ress else 'Nearest resistance: n/a',
    "Triple-top neckline/target/stop and trendlines are drawn from pattern cache; use as confluence, not standalone signal.",
    "Analysis context only — confirm with market regime, fundamentals, liquidity and OOS evidence."
]
axn.text(.01,.68,'Decision notes',color='white',fontsize=11,fontweight='bold')
axn.text(.01,.22,'  •  '.join(notes),color='#cbd5e1',fontsize=9.2)

fig.autofmt_xdate()
out=REPORTS/'MWG_pattern_map_chart.png'
fig.savefig(out,bbox_inches='tight',facecolor='#0b1220')
print(out,out.stat().st_size)
