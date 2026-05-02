from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
from app.market_data import _load_history, _compute_indicators, _detect_momentum_divergence
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT = Path('data/b4_near_support_macd_recover_relaxed_backtest.json')
EXCLUDE = {'VIC', 'VHM'}
HORIZON = 42


def f(v, d=0.0):
    try:
        if v is None:
            return d
        if hasattr(v, 'item'):
            v = v.item()
        if pd.isna(v):
            return d
        return float(v)
    except Exception:
        return d


def r(v, n=2):
    try:
        return round(float(v), n)
    except Exception:
        return None


def ichimoku_state(df):
    h = pd.to_numeric(df.high, errors='coerce')
    l = pd.to_numeric(df.low, errors='coerce')
    c = pd.to_numeric(df.close, errors='coerce')
    tenkan = (h.rolling(9).max() + l.rolling(9).min()) / 2
    kijun = (h.rolling(26).max() + l.rolling(26).min()) / 2
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    price = f(c.iloc[-1])
    a = f(span_a.iloc[-1])
    b = f(span_b.iloc[-1])
    t = f(tenkan.iloc[-1])
    k = f(kijun.iloc[-1])
    if not a or not b:
        return {'state': 'unknown', 'bullishTkCross': bool(t > k) if t and k else False, 'tenkan': r(t), 'kijun': r(k), 'cloudTop': None, 'cloudBottom': None}
    return {'state': 'above_cloud' if price > max(a, b) else 'below_cloud' if price < min(a, b) else 'in_cloud', 'bullishTkCross': bool(t > k), 'tenkan': r(t), 'kijun': r(k), 'cloudTop': r(max(a, b)), 'cloudBottom': r(min(a, b))}


def pivot_lows(vals, left=2, right=2):
    out = []
    vals = list(vals)
    for i in range(left, len(vals) - right):
        v = vals[i]
        if v is None or pd.isna(v):
            continue
        win = [x for x in vals[i-left:i+right+1] if x is not None and not pd.isna(x)]
        if win and all(v <= x for x in win):
            out.append((i, float(v)))
    return out


def bullish_divergence_detail(hist, ind_until):
    try:
        close = pd.to_numeric(hist.close, errors='coerce').tail(60).reset_index(drop=True)
        rsi = pd.to_numeric(ind_until['rsi14'], errors='coerce').tail(60).reset_index(drop=True)
        mh = pd.to_numeric(ind_until['histogram'], errors='coerce').tail(60).reset_index(drop=True)
        piv = pivot_lows(close, 2, 2)
        if len(piv) < 2:
            return {'rsiBullish': False, 'macdBullish': False, 'detail': 'not_enough_pivots'}
        p1, p2 = piv[-2], piv[-1]
        i1, i2 = p1[0], p2[0]
        price_lower = p2[1] < p1[1]
        return {
            'rsiBullish': bool(price_lower and f(rsi.iloc[i2]) > f(rsi.iloc[i1])),
            'macdBullish': bool(price_lower and f(mh.iloc[i2]) > f(mh.iloc[i1])),
            'priceLow1': r(p1[1]),
            'priceLow2': r(p2[1]),
            'rsiLow1': r(rsi.iloc[i1]),
            'rsiLow2': r(rsi.iloc[i2]),
            'macdHistLow1': r(mh.iloc[i1], 4),
            'macdHistLow2': r(mh.iloc[i2], 4),
        }
    except Exception as e:
        return {'rsiBullish': False, 'macdBullish': False, 'detail': repr(e)}


