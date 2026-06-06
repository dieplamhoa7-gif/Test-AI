from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import build_lh1_premium_v2_four_groups as base

OUT=Path('firebase_public/data/lh1_final_current_scan.json')
RESULTS=Path('firebase_public/data/strategy_results_cache.json')
FINAL_CFG=Path('data/lh1_final_2025_2026_priority_config.json')

def rr(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def pass_final(sc):
    mf=sc.get('moneyflow') or {}
    return (sc.get('trend',0)>=65 and sc.get('momentum',0)>=70 and sc.get('volumeMoneyflow',0)>=70 and sc.get('relativeMarket',0)>=45 and sc.get('total',0)>=84 and -1<=sc.get('rel20Pct',0)<=2 and mf.get('vwapSlope5',0)>=0 and mf.get('obvSlope20',0)>=-0.2)

def resistance_support(sym, entry):
    p=Path('firebase_public/data/charts')/f'{sym}.json'
    levels=[]; supports=[]
    try:
        j=json.loads(p.read_text(encoding='utf-8')); rows=j.get('rows') or []
        highs=[float(x.get('high')) for x in rows[-180:] if x.get('high') is not None]
        lows=[float(x.get('low')) for x in rows[-180:] if x.get('low') is not None]
        for win in [20,50,120,180]:
            if len(highs)>=win: levels.append(max(highs[-win:]))
            if len(lows)>=win: supports.append(min(lows[-win:]))
        rrw=rows[-140:]
        for i in range(2,len(rrw)-2):
            h=float(rrw[i].get('high') or 0); l=float(rrw[i].get('low') or 0)
            if h and all(h>=float(rrw[k].get('high') or 0) for k in [i-2,i-1,i+1,i+2]): levels.append(h)
            if l and all(l<=float(rrw[k].get('low') or 10**9) for k in [i-2,i-1,i+1,i+2]): supports.append(l)
    except Exception: pass
    res=sorted({round(x,2) for x in levels if x>entry*1.02})
    sup=sorted({round(x,2) for x in supports if entry*0.88<=x<entry*0.99}, reverse=True)
    target=res[0] if res else entry*1.12
    stop=min(entry*0.95, sup[0]*0.985) if sup else entry*0.95
    if stop<entry*0.93: stop=entry*0.95
    return rr(target), rr(stop), {'targetSource':'nearest_resistance_from_chart' if res else 'fallback_12pct','resistanceCandidates':res[:5],'supportCandidates':sup[:5]}

def missing(sc):
    mf=sc.get('moneyflow') or {}; out=[]
    checks=[('trend',sc.get('trend',0),65),('momentum',sc.get('momentum',0),70),('volumeMoneyflow',sc.get('volumeMoneyflow',0),70),('relativeMarket',sc.get('relativeMarket',0),45),('total',sc.get('total',0),84)]
    for k,v,need in checks:
        if v<need: out.append(f'{k}: hiện {rr(v)} / cần >= {need}')
    rel=sc.get('rel20Pct',0)
    if not (-1<=rel<=2): out.append(f'rel20Pct: hiện {rr(rel)} / cần -1..2')
    if mf.get('vwapSlope5',0)<0: out.append(f'vwapSlope5: hiện {rr(mf.get("vwapSlope5"))} / cần >=0')
    if mf.get('obvSlope20',0)<-0.2: out.append(f'obvSlope20: hiện {rr(mf.get("obvSlope20"),4)} / cần >=-0.2')
    return out

def main():
    cfg=json.loads(FINAL_CFG.read_text(encoding='utf-8')) if FINAL_CFG.exists() else {}
    histories={s:base.add_moneyflow(df) for s,df in base.load_histories().items()}
    market=base.build_market_proxy(histories)
    buy=[]; near=[]; latest=[]
    for sym,df in histories.items():
        ind=base._compute_indicators(df.copy())
        i=len(df)-1; price=base.f(df.iloc[i].close); hist=df.iloc[:i+1].copy(); row=ind.iloc[i]
        rs=base.calc_rs_levels_only(price,base.f(df.iloc[i].open),base.f(df.iloc[i].open),base.f(df.iloc[i].high),base.f(df.iloc[i].low),price,hist)
        ai=base.lh1.action_indicators(price,row,hist,ind.iloc[:i+1].copy())
        ok,reason=base.lh1.pass_b4(price,rs,ai)
        latest.append(str(df.iloc[i].time.date()))
        if not ok: continue
        sc=base.group_scores(sym,df,ind,i,ai,rs,market)
        miss=missing(sc); target,stop,meta=resistance_support(sym,price)
        item={'symbol':sym,'date':str(df.iloc[i].time.date()),'close':rr(price),'action':'BUY' if pass_final(sc) else 'WATCH','rankScore':rr(sc.get('total')),'entryPrice':rr(price),'buyPrice':rr(price),'targetPrice':target,'takeProfit':target,'stopLoss':stop,'targetPct':rr((target/price-1)*100) if price else None,'stopPct':rr((1-stop/price)*100) if price else None,'scores':sc,'entryIndicators':ai,'missingDetails':miss,'missingReasons':[x.split(':')[0] for x in miss],'hoverNote':'Đạt LH1 Final 2025-2026 Priority' if not miss else 'LH1 Final chưa mua: còn thiếu '+ '; '.join(miss[:8]),'levelMeta':meta,'source':'lh1_final_current_scan.json'}
        if item['action']=='BUY': buy.append(item)
        else: near.append(item)
    near.sort(key=lambda x:(len(x['missingDetails']), -(x['rankScore'] or 0)))
    out={'status':'completed','strategy':'LH1 Final 2025-2026 Priority / Sniper','createdAt':pd.Timestamp.now().isoformat(),'latestDates':sorted(set(latest))[-5:],'config':cfg,'buyCount':len(buy),'watchCount':min(len(near),20),'buy':buy,'watchlist':near[:20], 'note':'Only LH1 final output. Older LH1 variants should not be used for web signal.'}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    results=json.loads(RESULTS.read_text(encoding='utf-8'))
    for s in results.get('strategies',[]):
        if s.get('id')=='b4_trend_pullback':
            s['name']='LH1 Final'; s['buy']=buy; s['watchlist']=near[:20]; s['source']='data/lh1_final_current_scan.json'; s['method']='LH1 Final 2025-2026 Priority / Sniper only.'
    results['updatedAt']=pd.Timestamp.now().isoformat(); RESULTS.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'latestDates':out['latestDates'],'buyCount':len(buy),'watchCount':out['watchCount'],'buy':[x['symbol'] for x in buy],'watch':[x['symbol'] for x in near[:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
