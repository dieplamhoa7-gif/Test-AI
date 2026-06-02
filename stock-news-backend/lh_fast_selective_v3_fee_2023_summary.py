from lh_fast_2023_summary import load, add_ind, signals, summarize, START, END, WINDOWS
from pathlib import Path
from collections import defaultdict
import pandas as pd, json

OUT=Path('data/lh_fast_selective_v3_fee_2023_summary.json')
FEE_PCT = 0.5

def exit_trade(df,i,target=4.0,stop=6.0,horizon=15,minhold=3):
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
    pnl=(exitp-entry)/entry*100 - FEE_PCT
    return pnl,bars,outcome

def exit_wave(df,i):
    return exit_trade(df,i,target=6.0,stop=6.0,horizon=30,minhold=3)

def quality_ok(df,i,s):
    r=df.iloc[i]; p=float(r.close)
    # universal liquidity + avoid penny/noisy
    if pd.isna(r.volma20) or r.volma20<250000 or p<8: return False
    atrp=float(r.atr14)/p*100 if pd.notna(r.atr14) and p else 99
    if atrp>7.0: return False
    # strategy-specific gates, intentionally not too tight
    if s=='LH1':
        return pd.notna(r.ma50) and pd.notna(r.ma200) and p>r.ma50*0.98 and r.ma50>r.ma200*0.95 and pd.notna(r.roc20) and r.roc20>-10
    if s=='LH2':
        return pd.notna(r.rsi14) and 28<=r.rsi14<=58 and pd.notna(r.volr) and r.volr>=0.75
    if s=='LH3':
        return pd.notna(r.ma50) and p>=r.ma50*0.93 and pd.notna(r.rsi14) and r.rsi14>=36
    if s=='LH4':
        return pd.notna(r.ma20) and pd.notna(r.ma50) and p>r.ma50 and pd.notna(r.volr) and r.volr>=0.85
    return True

def main():
    hist=load(); all_trades=defaultdict(list)
    cooldown={'LH1':18,'LH2':16,'LH3':18,'LH4':35}
    for sym,df0 in hist.items():
        df=add_ind(df0); used={k:-1 for k in ['LH1','LH2','LH3','LH4']}
        for i in range(200,len(df)-45):
            t=pd.Timestamp(df.iloc[i].time)
            if t<START or t>=END: continue
            sigs=signals(df,i)
            # one signal per symbol/date max, priority from baseline performance
            for s in ['LH2','LH1','LH3','LH4']:
                if s not in sigs: continue
                if i<=used[s] or not quality_ok(df,i,s): continue
                res=exit_wave(df,i) if s=='LH4' else exit_trade(df,i)
                if not res: continue
                pnl,bars,outcome=res
                all_trades[s].append({'symbol':sym,'date':str(t.date()),'pnl':round(pnl,2),'bars':bars,'outcome':outcome})
                used[s]=i+max(bars,cooldown[s])
                break
    payload={'createdAt':pd.Timestamp.now().isoformat(),'method':'SELECTIVE V3 fee-aware fast. Rules: minimum hold T+3/3 days via minhold=3; subtract transaction cost/slippage 0.5% per completed trade. Uses original fast signals with liquidity/volatility/trend quality gates, longer cooldown, one prioritized signal per symbol/date. Exit: LH1/LH2/LH3 target4 stop6 horizon15; LH4 target6 stop6 horizon30. Research approximation only, not canonical production.','strategyMap':{'LH1':'Pullback','LH2':'Shakeout Rebound','LH3':'Support Rebound Hunter','LH4':'Wave Entry'},'windows':{}}
    for w,(st,en) in WINDOWS.items():
        payload['windows'][w]={}
        for s in ['LH1','LH2','LH3','LH4']:
            sub=[x for x in all_trades.get(s,[]) if st<=pd.Timestamp(x['date'])<en]
            payload['windows'][w][s]=summarize(sub)
    payload['allTradesSample']={s:all_trades.get(s,[])[:30] for s in ['LH1','LH2','LH3','LH4']}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(payload['windows'],ensure_ascii=False,indent=2))
if __name__=='__main__': main()
