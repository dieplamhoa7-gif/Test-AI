from __future__ import annotations
import json, pathlib, pandas as pd
import build_lh2_v6 as lh2

ROOT=pathlib.Path(__file__).resolve().parent
PUB=ROOT/'firebase_public'/'data'
OUT=PUB/'lh2_final_current_watchlist.json'
RESULTS=PUB/'strategy_results_cache.json'

def rr(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def resistance_support_from_chart(sym, entry):
    p=PUB/'charts'/f'{sym}.json'
    levels=[]; supports=[]
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        rows=data.get('rows') or []
        highs=[float(x.get('high')) for x in rows[-180:] if x.get('high') is not None]
        lows=[float(x.get('low')) for x in rows[-180:] if x.get('low') is not None]
        closes=[float(x.get('close')) for x in rows[-180:] if x.get('close') is not None]
        for win in [20,50,120,180]:
            if len(highs)>=win: levels.append(max(highs[-win:]))
            if len(lows)>=win: supports.append(min(lows[-win:]))
        # add simple local pivot highs/lows from last 120 bars
        rr=rows[-140:]
        for i in range(2,len(rr)-2):
            h=float(rr[i].get('high') or 0); l=float(rr[i].get('low') or 0)
            if h and all(h>=float(rr[j].get('high') or 0) for j in [i-2,i-1,i+1,i+2]): levels.append(h)
            if l and all(l<=float(rr[j].get('low') or 10**9) for j in [i-2,i-1,i+1,i+2]): supports.append(l)
    except Exception:
        pass
    # choose nearest resistance above entry with at least ~2% upside; fallback 12%
    resistances=sorted({round(x,2) for x in levels if x>entry*1.02})
    target=resistances[0] if resistances else entry*1.12
    # choose nearest support below entry but not too tight; fallback 5%
    below=sorted({round(x,2) for x in supports if entry*0.88<=x<entry*0.99}, reverse=True)
    support=below[0] if below else entry*0.95
    # stop slightly below support, but cap max risk around 7% unless support is very close
    stop=min(entry*0.95, support*0.985) if support<entry else entry*0.95
    if stop<entry*0.93: stop=entry*0.95
    return round(target,2), round(stop,2), {'targetSource':'nearest_resistance_from_chart' if resistances else 'fallback_12pct','stopSource':'support_or_5pct_risk','resistanceCandidates':resistances[:5],'supportCandidates':below[:5]}

def score_candidate(row, rs_rank, br, regime, e):
    checks=[]
    def add(name, ok, value, need, weight=1):
        checks.append({'name':name,'ok':bool(ok),'value':value,'need':need,'weight':weight})
    breakout20=lh2.f(row.close)>lh2.f(row.high20_prev); breakout50=lh2.f(row.close)>lh2.f(row.high50_prev)
    add('breakout_high20_or_high50', breakout20 or breakout50, {'breakout20':breakout20,'breakout50':breakout50}, True, 3)
    add('rsRank', rs_rank>=e['rsRank'], rr(rs_rank), f">={e['rsRank']}", 2)
    add('volumeRatio', e['volLo']<=lh2.f(row.volRatio)<=e['volHi'], rr(row.volRatio), f"{e['volLo']}..{e['volHi']}", 2)
    add('obvSlope20', lh2.f(row.obvSlope20)>=e['obv'], rr(row.obvSlope20,4), f">={e['obv']}", 2)
    add('vwapSlope5', lh2.f(row.vwapSlope5)>=e['vwap'], rr(row.vwapSlope5), f">={e['vwap']}", 2)
    add('breadth', br>=e['breadth'], rr(br), f">={e['breadth']}", 1)
    add('rangePos60', lh2.f(row.rangePos60)>=e['rangePos'], rr(row.rangePos60), f">={e['rangePos']}", 1)
    add('adx14', lh2.f(row.adx14)>=e['adx'], rr(row.adx14), f">={e['adx']}", 1)
    add('rsi14', e['rsiLo']<=lh2.f(row.rsi14)<=e['rsiHi'], rr(row.rsi14), f"{e['rsiLo']}..{e['rsiHi']}", 1)
    add('nearHigh252', lh2.f(row.nearHigh252)>=e['nearHigh'], rr(row.nearHigh252), f">={e['nearHigh']}", 1)
    if e.get('regime'): add('market_regime', regime==1, regime, 1, 1)
    if e.get('trend'): add('ma_trend', lh2.f(row.close)>=lh2.f(row.ma50) and lh2.f(row.ma20)>=lh2.f(row.ma50), {'close':rr(row.close),'ma20':rr(row.ma20),'ma50':rr(row.ma50)}, 'close>=ma50 & ma20>=ma50', 1)
    if e.get('macd'): add('macdHist', lh2.f(row.macdHist)>=0, rr(row.macdHist), '>=0', 1)
    total=sum(c['weight'] for c in checks); got=sum(c['weight'] for c in checks if c['ok'])
    missing=[c for c in checks if not c['ok']]
    return round(got/total*100,2), checks, missing

def main():
    hist=lh2.load(lh2.find_data()); mkt, rsRank=lh2.market(hist); e=lh2.PRESETS['BALANCED']['entry']
    candidates=[]; buy=[]; latest_dates=[]
    for sym,df in hist.items():
        if df.empty or sym not in rsRank.columns: continue
        i=len(df)-1; row=df.iloc[i]; date=row.time
        latest_dates.append(pd.Timestamp(date))
        if date not in mkt.index: continue
        rs=float(rsRank.loc[date,sym]) if pd.notna(rsRank.loc[date,sym]) else 0.0
        br=lh2.f(mkt.loc[date].breadth); regime=int(lh2.f(mkt.loc[date].regime))
        full=lh2.passes(row, rs, br, regime, e)
        score,checks,missing=score_candidate(row,rs,br,regime,e)
        close=lh2.f(row.close)
        entry=close
        target,stop,level_meta=resistance_support_from_chart(sym, entry)
        missing_details=[f"{m['name']}: hiện {m['value']} / cần {m['need']}" for m in missing]
        target_pct=(target/entry-1)*100 if entry else 0
        stop_pct=(1-stop/entry)*100 if entry else 0
        item={'symbol':sym,'date':str(pd.Timestamp(date).date()),'close':rr(close),'action':'BUY' if full else 'WATCH','rankScore':score,
              'entryPrice':rr(entry),'buyPrice':rr(entry),'targetPrice':rr(target),'takeProfit':rr(target),'stopLoss':rr(stop),'targetPct':rr(target_pct),'stopPct':rr(stop_pct),'levelMeta':level_meta,
              'missingCount':len(missing),'missingReasons':[m['name'] for m in missing[:8]],'missingDetails':missing_details[:12],
              'hoverNote':('Đạt đủ LH2 Final — có thể mua theo hệ thống.' if full else 'Chưa mua: còn thiếu ' + '; '.join(missing_details[:8])),
              'scores':{'rsRank':rr(rs),'volumeRatio':rr(row.volRatio),'obvSlope20':rr(row.obvSlope20,4),'vwapSlope5':rr(row.vwapSlope5),'breadth':rr(br),'rangePos60':rr(row.rangePos60),'adx14':rr(row.adx14),'rsi14':rr(row.rsi14),'nearHigh252':rr(row.nearHigh252),'breakout20':bool(lh2.f(row.close)>lh2.f(row.high20_prev)),'breakout50':bool(lh2.f(row.close)>lh2.f(row.high50_prev))},'checks':checks}
        if full: buy.append(item)
        else: candidates.append(item)
    candidates.sort(key=lambda x:(x['rankScore'],-x['missingCount']), reverse=True)
    # Always publish a practical watchlist: top near-pass candidates, even if none reaches strict 70+ score.
    watch=candidates[:20]
    out={'status':'completed','strategy':'LH2 Final / v6 BALANCED current scan','createdAt':pd.Timestamp.now().isoformat(),'latestDate':str(max(latest_dates).date()) if latest_dates else None,'buyCount':len(buy),'watchCount':len(watch),'buy':buy,'watchlist':watch,'note':'BUY = pass full LH2 Final. WATCH = top near-pass current candidates ranked by LH2 Final condition score; may still miss several strict filters.'}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    # Update web strategy_results_cache only (output/watchlist), not frontend.
    results=json.loads(RESULTS.read_text(encoding='utf-8'))
    results['updatedAt']=pd.Timestamp.now().isoformat()
    strategies=[s for s in results.get('strategies',[]) if s.get('id')!='lh2_final']
    strategies.append({'id':'lh2_final','name':'LH2 Final','buy':buy,'watchlist':watch,'rejectTop':[],'rejectCount':0,'source':'data/lh2_final_current_watchlist.json','canonical':True,'method':'LH2 v6 BALANCED current scan. BUY are full pass; WATCH are near-pass candidates.'})
    results['strategies']=strategies
    RESULTS.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'latestDate':out['latestDate'],'buyCount':len(buy),'watchCount':len(watch),'buySymbols':[x['symbol'] for x in buy],'watchSymbols':[x['symbol'] for x in watch[:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
