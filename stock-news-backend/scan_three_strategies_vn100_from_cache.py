from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

IND=Path('data/v3_full_indicator_cache_v2.json')
OUT=Path('data/three_strategies_vn100_cache_signals.json')

def f(v):
    try: return float(v or 0)
    except Exception: return 0.0

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def make_item(row, strategy, action, score, missing, reason):
    price=f(row.get('price')); rs=row.get('rs') or {}; sup=f(rs.get('activeSupportDay') or rs.get('supportDay')); res=f(rs.get('activeResistanceDay') or rs.get('resistanceDay'))
    return {'symbol':row.get('symbol'),'strategy':strategy,'action':action,'lastClose':r(price),'entryPrice':r(price),'stopLoss':r(price*0.94),'takeProfit':r(price*1.06),'support':r(sup),'resistance':r(res),'rankScore':r(score),'missingReasons':missing,'reason':reason,'asOfDate':row.get('date')}

def b4(row):
    ind=row.get('indicators') or {}; rs=row.get('rs') or {}; price=f(row.get('price')); sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
    if price<=0 or sup<=0: return None,'reject'
    dist=(price-sup)/price*100; rsi=f(ind.get('rsi14')); hist=f(ind.get('histogram')); ichi=((ind.get('ichimoku') or {}).get('state') or '')
    score=0; miss=[]
    if 48<=rsi<=62: score+=25
    else: miss.append('RSI 48-62')
    if hist>0: score+=25
    else: miss.append('MACD hồi phục')
    if dist<=3: score+=25
    else: miss.append('gần hỗ trợ <=3%')
    if ichi!='below_cloud': score+=25
    else: miss.append('không dưới mây')
    if score>=100: action='BUY'
    elif score>=75: action='WATCH'
    else: return None,'reject'
    return make_item(row,'b4_trend_pullback',action,score,miss,'Trend pullback từ cache indicator VN100.'), action.lower()

def support_rebound(row):
    ind=row.get('indicators') or {}; rs=row.get('rs') or {}; price=f(row.get('price')); sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
    if price<=0 or sup<=0: return None,'reject'
    dist=(price-sup)/price*100; rsi=f(ind.get('rsi14')); hist=f(ind.get('histogram')); vol=f(ind.get('volumeRatio'))
    score=0; miss=[]
    if dist<=2: score+=35
    else: miss.append('gần hỗ trợ <=2%')
    if rsi<=40: score+=35
    else: miss.append('RSI<=40')
    if hist>=0 or vol<=1.2: score+=30
    else: miss.append('MACD/volume ổn')
    if score>=100: action='BUY'
    elif score>=70: action='WATCH'
    else: return None,'reject'
    return make_item(row,'clean_split_a_bottom',action,score,miss,'Support rebound từ cache indicator VN100.'), action.lower()

def shakeout(row):
    ind=row.get('indicators') or {}; rs=row.get('rs') or {}; price=f(row.get('price')); sup=f(rs.get('activeSupportDay') or rs.get('supportDay'))
    if price<=0 or sup<=0: return None,'reject'
    break_pct=(sup-price)/sup*100
    if break_pct<2 or break_pct>4: return None,'reject'
    rsi=f(ind.get('rsi14')); vol=f(ind.get('volumeRatio')); hist=f(ind.get('histogram'))
    if rsi<20 or vol>2.4: return None,'reject'
    score=75+(4-abs(3-break_pct)*4)+(5 if 25<=rsi<=45 else 0)+(3 if vol<=1.3 else 0)
    x=make_item(row,'shakeout_breakdown_rebound','BUY',score,[],f'Shakeout: thủng support {break_pct:.1f}%, RSI {rsi:.1f}, volume {vol:.2f}, hist {hist:.2f}')
    x['breakSupportPct']=r(break_pct); x['stopLoss']=r(price*0.96); x['takeProfit']=r(price*1.06)
    return x,'buy'

def main():
    d=json.loads(IND.read_text(encoding='utf-8'))
    items=d.get('items',[])
    out={'createdAt':datetime.now().isoformat(),'source':str(IND),'note':'VN100 cache scan based on available indicator cache. Does not call provider. Universe limited to symbols present in cache.','inputCount':len(items),'strategies':{'b4_trend_pullback':{'buy':[],'watchlist':[],'rejects':[]},'clean_split_a_bottom':{'buy':[],'watchlist':[],'rejects':[]},'shakeout_breakdown_rebound':{'buy':[],'watchlist':[],'rejects':[]}}}
    for row in items:
        for sid,fn in [('b4_trend_pullback',b4),('clean_split_a_bottom',support_rebound),('shakeout_breakdown_rebound',shakeout)]:
            x,b=fn(row)
            if b=='buy': out['strategies'][sid]['buy'].append(x)
            elif b=='watch': out['strategies'][sid]['watchlist'].append(x)
            else: out['strategies'][sid]['rejects'].append(row.get('symbol'))
    for st in out['strategies'].values():
        st['buy'].sort(key=lambda x:x.get('rankScore',0), reverse=True); st['watchlist'].sort(key=lambda x:x.get('rankScore',0), reverse=True)
        st['summary']={'buy':len(st['buy']),'watch':len(st['watchlist']),'reject':len(st['rejects'])}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'inputCount':len(items),'summary':{k:v['summary'] for k,v in out['strategies'].items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
