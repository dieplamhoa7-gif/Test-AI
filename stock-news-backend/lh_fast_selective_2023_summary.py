from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd

SRC = Path('data/vn100_history_from_2023.json')
OUT = Path('data/lh_fast_selective_2023_summary.json')
START = pd.Timestamp('2023-01-01')
END = pd.Timestamp('2026-06-01')
WINDOWS = {
    '2023': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-01-01')),
    '2024': (pd.Timestamp('2024-01-01'), pd.Timestamp('2025-01-01')),
    '2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2026-01-01')),
    '2026_ytd': (pd.Timestamp('2026-01-01'), END),
    'all_2023_now': (START, END),
}

def load():
    obj=json.loads(SRC.read_text(encoding='utf-8'))
    out={}
    for sym,v in obj.get('symbols',{}).items():
        rows=v.get('rows') or []
        if not rows: continue
        df=pd.DataFrame(rows)
        df['time']=pd.to_datetime(df['time'])
        for c in ['open','high','low','close','volume']:
            df[c]=pd.to_numeric(df[c],errors='coerce')
        df=df.sort_values('time').reset_index(drop=True)
        out[sym]=df
    return out

def ma(s,n): return s.rolling(n).mean()
def rsi(close,n=14):
    d=close.diff(); up=d.clip(lower=0).rolling(n).mean(); dn=(-d.clip(upper=0)).rolling(n).mean(); rs=up/dn.replace(0,pd.NA); return 100-100/(1+rs)
