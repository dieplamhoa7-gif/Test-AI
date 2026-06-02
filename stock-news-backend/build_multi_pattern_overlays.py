from __future__ import annotations
import argparse, json, math, pathlib, sys
import pandas as pd

from pattern_engine.analyze import analyze

LABEL = {
    'support-cluster':'Hỗ trợ','resistance-cluster':'Kháng cự','support-trendline':'Trendline hỗ trợ','resistance-trendline':'Trendline kháng cự',
    'double-bottom':'2 Đáy','double-top':'2 Đỉnh','triple-bottom':'3 Đáy','triple-top':'3 Đỉnh','head-shoulders':'Vai-Đầu-Vai','inverse-head-shoulders':'VĐV ngược',
    'ascending-triangle':'Tam giác tăng','descending-triangle':'Tam giác giảm','symmetrical-triangle':'Tam giác cân','falling-wedge':'Nêm giảm','rising-wedge':'Nêm tăng',
    'up-channel':'Kênh tăng','down-channel':'Kênh giảm','darvas-box':'Hộp Darvas','cup-handle':'Cốc-Tay cầm','rounding-bottom':'Đáy tròn','rounding-top':'Đỉnh tròn',
    'bull-flag':'Cờ tăng','bear-flag':'Cờ giảm','spring-shakeout':'Spring','upthrust-bull-trap':'Upthrust','fvg-bullish':'FVG tăng','fvg-bearish':'FVG giảm',
    'order-block-bullish':'OB tăng','order-block-bearish':'OB giảm','no-demand':'No Demand','no-supply':'No Supply','volume-climax':'Climax',
    'Hammer':'Hammer','Bullish Engulfing':'Nhấn chìm tăng','Bearish Engulfing':'Nhấn chìm giảm','Shooting Star':'Shooting Star','Doji':'Doji','Marubozu':'Marubozu'
}
FRAME_TYPES={'support-cluster','resistance-cluster','support-trendline','resistance-trendline'}

def lab(t): return LABEL.get(t,t)
def color(direction, typ=''):
    if 'support' in typ or direction=='bullish': return '#16a34a'
    if 'resistance' in typ or direction=='bearish': return '#dc2626'
    return '#f5c542'
def finite(v):
    try: return v is not None and math.isfinite(float(v))
    except Exception: return False

