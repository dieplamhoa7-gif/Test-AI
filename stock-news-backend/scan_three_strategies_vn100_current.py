from __future__ import annotations
import json, time
from datetime import datetime
from pathlib import Path
from app.technical_filters import TECHNICAL_UNIVERSE
from app.strategy_recommendations import _shakeout_candidate
from app.market_data import get_market_symbol

MIDCAP50=['AAA','APH','BCG','BIC','BWE','CTD','CTS','D2D','DAT','DGC','DPM','DPR','EVF','FCN','FIT','FOX','GIL','HAH','HBC','HDC','HHS','HPX','HT1','IDI','KSB','LCG','LHG','MIG','NBB','NHA','NKG','ORS','PHR','QCG','SBT','SCR','SJS','SKG','SLS','TCH','TIG','TMS','TNG','TV2','VCG','VGC','VHC','VIX','VOS','VSC']
VN100=[]
for s in list(TECHNICAL_UNIVERSE)+MIDCAP50:
    if s not in VN100: VN100.append(s)
OUT=Path('data/three_strategies_vn100_current_signals.json')

def f(v):
    try: return float(v or 0)
    except Exception: return 0.0

def r(v,n=2):
    try: return round(float(v),n)
    except Exception: return None

def tech(item): return item.get('technical') or {}

def rs(item):
    t=tech(item); return f(t.get('activeSupportDay') or t.get('supportDay')), f(t.get('activeResistanceDay') or t.get('resistanceDay'))

def base_item(item, strategy):
    price=f(item.get('price')); support,res=rs(item)
    return {'symbol':str(item.get('ticker') or '').upper(),'strategy':strategy,'lastClose':r(price),'entryPrice':r(price),'stopLoss':r(price*0.94),'takeProfit':r(price*1.06),'support':r(support),'resistance':r(res),'asOfDate':item.get('asOfDate') or item.get('updatedAt')}

def b4(item):
    t=tech(item); price=f(item.get('price')); support,res=rs(item)
    if price<=0 or support<=0: return None,'reject'
    dist=(price-support)/price*100
    rsi=f(t.get('rsi14')); hist=f(t.get('histogram')); vol=f(t.get('volumeRatio')); ichi=(t.get('ichimoku') or {}).get('state') or t.get('ichimokuState') or ''
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
    x=base_item(item,'b4_trend_pullback'); x.update({'action':action,'rankScore':score,'missingReasons':miss,'reason':'Trend pullback: RSI/MACD hồi, gần hỗ trợ, tránh dưới mây.'}); return x,action.lower()

def support_rebound(item):
    t=tech(item); price=f(item.get('price')); support,res=rs(item)
    if price<=0 or support<=0: return None,'reject'
    dist=(price-support)/price*100; rsi=f(t.get('rsi14')); hist=f(t.get('histogram')); vol=f(t.get('volumeRatio'))
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
    x=base_item(item,'clean_split_a_bottom'); x.update({'action':action,'rankScore':score,'missingReasons':miss,'reason':'Support rebound: gần hỗ trợ, RSI thấp/quá bán, chờ hồi xác nhận.'}); return x,action.lower()

def shakeout(item):
    c=_shakeout_candidate(item)
    if not c: return None,'reject'
    c['strategy']='shakeout_breakdown_rebound'; c['action']='BUY'; c['entryPrice']=c.get('price'); c['takeProfit']=c.get('target')
    return c,'buy'

def main():
    out={'createdAt':datetime.now().isoformat(),'universe':'VN100 synthetic = TECHNICAL_UNIVERSE + MIDCAP50 unique','universeCount':len(VN100),'strategies':{'b4_trend_pullback':{'buy':[],'watchlist':[],'rejects':[]},'clean_split_a_bottom':{'buy':[],'watchlist':[],'rejects':[]},'shakeout_breakdown_rebound':{'buy':[],'watchlist':[],'rejects':[]}},'errors':[]}
    funcs=[('b4_trend_pullback',b4),('clean_split_a_bottom',support_rebound),('shakeout_breakdown_rebound',shakeout)]
    for i,sym in enumerate(VN100,1):
        try:
            item=get_market_symbol(sym, force_refresh=False)
            print(i,sym,'ok',flush=True)
            for sid,fn in funcs:
                x,b=fn(item)
                if b=='buy': out['strategies'][sid]['buy'].append(x)
                elif b=='watch': out['strategies'][sid]['watchlist'].append(x)
                else: out['strategies'][sid]['rejects'].append(sym)
            time.sleep(0.15)
        except Exception as e:
            out['errors'].append({'symbol':sym,'error':str(e)})
            print(i,sym,'ERR',e,flush=True)
            time.sleep(1.0)
    for sid,st in out['strategies'].items():
        st['buy'].sort(key=lambda x:x.get('rankScore',0), reverse=True); st['watchlist'].sort(key=lambda x:x.get('rankScore',0), reverse=True)
        st['summary']={'buy':len(st['buy']),'watch':len(st['watchlist']),'reject':len(st['rejects'])}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summary':{k:v['summary'] for k,v in out['strategies'].items()},'errors':len(out['errors'])},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
