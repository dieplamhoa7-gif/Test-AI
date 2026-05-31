from __future__ import annotations

import json
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
CLAUDE_ROOT = ROOT.parent / 'CLAUDE_INVESTMENT_MODEL_REVIEW' / 'stock-news-backend'
if str(CLAUDE_ROOT) not in sys.path:
    sys.path.insert(0, str(CLAUDE_ROOT))

from app.wyckoff_pipeline import analyze_wyckoff  # type: ignore
from wyckoff_features import latest_snapshot
from wyckoff_channel_detector import detect_local_wyckoff_channel


ACC_EVENTS = {'SC', 'ST', 'Spring', 'Test Spring', 'SOS', 'LPS'}
DIST_EVENTS = {'BC', 'UT', 'UTAD', 'SOW', 'LPSY'}

CHART_DIR = ROOT / 'firebase_public' / 'data' / 'charts'
STORY = ROOT / 'firebase_public' / 'data' / 'wyckoff_story_cache.json'
LEGACY_MWG = ROOT / 'firebase_public' / 'data' / 'wyckoff_hybrid_cache.json'
OUT = ROOT / 'firebase_public' / 'data' / 'wyckoff_hybrid_like_mwg_multi.json'
SYMBOLS = ['MWG', 'FPT', 'HPG', 'TCB', 'MBB', 'SSI', 'HDB']


