from __future__ import annotations
import json, pathlib

LABEL = {
    'support-cluster':'Hỗ trợ','resistance-cluster':'Kháng cự','support-trendline':'Trendline hỗ trợ','resistance-trendline':'Trendline kháng cự',
    'double-bottom':'2 Đáy','double-top':'2 Đỉnh','triple-bottom':'3 Đáy','triple-top':'3 Đỉnh','head-shoulders':'Vai-Đầu-Vai','inverse-head-shoulders':'VĐV ngược',
    'ascending-triangle':'Tam giác tăng','descending-triangle':'Tam giác giảm','symmetrical-triangle':'Tam giác cân','falling-wedge':'Nêm giảm','rising-wedge':'Nêm tăng',
    'up-channel':'Kênh tăng','down-channel':'Kênh giảm','darvas-box':'Hộp Darvas','cup-handle':'Cốc-Tay cầm','rounding-bottom':'Đáy tròn','rounding-top':'Đỉnh tròn',
    'bull-flag':'Cờ tăng','bear-flag':'Cờ giảm','spring-shakeout':'Spring','upthrust-bull-trap':'Upthrust','fvg-bullish':'FVG tăng','fvg-bearish':'FVG giảm',
    'order-block-bullish':'OB tăng','order-block-bearish':'OB giảm','no-demand':'No Demand','no-supply':'No Supply','volume-climax':'Climax'
}

def lab(t): return LABEL.get(t,t)
def color(direction, typ=''):
    if 'support' in typ or direction=='bullish': return '#16a34a'
    if 'resistance' in typ or direction=='bearish': return '#dc2626'
    return '#6b7280'

def convert(symbol='MWG'):
    root=pathlib.Path(__file__).resolve().parent
    src=root/'data'/'patterns'/f'{symbol}_patterns_forecast.json'
    out=root/'firebase_public'/'data'/'patterns'/f'{symbol}_patterns_overlay.json'
    d=json.loads(src.read_text(encoding='utf-8'))
    overlays={'symbol':symbol,'createdAt':d.get('createdAt'),'summary':d.get('summary',{}),'labels':[],'lines':[],'zones':[],'forecast':d.get('forecast',{}).get('points',[]),'scenarios':d.get('forecast',{}).get('scenarios',{})}
    seen=set()
    # keep stronger non-candlestick patterns + recent candles
    pats=d.get('patterns',[])
    for p in pats:
        typ=p.get('type',''); direction=p.get('direction','neutral'); cat=p.get('category','')
        score=float(p.get('score') or 0); conf=p.get('confidence','')
        if cat=='candlestick':
            if p.get('time') and score>=55:
                key=('candle',typ,p.get('time'))
                if key in seen: continue
                seen.add(key)
                overlays['labels'].append({'time':p.get('time'),'price':p.get('price'),'text':typ,'kind':'candlestick','direction':direction,'color':color(direction,typ),'score':score,'confidence':conf})
            continue
        if score < 65 and conf not in ('high','medium'): continue
        lv=p.get('levels') or {}
        # lines
        for ln in p.get('lines',[]) or []:
            pts=ln.get('points') or []
            if len(pts)>=2:
                overlays['lines'].append({'name':ln.get('name') or typ,'type':typ,'text':lab(typ),'direction':direction,'color':color(direction,typ),'points':[{'time':q.get('time'),'value':q.get('value')} for q in pts if q.get('time') and q.get('value') is not None],'score':score,'confidence':conf})
            elif len(pts)==1:
                q=pts[0]
                overlays['labels'].append({'time':q.get('time'),'price':q.get('value'),'text':lab(typ),'kind':ln.get('name') or typ,'direction':direction,'color':color(direction,typ),'score':score,'confidence':conf})
        # horizontal support/resistance from levels
        for k in ['support','resistance','target']:
            if lv.get(k):
                overlays['lines'].append({'name':k,'type':typ,'text':f"{lab(typ)} {k}",'direction':direction,'color':'#16a34a' if k=='support' else '#dc2626' if k=='resistance' else '#2563eb','points':[{'time':d.get('lastDate'),'value':lv[k]},{'time':d.get('forecast',{}).get('points',[{'time':d.get('lastDate')}])[-1].get('time'),'value':lv[k]}],'score':score,'confidence':conf,'dash':True})
        # zones
        if typ=='darvas-box' and lv.get('support') and lv.get('resistance'):
            t0=(p.get('lines') or [{}])[0].get('points',[{}])[0].get('time') or p.get('time')
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':t0,'to':d.get('lastDate'),'low':lv['support'],'high':lv['resistance'],'color':'rgba(168,85,247,0.10)'})
        if typ.startswith('fvg') and lv.get('gapLow') and lv.get('gapHigh'):
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':p.get('time'),'to':d.get('lastDate'),'low':lv['gapLow'],'high':lv['gapHigh'],'color':'rgba(22,163,74,0.18)' if 'bull' in typ else 'rgba(220,38,38,0.18)'})
        if typ.startswith('order-block') and lv.get('obLow') and lv.get('obHigh'):
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':p.get('time'),'to':d.get('lastDate'),'low':lv['obLow'],'high':lv['obHigh'],'color':'rgba(16,185,129,0.22)' if 'bull' in typ else 'rgba(244,63,94,0.22)'})
        # main label at pattern time
        if p.get('time') and p.get('price'):
            key=('pattern',typ,p.get('time'))
            if key not in seen:
                seen.add(key)
                tgt=f" → {lv.get('target')}" if lv.get('target') else ''
                overlays['labels'].append({'time':p.get('time'),'price':p.get('price'),'text':lab(typ)+tgt,'kind':'pattern','direction':direction,'color':color(direction,typ),'score':score,'confidence':conf})
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(overlays,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out, 'labels', len(overlays['labels']), 'lines', len(overlays['lines']), 'zones', len(overlays['zones']))
if __name__=='__main__': convert()
