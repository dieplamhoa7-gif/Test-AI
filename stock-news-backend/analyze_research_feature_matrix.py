#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PUBLIC = ROOT / 'firebase_public' / 'data'

FEATURES = [
    ('trend.ret5', 'trend_ret5'),
    ('trend.ret20', 'trend_ret20'),
    ('trend.ret60', 'trend_ret60'),
    ('trend.ma20Slope20', 'trend_ma20Slope20'),
    ('trend.ma50Slope20', 'trend_ma50Slope20'),
    ('trend.priceVsMa20Pct', 'trend_priceVsMa20Pct'),
    ('trend.priceVsMa50Pct', 'trend_priceVsMa50Pct'),
    ('momentum.rsi14', 'momentum_rsi14'),
    ('momentum.macdHist', 'momentum_macdHist'),
    ('momentum.macdHistSlope3', 'momentum_macdHistSlope3'),
    ('volume.volumeRatio20', 'volume_volumeRatio20'),
    ('volatility.atrPct', 'volatility_atrPct'),
    ('volatility.realizedVol20', 'volatility_realizedVol20'),
    ('volatility.bbWidth20', 'volatility_bbWidth20'),
    ('sr.distSupportPct', 'sr_distSupportPct'),
    ('sr.distResistancePct', 'sr_distResistancePct'),
    ('pattern.biasStrength', 'pattern_biasStrength'),
    ('pattern.bullScore', 'pattern_bullScore'),
    ('pattern.bearScore', 'pattern_bearScore'),
    ('pattern.topPatternScore', 'pattern_topPatternScore'),
]


def get(d, path):
    cur = d
    for p in path.split('.'):
        if not isinstance(cur, dict): return None
        cur = cur.get(p)
    return cur


def main():
    payload = json.loads((DATA/'research_feature_matrix_vn100.json').read_text(encoding='utf-8'))
    rows = []
    for item in payload['rows']:
        row = {'symbol': item['symbol'], 'date': item['date']}
        labels = item.get('labels', {})
        row['futureReturn20d'] = labels.get('futureReturn20d')
        row['futureMaxDrawdown20d'] = labels.get('futureMaxDrawdown20d')
        row['hitTarget6Pct20d'] = labels.get('hitTarget6Pct20d')
        row['symbolRegime'] = get(item, 'market.symbolRegime')
        row['volRegime'] = get(item, 'volatility.volRegime')
        row['patternBias'] = get(item, 'pattern.bias')
        for path, name in FEATURES:
            row[name] = get(item, path)
        rows.append(row)
    df = pd.DataFrame(rows)
    for c in [name for _, name in FEATURES] + ['futureReturn20d', 'futureMaxDrawdown20d']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    train = df[df['futureReturn20d'].notna()].copy()

    # Correlation with 20d future return
    feature_report = []
    for _, name in FEATURES:
        sub = train[[name, 'futureReturn20d', 'hitTarget6Pct20d']].dropna()
        if len(sub) < 200:
            continue
        corr = sub[name].corr(sub['futureReturn20d'], method='spearman')
        # top quintile vs bottom quintile
        try:
            q80 = sub[name].quantile(0.8); q20 = sub[name].quantile(0.2)
            top = sub[sub[name] >= q80]; bot = sub[sub[name] <= q20]
            top_ret = top['futureReturn20d'].mean(); bot_ret = bot['futureReturn20d'].mean()
            top_hit = top['hitTarget6Pct20d'].mean(); bot_hit = bot['hitTarget6Pct20d'].mean()
        except Exception:
            top_ret = bot_ret = top_hit = bot_hit = None
        feature_report.append({
            'feature': name,
            'n': int(len(sub)),
            'spearmanFutureReturn20d': round(float(corr), 4) if pd.notna(corr) else None,
            'topQuintileAvgReturn20d': round(float(top_ret), 4) if pd.notna(top_ret) else None,
            'bottomQuintileAvgReturn20d': round(float(bot_ret), 4) if pd.notna(bot_ret) else None,
            'topQuintileHit6Pct20d': round(float(top_hit), 4) if pd.notna(top_hit) else None,
            'bottomQuintileHit6Pct20d': round(float(bot_hit), 4) if pd.notna(bot_hit) else None,
            'spreadTopMinusBottom': round(float(top_ret - bot_ret), 4) if pd.notna(top_ret) and pd.notna(bot_ret) else None,
        })
    feature_report = sorted(feature_report, key=lambda x: abs(x.get('spearmanFutureReturn20d') or 0), reverse=True)

    # Feature correlation high pairs
    corr_df = train[[name for _, name in FEATURES]].corr(method='spearman')
    pairs = []
    cols = list(corr_df.columns)
    for i,a in enumerate(cols):
        for b in cols[i+1:]:
            v = corr_df.loc[a,b]
            if pd.notna(v) and abs(v) >= 0.75:
                pairs.append({'a': a, 'b': b, 'spearman': round(float(v),4)})
    pairs = sorted(pairs, key=lambda x: abs(x['spearman']), reverse=True)

    # Regime summary
    regimes = []
    for col in ['symbolRegime', 'volRegime', 'patternBias']:
        for val, g in train.groupby(col, dropna=True):
            regimes.append({
                'group': col,
                'value': str(val),
                'n': int(len(g)),
                'avgReturn20d': round(float(g['futureReturn20d'].mean()),4),
                'hit6Pct20d': round(float(g['hitTarget6Pct20d'].mean()),4),
                'avgDrawdown20d': round(float(g['futureMaxDrawdown20d'].mean()),4),
            })

    out = {
        'createdAt': datetime.now(timezone.utc).isoformat(),
        'source': 'data/research_feature_matrix_vn100.json',
        'rows': int(len(df)),
        'trainRowsWith20dLabel': int(len(train)),
        'featureReport': feature_report,
        'highCorrelationPairs': pairs[:80],
        'regimeSummary': regimes,
        'note': 'Exploratory feature training report. Correlation is not causation; use OOS/walk-forward before trusting.',
    }
    for p in [DATA/'research_feature_training_report.json', PUBLIC/'research_feature_training_report.json']:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
        print('wrote', p)
    print('top features')
    for f in feature_report[:10]:
        print(f)

if __name__ == '__main__':
    main()
