from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

DATA = Path('data')
OUT = DATA / 'lh_canonical_indicators_daily.json'

SOURCES = {
    'dailyV3': DATA / 'v3_full_indicator_cache_v2.json',
    'rsVn100': DATA / 'rs_levels_vn100_cache.json',
    'rsHsxAll': DATA / 'rs_levels_hsx_all_cache.json',
    'hourly': DATA / 'hourly_indicators_vn100_cache.json',
    'weekly': DATA / 'weekly_indicators_vn100_cache.json',
    'monthly': DATA / 'monthly_indicators_vn100_cache.json',
    'core12': DATA / 'core12_ml_sr_full_universe.json',
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return {'_loadError': repr(exc)}


def items_by_symbol(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get('items') or []:
        sym = str(row.get('symbol') or row.get('ticker') or '').strip().upper()
        if sym:
            out[sym] = row
    return out


def core12_by_symbol(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    rows = payload.get('items') or payload.get('rows') or []
    for row in rows:
        sym = str(row.get('symbol') or row.get('ticker') or '').strip().upper()
        if sym:
            out[sym] = row
    return out


def clean_source_meta(name: str, payload: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        'name': name,
        'path': str(path),
        'exists': path.exists(),
        'createdAt': payload.get('createdAt') or payload.get('updatedAt'),
        'count': payload.get('count') or len(payload.get('items') or payload.get('rows') or []),
        'errorCount': payload.get('errorCount'),
        'loadError': payload.get('_loadError'),
    }


def main() -> None:
    payloads = {name: load_json(path) for name, path in SOURCES.items()}
    daily = items_by_symbol(payloads['dailyV3'])
    rs_vn100 = items_by_symbol(payloads['rsVn100'])
    rs_hsx = items_by_symbol(payloads['rsHsxAll'])
    hourly = items_by_symbol(payloads['hourly'])
    weekly = items_by_symbol(payloads['weekly'])
    monthly = items_by_symbol(payloads['monthly'])
    core12 = core12_by_symbol(payloads['core12'])

    symbols = sorted(set().union(daily, rs_vn100, rs_hsx, hourly, weekly, monthly, core12))
    items = []
    for sym in symbols:
        d = daily.get(sym, {})
        indicators = d.get('indicators') or {}
        rs = d.get('rs') or rs_vn100.get(sym) or rs_hsx.get(sym) or {}
        item = {
            'symbol': sym,
            'date': d.get('date') or weekly.get(sym, {}).get('date') or monthly.get(sym, {}).get('date'),
            'price': d.get('price') or rs.get('price') or rs.get('lastClose'),
            'daily': indicators,
            'rs': rs,
            'hourly': hourly.get(sym),
            'weekly': weekly.get(sym),
            'monthly': monthly.get(sym),
            'core12': core12.get(sym),
            'raw': {
                'dailyV3': d or None,
            },
        }
        items.append(item)

    out = {
        'createdAt': datetime.now().isoformat(),
        'schemaVersion': 'lh-canonical-indicators-daily.v1',
        'note': 'Canonical daily indicator/feature store. Strategies should read this single output instead of recomputing indicators/R-S/timeframes.',
        'sources': [clean_source_meta(name, payloads[name], SOURCES[name]) for name in SOURCES],
        'count': len(items),
        'items': items,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'count': len(items), 'sources': out['sources']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
