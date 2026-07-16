from __future__ import annotations
import json, math
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PUBLIC_CHARTS = ROOT / 'firebase_public' / 'data' / 'charts'
HIST = DATA / 'vn100_history_2025_06_2026_05_cache.json'

def read(p: Path): return json.loads(p.read_text(encoding='utf-8'))
def write(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def calc_ma(rows, n):
    out=[]
    vals=[]
    for r in rows:
        vals.append(float(r.get('close') or 0))
        if len(vals)>n: vals.pop(0)
        if len(vals)==n: out.append({'time':r['time'],'value':round(sum(vals)/n,3)})
    return out

def calc_ema(rows, n):
    out=[]; ema=None; k=2/(n+1)
    for i,r in enumerate(rows):
        c=float(r.get('close') or 0)
        if not c: continue
        ema = c if ema is None else c*k + ema*(1-k)
        if i>=n-1: out.append({'time':r['time'],'value':round(ema,3)})
    return out

def calc_bb(rows, n=20, mult=2):
    up=[]; mid=[]; low=[]; vals=[]
    for r in rows:
        vals.append(float(r.get('close') or 0))
        if len(vals)>n: vals.pop(0)
        if len(vals)==n:
            m=sum(vals)/n
            sd=(sum((x-m)**2 for x in vals)/n)**0.5
            mid.append({'time':r['time'],'value':round(m,3)})
            up.append({'time':r['time'],'value':round(m+mult*sd,3)})
            low.append({'time':r['time'],'value':round(m-mult*sd,3)})
    return {'upper':up,'middle':mid,'lower':low}

def calc_rsi(rows, n=14):
    out=[]; gains=[]; losses=[]; prev=None
    for r in rows:
        c=float(r.get('close') or 0)
        if prev is None:
            prev=c; continue
        ch=c-prev; prev=c
        gains.append(max(ch,0)); losses.append(max(-ch,0))
        if len(gains)>n: gains.pop(0); losses.pop(0)
        if len(gains)==n:
            ag=sum(gains)/n; al=sum(losses)/n
            rsi=100 if al==0 else 100-(100/(1+ag/al))
            out.append({'time':r['time'],'value':round(rsi,2)})
    return out

def calc_macd(rows):
    ema12={x['time']:x['value'] for x in calc_ema(rows,12)}
    ema26=calc_ema(rows,26)
    macd=[{'time':x['time'],'value':round((ema12.get(x['time']) or 0)-x['value'],3)} for x in ema26 if x['time'] in ema12]
    # signal EMA over macd values
    sig=[]; ema=None; k=2/(9+1)
    for i,x in enumerate(macd):
        v=x['value']; ema = v if ema is None else v*k + ema*(1-k)
        if i>=8: sig.append({'time':x['time'],'value':round(ema,3)})
    sigmap={x['time']:x['value'] for x in sig}
    hist=[{'time':x['time'],'value':round(x['value']-sigmap[x['time']],3),'color':'#26a69a' if x['value']-sigmap[x['time']]>=0 else '#ef5350'} for x in macd if x['time'] in sigmap]
    return {'macd':macd,'signal':sig,'histogram':hist}



def _time_to_idx(rows):
    out = {}
    for i, r in enumerate(rows):
        t = r.get('time')
        if not t:
            continue
        out[str(t)] = i
        try:
            dt = datetime.fromisoformat(str(t)).replace(tzinfo=timezone.utc)
            out[str(int(dt.timestamp()))] = i
        except Exception:
            pass
    return out


def _same_time_format(src_time, row_time: str):
    # Keep legacy numeric UNIX-second overlays numeric; normal chart overlays use YYYY-MM-DD.
    if isinstance(src_time, (int, float)) or (isinstance(src_time, str) and src_time.isdigit()):
        try:
            dt = datetime.fromisoformat(row_time).replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            return row_time
    return row_time


def _extend_line_points(points, rows, idx_by_time, explicit_slope=None):
    if not isinstance(points, list) or len(points) < 2 or not rows:
        return points
    p1 = dict(points[0]); p2 = dict(points[-1])
    t1 = p1.get('time'); t2 = p2.get('time')
    latest_time = rows[-1].get('time')
    if not latest_time:
        return points
    i1 = idx_by_time.get(str(t1)); i2 = idx_by_time.get(str(t2)); ilast = len(rows) - 1
    if i1 is None:
        return points
    try:
        v1 = float(p1.get('value'))
        v2 = float(p2.get('value'))
        # Some generated overlays store the right endpoint as a future UNIX timestamp
        # (TradingView-style right extension). The frontend then shows the line running
        # past the candle area instead of ending at the newest real candle. Always snap
        # the right endpoint to rows[-1], projecting by slope where available.
        if i2 is None:
            slope = float(explicit_slope) if explicit_slope is not None else 0.0
        else:
            slope = float(explicit_slope) if explicit_slope is not None else ((v2 - v1) / (i2 - i1) if i2 != i1 else 0.0)
            if i2 == ilast and str(t2) == str(latest_time):
                return points
            if i2 == ilast:
                slope = float(explicit_slope) if explicit_slope is not None else ((v2 - v1) / (i2 - i1) if i2 != i1 else 0.0)
        p2['time'] = _same_time_format(t2, latest_time)
        p2['value'] = round(v1 + slope * (ilast - i1), 4)
        new_points = [dict(x) for x in points]
        new_points[-1] = p2
        return new_points
    except Exception:
        return points


def extend_overlays_to_latest(obj, rows):
    """Project stored trend/channel/pattern overlay endpoints to the newest candle.

    Daily chart refresh used to replace candles/indicators but preserve old overlay
    endpoints, so trendlines visually stopped at the date they were generated. This
    keeps the original anchors and extends only the rendered right endpoint.
    """
    if not isinstance(obj, dict) or not rows:
        return obj
    idx_by_time = _time_to_idx(rows)
    for key in ('trendlines', 'parallelChannels', 'pitchforks', 'linregChannels'):
        arr = obj.get(key)
        if not isinstance(arr, list):
            continue
        for item in arr:
            if not isinstance(item, dict):
                continue
            slope = item.get('slopePerBar', item.get('slope'))
            if isinstance(item.get('points'), list):
                item['points'] = _extend_line_points(item['points'], rows, idx_by_time, slope)
            for subkey in ('upper', 'lower', 'middle', 'median', 'lines'):
                sub = item.get(subkey)
                if isinstance(sub, list) and sub and isinstance(sub[0], dict) and 'points' not in sub[0]:
                    item[subkey] = _extend_line_points(sub, rows, idx_by_time, slope)
                elif isinstance(sub, list):
                    for line in sub:
                        if isinstance(line, dict) and isinstance(line.get('points'), list):
                            line['points'] = _extend_line_points(line['points'], rows, idx_by_time, line.get('slopePerBar', line.get('slope', slope)))
    for pat in obj.get('patterns') or []:
        if not isinstance(pat, dict):
            continue
        for line in pat.get('lines') or []:
            if isinstance(line, dict) and isinstance(line.get('points'), list):
                line['points'] = _extend_line_points(line['points'], rows, idx_by_time, line.get('slopePerBar', line.get('slope')))
    obj['overlayExtendedTo'] = rows[-1].get('time')
    return obj

def patch_chart_payload(symbol, rows, existing=None, frame='day'):
    obj = dict(existing or {})
    obj.update({
        'symbol': symbol,
        'frame': frame,
        'source': 'vn100_history_latest_merge',
        'rows': rows,
        'ma20': calc_ma(rows,20),
        'ma50': calc_ma(rows,50),
        'ema20': calc_ema(rows,20),
        'ema50': calc_ema(rows,50),
        'bollinger': calc_bb(rows,20,2),
        'macd': calc_macd(rows),
        'rsi': calc_rsi(rows,14),
        'updatedAt': datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds'),
        'latestTradingDate': rows[-1]['time'] if rows else None,
    })
    return obj

def main():
    hist=read(HIST)
    symbols=hist.get('symbols') or {}
    patched=0
    for sym,payload in symbols.items():
        rows = payload.get('rows') if isinstance(payload,dict) else None
        if not rows: continue
        s=str(sym).upper()
        # use full available rows; frontend already handles fit/range
        for name in [f'{s}.json', f'{s}_day.json']:
            p=PUBLIC_CHARTS/name
            existing=read(p) if p.exists() else {}
            old_last=(existing.get('rows') or [{}])[-1].get('time') if existing.get('rows') else None
            obj=patch_chart_payload(s, rows, existing, 'day')
            obj=extend_overlays_to_latest(obj, rows)
            write(p,obj)
            if old_last != rows[-1].get('time'):
                patched+=1
        # auto_chart_day keeps overlays but rows/indicators must be fresh
        p=PUBLIC_CHARTS/f'{s}_auto_chart_day.json'
        if p.exists():
            existing=read(p)
            obj=patch_chart_payload(s, rows, existing, 'day')
            obj=extend_overlays_to_latest(obj, rows)
            if isinstance(existing.get('summary'),dict):
                obj['summary']['asOfDate']=rows[-1]['time']
                obj['summary']['asOfPrice']=rows[-1].get('close')
            obj['asOfDate']=rows[-1]['time']; obj['asOfPrice']=rows[-1].get('close')
            write(p,obj)
    print('patched chart files for symbols', len(symbols), 'changed_last_date_files', patched)

if __name__=='__main__': main()
