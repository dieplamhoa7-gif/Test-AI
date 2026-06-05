from __future__ import annotations
import csv,json
from datetime import datetime
from pathlib import Path

def convert(src='data/tradingeconomics_deep_scrape_latest.json', out='data/tradingeconomics_visible_timeline.csv'):
    data=json.loads(Path(src).read_text(encoding='utf-8'))
    rows=[]
    fetched=data.get('fetchedAt') or datetime.now().isoformat()
    for key,item in data.get('data',{}).items():
        if item.get('actual') is not None:
            rows.append({'fetchedAt':fetched,'key':key,'indicator':item.get('title') or key,'value':item.get('actual'),'previous':item.get('previous'),'unit':item.get('unit'),'reference':item.get('reference'),'frequency':item.get('frequency'),'source':'TradingEconomics visible scrape','url':item.get('url')})
        for rel in item.get('related') or []:
            if rel.get('last') is not None:
                rows.append({'fetchedAt':fetched,'key':key+'.related','indicator':rel.get('indicator'),'value':rel.get('last'),'previous':rel.get('previous'),'unit':rel.get('unit'),'reference':rel.get('reference'),'frequency':'related_visible','source':'TradingEconomics visible scrape','url':item.get('url')})
    op=Path(out); op.parent.mkdir(exist_ok=True)
    with op.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['fetchedAt','key','indicator','value','previous','unit','reference','frequency','source','url']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    return {'rows':len(rows),'out':str(op)}
if __name__=='__main__':
    print(json.dumps(convert(),ensure_ascii=False,indent=2))
