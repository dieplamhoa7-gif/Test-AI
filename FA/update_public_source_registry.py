import json
from pathlib import Path
p=Path('data/source_registry.json')
reg=json.loads(p.read_text(encoding='utf-8'))
for s in reg.get('sources',[]):
    if s.get('id')=='fiinprox_manual':
        s['role']='manual_backfill_crosscheck'
        s['priority']='fallback_not_primary'
        s['notes']='Manual/premium source. Use for rich historical backfill and fields not covered by public sources; do not depend on it for daily automation.'
# add/ensure public replacement notes
reg['publicReplacementPlan']='FA/PUBLIC_MACRO_SOURCE_REPLACEMENT_PLAN.md'
reg['sourcePriority']=[
    'vcb_fx_xml','yfinance_global','vnstock_market','sbv_interbank','pinetree_morning_brief','worldbank_macro','fiinprox_manual','paid_placeholder_widata','paid_placeholder_tradingeconomics'
]
p.write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
print('updated',p)