def row_df(rows):
    df=pd.DataFrame(rows)
    if df.empty: return df
    rename={'time':'date','Date':'date','Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}
    df=df.rename(columns={k:v for k,v in rename.items() if k in df.columns})
    if 'date' not in df.columns and 'time' in df.columns: df['date']=df['time']
    need=['date','open','high','low','close','volume']
    df=df[[c for c in need if c in df.columns]].copy()
    for c in ['open','high','low','close','volume']:
        if c in df.columns: df[c]=pd.to_numeric(df[c],errors='coerce')
    df['date']=pd.to_datetime(df['date'], errors='coerce')
    df=df.dropna(subset=['date','open','high','low','close']).sort_values('date')
    return df

def _line_level(line):
    pts=line.get('points') or []
    vals=[]
    for p in pts:
        if finite(p.get('value')): vals.append(float(p.get('value')))
    if not vals: return None
    return sum(vals)/len(vals)

def _is_horizontal_rs_line(line):
    if not line.get('dash'): return False
    name=str(line.get('name') or '').lower()
    typ=str(line.get('type') or '').lower()
    return name in {'support','resistance','neckline','target'} or any(x in typ for x in ['support','resistance'])

def merge_nearby_rs_lines(lines, pct=0.01):
    """Gộp các đường ngang R/S/neckline/target cách nhau < pct để chart đỡ rối."""
    keep=[]; mergeable=[]
    for line in lines:
        if _is_horizontal_rs_line(line): mergeable.append(line)
        else: keep.append(line)
    buckets=[]
    for line in sorted(mergeable, key=lambda x: (_line_level(x) or 0)):
        lvl=_line_level(line)
        if lvl is None: continue
        found=None
        for b in buckets:
            if abs(lvl / max(0.0001, b['level']) - 1) < pct:
                found=b; break
        if found is None:
            buckets.append({'level':lvl,'items':[line]})
        else:
            found['items'].append(line)
            levels=[_line_level(x) for x in found['items'] if _line_level(x) is not None]
            weights=[max(1,float(x.get('score') or 1)) for x in found['items'] if _line_level(x) is not None]
            found['level']=sum(l*w for l,w in zip(levels,weights))/sum(weights)
    for b in buckets:
        items=sorted(b['items'], key=lambda x: float(x.get('score') or 0), reverse=True)
        best=dict(items[0])
        lvl=round(float(b['level']), 3)
        best['points']=[{**p,'value':lvl} for p in (best.get('points') or [])]
        if len(items)>1:
            best['text']=f"{best.get('text') or best.get('name') or 'R/S'} x{len(items)}"
            best['mergedCount']=len(items)
            best['mergedLevels']=[round(_line_level(x),3) for x in items if _line_level(x) is not None]
            best['score']=round(max(float(x.get('score') or 0) for x in items),1)
        keep.append(best)
    return keep

def overlay_from_analysis(r):
    fcpts=r.get('forecast',{}).get('points',[])
    last_forecast_time=(fcpts[-1].get('time') if fcpts else r.get('period',[None,r.get('lastDate')])[-1])
    overlays={'symbol':r.get('symbol'),'createdAt':r.get('createdAt'),'timeframe':r.get('timeframe'),'period':r.get('period'),'lastClose':r.get('lastClose'),'summary':r.get('summary',{}),'labels':[],'lines':[],'zones':[],'forecast':fcpts,'scenarios':r.get('forecast',{}).get('scenarios',{})}
    seen=set()
    pats=r.get('patterns',[])
    for p in pats:
        typ=p.get('type',''); direction=p.get('direction','neutral'); cat=p.get('category','')
        score=float(p.get('_composite_final') or p.get('composite') or p.get('score') or 0); conf=p.get('confidence','')
        role=p.get('role','')
        keep = role in ('primary','supporting') or score>=35 or typ in FRAME_TYPES or cat=='candlestick'
        if not keep: continue
        if cat=='candlestick' and score < 25 and p.get('score',0) < 55: continue
        lv=p.get('levels') or {}
        for ln in p.get('lines',[]) or []:
            pts=ln.get('points') or []
            if len(pts)>=2:
                clean=[{'time':q.get('time'),'value':q.get('value')} for q in pts if q.get('time') and finite(q.get('value'))]
                if len(clean)>=2:
                    overlays['lines'].append({'name':ln.get('name') or typ,'type':typ,'text':lab(typ),'direction':direction,'color':color(direction,typ),'points':clean,'score':round(score,1),'confidence':conf,'role':role})
            elif len(pts)==1:
                q=pts[0]
                if q.get('time') and finite(q.get('value')):
                    overlays['labels'].append({'time':q.get('time'),'price':q.get('value'),'text':lab(typ),'kind':ln.get('name') or typ,'direction':direction,'color':color(direction,typ),'score':round(score,1),'confidence':conf,'role':role})
        for k in ['support','resistance','neckline','target']:
            if finite(lv.get(k)):
                overlays['lines'].append({'name':k,'type':typ,'text':f"{lab(typ)} {k}",'direction':direction,'color':'#16a34a' if k=='support' else '#dc2626' if k=='resistance' else '#a855f7' if k=='neckline' else '#2563eb','points':[{'time':r.get('period',[None,None])[0],'value':lv[k]},{'time':last_forecast_time,'value':lv[k]}],'score':round(score,1),'confidence':conf,'role':role,'dash':True})
        if typ=='darvas-box' and finite(lv.get('support')) and finite(lv.get('resistance')):
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':p.get('time') or r.get('period',[None])[0],'to':r.get('period',[None,None])[-1],'low':lv['support'],'high':lv['resistance'],'color':'rgba(168,85,247,0.10)'})
        if typ.startswith('fvg') and finite(lv.get('gapLow')) and finite(lv.get('gapHigh')):
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':p.get('time'),'to':r.get('period',[None,None])[-1],'low':lv['gapLow'],'high':lv['gapHigh'],'color':'rgba(22,163,74,0.18)' if 'bull' in typ else 'rgba(220,38,38,0.18)'})
        if typ.startswith('order-block') and finite(lv.get('obLow')) and finite(lv.get('obHigh')):
            overlays['zones'].append({'type':typ,'text':lab(typ),'from':p.get('time'),'to':r.get('period',[None,None])[-1],'low':lv['obLow'],'high':lv['obHigh'],'color':'rgba(16,185,129,0.22)' if 'bull' in typ else 'rgba(244,63,94,0.22)'})
        if p.get('time') and finite(p.get('price')):
            key=(typ,p.get('time'),round(float(p.get('price')),2))
            if key not in seen:
                seen.add(key)
                suffix=f" {round(score)}" if score else ''
                overlays['labels'].append({'time':p.get('time'),'price':p.get('price'),'text':lab(typ)+suffix,'kind':'candlestick' if cat=='candlestick' else 'pattern','direction':direction,'color':color(direction,typ),'score':round(score,1),'confidence':conf,'role':role})
    overlays['lines']=merge_nearby_rs_lines(overlays['lines'], pct=0.01)
    return overlays

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--history',default='data/vn100_history_from_2023.json')
    ap.add_argument('--symbols',default='',help='Comma-separated symbols; empty=all')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--out-patterns',default='data/patterns')
    ap.add_argument('--out-public',default='firebase_public/data/patterns')
    args=ap.parse_args()
    root=pathlib.Path(__file__).resolve().parent
    hist=json.loads((root/args.history).read_text(encoding='utf-8'))
    all_symbols=hist.get('symbols',{})
    wanted=[x.strip().upper() for x in args.symbols.split(',') if x.strip()]
    symbols=wanted or sorted(all_symbols.keys())
    if args.limit: symbols=symbols[:args.limit]
    outp=root/args.out_patterns; outpub=root/args.out_public
    outp.mkdir(parents=True,exist_ok=True); outpub.mkdir(parents=True,exist_ok=True)
    overview=[]
    for sym in symbols:
        info=all_symbols.get(sym) or {}
        df=row_df(info.get('rows') or [])
        if len(df)<40:
            print(f'SKIP {sym}: {len(df)} bars')
            continue
        try:
            r=analyze(df,sym)
            clean={k:v for k,v in r.items() if not k.startswith('_')}
            (outp/f'{sym}_analysis.json').write_text(json.dumps(clean,ensure_ascii=False,indent=2),encoding='utf-8')
            ov=overlay_from_analysis(clean)
            (outpub/f'{sym}_patterns_overlay.json').write_text(json.dumps(ov,ensure_ascii=False,indent=2),encoding='utf-8')
            s=clean.get('summary',{})
            overview.append({'symbol':sym,'bias':s.get('bias'),'biasStrength':s.get('biasStrength'),'bullScore':s.get('bullScore'),'bearScore':s.get('bearScore'),'lastClose':clean.get('lastClose'),'patterns':len(clean.get('patterns',[])),'primarySignals':[x.get('type') for x in s.get('primarySignals',[])], 'overlay':f'/data/patterns/{sym}_patterns_overlay.json'})
            print(f"OK {sym:5} {clean.get('bars')} bars bias={s.get('bias')} strength={s.get('biasStrength')} patterns={len(clean.get('patterns',[]))}")
        except Exception as e:
            print(f'ERR {sym}: {e}')
            overview.append({'symbol':sym,'error':str(e)[:200]})
    overview.sort(key=lambda x: (0 if 'error' in x else 1, x.get('bias')=='bullish', x.get('biasStrength') or 0), reverse=True)
    port={'count':len(overview),'source':args.history,'stocks':overview,'note':'Research-only, not financial advice'}
    (outpub/'_portfolio_patterns_overview.json').write_text(json.dumps(port,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DONE',len(overview),'symbols')

if __name__=='__main__': main()