def atr(df,n=14):
    pc=df.close.shift(1); tr=pd.concat([(df.high-df.low),(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1); return tr.rolling(n).mean()

def add_ind(df):
    df=df.copy(); c=df.close; v=df.volume
    df['ma10']=ma(c,10); df['ma20']=ma(c,20); df['ma50']=ma(c,50); df['ma100']=ma(c,100); df['ma200']=ma(c,200)
    df['rsi14']=rsi(c); df['atr14']=atr(df); df['atrp']=df['atr14']/c*100
    df['volma20']=v.rolling(20).mean(); df['volr']=v/df['volma20']; df['roc20']=(c/c.shift(20)-1)*100; df['roc60']=(c/c.shift(60)-1)*100
    df['high20prev']=df.high.rolling(20).max().shift(1); df['high60prev']=df.high.rolling(60).max().shift(1)
    df['low20prev']=df.low.rolling(20).min().shift(1); df['low60prev']=df.low.rolling(60).min().shift(1)
    ema12=c.ewm(span=12,adjust=False).mean(); ema26=c.ewm(span=26,adjust=False).mean(); macd=ema12-ema26; sig=macd.ewm(span=9,adjust=False).mean(); df['hist']=macd-sig
    df['mkt_proxy']=None
    return df

def exit_trade(df,i,target=6,stop=4.5,horizon=20,minhold=3):
    if i+1>=len(df): return None
    entry=float(df.iloc[i+1].close); fut=df.iloc[i+2:i+2+horizon]
    if not entry or fut.empty: return None
    tgt=entry*(1+target/100); stp=entry*(1-stop/100); outcome='timeout'; exitp=float(fut.iloc[-1].close); bars=len(fut)
    for k,(_,row) in enumerate(fut.iterrows(),1):
        if k<minhold: continue
        hit_t=float(row.high)>=tgt; hit_s=float(row.low)<=stp
        if hit_s and hit_t: outcome='loss'; exitp=stp; bars=k; break
        if hit_t: outcome='win'; exitp=tgt; bars=k; break
        if hit_s: outcome='loss'; exitp=stp; bars=k; break
    pnl=(exitp-entry)/entry*100
    return pnl,bars,outcome

def exit_wave(df,i):
    return exit_trade(df,i,target=9,stop=5,horizon=42,minhold=4)

def good(*vals): return all(pd.notna(v) for v in vals)

def liquid(row):
    # Avoid illiquid/noisy names. Vietnamese data volume is shares; threshold kept moderate for VN100.
    return good(row.volma20, row.close) and row.volma20 >= 300000 and row.close >= 8

def market_ok(row):
    # Proxy at symbol level: avoid broken medium/long trend and extreme volatility.
    return good(row.ma20,row.ma50,row.ma100,row.atrp,row.roc60) and row.ma20 >= row.ma50*0.985 and row.atrp <= 5.5 and row.roc60 > -18

def signals(df, i):
    row=df.iloc[i]; prev=df.iloc[i-1] if i>0 else row; prev2=df.iloc[i-2] if i>1 else prev; out=[]
    price=float(row.close)
    if not liquid(row): return out
    # Global quality gate: fewer trades, less falling-knife.
    if not market_ok(row):
        return out

    # LH1 Pullback SELECTIVE: confirmed uptrend, controlled pullback, RSI turn, volume contraction not distribution.
    if good(row.ma10,row.ma20,row.ma50,row.ma200,row.rsi14,row.roc20,row.volr,row['hist'],prev['hist']):
        dist_ma20=(price/row.ma20-1)*100 if row.ma20 else 999
        tight_trend = price>row.ma50>row.ma200 and row.ma20>=row.ma50*1.005
        pullback_zone = -1.5 <= dist_ma20 <= 2.2 and price >= row.ma50*1.01
        momentum_ok = 48<=row.rsi14<=60 and row['hist']>=prev['hist'] and row.roc20>-4
        vol_ok = 0.65<=row.volr<=1.65
        if tight_trend and pullback_zone and momentum_ok and vol_ok:
            out.append('LH1')

    # LH2 Shakeout SELECTIVE: real support sweep + close recovery + volume, not just breakdown.
    if good(row.low20prev,row.rsi14,row.volr,row['hist'],prev['hist'],row.atrp) and row.low20prev>0:
        intraday_break=(row.low20prev-float(row.low))/row.low20prev*100
        close_reclaim=(price/row.low20prev-1)*100
        green_close = price >= float(row.open)*1.005
        if 1.2<=intraday_break<=5.5 and close_reclaim>=-0.5 and 34<=row.rsi14<=55 and row.volr>=1.05 and row['hist']>prev['hist'] and green_close:
            out.append('LH2')

    # LH3 SRH SELECTIVE: reaction near 20/60 support with actual reversal candle and improving MACD hist.
    support=max([x for x in [row.low20prev,row.low60prev] if x==x and x>0], default=0)
    if support and good(row.rsi14,row['hist'],prev['hist'],prev2['hist'],row.ma50,row.volr):
        dist=(price/support-1)*100
        bullish_reversal = price > float(row.open) and price > float(prev.close)
        hist_turn = row['hist']>prev['hist']>prev2['hist']
        if -0.6<=dist<=2.2 and 42<=row.rsi14<=58 and hist_turn and price>=row.ma50*0.99 and 0.8<=row.volr<=2.4 and bullish_reversal:
            out.append('LH3')

    # LH4 Wave SELECTIVE: stronger breakout with constructive base, require volume + trend quality.
    if i>=126:
        base=df.iloc[i-126:i]
        lo=float(base.low.min()); hi=float(base.high.max()); rng=(hi-lo)/lo*100 if lo else 999; pos=(price-lo)/(hi-lo)*100 if hi>lo else 0
        if good(row.high20prev,row.high60prev,row.ma20,row.ma50,row.rsi14,row['hist'],row.roc20,row.volr,row.atrp):
            base_ok = 18<=rng<=42 and pos>=70
            breakout = price>=row.high20prev*1.005 or price>=row.high60prev*0.995
            trend = price>row.ma20>row.ma50 and row.ma20>=row.ma50*1.01
            momentum = 58<=row.rsi14<=70 and row['hist']>0 and row.roc20>=5
            vol = 1.15<=row.volr<=2.8
            if base_ok and breakout and trend and momentum and vol:
                out.append('LH4')
    return out

def summarize(trades):
    n=len(trades); wins=[t for t in trades if t['pnl']>0]; losses=[t for t in trades if t['pnl']<0]
    return {'trades':n,'wins':len(wins),'losses':len(losses),'winRatePct':round(len(wins)/n*100,2) if n else 0,'avgPnlPct':round(sum(t['pnl'] for t in trades)/n,2) if n else 0,'sumPnlPct':round(sum(t['pnl'] for t in trades),2) if n else 0,'avgHold':round(sum(t['bars'] for t in trades)/n,2) if n else 0}

def main():
    hist=load(); all_trades=defaultdict(list)
    cooldown={'LH1':12,'LH2':10,'LH3':12,'LH4':25}
    for sym,df0 in hist.items():
        df=add_ind(df0)
        used={k:-1 for k in ['LH1','LH2','LH3','LH4']}
        for i in range(200,len(df)-45):
            t=pd.Timestamp(df.iloc[i].time)
            if t<START or t>=END: continue
            sigs=signals(df,i)
            # If multiple signal same day, prefer historically stronger selective order.
            for s in [x for x in ['LH2','LH1','LH3','LH4'] if x in sigs]:
                if i<=used[s]: continue
                res=exit_wave(df,i) if s=='LH4' else exit_trade(df,i,target=6,stop=4.5,horizon=20,minhold=3)
                if not res: continue
                pnl,bars,outcome=res
                all_trades[s].append({'symbol':sym,'date':str(t.date()),'pnl':round(pnl,2),'bars':bars,'outcome':outcome})
                used[s]=i+max(bars,cooldown[s])
    payload={'createdAt':pd.Timestamp.now().isoformat(),
             'method':'SELECTIVE FAST approximation. Built to reduce trades and improve winrate vs lh_fast_2023_summary. Extra filters: liquidity, trend/volatility gate, tighter entry confirmation, cooldown, smaller stop 4.5% for LH1/LH2/LH3; LH4 target9 stop5 horizon42.',
             'strategyMap':{'LH1':'Pullback','LH2':'Shakeout Rebound','LH3':'Support Rebound Hunter','LH4':'Wave Entry'},
             'windows':{}}
    for w,(st,en) in WINDOWS.items():
        payload['windows'][w]={}
        for s in ['LH1','LH2','LH3','LH4']:
            sub=[x for x in all_trades.get(s,[]) if st<=pd.Timestamp(x['date'])<en]
            payload['windows'][w][s]=summarize(sub)
    payload['allTradesSample']={s:all_trades.get(s,[])[:30] for s in ['LH1','LH2','LH3','LH4']}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['windows'],ensure_ascii=False,indent=2))
if __name__=='__main__': main()
