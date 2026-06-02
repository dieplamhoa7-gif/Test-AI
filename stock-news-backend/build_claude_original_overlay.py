from __future__ import annotations
import json, pathlib, math

LABEL = {
    'support-cluster':'Hỗ trợ','resistance-cluster':'Kháng cự','support-trendline':'Trendline hỗ trợ','resistance-trendline':'Trendline kháng cự',
    'double-bottom':'2 Đáy','double-top':'2 Đỉnh','triple-bottom':'3 Đáy','triple-top':'3 Đỉnh','head-shoulders':'Vai-Đầu-Vai','inverse-head-shoulders':'VĐV ngược',
    'ascending-triangle':'Tam giác tăng','descending-triangle':'Tam giác giảm','symmetrical-triangle':'Tam giác cân','falling-wedge':'Nêm giảm','rising-wedge':'Nêm tăng','up-channel':'Kênh tăng','down-channel':'Kênh giảm',
    'darvas-box':'Hộp Darvas','cup-handle':'Cốc-Tay cầm','rounding-bottom':'Đáy tròn','rounding-top':'Đỉnh tròn','bull-flag':'Cờ tăng','bear-flag':'Cờ giảm','spring-shakeout':'Spring','upthrust-bull-trap':'Upthrust','fvg-bullish':'FVG tăng','fvg-bearish':'FVG giảm','order-block-bullish':'OB tăng','order-block-bearish':'OB giảm','no-demand':'No Demand','no-supply':'No Supply','volume-climax':'Climax'
}
def lab(t): return LABEL.get(t,t)
def color(direction, typ=''):
    if 'support' in typ or direction=='bullish': return '#16a34a'
    if 'resistance' in typ or direction=='bearish': return '#dc2626'
    if 'neckline' in typ: return '#f59e0b'
    return '#6b7280'
def finite(v):
    try: return v is not None and math.isfinite(float(v))
    except Exception: return False

