from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from datetime import datetime,timedelta
from app.market_data import _load_history,_calc_technical
from app.technical_filters import TECHNICAL_UNIVERSE

LOOKBACK_DAYS=180
OOS_DAYS=60
MAX_SYMBOLS=50
HORIZON=20
MIN_ZONE_SCORE=55
EXCLUDE={"VIC","VHM"}
OUT=Path('data/v3_wide_stop_high_target_backtest.json')

VARIANTS=[]
for stop_atr in [0.6,0.8,1.0,1.2]:
 for target_r in [1.5,2.0,2.5,3.0]:
  for max_risk in [7.0,8.5,10.0]:
   for min_rr in [1.2,1.5,2.0]:
    VARIANTS.append({'stopAtr':stop_atr,'targetR':target_r,'maxRiskPct':max_risk,'minRR':min_rr})

def ema(s,span): return s.ewm(span=span,adjust=False).mean()
def enrich(df):
 df=df.copy()
 for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
 df['ma10']=df.close.rolling(10).mean(); df['ma20']=df.close.rolling(20).mean(); df['ma50']=df.close.rolling(50).mean(); df['vol20']=df.volume.rolling(20).mean()
 d=df.close.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean(); df['rsi']=100-(100/(1+g/l.replace(0,1e-9)))
 macd=ema(df.close,12)-ema(df.close,26); df['hist']=macd-ema(macd,9)
 tr=pd.concat([(df.high-df.low),(df.high-df.close.shift()).abs(),(df.low-df.close.shift()).abs()],axis=1).max(axis=1); df['atr']=tr.rolling(14).mean(); df['ret5']=df.close/df.close.shift(5)-1
 return df


def get_support_zones(tech, price):
    raw = tech.get('supportZonesDay') or []
    zones = []
    for z in raw:
        try:
            zones.append({'low': float(z.get('low')), 'high': float(z.get('high')), 'center': float(z.get('center')), 'score': float(z.get('score') or 60)})
        except Exception:
            pass
    if zones:
        return zones
    candidates = []
    for key in ['activeSupportDay', 'supportDay', 'nearSupportDay']:
        try:
            v = float(tech.get(key) or 0)
            if v > 0:
                candidates.append(v)
        except Exception:
            pass
    for v in tech.get('supportLevelsDay') or []:
        try:
            vv = float(v)
            if vv > 0:
                candidates.append(vv)
        except Exception:
            pass
    seen = []
    for c in candidates:
        if any(abs(c-x)/max(c,1) < 0.003 for x in seen):
            continue
        seen.append(c)
        dist = abs(price - c) / max(price, 1) * 100
        score = max(55, min(85, 80 - dist * 5))
        zones.append({'low': c * 0.985, 'high': c * 1.015, 'center': c, 'score': score})
    return zones

def confirm(prev,cur,zl,zh):
 rng=max(float(cur.high-cur.low),float(cur.close)*0.001); green=float(cur.close)>float(cur.open); close_pos=(float(cur.close)-float(cur.low))/rng; lower=(min(float(cur.open),float(cur.close))-float(cur.low))/rng
 holds=float(cur.close)>=zl and float(cur.low)<=zh; reclaim=float(cur.close)>max(float(prev.close),zh*0.995)
 return holds and close_pos>=0.55 and (green or lower>=0.38 or reclaim)

def setups_sym(sym,cutoff):
 df=_load_history(sym)
 if df is None or df.empty or len(df)<130: return []
 df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich(df); setups=[]
 for i in range(95,len(df)-HORIZON-1):
  if df.iloc[i].time<cutoff: continue
  touch=df.iloc[i]; conf=df.iloc[i+1]
  tech=_calc_technical(float(touch.close),float(touch.open),float(touch.open),float(touch.high),float(touch.low),float(touch.close),df.iloc[:i+1].copy())
  zones=[z for z in (get_support_zones(tech, float(touch.close))) if float(z.get('score') or 0)>=MIN_ZONE_SCORE]
  if not zones: continue
  zone=sorted(zones,key=lambda z: abs(float(touch.close)-float(z['center'])))[0]; zl,zh=float(zone['low']),float(zone['high'])
  if not(float(touch.low)<=zh and float(touch.close)>=zl): continue
  if not confirm(touch,conf,zl,zh): continue
  ma20=float(conf.ma20 or 0); ma50=float(conf.ma50 or 0); ma50p=float(df.iloc[i-10].ma50 or ma50)
  if not(float(conf.close)>=ma50*0.985 and ma20>=ma50*0.975 and ma50>=ma50p*0.985): continue
  if float(touch.ret5 or 0)<-0.09: continue
  rsi_ok=float(conf.rsi or 0)>=39 and float(conf.rsi or 0)>=float(touch.rsi or 0)-0.5
  hist_ok=float(conf['hist'] or 0)>=float(touch['hist'] or 0)
  vol_ok=float(conf.volume or 0)>=float(touch.volume or 0)*0.70 and float(touch.volume or 0)<=float(touch.vol20 or touch.volume)*2.2
  if sum([rsi_ok,hist_ok,vol_ok])<2: continue
  atr=float(conf.atr or float(conf.close)*0.03)
  res=[float(x) for x in (tech.get('resistanceLevelsDay') or []) if float(x)>float(conf.close)]
  setups.append({'symbol':sym,'date':str(conf.time.date()),'i':i,'entry':float(conf.close),'zl':zl,'zh':zh,'touchLow':float(touch.low),'confLow':float(conf.low),'atr':atr,'resistance':min(res) if res else None,'zoneScore':zone.get('score'),'future':df.iloc[i+2:i+2+HORIZON][['time','high','low','close']].assign(time=lambda x:x['time'].astype(str)).to_dict('records')})
 return setups

