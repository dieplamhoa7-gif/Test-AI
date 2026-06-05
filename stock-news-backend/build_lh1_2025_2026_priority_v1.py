import json, pathlib, itertools, pandas as pd
DATA=pathlib.Path('data')
SRC=DATA/'lh1_premium_v2_four_groups_backtest.json'
OUT=DATA/'lh1_2025_2026_priority_v1_backtest.json'
TRADES=json.loads(SRC.read_text(encoding='utf-8')).get('trades',[])

def sm(rows):
    n=len(rows); vals=[float(x.get('netPnlPct') or 0) for x in rows]; w=sum(v>0 for v in vals); stops=sum(x.get('exitType')=='stop' for x in rows)
    return {'trades':n,'wins':w,'losses':n-w,'winRatePct':round(w/n*100,2) if n else 0,'avgNetPnlPct':round(sum(vals)/n,2) if n else 0,'sumNetPnlPct':round(sum(vals),2),'stopRatePct':round(stops/n*100,2) if n else 0}

def rin(rows,a,b):
    aa=pd.Timestamp(a); bb=pd.Timestamp(b)
    return [x for x in rows if aa<=pd.Timestamp(x['signalDate'])<bb]

def passg(t,g):
    sc=t.get('scores') or {}; mf=sc.get('moneyflow') or {}
    rel=sc.get('rel20Pct',0); vwap=mf.get('vwapSlope5',0); obv=mf.get('obvSlope5',0)
    return (
        sc.get('trend',0)>=g['trend'] and
        sc.get('momentum',0)>=g['momentum'] and
        sc.get('volumeMoneyflow',0)>=g['volume'] and
        sc.get('relativeMarket',0)>=g['relative'] and
        sc.get('total',0)>=g['total'] and
        g['rel_lo']<=rel<=g['rel_hi'] and
        vwap>=g['vwap'] and obv>=g['obv']
    )

def gates():
    for total,trend,mom,vol,relative,rel_lo,rel_hi,vwap,obv in itertools.product(
        [72,76,80,84,88],[65,70,75],[70,75,80,90],[50,60,70,80],[45,50,55,60],[-5,-3,-1,0],[1,2,3,5,8],[-0.2,0,0.2,0.5],[-0.2,0,0.2,0.5]
    ):
        if rel_lo < rel_hi:
            yield {'total':total,'trend':trend,'momentum':mom,'volume':vol,'relative':relative,'rel_lo':rel_lo,'rel_hi':rel_hi,'vwap':vwap,'obv':obv}

def score(m25,m26,mall):
    # Prioritize 2025/2026, but penalize tiny samples and bad overall robustness.
    n25=m25['trades']; n26=m26['trades']; nall=mall['trades']
    if n25 < 4 or nall < 8: return -999999
    s=0
    s += m25['avgNetPnlPct']*4.0 + m25['winRatePct']*0.35 - m25['stopRatePct']*0.18 + min(n25,18)*0.6
    # 2026 has little data; reward if present and positive, don't require.
    if n26:
        s += m26['avgNetPnlPct']*3.0 + m26['winRatePct']*0.25 - m26['stopRatePct']*0.15 + min(n26,8)*0.8
    else:
        s -= 2
    s += mall['avgNetPnlPct']*1.0 + mall['winRatePct']*0.08 - mall['stopRatePct']*0.05
    if mall['avgNetPnlPct'] < 2 or mall['winRatePct'] < 50: s -= 20
    return s

rows2025=rin(TRADES,'2025-01-01','2026-01-01')
rows2026=rin(TRADES,'2026-01-01','2026-07-01')
rowsall=rin(TRADES,'2023-01-01','2026-07-01')
scored=[]
for g in gates():
    t25=[x for x in rows2025 if passg(x,g)]
    t26=[x for x in rows2026 if passg(x,g)]
    tall=[x for x in rowsall if passg(x,g)]
    m25=sm(t25); m26=sm(t26); mall=sm(tall); s=score(m25,m26,mall)
    if s>-999999:
        scored.append({'gate':g,'score':round(s,3),'summary2025':m25,'summary2026':m26,'summaryAll':mall,'trades':tall})
scored.sort(key=lambda x:(x['score'],x['summary2025']['avgNetPnlPct'],x['summaryAll']['trades']), reverse=True)
best=scored[0] if scored else None
out={'status':'completed','createdAt':pd.Timestamp.now().isoformat(),'method':'LH1 2025-2026 Priority v1 from LH1 premium universe','source':str(SRC),'policy':{'objective':'prioritize 2025 and 2026 performance, retain minimum all-period robustness','min2025Trades':4,'minAllTrades':8},'rawBaseline':{'2025':sm(rows2025),'2026':sm(rows2026),'all':sm(rowsall)},'best':{k:v for k,v in best.items() if k!='trades'} if best else None,'top20':[{k:v for k,v in x.items() if k!='trades'} for x in scored[:20]],'bestTrades':best['trades'] if best else []}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'best':out['best'],'rawBaseline':out['rawBaseline']},ensure_ascii=False,indent=2))
