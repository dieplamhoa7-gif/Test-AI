from __future__ import annotations
import json, urllib.request
from datetime import datetime
URL='https://lhinvestment.web.app'
FILES={
 'app_version':'/data/app_version.json',
 'market_data':'/data/market_data.json',
 'market_watch':'/data/market_watch.json',
 'charts_index':'/data/charts/index.json',
 'chart_MWG':'/data/charts/MWG.json',
 'warrants':'/data/warrants_data.json',
 'news_vi':'/data/news_cache.json',
 'news_en':'/data/news_cache_en.json',
 'strategy_results':'/data/strategy_results_cache.json',
 'strategy_matrix':'/data/strategy_matrix_cache.json',
 'intraday_report':'/data/final_auto_refresh_reports/intraday_latest.json',
 'warrants_report':'/data/final_auto_refresh_reports/warrants_latest.json',
}

def fetch(path):
    u=URL+path+'?ts='+datetime.now().strftime('%H%M%S')
    with urllib.request.urlopen(u,timeout=30) as r:
        txt=r.read().decode('utf-8','replace')
    return json.loads(txt), len(txt)

def first_date_news(arr):
    if isinstance(arr,list) and arr:
        return arr[0].get('published_at') or arr[0].get('date') or arr[0].get('fetched_at')

def summarize(name,j):
    if name=='chart_MWG':
        rows=j.get('rows') or []; return {'rows':len(rows),'last':rows[-1] if rows else None}
    if name=='charts_index': return {'count':j.get('count'), 'sample':(j.get('items') or [])[:2]}
    if name in ['market_data','market_watch']:
        items=j.get('items') if isinstance(j,dict) else j
        return {'count':len(items or []),'first':(items or [None])[0], 'updatedAt':j.get('updatedAt') if isinstance(j,dict) else None}
    if name=='warrants':
        items=j.get('items') if isinstance(j,dict) else j
        return {'count':len(items or []),'updatedAt':j.get('updatedAt') or j.get('createdAt') if isinstance(j,dict) else None,'first':(items or [None])[0]}
    if name.startswith('news'):
        return {'count':len(j) if isinstance(j,list) else len(j.get('items',[])), 'firstDate':first_date_news(j if isinstance(j,list) else j.get('items',[]))}
    if name.startswith('strategy'):
        return {'updatedAt':j.get('updatedAt'), 'strategies':[(s.get('shortName'),len(s.get('buy',[])),len(s.get('watchlist',[]))) for s in j.get('strategies',[])] if 'strategies' in j else None, 'rows':len(j.get('rows',[]))}
    return j

def main():
    out={}
    for name,path in FILES.items():
        try:
            j,n=fetch(path); out[name]={'ok':True,'bytes':n,'summary':summarize(name,j)}
        except Exception as e:
            out[name]={'ok':False,'error':str(e)}
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
