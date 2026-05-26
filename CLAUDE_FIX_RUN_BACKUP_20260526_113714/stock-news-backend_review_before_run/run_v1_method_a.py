import json
from datetime import datetime, timezone
from pathlib import Path
from app.market_data import get_market_symbol

UNIVERSE = ["FPT", "MWG", "SSI", "VCI", "HCM", "MBB", "TCB", "VPB", "MSN", "LPB", "TPB", "VRE", "CTD", "VIX", "VCG", "VHC"]

def fnum(x):
    try:
        if x is None or x == "": return None
        return float(x)
    except Exception:
        return None

def pick_tech(d):
    return d.get("technical") or d.get("tech") or {}

rows=[]; errors=[]
for sym in UNIVERSE:
    try:
        d=get_market_symbol(sym, force_refresh=False)
        tech=pick_tech(d)
        price=fnum(d.get("price") or d.get("lastPrice") or d.get("close"))
        support=fnum(tech.get("activeSupportDay") or tech.get("supportDay") or tech.get("support") or tech.get("nearestSupport"))
        resist=fnum(tech.get("activeResistanceDay") or tech.get("resistanceDay") or tech.get("resistance") or tech.get("nearestResistance"))
        if not price or not support or not resist or support <= 0:
            errors.append({"symbol":sym,"error":"missing price/support/resistance"}); continue
        entry_low=support
        entry_high=support*1.02
        stop=support*0.98
        target=resist
        dist=(price/support-1)*100
        risk=(price-stop)/price*100
        reward=(target-price)/price*100
        rr=reward/risk if risk>0 else None
        ok_zone=price <= entry_high and price >= stop
        ok_rr=rr is not None and rr >= 1.0
        action="Mua/Canh mua" if ok_zone and ok_rr else ("Chờ về vùng mua" if price>entry_high else "Loại")
        rows.append({
            "symbol":sym,"price":round(price,2),"support":round(support,2),"entry":f"{entry_low:.2f} - {entry_high:.2f}",
            "stopLoss":round(stop,2),"target":round(target,2),"distanceToSupportPct":round(dist,2),
            "riskPct":round(risk,2),"rewardPct":round(reward,2),"rr":round(rr,2) if rr is not None else None,
            "okZone":ok_zone,"okRR":ok_rr,"action":action,
        })
    except Exception as e:
        errors.append({"symbol":sym,"error":str(e)})

rows.sort(key=lambda x:(0 if x["action"]=="Mua/Canh mua" else 1 if x["action"]=="Chờ về vùng mua" else 2, - (x.get("rr") or -9)))
out={"updatedAt":datetime.now(timezone.utc).isoformat(),"method":"V1 Method A: entry S→S*1.02, stop S*0.98, target resistance, require RR>=1","items":rows,"errors":errors}
Path('data/v1_method_a_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