def convert(symbol='MWG'):
    root=pathlib.Path(__file__).resolve().parent
    src=root/'firebase_public'/'charts_debug'/f'{symbol}_patterns_forecast.json'
    pub=root/'firebase_public'/'data'/'patterns'/f'{symbol}_patterns_overlay.json'
    d=json.loads(src.read_text(encoding='utf-8'))
    pats=[p for p in d.get('patterns',[]) if p.get('category')!='candlestick']
    last=d.get('lastDate') or d.get('period',[None,None])[-1]
    fcpts=d.get('forecast',{}).get('points',[])
    last_fc=(fcpts[-1].get('time') if fcpts else last)
    ov={'symbol':symbol,'source':'claude-original-run_mwg_pattern_forecast','createdAt':d.get('createdAt'),'timeframe':d.get('timeframe'),'lastClose':d.get('lastClose'),'summary':d.get('summary',{}),'labels':[],'lines':[],'zones':[],'forecast':fcpts,'scenarios':d.get('forecast',{}).get('scenarios',{})}
    # Match Claude plot.py order and style more closely.
    # S/R + trendline
    for p in pats:
        t=p.get('type',''); direction=p.get('direction','neutral')
        if t in ('support-cluster','resistance-cluster'):
            pts=(p.get('lines') or [{}])[0].get('points') or []
            if pts and finite(pts[0].get('value')):
                y=float(pts[0]['value']); col='#16a34a' if 'support' in t else '#dc2626'
                ov['lines'].append({'type':t,'name':t,'text':f'{lab(t)} {y:g}','direction':direction,'color':col,'dash':True,'points':[{'time':pts[0].get('time'),'value':y},{'time':last,'value':y}],'score':p.get('score'),'confidence':p.get('confidence'),'claudeRole':'sr-cluster'})
                ov['labels'].append({'time':last,'price':y,'text':f'{lab(t)} {y:g}','kind':'sr-label','direction':direction,'color':col,'score':p.get('score'),'confidence':p.get('confidence'),'xAnchor':'right'})
        elif t in ('support-trendline','resistance-trendline'):
            lines=p.get('lines') or []
            if lines:
                pts=[{'time':q.get('time'),'value':q.get('value')} for q in (lines[0].get('points') or []) if q.get('time') and finite(q.get('value'))]
                if len(pts)>=2:
                    col='#0891b2' if 'support' in t else '#db2777'
                    ov['lines'].append({'type':t,'name':t,'text':lab(t),'direction':direction,'color':col,'points':pts,'score':p.get('score'),'confidence':p.get('confidence'),'claudeRole':'trendline'})
                    q=pts[-1]
                    ov['labels'].append({'time':q['time'],'price':q['value'],'text':lab(t),'kind':'trendline-label','direction':direction,'color':col,'score':p.get('score'),'confidence':p.get('confidence'),'yShift':12 if 'resistance' in t else -12})
    # double/triple/H&S/triangles: keep points and neckline exactly from Claude lines.
    for p in pats:
        t=p.get('type',''); direction=p.get('direction','neutral'); col=color(direction,t)
        if t.startswith(('double','triple')) or t in ('head-shoulders','inverse-head-shoulders','cup-handle') or 'triangle' in t or 'wedge' in t or 'channel' in t:
            for ln in p.get('lines') or []:
                pts=[{'time':q.get('time'),'value':q.get('value')} for q in (ln.get('points') or []) if q.get('time') and finite(q.get('value'))]
                if len(pts)>=2:
                    lcol='#f59e0b' if ln.get('name')=='neckline' else col
                    ov['lines'].append({'type':t,'name':ln.get('name') or t,'text':lab(t) if ln.get('name')!='neckline' else 'Neckline','direction':direction,'color':lcol,'dash':ln.get('name')=='neckline','points':pts,'score':p.get('score'),'confidence':p.get('confidence'),'claudeRole':'pattern-line'})
                elif len(pts)==1:
                    q=pts[0]
                    ov['labels'].append({'time':q['time'],'price':q['value'],'text':ln.get('name') or lab(t),'kind':'pivot-label','direction':direction,'color':col,'score':p.get('score'),'confidence':p.get('confidence')})
            anchor=None
            for ln in p.get('lines') or []:
                pts=ln.get('points') or []
                if pts and finite(pts[0].get('value')):
                    anchor=pts[0]; break
            if anchor:
                lv=p.get('levels') or {}; tgt=f" → {lv.get('target')}" if finite(lv.get('target')) else ''
                ov['labels'].append({'time':anchor.get('time'),'price':anchor.get('value'),'text':lab(t)+tgt,'kind':'pattern-title','direction':direction,'color':col,'score':p.get('score'),'confidence':p.get('confidence'),'yShift':32 if direction=='bearish' else -32})
        elif t=='darvas-box':
            lv=p.get('levels') or {}; lines=p.get('lines') or []
            x0=(lines[0].get('points') or [{}])[0].get('time') if lines else p.get('time')
            if finite(lv.get('support')) and finite(lv.get('resistance')):
                ov['zones'].append({'type':t,'text':lab(t),'from':x0,'to':last,'low':lv['support'],'high':lv['resistance'],'color':'rgba(168,85,247,0.10)'})
                ov['labels'].append({'time':x0,'price':lv['resistance'],'text':f"{lab(t)} {lv['support']}-{lv['resistance']}",'kind':'box-label','direction':direction,'color':'#7c3aed','score':p.get('score'),'confidence':p.get('confidence'),'yShift':10})
        elif t.startswith('fvg'):
            lv=p.get('levels') or {}
            if finite(lv.get('gapLow')) and finite(lv.get('gapHigh')):
                ov['zones'].append({'type':t,'text':lab(t),'from':p.get('time'),'to':last,'low':lv['gapLow'],'high':lv['gapHigh'],'color':'rgba(22,163,74,0.18)' if 'bull' in t else 'rgba(220,38,38,0.18)'})
        elif t.startswith('order-block'):
            lv=p.get('levels') or {}
            if finite(lv.get('obLow')) and finite(lv.get('obHigh')):
                ov['zones'].append({'type':t,'text':lab(t),'from':p.get('time'),'to':last,'low':lv['obLow'],'high':lv['obHigh'],'color':'rgba(16,185,129,0.22)' if 'bull' in t else 'rgba(244,63,94,0.22)'})
        elif t in ('spring-shakeout','upthrust-bull-trap') and p.get('time') and finite(p.get('price')):
            ov['labels'].append({'time':p.get('time'),'price':p.get('price'),'text':lab(t),'kind':'event-label','direction':direction,'color':col,'score':p.get('score'),'confidence':p.get('confidence')})
    # Forecast label, Claude style.
    if fcpts:
        q=fcpts[-1]
        if q.get('time') and finite(q.get('value')):
            ov['labels'].append({'time':q['time'],'price':q['value'],'text':f"Dự báo {q['value']}",'kind':'forecast-label','direction':'neutral','color':'#2563eb','score':100,'confidence':'high'})
    pub.parent.mkdir(parents=True,exist_ok=True)
    pub.write_text(json.dumps(ov,ensure_ascii=False,indent=2),encoding='utf-8')
    print(pub,'lines',len(ov['lines']),'labels',len(ov['labels']),'zones',len(ov['zones']))
if __name__=='__main__': convert()
