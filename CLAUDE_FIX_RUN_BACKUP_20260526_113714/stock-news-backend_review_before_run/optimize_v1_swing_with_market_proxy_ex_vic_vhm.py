from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from app.market_data import _load_history
from app.technical_filters import TECHNICAL_UNIVERSE
EXCLUDE={"VIC","VHM"}
UNIVERSE=[s for s in TECHNICAL_UNIVERSE if s not in EXCLUDE]
OUT=Path('data/v1_swing_market_proxy_ex_vic_vhm_optimization.json')
LOOKBACK_DAYS=240; OOS_DAYS=80; MAX_HORIZON=42
BASE_CONFIGS=[
 {'name':'3R_support_stop','horizon':20,'entry_pad':0.04,'stop_mode':'support_pad','stop_val':0.03,'target_mode':'fixed_3r','rsi_min':30,'vol_max':99.0},
 {'name':'1_5R_entry_stop','horizon':20,'entry_pad':0.03,'stop_mode':'entry_pct','stop_val':0.03,'target_mode':'fixed_1_5r','rsi_min':30,'vol_max':99.0},
 {'name':'resistance_loose','horizon':15,'entry_pad':0.02,'stop_mode':'support_pad','stop_val':0.02,'target_mode':'resistance','rsi_min':32,'vol_max':3.5},
]
REGIMES=['none','proxy_above_ma20','proxy_above_ma50','proxy_above_ma20_hist_up','proxy_rsi50','proxy_rsi45_hist_up','proxy_close_gt_ma20_ma20_up','proxy_close_gt_ma50_ma20_up','proxy_not_broken_ma50']

def enrich(df):
 df=df.copy(); df['close']=pd.to_numeric(df['close'],errors='coerce')
 if 'volume' not in df: df['volume']=0
 df['volume']=pd.to_numeric(df['volume'],errors='coerce')
 df['ma20']=df.close.rolling(20).mean(); df['ma50']=df.close.rolling(50).mean(); df['ma200']=df.close.rolling(200).mean(); df['vol20']=df.volume.rolling(20).mean()
 d=df.close.diff(); g=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); l=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); df['rsi']=100-(100/(1+g/l.replace(0,float('nan'))))
 ema12=df.close.ewm(span=12,adjust=False).mean(); ema26=df.close.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; df['macdHist']=macd-macd.ewm(span=9,adjust=False).mean(); df['histUp']=df.macdHist>df.macdHist.shift(3); df['ma20Up']=df.ma20>df.ma20.shift(5)
 return df

def enrich_stock(df):
 df=df.copy()
 for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
 df['ma50']=df.close.rolling(50).mean(); df['vol20']=df.volume.rolling(20).mean()
 d=df.close.diff(); g=d.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); l=(-d.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); df['rsi']=100-(100/(1+g/l.replace(0,float('nan'))))
 return df

def build_proxy():
 series=[]; used=[]
 for sym in UNIVERSE:
  df=_load_history(sym)
  if df is None or df.empty or len(df)<130: continue
  df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time')
  close=pd.to_numeric(df.close,errors='coerce')
  norm=close/close.dropna().iloc[0]*100
  s=pd.DataFrame({'time':df.time,'close':norm})
  series.append(s.set_index('time')['close'].rename(sym)); used.append(sym)
 proxy=pd.concat(series,axis=1).sort_index().dropna(thresh=max(8,int(len(series)*0.45)))
 out=pd.DataFrame({'time':proxy.index,'close':proxy.mean(axis=1).values,'volume':0})
 return enrich(out.reset_index(drop=True)), used

