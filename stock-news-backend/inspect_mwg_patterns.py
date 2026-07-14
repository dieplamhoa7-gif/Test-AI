import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open('firebase_public/data/pattern_reco_cache.json',encoding='utf-8'))
for it in d['items']:
    if it['symbol']=='MWG':
        pats=[p for p in it['patterns'] if 'double' in p['type'] or 'triple' in p['type']]
        print('MWG', len(pats))
        for p in pats[:8]: print(p['type'], p['score'], p['confidence'], p.get('status'), p['evidence']['notes'])
