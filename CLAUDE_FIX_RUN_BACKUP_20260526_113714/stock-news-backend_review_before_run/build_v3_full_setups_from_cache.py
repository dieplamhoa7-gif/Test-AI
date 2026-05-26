from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

IN=Path('data/v3_full_indicator_cache_v2.json')
OUT=Path('data/v3_full_setups_from_cache.json')

def f(v,d=0.0):
    try:
        if v is None: return d
        return float(v)
    except Exception: return d

def eval_setup(item, mode):
    ind=item.get('indicators') or {}; rs=item.get('rs') or {}; price=f(item.get('price'))
    score=f((ind.get('v3FullScore') or {}).get('score100'))
    rr=f(ind.get('riskReward'))
    rsi=f(ind.get('rsi14'),50); adx=f(ind.get('adx14')); pdi=f(ind.get('plusDi')); mdi=f(ind.get('minusDi'))
    hist=f(ind.get('histogram')); volr=f(ind.get('volumeRatio'),1); roc20=f(ind.get('roc20'))
    ichi=ind.get('ichimoku') or {}; ichi_state=ichi.get('state'); ichi_bull=bool(ichi.get('bullishTkCross'))
    bbp=f(ind.get('bbPercent'),0.5); eff=ind.get('effectiveTrend') or ''; div=ind.get('divergence') or {}
    support=f(rs.get('activeSupportDay') or rs.get('supportDay')); resistance=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'))
    support_zone=rs.get('supportZoneDay') or [support*0.985,support*1.015]
    dist_support=(price-support)/price*100 if price and support else 999
    reasons=[]; fails=[]
    # base gates
    if mode=='strict':
        req_score=58; max_dist=4.5; req_rr=0.8; require_ichi=True
    elif mode=='relaxed_ichimoku':
        req_score=52; max_dist=6.0; req_rr=0.65; require_ichi=False
    else: # loose_score
        req_score=47; max_dist=7.5; req_rr=0.5; require_ichi=False
    checks={
        'scoreOk': score>=req_score,
        'nearSupportOk': dist_support<=max_dist,
        'rrOk': rr>=req_rr,
        'rsiOk': 38<=rsi<=68,
        'macdOk': hist>=-0.08,
        'adxDiOk': (pdi>=mdi) or adx>=18,
        'volumeOk': 0.55<=volr<=2.5,
        'bollingerOk': bbp<=0.92,
        'rocOk': roc20>=-8,
        'ichimokuOk': (ichi_state=='above_cloud') or (not require_ichi and ichi_state in ['above_cloud','in_cloud','unknown']) or ichi_bull,
        'trendOk': not str(eff).startswith('Giảm') or score>=req_score+8,
        'divergenceOk': not bool(div.get('bearish')),
    }
    for k,v in checks.items():
        (reasons if v else fails).append(k)
    ok=all(checks.values())
    if not ok: return None, {'symbol':item.get('symbol'),'mode':mode,'score':score,'fails':fails,'distSupportPct':round(dist_support,2),'rr':rr,'ichimoku':ichi_state}
    entry_low=round(support_zone[0],2) if isinstance(support_zone,list) else round(support*0.985,2)
    entry_high=round(min(price, support_zone[1] if isinstance(support_zone,list) else support*1.015),2)
    stop=round(entry_low*0.95,2)
    risk=max(price-stop,0.01); target=round(price+risk*3,2)
    return {
        'symbol':item.get('symbol'),'date':item.get('date'),'mode':mode,'rankScore':score,'price':price,
        'entry':f'{entry_low} - {entry_high}','entryLow':entry_low,'entryHigh':entry_high,'stopLoss':stop,'target3R':target,
        'support':support,'resistance':resistance,'distSupportPct':round(dist_support,2),'riskReward':rr,
        'reason':f"V3-full {mode}: gần hỗ trợ, score {score}, RSI {rsi}, ADX {adx}, Ichimoku {ichi_state}, MACD hist {hist}, RR {rr}",
        'checks':checks,'indicators':ind,'rs':rs
    }, None

def main():
    data=json.load(open(IN,encoding='utf-8'))
    items=data.get('items') or []
    all_modes={}; diagnostics={}
    for mode in ['strict','relaxed_ichimoku','loose_score']:
        setups=[]; rejects=[]
        for item in items:
            s,r=eval_setup(item,mode)
            if s: setups.append(s)
            elif r: rejects.append(r)
        setups.sort(key=lambda x:(x['rankScore'],x['riskReward']),reverse=True)
        all_modes[mode]=setups; diagnostics[mode]=rejects[:80]
    chosen='strict'
    if len(all_modes[chosen])<5: chosen='relaxed_ichimoku'
    if len(all_modes[chosen])<5: chosen='loose_score'
    payload={'createdAt':datetime.now().isoformat(),'method':'Build current V3-full setups from indicator cache; no R/S recomputation. Auto relaxes Ichimoku/score if strict has too few setups.','input':str(IN),'counts':{k:len(v) for k,v in all_modes.items()},'chosenMode':chosen,'setups':all_modes[chosen],'allModes':all_modes,'diagnostics':diagnostics}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'counts':payload['counts'],'chosenMode':chosen,'chosenCount':len(payload['setups']),'top':[{'symbol':x['symbol'],'score':x['rankScore'],'entry':x['entry'],'stop':x['stopLoss'],'target':x['target3R']} for x in payload['setups'][:10]]},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