def regime_ok(row,rid):
 if rid=='none': return True
 c=float(row.close); ma20=float(row.ma20) if pd.notna(row.ma20) else 0; ma50=float(row.ma50) if pd.notna(row.ma50) else 0; rsi=float(row.rsi) if pd.notna(row.rsi) else 0; hist_up=bool(row.histUp); ma20_up=bool(row.ma20Up)
 return {
  'proxy_above_ma20': ma20>0 and c>=ma20,
  'proxy_above_ma50': ma50>0 and c>=ma50,
  'proxy_above_ma20_hist_up': ma20>0 and c>=ma20 and hist_up,
  'proxy_rsi50': rsi>=50,
  'proxy_rsi45_hist_up': rsi>=45 and hist_up,
  'proxy_close_gt_ma20_ma20_up': ma20>0 and c>=ma20 and ma20_up,
  'proxy_close_gt_ma50_ma20_up': ma50>0 and c>=ma50 and ma20_up,
  'proxy_not_broken_ma50': ma50>0 and c>=ma50*0.98,
 }.get(rid,True)

def levels(df,i,lookback=80):
 hist=df.iloc[max(0,i-lookback):i]
 if len(hist)<40: return None,None
 price=float(df.iloc[i].close); lows=pd.to_numeric(hist.low,errors='coerce').dropna().tolist(); highs=pd.to_numeric(hist.high,errors='coerce').dropna().tolist()
 sups=[float(x) for x in lows if float(x)<=price*1.01]; ress=[float(x) for x in highs if float(x)>price]
 if not sups: return None,None
 return max(sups), min(ress) if ress else None

def precompute(proxy):
 rows=[]; start=pd.Timestamp(datetime.now()-timedelta(days=LOOKBACK_DAYS)); proxy_by_date={str(r.time.date()):r for _,r in proxy.iterrows()}
 for sym in UNIVERSE:
  try:
   df=_load_history(sym)
   if df is None or df.empty or len(df)<130: print(sym,'NOH',flush=True); continue
   df=df.copy(); df['time']=pd.to_datetime(df.time); df=df.sort_values('time').reset_index(drop=True); df=enrich_stock(df); cnt=0
   for i in range(90,len(df)-MAX_HORIZON-1):
    date=str(df.iloc[i].time.date())
    if df.iloc[i].time<start or date not in proxy_by_date: continue
    price=pd.to_numeric(pd.Series([df.iloc[i].close]),errors='coerce').iloc[0]
    if pd.isna(price): continue
    price=float(price); support,resistance=levels(df,i)
    if not support: continue
    row=df.iloc[i]; future=df.iloc[i+1:i+1+MAX_HORIZON]
    vol=float(row.volume) if pd.notna(row.volume) else 0; vol20=float(row.vol20) if pd.notna(row.vol20) and float(row.vol20)>0 else (vol or 1)
    regimes={rid:regime_ok(proxy_by_date[date],rid) for rid in REGIMES}
    rows.append({'symbol':sym,'date':date,'price':price,'support':support,'resistance':resistance,'rsi':float(row.rsi) if pd.notna(row.rsi) else 0,'volRatio':vol/vol20 if vol20 else 1,'ma50':float(row.ma50) if pd.notna(row.ma50) else 0,'regimes':regimes,'future':future[['high','low','close','time']].assign(time=future['time'].astype(str)).to_dict('records')}); cnt+=1
   print(sym,cnt,flush=True)
  except Exception as e: print(sym,'ERR',e,flush=True)
 return rows

