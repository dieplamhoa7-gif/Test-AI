from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

SRC=Path('data/v3_clean_split_rs_action_backtest.json')
OUT=Path('data/v3_clean_split_baseline_locked.json')

def main():
    data=json.load(open(SRC,encoding='utf-8'))
    payload={
        'lockedAt':datetime.now().isoformat(),
        'name':'V3 clean split baseline - RS only for zones, action indicators only for decisions',
        'source':str(SRC),
        'status':'locked_baseline_before_A2_B2_relaxed_tests',
        'principle':{
            'RS_ENGINE':'Pivot/Swing/Volume-level/VWAP/Donchian/Fibonacci/MA anchors/ATR only create support-resistance zones and entry/stop/target references.',
            'ACTION_MODEL':'RSI/MACD/BB percent/Volume ratio/ROC/Ichimoku/Divergence decide action. R/S-derived indicators are not double-counted in strategy score.',
            'TRADE_MANAGEMENT':'distSupport, supportZone, resistanceZone, stop, target, partial/trailing are hard rules / management, not score components.'
        },
        'baselineResults':data,
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    compact={}
    for win,node in data.get('windows',{}).items():
        compact[win]={}
        for strat,snode in node.get('results',{}).items():
            compact[win][strat]={k:v.get('summary') for k,v in snode.items()}
    print(json.dumps({'output':str(OUT),'compact':compact},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
