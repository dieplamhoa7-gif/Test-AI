from __future__ import annotations
import json
import time
from datetime import datetime
from pathlib import Path
from app.strategy_recommendations import SHAKEOUT_UNIVERSE, _shakeout_candidate
from app.market_data import get_market_symbol

OUT = Path('data/shakeout_rebound_current_signals.json')

def main():
    buy=[]; reject=[]; errors=[]
    for idx, sym in enumerate(SHAKEOUT_UNIVERSE, 1):
        try:
            if idx > 1 and (idx - 1) % 18 == 0:
                print('sleep 65s to avoid provider rate limit', flush=True)
                time.sleep(65)
            item=get_market_symbol(sym, force_refresh=True)
            c=_shakeout_candidate(item)
            if c:
                c['action']='BUY'
                c['entryPrice']=c.get('price')
                c['takeProfit']=c.get('target')
                buy.append(c)
            else:
                reject.append(sym)
            print(sym, 'BUY' if c else 'reject', flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':str(e)})
            print(sym,'ERR',e,flush=True)
    buy.sort(key=lambda x:x.get('rankScore',0), reverse=True)
    payload={'createdAt':datetime.now().isoformat(),'strategy':'shakeout_breakdown_rebound','method':'Current scan using app.strategy_recommendations._shakeout_candidate only; not V3 Plus6 focused. Break support 2-4%, target +6%, stop -4%.','buy':buy,'watchlist':[],'rejects':reject,'errors':errors,'summary':{'buy':len(buy),'watch':0,'reject':len(reject),'errors':len(errors)}}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output':str(OUT),'summary':payload['summary'],'buy':[(x['symbol'],x.get('rankScore')) for x in buy]}, ensure_ascii=False, indent=2))
if __name__=='__main__': main()