def action_indicators(price, row, hist, ind_until):
    rsi = f(row.get('rsi14'), 50)
    macd = f(row.get('macd'))
    sig = f(row.get('signal'))
    mh = f(row.get('histogram'))
    bbp = f(row.get('bbPercent'), 0.5)
    volr = f(row.get('volumeRatio'), 1)
    roc20 = (price / f(hist.close.iloc[-21], price) - 1) * 100 if len(hist) > 21 else 0
    ret5 = (price / f(hist.close.iloc[-6], price) - 1) * 100 if len(hist) > 6 else 0
    div = _detect_momentum_divergence(ind_until)
    div2 = bullish_divergence_detail(hist, ind_until)
    ichi = ichimoku_state(hist)
    hists = [f(ind_until.iloc[j].get('histogram'), mh) for j in range(max(0, len(ind_until) - 4), len(ind_until))]
    macd_recovering = bool(len(hists) >= 3 and hists[-1] > hists[-2] > hists[-3])
    bullish_any = bool(div.get('bullish') or div2.get('rsiBullish') or div2.get('macdBullish'))
    return {
        'rsi': r(rsi),
        'macd': r(macd, 4),
        'macdSignal': r(sig, 4),
        'macdHist': r(mh, 4),
        'macdHistSeq': [r(x, 4) for x in hists],
        'macdHistRecovering': macd_recovering,
        'bbPercent': r(bbp, 3),
        'volumeRatio': r(volr, 2),
        'roc20': r(roc20),
        'ret5': r(ret5),
        'ichimoku': ichi,
        'bullishDivergence': bullish_any,
        'bullishDivergenceDetail': div2,
        'bearishDivergence': bool(div.get('bearish')),
    }


def pass_b4(price, rs, ai):
    sup = f(rs.get('activeSupportDay') or rs.get('supportDay'))
    dist = (price - sup) / price * 100 if price and sup else 999
    rsi = f(ai['rsi'])
    volr = f(ai['volumeRatio'])
    roc = f(ai['roc20'])
    mh = f(ai['macdHist'])
    bbp = f(ai['bbPercent'])
    ichi = ai['ichimoku']['state']
    # Relaxed variant requested by user: play close to support + MACD recovering,
    # loosen other conditions to see whether signal count improves.
    if ai.get('bearishDivergence'):
        return False, 'bearish_divergence'
    if ichi == 'below_cloud':
        return False, 'below_cloud'
    if dist > 2.5:
        return False, 'dist>2.5'
    if not (35 <= rsi <= 65):
        return False, 'rsi_not_35_65'
    if volr < 0.45 or volr > 3.0:
        return False, 'vol_bad'
    if roc < -15 or roc > 18:
        return False, 'roc_bad'
    if not ai.get('macdHistRecovering'):
        return False, 'macd_not_recovering'
    if bbp > 0.95:
        return False, 'bbp_too_high'
    return True, 'ok'


def trade_manage(df, i):
    entry = f(df.iloc[i + 1].close)
    stop = entry * 0.94
    target = entry * 1.06
    future = df.iloc[i + 2:i + 2 + HORIZON]
    if future.empty:
        return None
    size = 1.0
    realized = 0.0
    half = False
    peak = entry
    hold = len(future)
    exitd = str(future.iloc[-1].time.date())
    outcome = 'timeout'
    path = []
    for n, (_, row) in enumerate(future.iterrows(), 1):
        high = f(row.high)
        low = f(row.low)
        peak = max(peak, high)
        event = None
        if not half and high >= target:
            realized += 0.5 * 6
            size = 0.5
            half = True
            stop = max(stop, entry * 1.005)
            event = 'take_50_at_6'
        if half:
            stop = max(stop, entry * 1.005, peak * 0.97)
        if low <= stop:
            realized += size * ((stop - entry) / entry * 100)
            size = 0
            outcome = 'win' if realized > 0 else 'loss'
            hold = n
            exitd = str(row.time.date())
            event = (event + '+stop' if event else 'stop')
            path.append({'date': str(row.time.date()), 'open': r(row.open), 'high': r(row.high), 'low': r(row.low), 'close': r(row.close), 'stop': r(stop), 'event': event})
            break
        path.append({'date': str(row.time.date()), 'open': r(row.open), 'high': r(row.high), 'low': r(row.low), 'close': r(row.close), 'stop': r(stop), 'event': event})
    if size > 0:
        last = f(future.iloc[-1].close)
        realized += size * ((last - entry) / entry * 100)
        outcome = 'win' if realized > 0 else 'loss' if realized < 0 else 'flat'
    return {'outcome': outcome, 'entry': r(entry), 'stopInitial': r(entry * 0.94), 'target': r(target), 'pnlPct': r(realized), 'riskPct': 6, 'holdSessions': hold, 'exitDate': exitd, 'partialTaken': half, 'futurePath': path}


