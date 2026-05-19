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


def _first(values: list[Any], default: Any = None) -> Any:
    for v in values:
        if v is not None:
            return v
    return default


def build_preferred_indicators(daily: dict[str, Any], rs: dict[str, Any], core12: dict[str, Any] | None) -> dict[str, Any]:
    """Preferred production indicators.

    If Core12 has an overlapping indicator family, prefer Core12 feature values
    because they are tuned/selected by the Core12 ML config. Keep raw daily/R-S
    under `daily` and `rs` for audit/debug.
    """
    cvals = (core12 or {}).get('core12Values') or {}
    rsi = cvals.get('RSI') or {}
    adx = cvals.get('ADX_DMI') or {}
    roc = cvals.get('ROC_MOMENTUM') or {}
    ichi = cvals.get('ICHIMOKU') or {}
    ma = cvals.get('MA_EMA_WMA') or {}
    vwap = cvals.get('VWAP_VWMA') or {}
    sr = cvals.get('SR_CLUSTER') or {}
    mfi = cvals.get('MFI_CMF') or {}
    pvi = cvals.get('PVI_NVI') or {}
    trix = cvals.get('TRIX') or {}
    st = cvals.get('SUPERTREND') or {}

    preferred = dict(daily or {})
    source_map: dict[str, str] = {}

    def put(key: str, value: Any, source: str) -> None:
        if value is not None:
            preferred[key] = value
            source_map[key] = source

    # Overlap families: prefer Core12 tuned periods when present.
    # Also overwrite compatible public keys when the parameter difference is not material
    # for strategy direction/score. Large horizon changes keep explicit `*Preferred` keys.
    put('rsiPreferred', _first([rsi.get('RSI24'), rsi.get('RSI50'), daily.get('rsi14')]), 'core12.RSI' if rsi else 'daily.rsi14')
    put('rsiSlope5Preferred', _first([rsi.get('RSI24_slope5'), rsi.get('RSI50_slope5')]), 'core12.RSI')
    if rsi.get('RSI24') is not None:
        put('rsi14', rsi.get('RSI24'), 'core12.RSI24 replaces daily.rsi14')
    put('adxPreferred', _first([adx.get('ADX41'), daily.get('adx14')]), 'core12.ADX_DMI' if adx else 'daily.adx14')
    put('diSpreadPreferred', _first([adx.get('DI41_spread')]), 'core12.ADX_DMI')
    if adx.get('ADX41') is not None:
        put('adx14', adx.get('ADX41'), 'core12.ADX41 replaces daily.adx14')
    if adx.get('DI41_spread') is not None:
        spread = adx.get('DI41_spread')
        put('plusDi', max(float(spread), 0.0), 'core12.DI41_spread direction replaces daily.plusDi')
        put('minusDi', max(-float(spread), 0.0), 'core12.DI41_spread direction replaces daily.minusDi')
    put('rocPreferred', _first([roc.get('ROC52'), roc.get('ROC72'), roc.get('ROC80'), roc.get('ROC90'), daily.get('roc20')]), 'core12.ROC_MOMENTUM' if roc else 'daily.roc20')
    if roc.get('ROC52') is not None:
        put('roc20', roc.get('ROC52'), 'core12.ROC52 replaces daily.roc20 for momentum direction')
    put('momentumPreferred', _first([roc.get('MOM72'), roc.get('MOM80'), roc.get('MOM90'), roc.get('MOM52')]), 'core12.ROC_MOMENTUM')
    put('ichimokuCloudPreferred', ichi.get('ICHI5_29_89_cloud_pos'), 'core12.ICHIMOKU')
    put('ichimokuTkPreferred', ichi.get('ICHI5_29_89_tk'), 'core12.ICHIMOKU')
    if ichi:
        old_ichi = preferred.get('ichimoku') if isinstance(preferred.get('ichimoku'), dict) else {}
        core_state_raw = ichi.get('ICHI5_29_89_cloud_pos')
        if isinstance(core_state_raw, (int, float)):
            core_state = 'above_cloud' if core_state_raw > 0 else 'below_cloud' if core_state_raw < 0 else 'in_cloud'
        else:
            core_state = old_ichi.get('state')
        put('ichimoku', {**old_ichi, 'state': core_state, 'core12CloudPos': core_state_raw, 'core12Tk': ichi.get('ICHI5_29_89_tk'), 'source': 'core12.ICHIMOKU'}, 'core12.ICHIMOKU replaces daily.ichimoku state')
    put('maTrendPreferred', _first([ma.get('MA108_dist'), ma.get('EMA229_dist')]), 'core12.MA_EMA_WMA')
    put('maTrendSlope5Preferred', _first([ma.get('MA108_slope5'), ma.get('EMA229_slope5')]), 'core12.MA_EMA_WMA')
    put('vwapPreferred', _first([vwap.get('VWAP60_dist'), vwap.get('VWAP75_dist'), vwap.get('VWAP98_dist'), daily.get('vwapDay')]), 'core12.VWAP_VWMA' if vwap else 'daily.vwapDay')
    put('vwmaSlope5Preferred', _first([vwap.get('VWMA60_slope5'), vwap.get('VWMA75_slope5'), vwap.get('VWMA98_slope5')]), 'core12.VWAP_VWMA')
    if vwap.get('VWAP60_dist') is not None:
        put('vwapDay', vwap.get('VWAP60_dist'), 'core12.VWAP60_dist replaces daily.vwapDay as distance feature')
    put('mfiPreferred', _first([mfi.get('MFI20'), mfi.get('MFI60'), mfi.get('MFI61'), mfi.get('MFI73')]), 'core12.MFI_CMF')
    put('pviSlopePreferred', _first([pvi.get('PVI_slope63'), pvi.get('PVI_slope75')]), 'core12.PVI_NVI')
    put('nviSlopePreferred', _first([pvi.get('NVI_slope63'), pvi.get('NVI_slope75')]), 'core12.PVI_NVI')
    put('trixPreferred', _first([trix.get('TRIX38'), trix.get('TRIX58')]), 'core12.TRIX')
    put('trixSlope5Preferred', _first([trix.get('TRIX38_slope5'), trix.get('TRIX58_slope5')]), 'core12.TRIX')
    put('supertrendDirPreferred', st.get('ST15_5.0_dir'), 'core12.SUPERTREND')
    put('supertrendDistPreferred', st.get('ST15_5.0_dist'), 'core12.SUPERTREND')
    put('nearSupportPreferred', _first([sr.get('nearSupport'), rs.get('nearSupportDay')]), 'core12.SR_CLUSTER' if sr else 'rs.nearSupportDay')
    put('supportBrokenPreferred', sr.get('supportBroken'), 'core12.SR_CLUSTER')
    if sr.get('S1') is not None:
        put('supportPreferred', sr.get('S1'), 'core12.SR_CLUSTER')
        put('activeSupportDay', sr.get('S1'), 'core12.SR_CLUSTER.S1 replaces rs.activeSupportDay')
    elif rs.get('activeSupportDay') is not None:
        put('supportPreferred', rs.get('activeSupportDay'), 'rs.activeSupportDay')
    if sr.get('R1') is not None:
        put('resistancePreferred', sr.get('R1'), 'core12.SR_CLUSTER')
        put('activeResistanceDay', sr.get('R1'), 'core12.SR_CLUSTER.R1 replaces rs.activeResistanceDay')
    elif rs.get('activeResistanceDay') is not None:
        put('resistancePreferred', rs.get('activeResistanceDay'), 'rs.activeResistanceDay')

    preferred['_sourceMap'] = source_map
    return preferred


