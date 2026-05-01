from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from scan_three_strategies_vn100_from_cache import b4, support_rebound, shakeout

VN30=['ACB','BCM','BID','BVH','CTG','FPT','GAS','GVR','HDB','HPG','LPB','MBB','MSN','MWG','PLX','SAB','SHB','SSB','SSI','STB','TCB','TPB','VCB','VHM','VIB','VIC','VJC','VNM','VPB','VRE']
VN30X=[s for s in VN30 if s not in {'VIC','VHM'}]
IND=Path('data/v3_full_indicator_cache_v2.json')
OUT=Path('data/three_strategies_vn30x_cache_signals.json')

def main():
    d=json.loads(IND.read_text(encoding='utf-8'))
    rows={x.get('symbol'):x for x in d.get('items',[])}
    available=[s for s in VN30X if s in rows]
    missing=[s for s in VN30X if s not in rows]
    out={'createdAt':datetime.now().isoformat(),'universe':'VN30 excluding VIC/VHM','universeSymbols':VN30X,'availableCount':len(available),'missingSymbols':missing,'source':str(IND),'note':'Cache scan only; provider not called. Missing symbols are absent from indicator cache.','strategies':{'b4_trend_pullback':{'buy':[],'watchlist':[],'rejects':[]},'clean_split_a_bottom':{'buy':[],'watchlist':[],'rejects':[]},'shakeout_breakdown_rebound':{'buy':[],'watchlist':[],'rejects':[]}}}
    for sym in available:
        row=rows[sym]
        for sid,fn in [('b4_trend_pullback',b4),('clean_split_a_bottom',support_rebound),('shakeout_breakdown_rebound',shakeout)]:
            x,b=fn(row)
            if b=='buy': out['strategies'][sid]['buy'].append(x)
            elif b=='watch': out['strategies'][sid]['watchlist'].append(x)
            else: out['strategies'][sid]['rejects'].append(sym)
    for st in out['strategies'].values():
        st['buy'].sort(key=lambda x:x.get('rankScore',0), reverse=True); st['watchlist'].sort(key=lambda x:x.get('rankScore',0), reverse=True)
        st['summary']={'buy':len(st['buy']),'watch':len(st['watchlist']),'reject':len(st['rejects'])}
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUT),'availableCount':len(available),'missing':missing,'summary':{k:v['summary'] for k,v in out['strategies'].items()},'symbols':{k:{'buy':[x['symbol'] for x in v['buy']],'watch':[x['symbol'] for x in v['watchlist']]} for k,v in out['strategies'].items()}},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
