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
        stop=entry*lh2.PRESETS['BALANCED']['exit']['stop']
        target=entry*lh2.PRESETS['BALANCED']['exit']['target']
        missing_details=[f"{m['name']}: hiện {m['value']} / cần {m['need']}" for m in missing]
        item={'symbol':sym,'date':str(pd.Timestamp(date).date()),'close':rr(close),'action':'BUY' if full else 'WATCH','rankScore':score,
              'entryPrice':rr(entry),'buyPrice':rr(entry),'targetPrice':rr(target),'takeProfit':rr(target),'stopLoss':rr(stop),'targetPct':12,'stopPct':5,
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
