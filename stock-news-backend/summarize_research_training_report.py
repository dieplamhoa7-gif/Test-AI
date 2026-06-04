#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'data'/'research_feature_training_report.json').read_text(encoding='utf-8'))
lines=[]
lines.append('# Research Feature Training Report — VN100')
lines.append('')
lines.append(f"Created: {r['createdAt']}")
lines.append(f"Rows: {r['rows']:,}")
lines.append(f"Rows with 20d label: {r['trainRowsWith20dLabel']:,}")
lines.append('')
lines.append('## Top feature observations vs futureReturn20d')
lines.append('')
for f in r['featureReport'][:12]:
    lines.append(f"- **{f['feature']}**: Spearman {f['spearmanFutureReturn20d']}; top20 avg {f['topQuintileAvgReturn20d']}; bottom20 avg {f['bottomQuintileAvgReturn20d']}; spread {f['spreadTopMinusBottom']}; hit6 top/bottom {f['topQuintileHit6Pct20d']} / {f['bottomQuintileHit6Pct20d']}")
lines.append('')
lines.append('## Interpretation')
lines.append('')
lines.append('- `sr_distSupportPct` âm khá rõ: càng xa hỗ trợ gần nhất thì future return 20d càng kém; nhóm gần hỗ trợ có avg return tốt hơn. Điều này ủng hộ hướng support-rebound/touch-zone nhưng cần kiểm OOS kỹ vì support hiện đang dùng snapshot pattern mới nhất, cần phiên bản rolling để production không leak.')
lines.append('- `sr_distResistancePct` dương khá rõ: còn nhiều room tới kháng cự thì future return tốt hơn; nếu sát kháng cự thì kém hơn. Đây là feature hợp lý cho risk/reward.')
lines.append('- Volatility (`atrPct`, `realizedVol20`) có tương quan âm nhẹ với future return trung bình, nhưng hit target 6% ở top vol lại cao hơn; nghĩa là vol cao có nhiều cơ hội chạy mạnh nhưng return trung bình/risk xấu hơn. Nên dùng vol cho sizing/risk, không đơn giản loại bỏ.')
lines.append('- Pattern score hiện có tín hiệu yếu hơn S/R distance. Pattern nên dùng như overlay/confluence, chưa nên làm tín hiệu chính nếu chưa có rolling backtest.')
lines.append('')
lines.append('## High-correlation feature pairs')
lines.append('')
for p in r['highCorrelationPairs'][:20]:
    lines.append(f"- {p['a']} ↔ {p['b']}: {p['spearman']}")
lines.append('')
lines.append('## Regime summary')
lines.append('')
for g in r['regimeSummary']:
    lines.append(f"- {g['group']}={g['value']}: n={g['n']}, avg20d={g['avgReturn20d']}, hit6={g['hit6Pct20d']}, avgDD={g['avgDrawdown20d']}")
lines.append('')
lines.append('## Next steps')
lines.append('')
lines.append('1. Fix potential leakage for S/R/pattern: build rolling pattern/SR features at each date, not latest snapshot only.')
lines.append('2. Backtest explicit strategies using these features: near-support + room-to-resistance + volatility filter.')
lines.append('3. Build feature correlation/PCA grouping to reduce duplicate indicators.')
lines.append('4. Add expected value metrics into strategy cache.')
lines.append('5. Only after OOS checks, consider simple ML probability model.')

out=ROOT/'reports'/'research_feature_training_report_vn100.md'
out.parent.mkdir(exist_ok=True)
out.write_text('\n'.join(lines),encoding='utf-8')
print(out)