def core12_decision(core12: dict[str, Any] | None) -> dict[str, Any] | None:
    if not core12:
        return None
    keys = ['symbol', 'sectorGroup', 'configSector', 'task', 'date', 'close', 'currentZone', 'mlConfig', 'core12Signals', 'priceStatus', 'reason', 'core12Positive', 'core12Negative', 'core12Neutral', 'holdScore', 'breakRiskScore', 'finalStatus']
    return {k: core12.get(k) for k in keys if k in core12}


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
        c12 = core12.get(sym)
        item = {
            'symbol': sym,
            'date': d.get('date') or weekly.get(sym, {}).get('date') or monthly.get(sym, {}).get('date'),
            'price': d.get('price') or rs.get('price') or rs.get('lastClose'),
            'preferred': build_preferred_indicators(indicators, rs, c12),
            'daily': indicators,
            'rs': rs,
            'hourly': hourly.get(sym),
            'weekly': weekly.get(sym),
            'monthly': monthly.get(sym),
            'core12': core12_decision(c12),
            'raw': {
                'dailyV3': d or None,
                'core12Values': (c12 or {}).get('core12Values') if c12 else None,
            },
        }
        items.append(item)

    out = {
        'createdAt': datetime.now().isoformat(),
        'schemaVersion': 'lh-canonical-indicators-daily.v1',
        'note': 'Canonical daily indicator/feature store. Overlapping indicator families prefer Core12 tuned features in `preferred`; raw daily/R-S/Core12 values remain for audit.',
        'sources': [clean_source_meta(name, payloads[name], SOURCES[name]) for name in SOURCES],
        'count': len(items),
        'items': items,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(OUT), 'count': len(items), 'sources': out['sources']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
