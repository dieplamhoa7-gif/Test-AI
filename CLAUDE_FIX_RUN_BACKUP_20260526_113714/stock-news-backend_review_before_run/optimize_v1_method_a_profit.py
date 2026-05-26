from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from app.market_data import _load_history
from app.technical_filters import TECHNICAL_UNIVERSE

EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]
OUT=Path('data/v1_method_a_profit_optimization.json')
LOOKBACK_DAYS=180; OOS_DAYS=60; HORIZON=10
GRIDS=[]
for entry_pad in [0.01,0.015,0.02,0.025]:
 for stop_pad in [0.015,0.02,0.025,0.03]:
  for min_rr in [1.0,1.2,1.5]:
   for target_mode in ['resistance','max_res_1r','fixed_1_5r','fixed_2r']:
    for rsi_min in [38,42,45]:
     GRIDS.append(dict(entry_pad=entry_pad,stop_pad=stop_pad,min_rr=min_rr,target_mode=target_mode,rsi_min=rsi_min))

def enrich(df):
 df=df.copy()
 for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
 df['vol20']=df.volume.rolling(20).mean(); df['ma20']=df.close.rolling(20).mean(); df['ma50']=df.close.rolling(50).mean()
 d=df.close.diff(); g=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); l=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); df['rsi']=100-(100/(1+g/l.replace(0,float('nan'))))
 ema12=df.close.ewm(span=12,adjust=False).mean(); ema26=df.close.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; df['macdHist']=macd-macd.ewm(span=9,adjust=False).mean()
 return df

def levels(df,i,lookback=60):
 hist=df.iloc[max(0,i-lookback):i]
 if len(hist)<30: return None,None
 price=float(df.iloc[i].close)
 lows=pd.to_numeric(hist.low,errors='coerce').dropna().tolist(); highs=pd.to_numeric(hist.high,errors='coerce').dropna().tolist()
 sups=[float(x) for x in lows if float(x)<=price*1.005]; ress=[float(x) for x in highs if float(x)>price]
 if not sups or not ress: return None,None
 return max(sups), min(ress)

def precompute():
 rows=[]; start=pd.Timestamp(datetime.now()-timedelta(days=LOOKBACK_DAYS))
 for sym in UNIVERSE:
  try:
   df=_load_history(sym)
   if df is None or df.empty or len(df)<100: print(sym,'NOH',flush=True); continue
   df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich(df)
   cnt=0
   for i in range(70,len(df)-HORIZON-1):
    if df.iloc[i].time<start: continue
    price=pd.to_numeric(pd.Series([df.iloc[i].close]),errors='coerce').iloc[0]
    if pd.isna(price): continue
    price=float(price); support,resistance=levels(df,i)
    if not support or not resistance: continue
    row=df.iloc[i]
    future=df.iloc[i+1:i+1+HORIZON]
    rows.append({
     'symbol':sym,'date':str(row.time.date()),'price':price,'support':support,'resistance':resistance,
     'rsi':float(row.rsi) if pd.notna(row.rsi) else 0,
     'volRatio':float(row.volume)/(float(row.vol20) if pd.notna(row.vol20) and float(row.vol20)>0 else max(float(row.volume),1)),
     'hist':float(row.macdHist) if pd.notna(row.macdHist) else 0,
     'ma20':float(row.ma20) if pd.notna(row.ma20) else 0,
     'ma50':float(row.ma50) if pd.notna(row.ma50) else 0,
     'future':future[['high','low','close','time']].assign(time=future['time'].astype(str)).to_dict('records')
    }); cnt+=1
   print(sym,cnt,flush=True)
  except Exception as e: print(sym,'ERR',e,flush=True)
 return rows

def trade_for(row,cfg):
 p=row['price']; s=row['support']; res=row['resistance']
 if not (s<=p<=s*(1+cfg['entry_pad'])): return None
 if row['rsi']<cfg['rsi_min'] or row['volRatio']>2.5: return None
 if row['ma50']>0 and p<row['ma50']*0.96: return None
 stop=s*(1-cfg['stop_pad']); risk=p-stop
 if risk<=0: return None
 if cfg['target_mode']=='resistance': target=res
 elif cfg['target_mode']=='max_res_1r': target=res if (res-p)>=risk else p+risk
 elif cfg['target_mode']=='fixed_1_5r': target=p+risk*1.5
 else: target=p+risk*2.0
 reward=target-p; rr=reward/risk
 if rr<cfg['min_rr']: return None
 outcome='timeout'; exitp=float(row['future'][-1]['close']); hold=len(row['future'])
 for k,r in enumerate(row['future'],1):
  hit_stop=float(r['low'])<=stop; hit_target=float(r['high'])>=target
  if hit_stop and hit_target: outcome='loss'; exitp=stop; hold=k; break
  if hit_target: outcome='win'; exitp=target; hold=k; break
  if hit_stop: outcome='loss'; exitp=stop; hold=k; break
 pnl=(exitp-p)/p*100
 return {'symbol':row['symbol'],'date':row['date'],'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(p,2),'support':round(s,2),'stop':round(stop,2),'target':round(target,2),'rr':round(rr,2),'riskPct':round(risk/p*100,2),'holdSessions':hold}

def summ(ts):
 n=len(ts); w=[t for t in ts if t['outcome']=='win']; l=[t for t in ts if t['outcome']=='loss']; to=[t for t in ts if t['outcome']=='timeout']
 def sm(xs,k): return round(sum(float(x[k]) for x in xs),2) if xs else 0
 def avg(xs,k): return round(sm(xs,k)/len(xs),2) if xs else 0
 return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'totalWinPct':sm(w,'pnlPct'),'totalLossPct':sm(l,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRR':avg(ts,'rr'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
 rows=precompute(); split=pd.Timestamp(datetime.now()-timedelta(days=OOS_DAYS)); results=[]; best=None
 for cfg in GRIDS:
  ts=[t for r in rows for t in [trade_for(r,cfg)] if t]
  sample=[t for t in ts if pd.Timestamp(t['date'])<split]; oos=[t for t in ts if pd.Timestamp(t['date'])>=split]
  ss=summ(sample); os=summ(oos); allsum=summ(ts)
  score=os['sumPnlPct'] + os['avgPnlPct']*20 + min(os['totalTrades'],40)*0.2
  rec={'config':cfg,'score':round(score,2),'sample':ss,'oos':os,'all':allsum}
  results.append(rec)
 results.sort(key=lambda x:(x['oos']['sumPnlPct'],x['oos']['avgPnlPct'],x['sample']['sumPnlPct']), reverse=True)
 top=results[:20]
 best_cfg=top[0]['config'] if top else None
 best_trades=[]
 if best_cfg:
  best_trades=[t for r in rows for t in [trade_for(r,best_cfg)] if t]
 payload={'createdAt':datetime.now().isoformat(),'method':'Optimize V1 Method A for profit; output file for reuse; exclude VIC/VHM','lookbackDays':LOOKBACK_DAYS,'sampleDays':LOOKBACK_DAYS-OOS_DAYS,'oosDays':OOS_DAYS,'horizonSessions':HORIZON,'gridCount':len(GRIDS),'topResults':top,'bestTrades':best_trades}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(top[:5],ensure_ascii=True,indent=2)); print('saved',OUT)
if __name__=='__main__': main()