def trade_for(row,cfg,rid):
 if not row['regimes'].get(rid,False): return None
 p=row['price']; s=row['support']; res=row.get('resistance')
 if not (s<=p<=s*(1+cfg['entry_pad'])): return None
 if row['rsi']<cfg['rsi_min'] or row['volRatio']>cfg['vol_max']: return None
 if row['ma50']>0 and p<row['ma50']*0.90: return None
 stop=s*(1-cfg['stop_val']) if cfg['stop_mode']=='support_pad' else p*(1-cfg['stop_val']); risk=p-stop
 if risk<=0: return None
 if cfg['target_mode']=='fixed_3r': target=p+risk*3
 elif cfg['target_mode']=='fixed_1_5r': target=p+risk*1.5
 elif cfg['target_mode']=='resistance':
  if not res or res<=p: return None
  target=res
 else: target=p+risk*2
 future=row['future'][:cfg['horizon']]
 outcome='timeout'; exitp=float(future[-1]['close']); hold=len(future)
 for k,r in enumerate(future,1):
  hit_stop=float(r['low'])<=stop; hit_target=float(r['high'])>=target
  if hit_stop and hit_target: outcome='loss'; exitp=stop; hold=k; break
  if hit_target: outcome='win'; exitp=target; hold=k; break
  if hit_stop: outcome='loss'; exitp=stop; hold=k; break
 pnl=(exitp-p)/p*100; rr=(target-p)/risk
 return {'symbol':row['symbol'],'date':row['date'],'outcome':outcome,'pnlPct':round(pnl,2),'entry':round(p,2),'support':round(s,2),'stop':round(stop,2),'target':round(target,2),'rr':round(rr,2),'riskPct':round(risk/p*100,2),'holdSessions':hold}

def summ(ts):
 n=len(ts); w=[t for t in ts if t['outcome']=='win']; l=[t for t in ts if t['outcome']=='loss']; to=[t for t in ts if t['outcome']=='timeout']
 def sm(xs,k): return round(sum(float(x[k]) for x in xs),2) if xs else 0
 def avg(xs,k): return round(sm(xs,k)/len(xs),2) if xs else 0
 return {'totalTrades':n,'wins':len(w),'losses':len(l),'timeouts':len(to),'winRatePct':round(len(w)/n*100,2) if n else 0,'lossRatePct':round(len(l)/n*100,2) if n else 0,'timeoutRatePct':round(len(to)/n*100,2) if n else 0,'avgPnlPct':avg(ts,'pnlPct'),'sumPnlPct':sm(ts,'pnlPct'),'totalWinPct':sm(w,'pnlPct'),'totalLossPct':sm(l,'pnlPct'),'avgWinPct':avg(w,'pnlPct'),'avgLossPct':avg(l,'pnlPct'),'avgRR':avg(ts,'rr'),'avgRiskPct':avg(ts,'riskPct'),'avgHoldSessions':avg(ts,'holdSessions')}

def main():
 proxy,used=build_proxy(); rows=precompute(proxy); split=pd.Timestamp(datetime.now()-timedelta(days=OOS_DAYS)); results=[]
 for cfg in BASE_CONFIGS:
  for rid in REGIMES:
   ts=[t for r in rows for t in [trade_for(r,cfg,rid)] if t]
   sample=[t for t in ts if pd.Timestamp(t['date'])<split]; oos=[t for t in ts if pd.Timestamp(t['date'])>=split]
   ss=summ(sample); os=summ(oos); allsum=summ(ts)
   penalty=0
   if os['totalTrades']<8: penalty+=50
   if ss['sumPnlPct']<0: penalty+=abs(ss['sumPnlPct'])*0.15
   score=os['sumPnlPct']+os['avgPnlPct']*8+ss['sumPnlPct']*0.2+min(os['totalTrades'],50)*0.25-penalty
   results.append({'base':cfg['name'],'regime':rid,'score':round(score,2),'config':cfg,'sample':ss,'oos':os,'all':allsum})
 results.sort(key=lambda x:x['score'], reverse=True)
 best=results[0]; best_trades=[t for r in rows for t in [trade_for(r,best['config'],best['regime'])] if t]
 payload={'createdAt':datetime.now().isoformat(),'method':'V1 swing with custom market proxy excluding VIC/VHM; output file for reuse','proxySymbolsUsed':used,'excluded':sorted(EXCLUDE),'topResults':results,'bestTrades':best_trades}
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(results[:12],ensure_ascii=True,indent=2)); print('saved',OUT)
if __name__=='__main__': main()
