import json, statistics
from pathlib import Path
from collections import defaultdict
obj=json.loads(Path('data/lh1_canonical_t3_fee_2023_to_now.json').read_text(encoding='utf-8'))
trades=obj['trades']
fields=['rsi','macdHist','bbPercent','volumeRatio','roc20','ret5']
def f(x):
 try:return float(x)
 except:return None
for group,name in [(lambda t:t['netPnlPct']>0,'WIN'),(lambda t:t['netPnlPct']<=0,'LOSS')]:
 print('\n'+name)
 xs=[t for t in trades if group(t)]
 print('n',len(xs),'avg pnl',round(sum(t['netPnlPct'] for t in xs)/len(xs),2))
 for fld in fields:
  vals=[f((t.get('entryIndicators') or {}).get(fld)) for t in xs]
  vals=[v for v in vals if v is not None]
  if vals:
   print(fld,'avg',round(statistics.mean(vals),3),'med',round(statistics.median(vals),3),'min',round(min(vals),3),'max',round(max(vals),3))
 print('cloud',defaultdict(int, {k:sum(1 for t in xs if (t.get('entryIndicators') or {}).get('ichimoku',{}).get('state')==k) for k in ['above_cloud','inside_cloud','below_cloud']}))
 print('bullDiv',sum(1 for t in xs if (t.get('entryIndicators') or {}).get('bullishDivergence')),'bearDiv',sum(1 for t in xs if (t.get('entryIndicators') or {}).get('bearishDivergence')))

# test simple added filters on existing accepted trades
filters={
 'base':lambda ai: True,
 'vol_0.7_1.8':lambda ai: 0.7<=f(ai.get('volumeRatio'))<=1.8,
 'vol_0.8_1.8':lambda ai: 0.8<=f(ai.get('volumeRatio'))<=1.8,
 'rsi_50_60':lambda ai: 50<=f(ai.get('rsi'))<=60,
 'bb_0.35_0.75':lambda ai: 0.35<=f(ai.get('bbPercent'))<=0.75,
 'roc_-3_4':lambda ai: -3<=f(ai.get('roc20'))<=4,
 'ret5_-3_3':lambda ai: -3<=f(ai.get('ret5'))<=3,
 'no_bull_div_required':lambda ai: not ai.get('bullishDivergence'),
 'bull_div_required':lambda ai: bool(ai.get('bullishDivergence')),
 'combo_clean':lambda ai: 0.7<=f(ai.get('volumeRatio'))<=1.8 and 48<=f(ai.get('rsi'))<=60 and 0.25<=f(ai.get('bbPercent'))<=0.75 and -4<=f(ai.get('roc20'))<=4 and -4<=f(ai.get('ret5'))<=4,
 'combo_tight':lambda ai: 0.8<=f(ai.get('volumeRatio'))<=1.6 and 50<=f(ai.get('rsi'))<=60 and 0.35<=f(ai.get('bbPercent'))<=0.7 and -3<=f(ai.get('roc20'))<=3 and -3<=f(ai.get('ret5'))<=3,
}
for name,fn in filters.items():
 xs=[t for t in trades if fn(t['entryIndicators'])]
 if not xs: continue
 wins=sum(1 for t in xs if t['netPnlPct']>0); sm=sum(t['netPnlPct'] for t in xs)
 print('FILTER',name,'trades',len(xs),'wr',round(wins/len(xs)*100,2),'avg',round(sm/len(xs),2),'sum',round(sm,2))
