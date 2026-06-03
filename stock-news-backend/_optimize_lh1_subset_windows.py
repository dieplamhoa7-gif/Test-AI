import json
from pathlib import Path
import pandas as pd

obj=json.loads(Path('data/lh1_canonical_t3_fee_2023_to_now.json').read_text(encoding='utf-8'))
trades=obj['trades']
candidates={
'strict_best':['HPG','VND','HCM','TCB','MBB','ACB','VIB','ANV','VHC'],
'balanced_best':['MWG','HPG','VND','HCM','TCB','MBB','ACB','CTG','VIB','KDH','VNM','ANV','VHC'],
'quality_positive':['MWG','HPG','VND','HCM','MBS','TCB','MBB','ACB','CTG','VIB','KDH','GVR','VNM','PVD','DIG','PC1','ANV','VHC'],
'remove_negative':['MWG','HPG','VCI','VND','HCM','MBS','TCB','MBB','ACB','CTG','VPB','VIB','KDH','NVL','GVR','VNM','MSN','SAB','GAS','PVD','DCM','HSG','DIG','PC1','KSB','ANV','VHC'],
}
windows={
'2023':('2023-01-01','2024-01-01'),
'2024':('2024-01-01','2025-01-01'),
'2025':('2025-01-01','2026-01-01'),
'2026_ytd':('2026-01-01','2026-06-01'),
'all':('2023-01-01','2026-06-01'),
}
def met(ts):
 n=len(ts); wins=sum(1 for t in ts if t['netPnlPct']>0); sm=sum(t['netPnlPct'] for t in ts)
 return {'trades':n,'winRatePct':round(wins/n*100,2) if n else 0,'avgNetPnlPct':round(sm/n,2) if n else 0,'sumNetPnlPct':round(sm,2)}
for name,syms in candidates.items():
 print('\n',name, syms)
 for w,(a,b) in windows.items():
  st=pd.Timestamp(a); en=pd.Timestamp(b)
  xs=[t for t in trades if t['symbol'] in syms and st<=pd.Timestamp(t['signalDate'])<en]
  print(w,met(xs))
