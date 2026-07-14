from __future__ import annotations
import numpy as np
from .core import split_pivots, pct, clamp


def _d(df, i): return df['date'].iloc[int(i)].strftime('%Y-%m-%d')
def _conf(s): return 'high' if s>=70 else 'medium' if s>=58 else 'low'

def detect_double_triple_v2(df, pivots, recent_bars=180, max_span=180):
    """Ranked detector for double/triple tops-bottoms.

    More practical than hard filters: it scores geometry and keeps weak candidates
    as low confidence instead of silently discarding everything.
    """
    highs,lows=split_pivots(pivots); n=len(df); close=float(df['close'].iloc[-1])
    atr=float(df['atr20'].iloc[-1] if not np.isnan(df['atr20'].iloc[-1]) else close*.03)
    ha,la,ca=df['high'].values,df['low'].values,df['close'].values
    out=[]
    def neck_between(a,b,is_bottom):
        seg=slice(a+1,b)
        if b-a<3: return None
        if is_bottom:
            j=a+1+int(np.argmax(ha[seg])); return j,float(ha[j])
        j=a+1+int(np.argmin(la[seg])); return j,float(la[j])
    def prom(ix,val,is_bottom,win=10):
        a,b=max(0,ix-win),min(n,ix+win+1)
        if is_bottom: return min(float(ha[a:ix+1].max())-val, float(ha[ix:b].max())-val)
        return min(val-float(la[a:ix+1].min()), val-float(la[ix:b].min()))
    def make(kind_list, combo, typ, is_bottom):
        for i in range(len(kind_list)-combo+1):
            grp=kind_list[i:i+combo]; idx=[g['index'] for g in grp]; vals=[float(g['value']) for g in grp]
            if idx!=sorted(idx) or len(set(idx))<combo: continue
            gaps=[b-a for a,b in zip(idx[:-1],idx[1:])]
            span=idx[-1]-idx[0]
            if span<8 or span>max_span or idx[-1]<n-recent_bars or any(g<5 for g in gaps): continue
            necks=[]
            for a,b in zip(idx[:-1],idx[1:]):
                nk=neck_between(a,b,is_bottom)
                if nk: necks.append(nk)
            if len(necks)!=combo-1: continue
            level=float(np.mean(vals)); spread=max(vals)-min(vals); spread_pct=spread/max(level,1e-9)
            neck = max(v for _,v in necks) if is_bottom else min(v for _,v in necks)
            depth = (neck-max(vals)) if is_bottom else (min(vals)-neck)
            if depth<=0: continue
            proms=[prom(ix,v,is_bottom) for ix,v in zip(idx,vals)]
            prom_atr=float(np.mean(proms)/max(atr,1e-9))
            sym=1.0 if len(gaps)<2 else min(gaps)/max(gaps)
            status='forming'
            post=ca[idx[-1]+1:]
            if is_bottom:
                if any(post>neck): status='confirmed'
                elif close>=neck*.97: status='watch'
                target=neck+(neck-level); stop=min(vals)-atr; direction='bullish'; key='support'
            else:
                if any(post<neck): status='confirmed'
                elif close<=neck*1.03: status='watch'
                target=neck-(level-neck); stop=max(vals)+atr; direction='bearish'; key='resistance'
            score=42 + combo*4 + min(prom_atr*8,16) + min(depth/max(atr,1e-9)*5,14) + sym*8
            score -= min(spread_pct*100*3,18)
            if status=='confirmed': score+=10
            elif status=='watch': score+=5
            score=clamp(score)
            shape=[]; point_lines=[]
            for k,(ix,v) in enumerate(zip(idx,vals),1):
                shape.append({'time':_d(df,ix),'value':round(v,2)})
                point_lines.append({'name':'bottom' if is_bottom else 'top','type':'point','points':[{'time':_d(df,ix),'value':round(v,2)}]})
                if k-1<len(necks): shape.append({'time':_d(df,necks[k-1][0]),'value':round(necks[k-1][1],2)})
            lines=[{'name':'shape','type':'diagonal','points':shape},{'name':'neckline','type':'horizontal','points':[{'time':_d(df,idx[0]),'value':round(neck,2)},{'time':_d(df,n-1),'value':round(neck,2)}]},*point_lines]
            out.append({'type':typ,'category':'chart-pattern','tier':1,'direction':direction,'time':_d(df,idx[-1]),'price':round(close,2),'score':round(score,1),'confidence':_conf(score),'status':status,'levels':{key:round(level,2),'neckline':round(neck,2),'target':round(target,2),'stop':round(stop,2)},'lines':lines,'evidence':{'notes':f'{combo} '+('đáy' if is_bottom else 'đỉnh')+f' ranked-v2: spread {spread_pct*100:.1f}%, depth {depth/max(atr,1e-9):.1f} ATR, prominence {prom_atr:.1f} ATR, symmetry {sym:.2f}','touchPoints':[{'time':_d(df,ix),'value':round(v,2)} for ix,v in zip(idx,vals)],'patternStatus':status,'qualityV2':{'spreadPct':round(spread_pct*100,2),'depthAtr':round(depth/max(atr,1e-9),2),'promAtr':round(prom_atr,2),'symmetry':round(sym,2)}}})
    for c,t in [(2,'double-bottom'),(3,'triple-bottom')]: make(lows,c,t,True)
    for c,t in [(2,'double-top'),(3,'triple-top')]: make(highs,c,t,False)
    out=sorted(out,key=lambda x:x['score'],reverse=True)
    kept=[]
    per_type={}
    for p in out:
        pts={x['time'] for x in p['evidence']['touchPoints']}
        lv=p.get('levels',{})
        key_lv=lv.get('neckline') or lv.get('support') or lv.get('resistance') or 0
        if any(p['type']==q['type'] and (len(pts & {x['time'] for x in q['evidence']['touchPoints']})>=len(pts)-1 or abs(float(key_lv)-float((q.get('levels',{}).get('neckline') or q.get('levels',{}).get('support') or q.get('levels',{}).get('resistance') or 0))) <= close*0.012) for q in kept):
            continue
        if per_type.get(p['type'],0) >= 1:
            continue
        per_type[p['type']]=per_type.get(p['type'],0)+1
        kept.append(p)
    return kept[:6]