def load_rows(symbol: str) -> pd.DataFrame:
    obj = json.loads((CHART_DIR / f'{symbol}.json').read_text(encoding='utf-8'))
    rows = obj if isinstance(obj, list) else obj.get('rows', [])
    df = pd.DataFrame(rows)
    df['time'] = pd.to_datetime(df['time'])
    for c in ['open', 'high', 'low', 'close', 'volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df.sort_values('time').reset_index(drop=True)


def atr_series(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h = df['high'].astype(float); l = df['low'].astype(float); c = df['close'].astype(float)
    tr = pd.concat([(h-l), (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False).mean()


def extend_main_tr(df: pd.DataFrame, tr: dict | None) -> dict | None:
    """Extend main TR while later candles still respect the same Wyckoff range.

    The upstream Claude TR detector may stop at the first valid SC/AR/ST segment.
    For the board, the main TR box should continue through later bars when price
    remains inside the same range or briefly overshoots and reclaims it. Stop only
    after a real acceptance outside the range.
    """
    if not tr or df.empty:
        return tr
    out = dict(tr)
    n = len(df)
    start = max(0, min(n - 1, int(out.get('start_idx', 0))))
    end = max(start, min(n - 1, int(out.get('end_idx', n - 1))))
    low = float(out.get('low', df['low'].iloc[start:end + 1].min()))
    high = float(out.get('high', df['high'].iloc[start:end + 1].max()))
    width = max(0.001, high - low)
    atr = atr_series(df, 14)
    close_outside_streak = 0
    last_inside_or_reclaim = end
    for i in range(end + 1, n):
        row = df.iloc[i]
        op, cl, hi, lo = map(float, [row['open'], row['close'], row['high'], row['low']])
        atr_v = float(atr.iloc[i]) if pd.notna(atr.iloc[i]) and float(atr.iloc[i]) > 0 else width * 0.03
        soft = max(width * 0.035, atr_v * 0.6)
        body_hi = max(op, cl)
        body_lo = min(op, cl)
        body_inside = body_hi <= high + soft and body_lo >= low - soft
        reclaimed_inside = lo < low - soft and cl >= low
        rejected_supply = hi > high + soft and cl <= high
        if body_inside or reclaimed_inside or rejected_supply:
            last_inside_or_reclaim = i
            close_outside_streak = 0
            continue
        close_outside = cl > high + soft or cl < low - soft
        close_outside_streak = close_outside_streak + 1 if close_outside else 0
        if close_outside_streak >= 3:
            break
        last_inside_or_reclaim = i
    if last_inside_or_reclaim > end:
        out['original_end_idx'] = end
        out['end_idx'] = int(last_inside_or_reclaim)
        out['extended'] = True
        out['extendMethod'] = 'respect_range_until_acceptance_break'
        segs = out.get('phase_segments') or []
        if segs:
            segs = [dict(s) for s in segs]
            segs[-1]['end'] = int(last_inside_or_reclaim)
            out['phase_segments'] = segs
    return out


def pick_main_tr(trs: list[dict], last_idx: int, df: pd.DataFrame | None = None) -> dict | None:
    non_local = [tr for tr in trs if not tr.get('is_local')]
    if not non_local:
        return None
    def score(tr: dict) -> float:
        length = tr.get('end_idx', 0) - tr.get('start_idx', 0)
        proximity = 100 - abs(last_idx - tr.get('end_idx', 0))
        return length * 0.7 + max(proximity, 0) * 0.3
    picked = max(non_local, key=score)
    return extend_main_tr(df, picked) if df is not None else picked


def pick_local_trs(trs: list[dict], main_tr: dict | None) -> list[dict]:
    if not main_tr:
        return []
    out = []
    main_span = main_tr.get('end_idx', 0) - main_tr.get('start_idx', 0)
    for tr in trs:
        if tr is main_tr:
            continue
        if tr.get('start_idx', 0) < main_tr.get('start_idx', 0):
            continue
        if tr.get('end_idx', 0) > main_tr.get('end_idx', 0):
            continue
        span = tr.get('end_idx', 0) - tr.get('start_idx', 0)
        if span > main_span * 0.6:
            continue
        out.append(tr)
    out.sort(key=lambda x: x.get('end_idx', 0), reverse=True)
    return out[:2]


def active_phase_box(main_tr: dict | None, last_idx: int) -> dict | None:
    if not main_tr:
        return None
    for seg in main_tr.get('phase_segments', []):
        if seg.get('start') is not None and seg.get('end') is not None and seg['start'] <= last_idx <= seg['end']:
            return seg
    segs = main_tr.get('phase_segments', [])
    return segs[-1] if segs else None


def enrich_event(ev: dict, rows: list[dict]) -> dict:
    idx = max(0, min(len(rows) - 1, int(ev.get('idx', 0))))
    r = rows[idx]
    return {'type': ev.get('type'), 'idx': idx, 'time': r['time'], 'price': float(ev.get('price') or r['close'])}


def detect_support_6m(frame: pd.DataFrame) -> dict | None:
    hist = frame.tail(126).reset_index(drop=True)
    if len(hist) < 50:
        return None
    recent = hist.tail(60).reset_index(drop=True)
    tr_low = float(recent['low'].min())
    tr_high = float(recent['high'].max())
    width = max(0.001, tr_high - tr_low)
    lower_top = tr_low + width * 0.20
    event_idxs = []
    for i in range(2, len(recent) - 2):
        lo = float(recent.iloc[i]['low']); hi = float(recent.iloc[i]['high'])
        is_local_low = all(lo <= float(recent.iloc[j]['low']) for j in range(i - 2, i + 3) if j != i)
        after = recent.iloc[i + 1:min(len(recent), i + 7)]
        reacts = len(after) > 0 and float(after['high'].max()) > hi
        if is_local_low and lo <= lower_top and reacts:
            event_idxs.append(i)
    if not event_idxs:
        event_idxs = [int(recent['low'].idxmin())]
    selected = recent.iloc[event_idxs]
    zone_low = float(selected['low'].min())
    zone_high = float(selected[['open', 'close']].max(axis=1).max())
    first = min(event_idxs)
    return {
        'kind': 'wyckoff_support_6m', 'type': 'support', 'method': 'wyckoff_tr_floor_test_cluster',
        'price': round(tr_low, 2), 'low': round(zone_low, 2), 'high': round(zone_high, 2),
        'touches': len(event_idxs), 'reactions': len(event_idxs), 'breaks': 0,
        'score': round(len(event_idxs) * 27 + 30, 2),
        'from': str(pd.Timestamp(recent.iloc[max(0, first - 1)]['time']).date()),
        'to': str(pd.Timestamp(recent.iloc[-1]['time']).date()),
        'sourceEvents': [{'time': str(pd.Timestamp(recent.iloc[i]['time']).date()), 'low': round(float(recent.iloc[i]['low']),2), 'bodyTop': round(max(float(recent.iloc[i]['open']), float(recent.iloc[i]['close'])),2)} for i in event_idxs],
    }


def detect_resistance_6m(frame: pd.DataFrame) -> dict | None:
    hist = frame.tail(126).reset_index(drop=True)
    if len(hist) < 50:
        return None
    recent = hist.tail(60).reset_index(drop=True)
    tr_low = float(recent['low'].min())
    tr_high = float(recent['high'].max())
    width = max(0.001, tr_high - tr_low)
    upper_bottom = tr_high - width * 0.20
    event_idxs = []
    for i in range(2, len(recent) - 2):
        hi = float(recent.iloc[i]['high']); lo = float(recent.iloc[i]['low'])
        is_local_high = all(hi >= float(recent.iloc[j]['high']) for j in range(i - 2, i + 3) if j != i)
        after = recent.iloc[i + 1:min(len(recent), i + 7)]
        reacts = len(after) > 0 and float(after['low'].min()) < lo
        if is_local_high and hi >= upper_bottom and reacts:
            event_idxs.append(i)
    if not event_idxs:
        event_idxs = [int(recent['high'].idxmax())]
    selected = recent.iloc[event_idxs]
    zone_low = float(selected[['open', 'close']].min(axis=1).min())
    zone_high = float(selected['high'].max())
    first = min(event_idxs)
    return {
        'kind': 'wyckoff_resistance_6m', 'type': 'resistance', 'method': 'wyckoff_tr_ceiling_test_cluster',
        'price': round(tr_high, 2), 'low': round(zone_low, 2), 'high': round(zone_high, 2),
        'touches': len(event_idxs), 'reactions': len(event_idxs), 'breaks': 0,
        'score': round(len(event_idxs) * 27 + 30, 2),
        'from': str(pd.Timestamp(recent.iloc[max(0, first - 1)]['time']).date()),
        'to': str(pd.Timestamp(recent.iloc[-1]['time']).date()),
        'sourceEvents': [{'time': str(pd.Timestamp(recent.iloc[i]['time']).date()), 'high': round(float(recent.iloc[i]['high']),2), 'bodyLow': round(min(float(recent.iloc[i]['open']), float(recent.iloc[i]['close'])),2)} for i in event_idxs],
    }


def detect_cluster_zone(frame: pd.DataFrame, lookback: int, zone_type: str) -> dict | None:
    hist = frame.tail(lookback).reset_index(drop=True)
    if len(hist) < 80:
        return None
    pivots = []
    for i in range(2, len(hist)-2):
        price = float(hist.iloc[i]['low'] if zone_type == 'support' else hist.iloc[i]['high'])
        ok = all((price <= float(hist.iloc[j]['low'])) if zone_type == 'support' else (price >= float(hist.iloc[j]['high'])) for j in range(i-2, i+3) if j != i)
        if ok:
            pivots.append({'idx': i, 'price': price})
    if not pivots:
        i = int(hist['low'].idxmin() if zone_type == 'support' else hist['high'].idxmax())
        pivots = [{'idx': i, 'price': float(hist.iloc[i]['low'] if zone_type == 'support' else hist.iloc[i]['high'])}]
    clusters = []
    for p in pivots:
        found = None
        for c in clusters:
            if abs(p['price'] / c['price'] - 1) <= 0.018:
                found = c; break
        if found:
            found['items'].append(p); found['price'] = sum(x['price'] for x in found['items']) / len(found['items'])
        else:
            clusters.append({'price': p['price'], 'items': [p]})
    best = None
    avg_range = float((hist['high']-hist['low']).clip(lower=0.001).mean())
    for c in clusters:
        price = float(c['price']); tol = max(price * 0.01, avg_range * 0.45)
        touches = reactions = breaks = 0; last=-99
        for i,row in hist.iterrows():
            op,cl,hi,lo = map(float,[row['open'],row['close'],row['high'],row['low']])
            near = abs((lo if zone_type == 'support' else hi) - price) <= tol
            if near and i-last >= 3:
                touches += 1; last = i
                after = hist.iloc[i+1:min(len(hist), i+7)]
                if len(after):
                    if zone_type == 'support' and float(after['high'].max()) >= price + tol: reactions += 1
                    if zone_type == 'resistance' and float(after['low'].min()) <= price - tol: reactions += 1
            if zone_type == 'support' and min(op,cl) < price - tol: breaks += 1
            if zone_type == 'resistance' and max(op,cl) > price + tol: breaks += 1
        score = touches * 10 + reactions * 8 - breaks * 4 + min(20, len(c['items'])*4)
        z = {'kind': f'wyckoff_{zone_type}_{lookback}', 'type': zone_type, 'method': 'historical_hard_' + zone_type, 'price': round(price,2), 'low': round(price-tol,2), 'high': round(price+tol,2), 'touches': touches, 'reactions': reactions, 'breaks': breaks, 'score': round(score,2), 'from': str(pd.Timestamp(hist.iloc[0]['time']).date()), 'to': str(pd.Timestamp(hist.iloc[-1]['time']).date())}
        if best is None or z['score'] > best['score']:
            best = z
    return best


def detect_core_events(frame: pd.DataFrame, main_tr: dict | None) -> list[dict]:
    if not main_tr:
        return []
    df = frame.reset_index(drop=True); n=len(df)
    s=max(0,min(n-1,int(main_tr.get('start_idx',0)))); e=max(s,min(n-1,int(main_tr.get('end_idx',n-1))))
    tr_low=float(main_tr.get('low', df['low'].iloc[s:e+1].min())); tr_high=float(main_tr.get('high', df['high'].iloc[s:e+1].max()))
    width=max(0.001,tr_high-tr_low); atr=atr_series(df,14); vma=df['volume'].rolling(20,min_periods=5).mean(); out=[]
    def add(tp,idx,price,reason): out.append({'type':tp,'idx':int(idx),'time':str(pd.Timestamp(df.iloc[idx]['time']).date()),'price':round(float(price),2),'reason':reason})
    early_end=min(e, s+max(12,int((e-s+1)*0.28))); sc_idx=None; cands=[]
    for i in range(s, early_end+1):
        lo,hi,vol=map(float,[df.iloc[i]['low'],df.iloc[i]['high'],df.iloc[i]['volume']]); av=float(atr.iloc[i]) if pd.notna(atr.iloc[i]) else max(0.001,hi-lo); vv=float(vma.iloc[i]) if pd.notna(vma.iloc[i]) and float(vma.iloc[i])>0 else vol
        if lo <= tr_low + width*0.12:
            cands.append(((tr_low+width*0.12-lo)/width + (1 if hi-lo>=av*.9 else 0) + (1 if vol>=vv*1.05 else 0), i, lo))
    if cands:
        _,sc_idx,sc_price=max(cands,key=lambda x:x[0]); add('SC',sc_idx,sc_price,'Selling climax near TR floor')
    ar_idx=None
    if sc_idx is not None:
        for i in range(sc_idx+1,min(e+1,sc_idx+18)):
            hi=float(df.iloc[i]['high'])
            if hi >= tr_low + width*.45:
                ar_idx=i; add('AR',i,hi,'Automatic rally after SC'); break
    if sc_idx is not None and ar_idx is not None:
        for i in range(ar_idx+1,min(e+1,ar_idx+28)):
            lo=float(df.iloc[i]['low'])
            if lo <= tr_low+width*.18 and lo >= float(df.iloc[sc_idx]['low'])*.97:
                add('ST',i,lo,'Secondary test after AR'); break
    out.sort(key=lambda x:x['idx']); return out


def analyze_post_tr(df: pd.DataFrame, main_tr: dict | None) -> dict | None:
    if not main_tr: return None
    end=int(main_tr.get('end_idx',len(df)-1))
    if end>=len(df)-1: return None
    tr_low=float(main_tr['low']); post=df.iloc[end+1:].reset_index(drop=True); min_low=float(post['low'].min()); last_close=float(post.iloc[-1]['close'])
    if min_low<tr_low and last_close>tr_low: label,bias='Spring candidate','bullish_reclaim_watch'
    elif min_low<tr_low and len(post)>=2 and float(post.iloc[-1]['close'])<tr_low and float(post.iloc[-2]['close'])<tr_low: label,bias='Accepted below TR','markdown_watch'
    elif min_low<tr_low: label,bias='Break below TR','risk'
    else: label,bias='Inside/Post TR','range'
    return {'label':label,'bias':bias,'postStart':str(pd.Timestamp(df.iloc[end+1]['time']).date()),'lastTime':str(pd.Timestamp(post.iloc[-1]['time']).date()),'trLow':round(tr_low,2),'trHigh':round(float(main_tr['high']),2),'minLow':round(min_low,2),'lastClose':round(last_close,2)}


def detect_sideway_channel(df: pd.DataFrame, main_tr: dict | None) -> dict:
    n = len(df)
    if n < 40:
        return {'type': 'unknown', 'slopePct': None, 'confidence': 0, 'reason': 'not enough data'}
    if main_tr:
        s = max(0, int(main_tr.get('start_idx', max(0, n - 80))))
        e = min(n - 1, int(main_tr.get('end_idx', n - 1)))
        window = df.iloc[s:e + 1].copy()
        if len(window) < 35:
            window = df.tail(80).copy()
    else:
        window = df.tail(80).copy()
    window = window.reset_index(drop=True)
    x = pd.Series(range(len(window)), dtype=float)
    mid = float(window['close'].median()) if len(window) else 0.0
    if mid <= 0 or x.var() == 0:
        return {'type': 'unknown', 'slopePct': None, 'confidence': 0, 'reason': 'bad price data'}
    low_slope = float(pd.Series(window['low']).astype(float).cov(x) / x.var())
    high_slope = float(pd.Series(window['high']).astype(float).cov(x) / x.var())
    close_slope = float(pd.Series(window['close']).astype(float).cov(x) / x.var())
    slope_pct = close_slope / mid * 100
    width_pct = (float(window['high'].max()) - float(window['low'].min())) / mid * 100
    if low_slope > 0 and high_slope > 0 and 0.015 <= slope_pct <= 0.22:
        typ = 'SIDEWAY_UP'
        reason = 'higher lows and higher highs inside a mild rising range'
    elif low_slope < 0 and high_slope < 0 and -0.22 <= slope_pct <= -0.015:
        typ = 'SIDEWAY_DOWN'
        reason = 'lower highs and lower lows inside a mild falling range'
    elif abs(slope_pct) < 0.04:
        typ = 'SIDEWAY_FLAT'
        reason = 'range is mostly flat'
    elif slope_pct > 0.22:
        typ = 'UPTREND_NOT_SIDEWAY'
        reason = 'slope is too steep for sideway up'
    elif slope_pct < -0.22:
        typ = 'DOWNTREND_NOT_SIDEWAY'
        reason = 'slope is too steep for sideway down'
    else:
        typ = 'MIXED_RANGE'
        reason = 'channel slopes are mixed or weak'
    conf = max(0, min(100, 70 - abs(width_pct - 18) * 1.2 + min(20, len(window) / 4)))
    return {
        'type': typ,
        'slopePctPerBar': round(slope_pct, 4),
        'widthPct': round(width_pct, 2),
        'confidence': round(conf, 1),
        'reason': reason,
    }


def analyze_current_trend(df: pd.DataFrame, main_tr: dict | None, phase_box: dict | None, events: list[dict], scores: dict, post_tr: dict | None, sideway: dict) -> dict:
    close = df['close'].astype(float)
    ma20 = float(close.tail(20).mean()) if len(close) >= 20 else float(close.mean())
    ma50 = float(close.tail(50).mean()) if len(close) >= 50 else ma20
    ma20_prev = float(close.iloc[-21:-1].mean()) if len(close) >= 21 else ma20
    ma50_prev = float(close.iloc[-51:-1].mean()) if len(close) >= 51 else ma50
    last_close = float(close.iloc[-1]) if len(close) else None
    phase = phase_box.get('phase') if phase_box else None
    event_types = {e.get('type') for e in events}
    spring_score = float(scores.get('springScore', 0) or 0)
    upthrust_score = float(scores.get('upthrustScore', 0) or 0)
    sos_score = float(scores.get('sosScore', 0) or 0)
    sow_score = float(scores.get('sowScore', 0) or 0)
    net = round((spring_score + sos_score) - (upthrust_score + sow_score), 1)

    trend = 'NEUTRAL'
    structure = 'RANGE'
    confidence = 52.0
    reasons = []

    bullish_break = post_tr and post_tr.get('bias') in ('markup_watch', 'bullish_reclaim_watch')
    bearish_break = post_tr and post_tr.get('bias') == 'markdown_watch'
    weakness_present = ('SOW' in event_types or 'LPSY' in event_types or 'UTAD' in event_types or bearish_break or net < -8)
    strength_present = ('SOS' in event_types or 'LPS' in event_types or bullish_break or net > 8)

    if bullish_break and last_close is not None and ma20 >= ma20_prev:
        trend = 'MARKUP_EARLY'
        structure = 'BULLISH_EXPANSION'
        confidence = 74.0
        reasons.append('post-TR bullish break/reclaim detected')
    elif bearish_break and last_close is not None and ma20 <= ma20_prev:
        trend = 'MARKDOWN_EARLY'
        structure = 'BEARISH_EXPANSION'
        confidence = 74.0
        reasons.append('accepted below trading range')
    elif strength_present and not weakness_present and ('SOS' in event_types or 'LPS' in event_types):
        trend = 'SIDEWAY_UP'
        structure = 'ACCUMULATION_TO_MARKUP'
        confidence = 72.0
        reasons.append('SOS/LPS indicates strength inside/up from range')
    elif weakness_present and ('SOW' in event_types or 'LPSY' in event_types or 'UTAD' in event_types):
        trend = 'SIDEWAY_DOWN'
        structure = 'DISTRIBUTION_TO_MARKDOWN'
        confidence = 72.0
        reasons.append('SOW/LPSY/UTAD indicates weakness inside/down from range')
    elif sideway.get('type') == 'SIDEWAY_UP' and not weakness_present and ma20 >= ma20_prev:
        trend = 'SIDEWAY_UP'
        structure = 'RISING_RANGE'
        confidence = max(confidence, float(sideway.get('confidence') or 0))
        reasons.append('channel slope shows higher lows and higher highs')
    elif sideway.get('type') == 'SIDEWAY_DOWN' and (weakness_present or ma20 <= ma20_prev):
        trend = 'SIDEWAY_DOWN'
        structure = 'FALLING_RANGE'
        confidence = max(confidence, float(sideway.get('confidence') or 0))
        reasons.append('channel slope shows lower highs and lower lows')
    elif sideway.get('type') == 'SIDEWAY_FLAT':
        trend = 'SIDEWAY_FLAT'
        structure = 'BALANCED_RANGE'
        confidence = max(confidence, float(sideway.get('confidence') or 0))
        reasons.append('channel slope is mostly flat')
    elif sideway.get('type') == 'SIDEWAY_UP' and weakness_present:
        trend = 'RANGE_WITH_WEAKNESS'
        structure = 'FAILED_SIDEWAY_UP'
        confidence = max(confidence, float(sideway.get('confidence') or 0) - 8)
        reasons.append('price slope rose, but Wyckoff weakness overrides sideway up')
    elif sideway.get('type') == 'SIDEWAY_DOWN' and strength_present:
        trend = 'RANGE_WITH_STRENGTH'
        structure = 'FAILED_SIDEWAY_DOWN'
        confidence = max(confidence, float(sideway.get('confidence') or 0) - 8)
        reasons.append('price slope fell, but Wyckoff strength overrides sideway down')

    if last_close is not None and ma20 > ma50 and ma20 >= ma20_prev and trend in ('NEUTRAL', 'SIDEWAY_FLAT'):
        trend = 'UPTREND_WITHIN_RANGE'
        structure = 'BULLISH_DRIFT'
        confidence = max(confidence, 64.0)
        reasons.append('ma20 above ma50 and both stable/up')
    elif last_close is not None and ma20 < ma50 and ma20 <= ma20_prev and trend in ('NEUTRAL', 'SIDEWAY_FLAT'):
        trend = 'DOWNTREND_WITHIN_RANGE'
        structure = 'BEARISH_DRIFT'
        confidence = max(confidence, 64.0)
        reasons.append('ma20 below ma50 and both stable/down')

    if net > 10:
        reasons.append('net Wyckoff strength score is positive')
        confidence = min(88.0, confidence + 4.0)
    elif net < -10:
        reasons.append('net Wyckoff weakness score is negative')
        confidence = min(88.0, confidence + 4.0)

    return {
        'trend': trend,
        'structure': structure,
        'phase': phase,
        'confidence': round(confidence, 1),
        'ma20': round(ma20, 2),
        'ma50': round(ma50, 2),
        'ma20SlopeUp': bool(ma20 >= ma20_prev),
        'ma50SlopeUp': bool(ma50 >= ma50_prev),
        'sidewayType': sideway.get('type'),
        'scoreNet': net,
        'reasons': reasons[:4],
    }


def build_model_state(symbol: str, df: pd.DataFrame, main_tr: dict | None, phase_box: dict | None, events: list[dict], summary: dict, scores: dict, post_tr: dict | None) -> dict:
    last_close = float(df.iloc[-1]['close']) if len(df) else None
    tr_low = float(main_tr['low']) if main_tr else None
    tr_high = float(main_tr['high']) if main_tr else None
    sideway = detect_sideway_channel(df, main_tr)
    wyckoff_channel = detect_local_wyckoff_channel(df, main_tr=main_tr, events=events, scores=scores, symbol=symbol)
    if wyckoff_channel.get('type') in ('SIDEWAY_UP', 'SIDEWAY_DOWN'):
        sideway = {
            **sideway,
            'type': wyckoff_channel.get('type'),
            'confidence': wyckoff_channel.get('confidence'),
            'reason': wyckoff_channel.get('reason'),
            'method': 'local_pivot_wyckoff_channel',
        }
    phase = phase_box.get('phase') if phase_box else None
    event_types = {e.get('type') for e in events}
    spring_score = float(scores.get('springScore', 0) or 0)
    upthrust_score = float(scores.get('upthrustScore', 0) or 0)
    sos_score = float(scores.get('sosScore', 0) or 0)
    sow_score = float(scores.get('sowScore', 0) or 0)
    demand_score = round(spring_score + sos_score, 1)
    supply_score = round(upthrust_score + sow_score, 1)
    current_trend = analyze_current_trend(df, main_tr, phase_box, events, scores, post_tr, sideway)

    state = 'RANGE_WAIT'
    action = 'WAIT'
    rationale = []

    if 'Spring' in event_types or 'Test Spring' in event_types:
        state = 'PHASE_C_SPRING_TEST'
        action = 'WATCH_BUY'
        rationale.append('spring/test detected near TR floor')
    if 'SOS' in event_types or 'LPS' in event_types:
        state = 'PHASE_D_STRENGTH'
        action = 'BUY_CANDIDATE'
        rationale.append('SOS/LPS suggests demand confirmation')
    if 'SOW' in event_types or 'LPSY' in event_types or 'UTAD' in event_types:
        state = 'MARKDOWN_RISK'
        action = 'AVOID_OR_SELL'
        rationale.append('distribution/markdown events detected')
    if post_tr and post_tr.get('bias') == 'markdown_watch':
        state = 'POST_TR_MARKDOWN'
        action = 'AVOID_OR_SELL'
        rationale.append('price accepted below TR')
    elif post_tr and post_tr.get('bias') == 'bullish_reclaim_watch' and action == 'WAIT':
        state = 'POST_TR_RECLAIM'
        action = 'WATCH_BUY'
        rationale.append('price reclaimed above TR floor')
    elif phase == 'E' and tr_high is not None and last_close is not None and last_close > tr_high:
        state = 'PHASE_E_MARKUP'
        action = 'HOLD_OR_TRAIL'
        rationale.append('price left trading range upward')

    confirm_above = None
    invalid_below = None
    target_zone = None
    entry_zone = None
    if main_tr:
        width = max(0.001, float(main_tr['high']) - float(main_tr['low']))
        entry_zone = [round(float(main_tr['low']), 2), round(float(main_tr['low']) + width * 0.18, 2)]
        confirm_above = round(float(main_tr['low']) + width * 0.62, 2)
        invalid_below = round(float(main_tr['low']) - width * 0.06, 2)
        target_zone = [round(float(main_tr['high']) - width * 0.08, 2), round(float(main_tr['high']), 2)]
        if action in ('AVOID_OR_SELL',):
            confirm_above = round(float(main_tr['high']) - width * 0.12, 2)
            invalid_below = round(float(main_tr['low']), 2)

    return {
        'state': state,
        'action': action,
        'phase': phase,
        'methodBias': summary.get('methodBias') or summary.get('bias'),
        'phaseInterpretation': summary.get('phaseInterpretation'),
        'currentTrend': current_trend,
        'wyckoffChannel': wyckoff_channel,
        'sidewayType': sideway.get('type'),
        'sidewayConfidence': sideway.get('confidence'),
        'sideway': sideway,
        'demandScore': demand_score,
        'supplyScore': supply_score,
        'entryZone': entry_zone,
        'confirmAbove': confirm_above,
        'invalidBelow': invalid_below,
        'targetZone': target_zone,
        'lastClose': round(last_close, 2) if last_close is not None else None,
        'rationale': rationale,
    }


def build_symbol(symbol: str, story: dict) -> dict:
    df = load_rows(symbol)
    rows = [{'time':str(pd.Timestamp(r['time']).date()),'open':float(r['open']),'high':float(r['high']),'low':float(r['low']),'close':float(r['close']),'volume':float(r['volume'])} for _,r in df.iterrows()]
    if symbol == 'MWG' and LEGACY_MWG.exists():
        base = json.loads(LEGACY_MWG.read_text(encoding='utf-8'))
        base['resistancesByWindow'] = {
            '6m': detect_resistance_6m(df),
            '1y': detect_cluster_zone(df, 252, 'resistance'),
        }
        summary = dict((base.get('story') or {}).get('summary') or {})
        scores = summary.get('quantScores') or summary.get('scores') or {}
        main_tr = base.get('mainTr')
        phase_box = base.get('phaseBox')
        events = base.get('events') or []
        post_tr = base.get('postTrAction')
        base['modelState'] = build_model_state(symbol, df, main_tr, phase_box, events, summary, scores, post_tr)
        base['story']['summary']['methodBias'] = summary.get('methodBias') or summary.get('bias') or base['modelState'].get('methodBias')
        base['story']['summary']['quantScores'] = scores
        return base
    pipe = analyze_wyckoff(symbol, df.copy())
    trs = pipe.get('trading_ranges', [])
    main_tr = pick_main_tr(trs, len(rows)-1, df)
    local_trs = pick_local_trs(trs, main_tr)
    phase_box = active_phase_box(main_tr, len(rows)-1)
    events = detect_core_events(df, main_tr)
    seen={(e.get('type'),e.get('idx')) for e in events}
    keep={'SC','AR','ST','Spring','Shake_out','Test Spring','SOS','UT','UTAD','SOW','LPS','LPSY'}
    for tr in trs:
        for ev in tr.get('events',[]):
            en=enrich_event(ev,rows); key=(en.get('type'),en.get('idx'))
            if en.get('type') in keep and key not in seen: events.append(en); seen.add(key)
    events.sort(key=lambda e:e.get('idx',0))
    quant_snapshot = latest_snapshot(rows, symbol=symbol, lookback=60)
    post_tr = analyze_post_tr(df, main_tr)
    summary = dict(story.get('summary', {}))
    scores = ((quant_snapshot or {}).get('scores') or {})
    range_bias = (scores.get('bias') or summary.get('bias') or 'range')
    if post_tr and post_tr.get('bias') == 'bullish_reclaim_watch':
        method_bias = 'accumulation_reclaim_watch'
    elif post_tr and post_tr.get('bias') == 'markdown_watch':
        method_bias = 'distribution_markdown_watch'
    elif range_bias == 'range' and scores.get('springScore', 0) >= scores.get('upthrustScore', 0):
        method_bias = 'range_accumulation_candidate'
    elif range_bias == 'range' and scores.get('upthrustScore', 0) > scores.get('springScore', 0):
        method_bias = 'range_distribution_candidate'
    else:
        method_bias = range_bias
    summary['methodBias'] = method_bias
    summary['quantScores'] = scores
    summary['eventConfidence'] = {e['type']: round(min(100.0, 45.0 + scores.get('springScore', 0) * 0.6), 1) if e['type'] in ('SC','ST','Spring','Test Spring') else round(min(100.0, 45.0 + scores.get('upthrustScore', 0) * 0.6), 1) for e in events}
    if phase_box and phase_box.get('phase') == 'B' and any(e.get('type') in ('Spring','Test Spring') for e in events):
        summary['phaseInterpretation'] = 'Phase C candidate'
    elif phase_box and phase_box.get('phase') == 'B' and any(e.get('type') in ('SOS','LPS') for e in events):
        summary['phaseInterpretation'] = 'Phase D candidate'
    elif phase_box and phase_box.get('phase') == 'B' and any(e.get('type') in ('SOW','LPSY','UTAD') for e in events):
        summary['phaseInterpretation'] = 'Phase D/E markdown risk'
    else:
        summary['phaseInterpretation'] = f"Phase {phase_box.get('phase')}" if phase_box else 'No clear phase'
    model_state = build_model_state(symbol, df, main_tr, phase_box, events, summary, scores, post_tr)
    return {
        'createdAt': pd.Timestamp.now().isoformat(), 'symbol': symbol, 'source':'like-mwg-hybrid-multi', 'rows':len(rows),
        'mainTr': main_tr, 'localTrs': local_trs, 'phaseBox': phase_box, 'events': events,
        'supportsByWindow': {'6m': detect_support_6m(df), '1y': detect_cluster_zone(df, 252, 'support')},
        'resistancesByWindow': {'6m': detect_resistance_6m(df), '1y': detect_cluster_zone(df, 252, 'resistance')},
        'postTrAction': post_tr,
        'modelState': model_state,
        'story': {'summary':summary,'zones':story.get('zones',[]),'snapshot':quant_snapshot or story.get('snapshot',{}),'arrows':story.get('arrows',[])},
    }


def main():
    stories=json.loads(STORY.read_text(encoding='utf-8')).get('symbols',{})
    out={'createdAt':pd.Timestamp.now().isoformat(),'mode':'like-mwg-hybrid-multi','symbols':{}}
    for s in SYMBOLS:
        try:
            out['symbols'][s]=build_symbol(s, stories.get(s,{}))
            print(s, 'ok', 'events', len(out['symbols'][s].get('events',[])), 'mainTr', bool(out['symbols'][s].get('mainTr')))
        except Exception as e:
            print(s, 'ERR', repr(e))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output':str(OUT),'symbols':list(out['symbols'])},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
