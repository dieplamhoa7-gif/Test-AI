from __future__ import annotations
import json, datetime as dt
from pathlib import Path
import importlib.util
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parent
HIST=ROOT / 'data/vn100_history_2025_06_2026_05_cache.json'
CFG=ROOT / 'data/core12_group_combo_config.json'
OUT=ROOT / 'data/core12_ml_sr_full_universe.json'
CSV=ROOT / 'data/core12_ml_sr_full_universe_summary.csv'
spec=importlib.util.spec_from_file_location('combo', ROOT / 'ml_core12_group_combo_search.py')
combo=importlib.util.module_from_spec(spec); spec.loader.exec_module(combo)
spec2=importlib.util.spec_from_file_location('major', ROOT / 'build_sr_levels_major_selected.py')
major=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(major)

def sector(sym):
    return combo.sg(sym)

def fmt_zone(lv):
    return f"{lv.get('low'):.2f}-{lv.get('high'):.2f}" if lv else ''

def strength_label(lv):
    if not lv: return ''
    s=float(lv.get('strength',0)); t=int(lv.get('touches',0))
    if s>=8 or t>=5: return 'strong'
    if s>=5 or t>=3: return 'medium'
    return 'weak'

def latest_core12_values(df, indicators, params_map, sr_item):
    vals={}; signals=[]
    for ind in indicators:
        params=params_map.get(ind,{})
        if ind=='SR_CLUSTER':
            close=float(df.close.iloc[-1]); cur=(sr_item.get('currentZone') or []); s=sr_item.get('supports') or []; r=sr_item.get('resistances') or []
            s1=s[0] if s else None; r1=r[0] if r else None
            near_s=bool(cur) or (s1 and close <= float(s1['high']) + max(close*0.015, float(sr_item.get('atr14') or 0)*0.5))
            broken=bool(s1 and close < float(s1['low']) - max(close*0.005, float(sr_item.get('atr14') or 0)*0.25))
            vals['SR_CLUSTER']={'nearSupport':near_s,'supportBroken':broken,'S1':fmt_zone(s1),'R1':fmt_zone(r1)}
            signals.append(('SR_CLUSTER', 1 if near_s and not broken else (-1 if broken else 0), 'near support' if near_s and not broken else ('support broken' if broken else 'neutral')))
            continue
        out=combo.calc(df,ind,params if isinstance(params,list) else [],{})
        last={k:float(v.iloc[-1]) if hasattr(v,'iloc') and pd.notna(v.iloc[-1]) else 0.0 for k,v in out.items()}
        vals[ind]=last
        # generic interpretation for hold/break, intentionally transparent not retrained.
        score=0; reason=[]
        for k,v in last.items():
            kl=k.lower()
            if any(x in kl for x in ['dist','cloud_pos']):
                if v>=0: score+=1; reason.append(f'{k}>=0')
                else: score-=1; reason.append(f'{k}<0')
            elif any(x in kl for x in ['slope','hist','trix','roc','mom']):
                if v>0: score+=1; reason.append(f'{k}>0')
                elif v<0: score-=1; reason.append(f'{k}<0')
            elif 'rsi' in kl:
                if 40<=v<=70: score+=1; reason.append(f'{k} healthy')
                elif v<35: score-=1; reason.append(f'{k} weak')
            elif 'mfi' in kl or 'cmf' in kl:
                if v>=45: score+=1; reason.append(f'{k} ok')
                else: score-=1; reason.append(f'{k} weak')
            elif 'dir' in kl:
                score += 1 if v>0 else -1; reason.append(f'{k}={v:.2f}')
            elif 'spread' in kl or 'tk' in kl:
                if v>=0: score+=1; reason.append(f'{k}>=0')
                else: score-=1; reason.append(f'{k}<0')
        sig=1 if score>0 else (-1 if score<0 else 0)
        signals.append((ind,sig,'; '.join(reason[:3])))
    return vals,signals

