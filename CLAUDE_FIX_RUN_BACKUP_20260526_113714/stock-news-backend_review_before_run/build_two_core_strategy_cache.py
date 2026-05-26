from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from app.market_data import get_market_symbol

V1_UNIVERSE=["FPT","MWG","HPG","SSI","VCI","VND","HCM","MBS","TCB","MBB","ACB","CTG","BID","VPB","STB","VIB","VRE","KDH","DXG","NVL","KBC","GEX","GVR","PNJ","VNM","MSN","SAB","GAS","PLX","PVD","PVS","DGC","DCM","DPM","HSG","NKG","DIG","CEO","VTP","CTR","REE","PC1","SZC","BCM","HDG","KSB","ANV","VHC"]
V2_UNIVERSE=["MSN","FPT","LPB","TPB","VPB","VRE","SSI","LCG","AAA","APH","BIC","CTD","FIT","HHS","HPX","HT1","MIG","QCG","SJS","VCG","VHC","VIX","GIL","HDC","EVF"]
EXCLUDE={"VIC","VHM"}

def sf(x,default=0.0):
    try: return float(x or default)
    except Exception: return default

def tech_of(item): return item.get('technical') or {}
def price_of(item): return sf(item.get('price') or item.get('lastPrice') or item.get('close'))
def support_of(t): return sf(t.get('activeSupportDay') or t.get('supportDay') or t.get('nearestSupport') or t.get('support'))
def resistance_of(t): return sf(t.get('activeResistanceDay') or t.get('resistanceDay') or t.get('nearestResistance') or t.get('resistance'))

def v1(item):
    sym=str(item.get('ticker') or item.get('symbol') or '').upper(); p=price_of(item); t=tech_of(item); s=support_of(t); r=resistance_of(t)
    if not sym or p<=0 or s<=0 or r<=p: return None
    entry_low=s; entry_high=s*1.02; stop=s*0.98; target=r
    dist=(p/s-1)*100; risk=(p-stop)/p*100; reward=(target-p)/p*100; rr=reward/risk if risk>0 else 0
    rsi=sf(t.get('rsi14')); vol=sf(t.get('volumeRatio'),1); hist=sf(t.get('histogram'))
    in_zone=entry_low<=p<=entry_high; ok_rr=rr>=1.0; ok_quality=(rsi>=38 and vol<=2.5)
    if in_zone and ok_rr and ok_quality:
        action='Có thể mua thăm dò'
    elif p>entry_high:
        action='Chờ về vùng mua'
    else:
        action='Theo dõi'
    return {'symbol':sym,'entry':f'{entry_low:.2f} - {entry_high:.2f}','stopLoss':f'{stop:.2f}','target':f'{target:.2f}','action':action,'rank':round(rr*25 + max(0,2-abs(dist))*10 + max(0,rsi-38)*0.5,2),'rr':round(rr,2),'price':round(p,2),'support':round(s,2),'distanceToSupportPct':round(dist,2),'riskPct':round(risk,2),'rewardPct':round(reward,2),'reason':f'Giá {p:.2f}; vùng mua chỉ từ hỗ trợ {s:.2f} đến {entry_high:.2f}. Stop theo Cách A dưới hỗ trợ 2% tại {stop:.2f}; target kháng cự {target:.2f}; RR {rr:.2f}. RSI {rsi:.1f}, volume {vol:.2f}, MACD hist {hist:.2f}. '+('Đạt vùng mua.' if in_zone and ok_rr and ok_quality else 'Chưa đạt mua ngay, ưu tiên chờ đúng vùng.')}

def v2(item):
    sym=str(item.get('ticker') or item.get('symbol') or '').upper(); p=price_of(item); t=tech_of(item); s=support_of(t)
    if not sym or p<=0 or s<=0: return None
    break_pct=(s-p)/s*100
    # Current-data approximation from cached R/S: price below support 2-4% means active shakeout candidate.
    active=2.0<=break_pct<=4.0
    entry=p; stop=entry*0.96; target=entry*1.06
    rsi=sf(t.get('rsi14')); vol=sf(t.get('volumeRatio'),1); hist=sf(t.get('histogram'))
    action='Có thể mua rũ' if active else 'Chưa có tín hiệu rũ'
    if not active: return None
    return {'symbol':sym,'entry':f'{entry:.2f}','stopLoss':f'{stop:.2f}','target':f'{target:.2f}','action':action,'rank':round(100-abs(break_pct-3)*15 + max(0,55-rsi)*0.2,2),'price':round(p,2),'support':round(s,2),'breakSupportPct':round(break_pct,2),'riskPct':4.0,'rewardPct':6.0,'rr':1.5,'reason':f'Giá {p:.2f} đang dưới hỗ trợ {s:.2f} khoảng {break_pct:.2f}%, nằm trong vùng rũ 2-4%. Stop -4% tại {stop:.2f}, target +6% tại {target:.2f}. RSI {rsi:.1f}, volume {vol:.2f}, MACD hist {hist:.2f}.'}

def main():
    v1_items=[]; v2_items=[]; errors=[]
    for sym in V1_UNIVERSE:
        if sym in EXCLUDE: continue
        try:
            x=v1(get_market_symbol(sym, force_refresh=False))
            if x: v1_items.append(x)
        except Exception as e: errors.append({'symbol':sym,'error':str(e)})
    for sym in V2_UNIVERSE:
        if sym in EXCLUDE: continue
        try:
            x=v2(get_market_symbol(sym, force_refresh=False))
            if x: v2_items.append(x)
        except Exception as e: errors.append({'symbol':sym,'error':str(e)})
    # For V1 show actionable first, then best watchlist. Do not call them buy if not in zone.
    v1_items.sort(key=lambda x:(0 if x['action'].startswith('Có thể') else 1, -x['rank']))
    v2_items.sort(key=lambda x:-x['rank'])
    payload={'updatedAt':datetime.now(timezone.utc).isoformat(),'note':'Kết quả cache cho 2 chiến lược core, đọc R/S đã có từ market-data cache; web chỉ hiển thị, không chạy lại R/S. Loại VIC/VHM.','strategies':[{'id':'support_buy_v1_method_a','name':'Chiến lược 1: Mua tại điểm hỗ trợ - Cách A','items':v1_items[:12]},{'id':'shakeout_target6','name':'Chiến lược 2: Mua khi cổ phiếu rũ Target +6%','items':v2_items[:12]}],'errors':errors}
    Path('data/strategy_results_cache.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'v1':len(v1_items),'v1_buy':sum(1 for x in v1_items if x['action'].startswith('Có thể')),'v2':len(v2_items),'errors':len(errors),'top_v1':v1_items[:5],'top_v2':v2_items[:5]},ensure_ascii=True,indent=2))
if __name__=='__main__': main()
