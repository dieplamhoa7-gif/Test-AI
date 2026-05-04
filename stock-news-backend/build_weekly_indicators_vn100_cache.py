from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from app.market_data import _load_history, _compute_indicators
from app.technical_filters import TECHNICAL_UNIVERSE

OUT = Path('data/weekly_indicators_vn100_cache.json')
TMP = Path('data/weekly_indicators_vn100_cache.partial.json')
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
        'method': 'Weekly technical indicator cache from weekly OHLC. Web reads output only.',
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


def weekly_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work['time'] = pd.to_datetime(work['time'])
    work = work.sort_values('time').set_index('time')
    agg = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}
    if 'volume' in work.columns:
        agg['volume'] = 'sum'
    wk = work.resample('W-FRI').agg(agg).dropna(subset=['open', 'high', 'low', 'close']).reset_index()
    return wk


def run_symbol(sym: str) -> tuple[dict | None, str | None]:
    df = _load_history(sym)
    if df is None or df.empty:
        return None, 'missing history'
    wk = weekly_ohlc(df)
    if len(wk) < 20:
        return None, f'insufficient weekly history {len(wk)}'
    ind = _compute_indicators(wk.copy())
    ind['ma10'] = pd.to_numeric(ind['close'], errors='coerce').rolling(10).mean()
    row = ind.iloc[-1]
    item = {
        'symbol': sym,
        'date': str(pd.to_datetime(row.get('time')).date()),
        'weeklyBars': len(wk),
        'rsi14Week': r(row.get('rsi14')),
        'adx14Week': r(row.get('adx14')),
        'plusDiWeek': r(row.get('plusDi')),
        'minusDiWeek': r(row.get('minusDi')),
        'ma10Week': r(row.get('ma10')),
        'ma20Week': r(row.get('ma20')),
        'ma50Week': r(row.get('ma50')),
        'ma200Week': r(row.get('ma200')),
        'bbUpperWeek': r(row.get('bbUpper')),
        'bbLowerWeek': r(row.get('bbLower')),
        'bbMiddleWeek': r(row.get('bbMiddle') if 'bbMiddle' in row else row.get('bbMid')),
        'bbPercentWeek': r(row.get('bbPercent'), 3),
        'macdWeek': r(row.get('macd'), 4),
        'signalWeek': r(row.get('signal'), 4),
        'histogramWeek': r(row.get('histogram'), 4),
    }
    return item, None


def main() -> None:
    universe = load_universe()
    items, errors = load_partial()
    done = {x.get('symbol') for x in items} | {x.get('symbol') for x in errors}
    calls = 0
    print('weekly universe', len(universe), 'already done', len(done), flush=True)
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
                print(sym, 'OK', item.get('ma20Week'), item.get('ma50Week'), item.get('ma200Week'), 'bars', item.get('weeklyBars'), flush=True)
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
