from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime
import pandas as pd
from app.market_data import _load_history
from app.rs_levels import calc_rs_levels_only
from app.technical_filters import TECHNICAL_UNIVERSE

OUT=Path('data/rs_levels_vn100_cache.json')
TMP=Path('data/rs_levels_vn100_cache.partial.json')
REM=Path('data/vn100_remaining_symbols.json')
SLEEP_EVERY=18
SLEEP_SECONDS=65
MIN_HISTORY=30


def load_universe() -> list[str]:
    base=[str(s).strip().upper() for s in TECHNICAL_UNIVERSE if str(s).strip()]
    extra=[]
    if REM.exists():
        try:
            data=json.loads(REM.read_text(encoding='utf-8'))
            extra=[str(s).strip().upper() for s in data.get('symbols',[]) if str(s).strip()]
        except Exception:
            extra=[]
    universe=[]
    for s in base+extra:
        if s and s not in universe:
            universe.append(s)
    return universe


def load_partial():
    if not TMP.exists(): return [], []
    try:
        d=json.loads(TMP.read_text(encoding='utf-8'))
        return d.get('items',[]), d.get('errors',[])
    except Exception:
        return [], []


def save(items, errors, universe, final=False):
    payload={
        'createdAt':datetime.now().isoformat(),
        'universe':'VN100 local universe = TECHNICAL_UNIVERSE + data/vn100_remaining_symbols.json',
        'method':'R/S-only VN100 cache; calc_rs_levels_only with per-timeframe MA anchors; output-only for web',
        'universeCount':len(universe),
        'count':len(items),
        'errorCount':len(errors),
        'items':items,
        'errors':errors,
    }
    (OUT if final else TMP).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')


def _sticky_support_from_previous(sym: str, price: float, current: dict, previous_items: dict[str, dict]) -> dict:
    prev = previous_items.get(sym) or {}
    prev_support = prev.get('activeSupportDay') or prev.get('supportDay')
    if not prev_support:
        return current
    try:
        prev_support = float(prev_support)
        cur_support = float(current.get('activeSupportDay') or current.get('supportDay') or 0)
        atr = float(current.get('atr') or prev.get('atr') or max(price * 0.02, 0.01))
    except Exception:
        return current
    if not cur_support or cur_support >= prev_support:
        return current
    prev_zone = prev.get('supportZoneDay') if isinstance(prev.get('supportZoneDay'), list) else None
    if prev_zone and len(prev_zone) >= 2:
        zone_low = float(prev_zone[0]); zone_high = float(prev_zone[1])
    else:
        zone_low = prev_support - atr * 0.25; zone_high = prev_support + atr * 0.25
    breakdown_buffer = max(atr * 0.20, prev_support * 0.006)
    confirmed_breakdown = price < (zone_low - breakdown_buffer)
    if confirmed_breakdown:
        current['previousSupportDay'] = round(prev_support, 2)
        current['previousSupportZoneDay'] = [round(zone_low, 2), round(zone_high, 2)]
        current['supportTransitionDay'] = 'confirmed_breakdown_to_lower_support'
        return current
    # Price is still testing/holding the previous support zone; keep old active support.
    current['computedSupportDay'] = current.get('supportDay')
    current['computedActiveSupportDay'] = current.get('activeSupportDay')
    current['supportDay'] = round(prev_support, 2)
    current['activeSupportDay'] = round(prev_support, 1)
    current['supportZoneDay'] = [round(zone_low, 2), round(zone_high, 2)]
    current['srStatusDay'] = 'Đang test hỗ trợ cũ' if price >= zone_low else 'Cảnh báo sát vùng thủng hỗ trợ cũ'
    levels = current.get('supportLevelsDay') or []
    merged = [round(prev_support, 1)] + [x for x in levels if abs(float(x) - prev_support) > 0.15]
    current['supportLevelsDay'] = merged[:5]
    current['nextSupportDay'] = round(cur_support, 1)
    current['supportTransitionDay'] = 'kept_previous_support_until_breakdown_confirmed'
    return current


def run_symbol(sym:str, previous_items: dict[str, dict] | None = None):
    df=_load_history(sym)
    if df is None or df.empty: return None,'missing history'
    df=df.copy(); df['time']=pd.to_datetime(df['time']); df=df.sort_values('time').reset_index(drop=True)
    if len(df)<MIN_HISTORY: return None,f'insufficient history {len(df)}'
    last=df.iloc[-1]; price=float(last['close'])
    rs=calc_rs_levels_only(price,float(last.get('open',price)),float(last.get('open',price)),float(last.get('high',price)),float(last.get('low',price)),price,df)
    rs=_sticky_support_from_previous(sym, price, rs, previous_items or {})
    return {'symbol':sym,'date':str(last['time'].date()),'price':round(price,2),**rs},None


def main():
    universe=load_universe(); previous_items={x.get('symbol'):x for x in (json.loads(OUT.read_text(encoding='utf-8')).get('items',[]) if OUT.exists() else [])}
    items, errors=load_partial()
    done={x.get('symbol') for x in items}|{x.get('symbol') for x in errors}
    calls=0
    print('VN100 universe',len(universe),'already done',len(done),flush=True)
    for sym in universe:
        if sym in done:
            print(sym,'SKIP',flush=True); continue
        if calls and calls % SLEEP_EVERY == 0:
            print('sleep',SLEEP_SECONDS,'seconds for rate limit',flush=True); time.sleep(SLEEP_SECONDS)
        try:
            item,err=run_symbol(sym, previous_items); calls+=1
            if item:
                items.append(item); print(sym,'OK',item.get('activeSupportWeek'),item.get('activeResistanceWeek'),item.get('activeSupportMonth'),item.get('activeResistanceMonth'),flush=True)
            else:
                errors.append({'symbol':sym,'error':err}); print(sym,'ERR',err,flush=True)
        except Exception as e:
            errors.append({'symbol':sym,'error':repr(e)}); print(sym,'ERR',repr(e),flush=True)
        save(items,errors,universe,final=False)
    save(items,errors,universe,final=True)
    print('saved',OUT,'universe',len(universe),'count',len(items),'errors',len(errors),flush=True)

if __name__=='__main__': main()
