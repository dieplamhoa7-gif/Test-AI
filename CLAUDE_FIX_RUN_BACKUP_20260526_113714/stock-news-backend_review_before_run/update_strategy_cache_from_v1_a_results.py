import json
from pathlib import Path
src=Path('data/v1_method_a_results.json')
old=json.loads(src.read_text(encoding='utf-8'))
items=[]
for x in old.get('items',[]):
    if x.get('symbol') in {'VIC','VHM'}: continue
    if x.get('action') == 'Mua/Canh mua': label='Có thể mua thăm dò'
    elif x.get('action') == 'Chờ về vùng mua': label='Chờ về vùng mua'
    else: label='Theo dõi'
    items.append({
        'symbol':x['symbol'],
        'entry':x['entry'],
        'stopLoss':str(x['stopLoss']),
        'target':str(x['target']),
        'action':label,
        'rank':x.get('rr') or 0,
        'price':x.get('price'),
        'support':x.get('support'),
        'distanceToSupportPct':x.get('distanceToSupportPct'),
        'riskPct':x.get('riskPct'),
        'rewardPct':x.get('rewardPct'),
        'rr':x.get('rr'),
        'reason':f"Giá hiện tại {x.get('price')} cách hỗ trợ {x.get('distanceToSupportPct')}%. Vùng mua Cách A là {x.get('entry')}; stop dưới hỗ trợ 2% tại {x.get('stopLoss')}; target kháng cự {x.get('target')}; RR {x.get('rr')}. {('Chưa mua ngay, chờ về đúng vùng.' if label!='Có thể mua thăm dò' else 'Đạt vùng mua và RR.') }"
    })
items.sort(key=lambda x:(0 if x['action'].startswith('Có thể') else 1, -float(x.get('rank') or 0)))
payload={
 'updatedAt':old.get('updatedAt'),
 'note':'Cache tĩnh dựng từ kết quả V1 Cách A đã tính sẵn; không chạy lại R/S. Loại VIC/VHM.',
 'strategies':[
   {'id':'support_buy_v1_method_a','name':'Chiến lược 1: Mua tại điểm hỗ trợ - Cách A','items':items[:12]},
   {'id':'shakeout_target6','name':'Chiến lược 2: Mua khi cổ phiếu rũ Target +6%','items':[]}
 ],
 'errors':[]
}
Path('data/strategy_results_cache.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
print('updated cache', len(items), 'items')
