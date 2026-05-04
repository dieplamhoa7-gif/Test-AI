from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.market_data import _load_history, _compute_indicators
from app.technical_filters import TECHNICAL_UNIVERSE

OUT = Path('data/monthly_indicators_vn100_cache.json')
TMP = Path('data/monthly_indicators_vn100_cache.partial.json')
REM = Path('data/vn100_remaining_symbols.json')
SLEEP_EVERY = 18
SLEEP_SECONDS = 65



def hsx_universe_from_rs():
    p=Path('data/rs_levels_hsx_all_cache.json')
    if p.exists():
        try:
            data=json.loads(p.read_text(encoding='utf-8'))
            syms=[]
            for row in data.get('items',[]):
                sym=str(row.get('symbol') or row.get('ticker') or '').strip().upper()
                if sym and sym not in syms: syms.append(sym)
            if syms: return syms
        except Exception:
            pass
    return None

def load_universe() -> list[str]:
    hsx = hsx_universe_from_rs()
    if hsx:
        return hsx
    base = [str(s).strip().upper() for s in TECHNICAL_UNIVERSE if str(s).strip()]
    extra: list[str] = []
    if REM.exists():
        try:
            data = json.loads(REM.read_text(encoding='utf-8'))
            extra = [str(s).strip().upper() for s in data.get('symbols', []) if str(s).strip()]
        except Exception:
            extra = []
    out: list[str] = []
    for sym in base + extra:
        if sym and sym not in out:
            out.append(sym)
    return out


def load_partial() -> tuple[list[dict], list[dict]]:
    if not TMP.exists():
        return [], []
    try:
        data = json.loads(TMP.read_text(encoding='utf-8'))
        return data.get('items', []), data.get('errors', [])
    except Exception:
        return [], []


def save(items: list[dict], errors: list[dict], universe: list[str], final: bool = False) -> None:
    payload = {
        'createdAt': datetime.now().isoformat(),
        'universe': 'VN100 local universe',
        'method': 'Monthly technical indicator cache from monthly OHLC. Web reads output only. MA row uses MA10/20/50.',
        'universeCount': len(universe),
        'count': len(items),
        'errorCount': len(errors),
        'items': items,
        'errors': errors,
    }
    (OUT if final else TMP).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def r(value, digits=2):
    try:
        if value is None or pd.isna(value):
            return None
        return round(float(value), digits)
    except Exception:
        return None


def monthly_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work['time'] = pd.to_datetime(work['time'])
    work = work.sort_values('time').set_index('time')
    agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    if 'volume' in work.columns:
        agg['volume'] = 'sum'
    mo = work.resample('ME').agg(agg).dropna(subset=['open', 'high', 'low', 'close']).reset_index()
    return mo


def run_symbol(sym: str) -> tuple[dict | None, str | None]:
    df = _load_history(sym)
    if df is None or df.empty:
        return None, 'missing history'
    mo = monthly_ohlc(df)
    if len(mo) < 10:
        return None, f'insufficient monthly history {len(mo)}'
    ind = _compute_indicators(mo.copy())
    close = pd.to_numeric(ind['close'], errors='coerce')
    ind['ma10'] = close.rolling(10).mean()
    bb10_mid = close.rolling(10).mean()
    bb10_std = close.rolling(10).std()
    ind['bb10Upper'] = bb10_mid + bb10_std * 2
    ind['bb10Lower'] = bb10_mid - bb10_std * 2
    ind['bb10Middle'] = bb10_mid
    ind['bb10Percent'] = (close - ind['bb10Lower']) / (ind['bb10Upper'] - ind['bb10Lower']).replace(0, float('nan'))
    row = ind.iloc[-1]
    item = {
        'symbol': sym,
        'date': str(pd.to_datetime(row.get('time')).date()),
        'monthlyBars': len(mo),
        'rsi14Month': r(row.get('rsi14')),
        'adx14Month': r(row.get('adx14')),
        'plusDiMonth': r(row.get('plusDi')),
        'minusDiMonth': r(row.get('minusDi')),
        'ma10Month': r(row.get('ma10')),
        'ma20Month': r(row.get('ma20')),
        'ma50Month': r(row.get('ma50')),
        'bbUpperMonth': r(row.get('bbUpper') if r(row.get('bbUpper')) is not None else row.get('bb10Upper')),
        'bbLowerMonth': r(row.get('bbLower') if r(row.get('bbLower')) is not None else row.get('bb10Lower')),
        'bbMiddleMonth': r(row.get('bbMiddle') if r(row.get('bbMiddle') if 'bbMiddle' in row else row.get('bbMid')) is not None else row.get('bb10Middle')),
        'bbPercentMonth': r(row.get('bbPercent') if r(row.get('bbPercent'), 3) is not None else row.get('bb10Percent'), 3),
        'macdMonth': r(row.get('macd'), 4),
        'signalMonth': r(row.get('signal'), 4),
        'histogramMonth': r(row.get('histogram'), 4),
    }
    return item, None


def main() -> None:
    universe = load_universe()
    items, errors = load_partial()
    done = {x.get('symbol') for x in items} | {x.get('symbol') for x in errors}
    calls = 0
    print('monthly universe', len(universe), 'already done', len(done), flush=True)
    for sym in universe:
        if sym in done:
            print(sym, 'SKIP', flush=True)
            continue
        if calls and calls % SLEEP_EVERY == 0:
            print('sleep', SLEEP_SECONDS, 'seconds for rate limit', flush=True)
            time.sleep(SLEEP_SECONDS)
        try:
            item, err = run_symbol(sym)
            calls += 1
            if item:
                items.append(item)
                print(sym, 'OK', item.get('ma10Month'), item.get('ma20Month'), item.get('ma50Month'), 'bars', item.get('monthlyBars'), flush=True)
            else:
                errors.append({'symbol': sym, 'error': err})
                print(sym, 'ERR', err, flush=True)
        except Exception as exc:
            errors.append({'symbol': sym, 'error': repr(exc)})
            print(sym, 'ERR', repr(exc), flush=True)
        save(items, errors, universe, final=False)
    save(items, errors, universe, final=True)
    print('saved', OUT, 'count', len(items), 'errors', len(errors), flush=True)


if __name__ == '__main__':
    main()
