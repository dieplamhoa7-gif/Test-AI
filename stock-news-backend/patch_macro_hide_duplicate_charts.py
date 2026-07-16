import json
import re
from pathlib import Path

PAGES=[Path('firebase_public/macro.html')]
HIDE_KEYS={
    'policy': 'duplicate of mp_policy_refi / LS tái cấp vốn',
    'gdp_growth': 'duplicate of gdp_growth_q_ff / forward-filled quarterly GDP YoY',
    'omo_net': 'duplicate of mp_reverse_repo_net / Reverse Repo net',
}
STAMP='LH_MACRO_HIDE_DUPLICATES_20260716_1640'

for p in PAGES:
    s=p.read_text(encoding='utf-8',errors='ignore')
    m=re.search(r'const DATA=(\{.*?\});\n',s,re.S)
    if not m:
        raise SystemExit(f'No DATA in {p}')
    data=json.loads(m.group(1))
    indicators=data.get('indicators',{})
    for key, reason in HIDE_KEYS.items():
        if key not in indicators:
            raise SystemExit(f'Missing key {key}')
        indicators[key]['group']='_hidden'
        indicators[key]['hiddenReason']=reason
    new='const DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n'
    s=s[:m.start()]+new+s[m.end():]
    if STAMP not in s:
        s=s.replace('<head>','<head>\n<!-- '+STAMP+' -->',1)
    p.write_text(s,encoding='utf-8')

# verify
s=Path('firebase_public/macro.html').read_text(encoding='utf-8',errors='ignore')
m=re.search(r'const DATA=(\{.*?\});\n',s,re.S)
d=json.loads(m.group(1))
vis=[k for k,v in d['indicators'].items() if v.get('group')!='_hidden']
hid=[k for k,v in d['indicators'].items() if v.get('group')=='_hidden']
print('visible',len(vis),'hidden',len(hid),hid)
for k in HIDE_KEYS:
    print(k,d['indicators'][k].get('group'),d['indicators'][k].get('hiddenReason'))
