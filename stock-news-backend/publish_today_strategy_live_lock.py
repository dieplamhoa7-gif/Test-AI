from __future__ import annotations
import json, shutil, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUTDIR=ROOT/'outputs'/'strategy_runs'
LOCK=ROOT/'data'/'live_strategy_lock'
PUBLIC=ROOT/'firebase_public'/'data'
DATA=ROOT/'data'

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

cands=sorted(OUTDIR.glob('lh_4_strategies_today_readonly_*.json'), key=lambda p:p.stat().st_mtime, reverse=True)
if not cands: raise SystemExit('No readonly strategy output found')
src=cands[0]
payload=load(src)
now=datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')
strategies=payload['strategies']
res={
  'updatedAt': now,
  'note': 'Live 4-strategy signal cache rebuilt from today market_data overlay on canonical indicators; published by user request on 2026-07-20.',
  'canonical': True,
  'sourceFiles': payload.get('sourceFiles') or [],
  'marketLatestTradingDate': payload.get('marketLatestTradingDate'),
  'marketUpdatedAt': payload.get('marketUpdatedAt'),
  'overlaidSymbols': payload.get('overlaidSymbols'),
  'strategies': strategies,
}
# Build matrix from existing shape, replacing columns/buckets with current strategy output.
old=load(PUBLIC/'strategy_matrix_cache.json') if (PUBLIC/'strategy_matrix_cache.json').exists() else {'columns':[]}
old_cols={c.get('signalKey') or c.get('id'): c for c in old.get('columns',[]) if isinstance(c,dict)}
cols=[]
for idx, st in enumerate(strategies, start=1):
    sid=st['id']
    col=dict(old_cols.get(sid) or {})
    col.update({
        'signalKey': sid,
        'name': st.get('name') or sid,
        'shortName': st.get('name') or sid,
        'priority': idx,
        'buckets': {
            'buy': st.get('buy') or [],
            'watch': st.get('watchlist') or [],
            'avoid': st.get('rejectTop') or [],
        },
    })
    col.setdefault('id', sid)
    cols.append(col)
mx={
  'updatedAt': now,
  'title': 'LH Current Strategy Matrix',
  'note': 'Current LH1-LH4 matrix rebuilt from today 4-strategy run and market_data overlay.',
  'displayMode': old.get('displayMode','matrix'),
  'buyCount': sum(len(c['buckets']['buy']) for c in cols),
  'watchCount': sum(len(c['buckets']['watch']) for c in cols),
  'columns': cols,
  'source': 'strategy_results_cache.json',
  'schema': 'lh-strategy-matrix.v2',
  'marketLatestTradingDate': payload.get('marketLatestTradingDate'),
  'marketUpdatedAt': payload.get('marketUpdatedAt'),
}
app=load(PUBLIC/'app_version.json') if (PUBLIC/'app_version.json').exists() else {}
app.update({
  'strategyLive': 'lh-4-strategies-today-20260720',
  'strategyLiveUpdatedAt': now,
  'strategyLiveSource': str(src).replace('\\','/'),
  'strategyMarketLatestTradingDate': payload.get('marketLatestTradingDate'),
  'strategyMarketUpdatedAt': payload.get('marketUpdatedAt'),
})
for base in [LOCK, DATA, PUBLIC]:
    write(base/'strategy_results_cache.json', res)
    write(base/'strategy_matrix_cache.json', mx)
    write(base/'app_version.json', app)
print(json.dumps({
  'source': str(src),
  'updatedAt': now,
  'buyWatch': [{'id':s['id'],'buy':len(s.get('buy') or []),'watch':len(s.get('watchlist') or [])} for s in strategies],
  'hashes': {str(PUBLIC/name): sha(PUBLIC/name) for name in ['app_version.json','strategy_results_cache.json','strategy_matrix_cache.json']}
},ensure_ascii=False,indent=2))
