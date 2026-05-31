import json
from pathlib import Path

# Public/sourced inputs gathered in-session
shares_m = 1463.0          # million shares
price = 70000.0            # VND/share (model current placeholder; update if needed)
net_debt_bn = 7000.0       # VND bn placeholder from model until BS tied out
mwg_market_cap_bn = shares_m * price / 1000.0
mwg_ev_bn = mwg_market_cap_bn + net_debt_bn

# CafeF sourced / public narrative inputs
bhx_rev_2026_bn = 55500.0      # CafeF article says BHX planned revenue ~55.5k bn in 2026
bhx_profit_2026_bn = 1800.0    # CafeF article says BHX planned profit ~1.8k bn in 2026
bhx_margin_2026 = bhx_profit_2026_bn / bhx_rev_2026_bn

bhx_rev_q1_2026_bn = 13100.0   # CafeF article
bhx_profit_q1_2026_bn = 400.0  # public article says gần 400 tỷ
bhx_margin_q1_2026 = bhx_profit_q1_2026_bn / bhx_rev_q1_2026_bn

# DMX sourced / public narrative inputs
# Q1/2026 LNST about 2,219 bn, revenue and profit +30%/+49% YoY. 2026-2030 CAGR revenue 11%.
dmx_profit_q1_2026_bn = 2219.0
# IPO-related base valuation from public article / model placeholder range
# Use scenario valuations because exact prospectus financials not fully loaded yet.
dmx_val_bear_bn = 32000.0
dmx_val_base_bn = 45000.0
dmx_val_bull_bn = 60000.0

# BHX valuation scenarios using both sales multiple and earnings cross-check
bhx_sales_mult = {'bear':0.50,'base':0.65,'bull':0.80}
bhx_pe = {'bear':18.0,'base':22.0,'bull':26.0}

rows = {}
for case in ['bear','base','bull']:
    bhx_ev_sales = bhx_rev_2026_bn * bhx_sales_mult[case]
    bhx_equity_pe = bhx_profit_2026_bn * bhx_pe[case]
    bhx_value_bn = (bhx_ev_sales + bhx_equity_pe) / 2.0
    dmx_value_bn = {'bear':dmx_val_bear_bn,'base':dmx_val_base_bn,'bull':dmx_val_bull_bn}[case]
    implied_tgdd_other_bn = mwg_ev_bn - bhx_value_bn - dmx_value_bn
    rows[case] = {
        'MWG_market_cap_bn': mwg_market_cap_bn,
        'MWG_EV_bn': mwg_ev_bn,
        'BHX_rev_2026_bn': bhx_rev_2026_bn,
        'BHX_profit_2026_bn': bhx_profit_2026_bn,
        'BHX_margin_2026': bhx_margin_2026,
        'BHX_ev_sales_bn': bhx_ev_sales,
        'BHX_equity_pe_bn': bhx_equity_pe,
        'BHX_valuation_bn': bhx_value_bn,
        'BHX_pct_of_MWG_EV': bhx_value_bn / mwg_ev_bn,
        'DMX_valuation_bn': dmx_value_bn,
        'DMX_pct_of_MWG_EV': dmx_value_bn / mwg_ev_bn,
        'TGDD_plus_other_implied_bn': implied_tgdd_other_bn,
        'TGDD_plus_other_pct_of_MWG_EV': implied_tgdd_other_bn / mwg_ev_bn,
    }

summary = {
    'inputs': {
        'shares_m': shares_m,
        'price_vnd_per_share': price,
        'net_debt_bn': net_debt_bn,
        'MWG_market_cap_bn': mwg_market_cap_bn,
        'MWG_EV_bn': mwg_ev_bn,
        'BHX_margin_q1_2026': bhx_margin_q1_2026,
        'BHX_margin_2026_plan': bhx_margin_2026,
        'DMX_profit_q1_2026_bn': dmx_profit_q1_2026_bn,
    },
    'scenarios': rows,
    'notes': [
        'BHX revenue/profit 2026 plan from public CafeF article cited in chat.',
        'BHX Q1 2026 revenue/profit from public CafeF article cited in chat.',
        'DMX exact full-year standalone financials not fully loaded; valuation shown as scenario range anchored to IPO-related public narrative and prior base placeholders.',
        'MWG EV uses price 70,000 and net debt 7,000 bn from current model placeholders; update these for live-accurate output.',
        'This is a public-input SOTP approximation, not audited final fairness value.'
    ]
}

Path('mwg_sotp_public_output.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

for case,data in rows.items():
    print(case.upper())
    print(' MWG EV bn           :', round(data['MWG_EV_bn'],1))
    print(' BHX valuation bn    :', round(data['BHX_valuation_bn'],1), f"({data['BHX_pct_of_MWG_EV']*100:.1f}% EV)")
    print(' DMX valuation bn    :', round(data['DMX_valuation_bn'],1), f"({data['DMX_pct_of_MWG_EV']*100:.1f}% EV)")
    print(' TGDD+other implied  :', round(data['TGDD_plus_other_implied_bn'],1), f"({data['TGDD_plus_other_pct_of_MWG_EV']*100:.1f}% EV)")
    print()
print('Saved mwg_sotp_public_output.json')