def trade_from_setup(s,cfg):
 entry=s['entry']; atr=s['atr']
 stop=min(s['zl']-cfg['stopAtr']*atr, s['touchLow']-0.2*atr, s['confLow']-0.2*atr)
 risk=entry-stop
 if risk<=0: return None
 risk_pct=risk/entry*100
 if risk_pct<1.0 or risk_pct>cfg['maxRiskPct']: return None
 target=entry+risk*cfg['targetR']
 if s.get('resistance') and s['resistance']>entry:
  rr_res=(s['resistance']-entry)/risk
  # allow resistance target only if not too tiny; otherwise keep high target R
  if rr_res>=cfg['minRR'] and rr_res>=cfg['targetR']*0.75:
   target=s['resistance']
 rr=(target-entry)/risk
 if rr<cfg['minRR']: return None
 future=s['future']; outcome='timeout'; exitp=float(future[-1]['close']); exitd=future[-1]['time'][:10]; hold=len(future)
 for k,r in enumerate(future,1):
  hit_stop=float(r['low'])<=stop; hit_target=float(r['high'])>=target
  if hit_stop and hit_target: outcome='loss'; exitp=stop; exitd=r['time'][:10]; hold=k; break
  if hit_target: outcome='win'; exitp=target; exitd=r['time'][:10]; hold=k; break
  if hit_stop: outcome='loss'; exitp=stop; exitd=r['time'][:10]; hold=k; break
 pnl=(exitp-entry)/entry*100
 return {'symbol':s['symbol'],'date':s['date'],'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(entry,2),'stop':round(stop,2),'target':round(target,2),'riskPct':round(risk_pct,2),'rr':round(rr,2),'holdSessions':hold,'exitDate':exitd,'zoneScore':s.get('zoneScore')}

def summ(ts):
 n=len(ts); w=[t for t in ts if t['outcome']=='win']; l=[t for t in ts if t['outcome']=='loss']; to=[t for t in ts if t['outcome']=='timeout']
 def sm(xs,k): return round(sum(float(x[k]) for x in xs),2) if xs else 0
 def avg(xs,k): return round(sm(xs,k)/len(xs),2) if xs else 0
 return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'lossRatePct':round(len(l)/n*100,2) if n else 0,'timeoutRatePct':round(len(to)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'totalWinPct':sm(w,'pnlPct'),'totalLossPct':sm(l,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRR':avg(ts,'rr'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
 cutoff=pd.Timestamp(datetime.now()-timedelta(days=LOOKBACK_DAYS)); split=pd.Timestamp(datetime.now()-timedelta(days=OOS_DAYS))
 setups=[]
 for sym in [s for s in TECHNICAL_UNIVERSE[:MAX_SYMBOLS] if s not in EXCLUDE]:
  try:
   x=setups_sym(sym,cutoff); setups+=x; print(sym,len(x),flush=True)
  except Exception as e: print(sym,'ERR',e,flush=True)
 results=[]
 for cfg in VARIANTS:
  trades=[t for s in setups for t in [trade_from_setup(s,cfg)] if t]
  sample=[t for t in trades if pd.Timestamp(t['date'])<split]; oos=[t for t in trades if pd.Timestamp(t['date'])>=split]
  ss=summ(sample); os=summ(oos); allsum=summ(trades)
  penalty=0
  if os['totalTrades']<5: penalty+=50
  if ss['sumPnlPct']<0: penalty+=abs(ss['sumPnlPct'])*0.2
  score=os['sumPnlPct']+os['avgPnlPct']*10+ss['sumPnlPct']*0.15+min(os['totalTrades'],30)*0.3-penalty
  results.append({'config':cfg,'score':round(score,2),'sample':ss,'oos':os,'all':allsum})
 results.sort(key=lambda x:x['score'],reverse=True)
 best_cfg=results[0]['config']; best_trades=[t for s in setups for t in [trade_from_setup(s,best_cfg)] if t]
 payload={'createdAt':datetime.now().isoformat(),'method':'Confirmed Support V3 base with wider stop and higher target; output file for reuse','lookbackDays':LOOKBACK_DAYS,'sampleDays':LOOKBACK_DAYS-OOS_DAYS,'oosDays':OOS_DAYS,'horizonSessions':HORIZON,'minZoneScore':MIN_ZONE_SCORE,'excluded':sorted(EXCLUDE),'variantCount':len(VARIANTS),'setupsCount':len(setups),'topResults':results[:30],'bestTrades':best_trades}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(results[:8],ensure_ascii=True,indent=2)); print('saved',OUT)
if __name__=='__main__': main()