def summ(ts):
    n = len(ts)
    w = [x for x in ts if f(x['pnlPct']) > 0]
    l = [x for x in ts if f(x['pnlPct']) < 0]
    avg = lambda xs, k: round(sum(f(x[k]) for x in xs) / len(xs), 2) if xs else 0
    sm = lambda xs, k: round(sum(f(x[k]) for x in xs), 2) if xs else 0
    return {'totalTrades': n, 'wins': len(w), 'losses': len(l), 'winRatePct': round(len(w) / n * 100, 2) if n else 0, 'avgPnlPct': avg(ts, 'pnlPct'), 'sumPnlPct': sm(ts, 'pnlPct'), 'avgWinPct': avg(w, 'pnlPct'), 'avgLossPct': avg(l, 'pnlPct'), 'avgHoldSessions': avg(ts, 'holdSessions')}


def load_histories(symbols):
    out = {}
    for idx, sym in enumerate(symbols, 1):
        try:
            df = _load_history(sym)
            out[sym] = df
            print('history', idx, sym, 0 if df is None else len(df), flush=True)
        except Exception as e:
            out[sym] = None
            print('history', idx, sym, 'ERR', e, flush=True)
        if idx % 15 == 0:
            time.sleep(40)
        else:
            time.sleep(1.05)
    return out


def run_window(name, start, end, histories):
    trades = []
    rejects = Counter()
    counts = {}
    for sym in TECHNICAL_UNIVERSE[:50]:
        if sym in EXCLUDE:
            continue
        df = histories.get(sym)
        if df is None or df.empty or len(df) < 260:
            counts[sym] = {'error': 'missing/short'}
            continue
        df = df.copy()
        df['time'] = pd.to_datetime(df.time)
        df = df.sort_values('time').reset_index(drop=True)
        ind = _compute_indicators(df.copy())
        c = {'loops': 0, 'trades': 0}
        for i in range(100, len(df) - HORIZON - 2):
            t = df.iloc[i].time
            if t < start or t >= end:
                continue
            c['loops'] += 1
            hist = df.iloc[:i + 1].copy()
            row = ind.iloc[i]
            price = f(df.iloc[i].close)
            rs = calc_rs_levels_only(price, f(df.iloc[i].open), f(df.iloc[i].open), f(df.iloc[i].high), f(df.iloc[i].low), price, hist)
            ai = action_indicators(price, row, hist, ind.iloc[:i + 1].copy())
            ok, reason = pass_b4(price, rs, ai)
            if not ok:
                rejects[reason] += 1
                continue
            tr = trade_manage(df, i)
            if tr:
                sup = f(rs.get('activeSupportDay') or rs.get('supportDay'))
                dist = (price - sup) / price * 100 if price and sup else 999
                tr.update({'symbol': sym, 'signalDate': str(df.iloc[i].time.date()), 'entryDate': str(df.iloc[i + 1].time.date()), 'strategy': 'B4_trend_pullback_locked', 'distSupportPct': r(dist), 'support': rs.get('activeSupportDay'), 'resistance': rs.get('activeResistanceDay'), 'supportZone': rs.get('supportZoneDay'), 'resistanceZone': rs.get('resistanceZoneDay'), 'entryIndicators': ai})
                trades.append(tr)
                c['trades'] += 1
        counts[sym] = c
        print(name, sym, c, flush=True)
    return {'window': name, 'start': str(start.date()), 'end': str(end.date()), 'summary': summ(trades), 'trades': trades, 'rejects': dict(rejects.most_common(20)), 'counts': counts}


def main():
    symbols = TECHNICAL_UNIVERSE[:50]
    histories = load_histories(symbols)
    now = pd.Timestamp(datetime.now())
    current = run_window('current180', now - timedelta(days=180), now, histories)
    prev = run_window('prev3m', now - timedelta(days=270), now - timedelta(days=180), histories)
    payload = {'createdAt': datetime.now().isoformat(), 'name': 'B4 Near Support MACD Recover relaxed', 'exit': {'targetPct': 6, 'takeProfitAtTargetPct': 50, 'trailingAfterTarget': 'max(entry+0.5%, peak-3%)', 'stopPct': 6}, 'current180': current, 'prev3m': prev}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'current180': current['summary'], 'prev3m': prev['summary']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
