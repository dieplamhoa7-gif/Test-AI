import json
from pathlib import Path

# Core sourced/public data used
shares_m = 1463.0
price = 70000.0
net_debt_bn = 7000.0  # still placeholder until BS is fully loaded

# MWG consolidated 2025 sourced from CafeF KQKD
mwg_rev_2025 = 155_928.145619367
mwg_pat_2025 = 7_072.622885875
mwg_patmi_2025 = 7_033.730770169
mwg_net_margin_2025 = mwg_pat_2025 / mwg_rev_2025

# BHX public inputs
bhx_rev_q1_2026 = 13_100.0
bhx_pat_q1_2026 = 400.0
bhx_margin_q1_2026 = bhx_pat_q1_2026 / bhx_rev_q1_2026
bhx_rev_2026 = 55_500.0
bhx_pat_2026 = 1_800.0
bhx_margin_2026 = bhx_pat_2026 / bhx_rev_2026

# DMX public inputs
# Q1/2026 PAT about 2,219 bn; annualized with haircut because Q1 often not full-year run-rate
# three run-rate factors for realism

def dmx_annual_pat(q1_pat, factor):
    return q1_pat * factor

# We now use earnings-based valuation first, then cross-check with IPO range.
# TGDD is valued conservatively as mature business using implied PAT slice and lower multiple.

cases = {
    'Bear': {
        'bhx_pe': 16.0,
        'bhx_ev_sales': 0.45,
        'dmx_q1_factor': 3.2,
        'dmx_pe': 10.0,
        'tgdd_pat': 900.0,
        'tgdd_pe': 8.0,
        'other_value': 2000.0,
    },
    'Base': {
        'bhx_pe': 20.0,
        'bhx_ev_sales': 0.55,
        'dmx_q1_factor': 3.5,
        'dmx_pe': 11.0,
        'tgdd_pat': 1100.0,
        'tgdd_pe': 9.0,
        'other_value': 2500.0,
    },
    'Bull': {
        'bhx_pe': 24.0,
        'bhx_ev_sales': 0.70,
        'dmx_q1_factor': 3.8,
        'dmx_pe': 12.0,
        'tgdd_pat': 1300.0,
        'tgdd_pe': 10.0,
        'other_value': 3000.0,
    },
}

out = {
    'price_used': price,
    'shares_m': shares_m,
    'net_debt_bn': net_debt_bn,
    'mwg_2025': {
        'rev_bn': mwg_rev_2025,
        'pat_bn': mwg_pat_2025,
        'patmi_bn': mwg_patmi_2025,
        'net_margin': mwg_net_margin_2025,
    },
    'bhx_public': {
        'rev_q1_2026_bn': bhx_rev_q1_2026,
        'pat_q1_2026_bn': bhx_pat_q1_2026,
        'margin_q1_2026': bhx_margin_q1_2026,
        'rev_2026_plan_bn': bhx_rev_2026,
        'pat_2026_plan_bn': bhx_pat_2026,
        'margin_2026_plan': bhx_margin_2026,
    },
    'cases': {}
}

for name, c in cases.items():
    bhx_sales_value = bhx_rev_2026 * c['bhx_ev_sales']
    bhx_pe_value = bhx_pat_2026 * c['bhx_pe']
    bhx_value = (bhx_sales_value + bhx_pe_value) / 2.0

    dmx_pat = dmx_annual_pat(2219.0, c['dmx_q1_factor'])
    dmx_value = dmx_pat * c['dmx_pe']

    tgdd_value = c['tgdd_pat'] * c['tgdd_pe']
    other_value = c['other_value']

    mwg_ev = bhx_value + dmx_value + tgdd_value + other_value
    mwg_equity = mwg_ev - net_debt_bn
    target_price = mwg_equity * 1000.0 / shares_m
    upside = target_price / price - 1.0

    out['cases'][name] = {
        'BHX': {
            'sales_value_bn': bhx_sales_value,
            'pe_value_bn': bhx_pe_value,
            'blended_value_bn': bhx_value,
        },
        'DMX': {
            'annualized_pat_bn': dmx_pat,
            'pe': c['dmx_pe'],
            'value_bn': dmx_value,
        },
        'TGDD': {
            'pat_assumption_bn': c['tgdd_pat'],
            'pe': c['tgdd_pe'],
            'value_bn': tgdd_value,
        },
        'Other': other_value,
        'MWG_EV_bn': mwg_ev,
        'MWG_equity_bn': mwg_equity,
        'TargetPrice': target_price,
        'Upside': upside,
    }

Path('mwg_refined_model_output.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

for name, v in out['cases'].items():
    print(name)
    print(' BHX value bn:', round(v['BHX']['blended_value_bn'],1))
    print(' DMX value bn:', round(v['DMX']['value_bn'],1), '| annualized PAT', round(v['DMX']['annualized_pat_bn'],1))
    print(' TGDD value bn:', round(v['TGDD']['value_bn'],1))
    print(' Other bn:', round(v['Other'],1))
    print(' MWG EV bn:', round(v['MWG_EV_bn'],1))
    print(' Target price:', round(v['TargetPrice'],0), '| Upside', f"{v['Upside']*100:.1f}%")
    print()