def classify(close,sr_item,signals):
    cur=(sr_item.get('currentZone') or []); s=sr_item.get('supports') or []
    s1=s[0] if s else None; atr=float(sr_item.get('atr14') or 0)
    support_broken=False; base='CHƯA CÓ S1 RÕ'; reason='không đủ cụm hỗ trợ major'
    if cur:
        base='GIỮ VÙNG HIỆN TẠI'; reason='close nằm trong/gần current zone'
    elif s1:
        buf=max(close*0.005, atr*0.25)
        if close < float(s1['low'])-buf:
            support_broken=True; base='GÃY HỖ TRỢ'; reason=f"close dưới S1 {fmt_zone(s1)}"
        elif close <= float(s1['high'])+max(close*0.012,atr*0.5):
            base='TEST S1 / CHƯA GÃY RÕ'; reason=f"close sát S1 {fmt_zone(s1)}"
        else:
            dist=(close-float(s1['center']))/close*100; base='GIỮ TRÊN HỖ TRỢ'; reason=f"trên S1 khoảng {dist:.2f}%"
    pos=sum(1 for _,v,_ in signals if v>0); neg=sum(1 for _,v,_ in signals if v<0); neu=sum(1 for _,v,_ in signals if v==0)
    total=max(1,pos+neg+neu); hold_score=round(pos/total*100,2); break_score=round(neg/total*100,2)
    if support_broken and neg>=pos: final='GÃY HỖ TRỢ - CORE12 XÁC NHẬN YẾU'
    elif support_broken: final='GÃY HỖ TRỢ GIÁ, CORE12 CHƯA ĐỒNG THUẬN'
    elif base.startswith('TEST') and neg>pos: final='TEST HỖ TRỢ - RỦI RO GÃY CAO'
    elif pos>=neg+2: final='GIỮ HỖ TRỢ / CORE12 ỦNG HỘ'
    elif neg>=pos+2: final='GIỮ GIÁ NHƯNG CORE12 YẾU'
    else: final=base
    return {'priceStatus':base,'reason':reason,'core12Positive':pos,'core12Negative':neg,'core12Neutral':neu,'holdScore':hold_score,'breakRiskScore':break_score,'finalStatus':final}

def main():
    hist=json.load(open(HIST,encoding='utf-8'))['symbols']; cfg=json.load(open(CFG,encoding='utf-8'))['selected']
    items=[]; flat=[]
    for sym in sorted(hist):
        rows=hist[sym]['rows']; df=pd.DataFrame(rows).sort_values('time').reset_index(drop=True)
        for c in ['open','high','low','close','volume']: df[c]=pd.to_numeric(df[c],errors='coerce')
        sec=sector(sym); use_sec=sec if sec in cfg and 'RS' in cfg[sec] else ('ALL' if 'ALL' in cfg and 'RS' in cfg.get('ALL',{}) else None)
        if not use_sec: continue
        rs_cfg=cfg[use_sec]['RS']; indicators=rs_cfg['indicators']; params=rs_cfg.get('indicatorParams',{})
        sr=major.analyze_major(sym,rows); close=float(sr['close'])
        vals,signals=latest_core12_values(df,indicators,params,sr); st=classify(close,sr,signals)
        s=sr.get('supports') or []; r=sr.get('resistances') or []; cur=sr.get('currentZone') or []
        item={'symbol':sym,'sectorGroup':sec,'configSector':use_sec,'task':'RS','date':sr.get('date'),'close':close,'S1':s[0] if len(s)>0 else None,'S2':s[1] if len(s)>1 else None,'R1':r[0] if len(r)>0 else None,'R2':r[1] if len(r)>1 else None,'currentZone':cur[0] if cur else None,'mlConfig':{'indicators':indicators,'indicatorParams':params,'model':rs_cfg.get('model'),'mode':rs_cfg.get('mode'),'avgPrecision':rs_cfg.get('avgPrecision'),'avgRecall':rs_cfg.get('avgRecall')},'core12Values':vals,'core12Signals':[{'indicator':a,'signal':b,'reason':c} for a,b,c in signals],**st}
        items.append(item)
        flat.append({'symbol':sym,'sectorGroup':sec,'configSector':use_sec,'date':sr.get('date'),'close':close,'currentZone':fmt_zone(cur[0]) if cur else '', 'S1':fmt_zone(s[0]) if len(s)>0 else '', 'S1_strength':strength_label(s[0]) if len(s)>0 else '', 'S2':fmt_zone(s[1]) if len(s)>1 else '', 'R1':fmt_zone(r[0]) if len(r)>0 else '', 'R1_strength':strength_label(r[0]) if len(r)>0 else '', 'R2':fmt_zone(r[1]) if len(r)>1 else '', 'core12Indicators':' + '.join(indicators),'mlModel':rs_cfg.get('model'),'mlAvgP':rs_cfg.get('avgPrecision'),'mlAvgR':rs_cfg.get('avgRecall'), **st})
    payload={'createdAt':dt.datetime.now().isoformat(timespec='seconds'),'source':str(HIST),'config':str(CFG),'method':'SR_CLUSTER gives concrete S/R zones; Core12 group-combo ML config supplies selected indicators and ML-optimized parameters for RS/support-hold confirmation. No retraining/search in this scanner.','count':len(items),'items':items}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    pd.DataFrame(flat).to_csv(CSV,index=False,encoding='utf-8-sig')
    print(json.dumps({'out':str(OUT),'csv':str(CSV),'count':len(items),'sample':flat[:5]},ensure_ascii=True,indent=2,default=str))
if __name__=='__main__': main()
