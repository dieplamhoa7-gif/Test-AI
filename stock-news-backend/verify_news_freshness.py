import json, sys, email.utils
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
MAX_AGE_HOURS=36
FILES=[ROOT/'data/news_cache.json',ROOT/'firebase_public/data/news_cache.json']
def parse_dt(v):
    if not v: return None
    s=str(v)
    try:
        if ',' in s and '+' in s: return email.utils.parsedate_to_datetime(s)
        return datetime.fromisoformat(s.replace('Z','+00:00'))
    except Exception: return None
def newest(path):
    d=json.loads(path.read_text(encoding='utf-8'))
    items=d if isinstance(d,list) else (d.get('items') or d.get('news') or [])
    dates=[parse_dt(x.get('published_at') or x.get('publishedAt') or x.get('date') or x.get('time')) for x in items if isinstance(x,dict)]
    dates=[x.astimezone(timezone.utc) if x.tzinfo else x.replace(tzinfo=timezone.utc) for x in dates if x]
    return (max(dates) if dates else None), len(items), (items[0].get('title') if items and isinstance(items[0],dict) else None)
errs=[]; info={}
now=datetime.now(timezone.utc)
for p in FILES:
    if not p.exists(): errs.append(f'missing {p}'); continue
    dt,n,title=newest(p); info[str(p.relative_to(ROOT))]={'newest':dt.isoformat() if dt else None,'items':n,'topTitle':title}
    if not dt: errs.append(f'no parseable date in {p}')
    elif now-dt>timedelta(hours=MAX_AGE_HOURS): errs.append(f'stale {p}: newest {dt.isoformat()} > {MAX_AGE_HOURS}h')
# public must match data count/newest after build
try:
    d0=newest(FILES[0]); d1=newest(FILES[1])
    if d0[:2]!=d1[:2]: errs.append('data and firebase_public news freshness/count mismatch')
except Exception as e: errs.append(f'compare failed {e}')
print(json.dumps({'ok':not errs,'errors':errs,'info':info},ensure_ascii=False,indent=2))
sys.exit(1 if errs else 0)
