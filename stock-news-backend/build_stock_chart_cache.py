from pathlib import Path
import json, statistics
SRC=Path('data/vn100_history_2025_06_2026_05_cache.json')
OUT=Path('firebase_public/data/charts')
MAX_ROWS=260

def ma(rows,n):
    out=[]
    for i in range(len(rows)):
        if i+1>=n:
            vals=[r['close'] for r in rows[i+1-n:i+1]]
            out.append({'time':rows[i]['time'],'value':round(sum(vals)/n,4)})
    return out

def ema(rows,n):
    out=[]; k=2/(n+1); e=None
    for r in rows:
        c=r['close']; e=c if e is None else c*k+e*(1-k)
        out.append({'time':r['time'],'value':round(e,4)})
    return out

def rsi(rows,n=14):
    out=[]; gains=[]; losses=[]
    for i in range(1,len(rows)):
        ch=rows[i]['close']-rows[i-1]['close']; gains.append(max(ch,0)); losses.append(max(-ch,0))
        if i>=n:
            g=sum(gains[-n:])/n; l=sum(losses[-n:])/n; val=100 if l==0 else 100-100/(1+g/l)
            out.append({'time':rows[i]['time'],'value':round(val,2)})
    return out

def boll(rows,n=20):
    up=[]; mid=[]; low=[]
    for i in range(len(rows)):
        if i+1>=n:
            vals=[r['close'] for r in rows[i+1-n:i+1]]; m=sum(vals)/n; sd=statistics.pstdev(vals)
            t=rows[i]['time']; mid.append({'time':t,'value':round(m,4)}); up.append({'time':t,'value':round(m+2*sd,4)}); low.append({'time':t,'value':round(m-2*sd,4)})
    return {'upper':up,'middle':mid,'lower':low}

def macd(rows):
    e12=ema(rows,12); e26=ema(rows,26); m=[]
    for a,b in zip(e12,e26): m.append({'time':a['time'],'value':round(a['value']-b['value'],4)})
    sig=[]; k=2/10; e=None
    for x in m:
        e=x['value'] if e is None else x['value']*k+e*(1-k); sig.append({'time':x['time'],'value':round(e,4)})
    hist=[{'time':a['time'],'value':round(a['value']-b['value'],4)} for a,b in zip(m,sig)]
    return {'macd':m,'signal':sig,'histogram':hist}

def trendlines(rows):
    if len(rows)<40: return []
    recent=rows[-120:]
    lows=sorted(range(len(recent)), key=lambda i: recent[i]['low'])[:2]
    highs=sorted(range(len(recent)), key=lambda i: recent[i]['high'], reverse=True)[:2]
    lines=[]
    for idxs, key, kind in [(sorted(lows),'low','support'),(sorted(highs),'high','resistance')]:
        if len(idxs)==2 and idxs[0]!=idxs[1]:
            lines.append({'type':kind,'points':[{'time':recent[idxs[0]]['time'],'value':recent[idxs[0]][key]},{'time':recent[idxs[1]]['time'],'value':recent[idxs[1]][key]}]})
    return lines

def aggregate(rows,frame):
    if frame=='day': return rows
    from datetime import date
    out=[]; cur=None; curkey=None
    for r in rows:
        y,m,d=map(int,r['time'][:10].split('-')); dt=date(y,m,d)
        key=f'{dt.isocalendar().year}-W{dt.isocalendar().week:02d}' if frame=='week' else f'{y:04d}-{m:02d}'
        tm=dt.isoformat() if frame=='week' else f'{y:04d}-{m:02d}-01'
        if key!=curkey:
            if cur: out.append(cur)
            curkey=key; cur={'time':tm,'open':r['open'],'high':r['high'],'low':r['low'],'close':r['close'],'volume':r.get('volume',0)}
        else:
            cur['high']=max(cur['high'],r['high']); cur['low']=min(cur['low'],r['low']); cur['close']=r['close']; cur['volume']+=r.get('volume',0)
    if cur: out.append(cur)
    return out

def payload(sym,source,rows,frame):
    rows=rows[-(120 if frame=='month' else 180 if frame=='week' else MAX_ROWS):]
    lines=trendlines(rows)
    return {'symbol':sym,'frame':frame,'source':source,'rows':rows,'ma20':ma(rows,20),'ma50':ma(rows,50),'ema20':ema(rows,20),'ema50':ema(rows,50),'bollinger':boll(rows),'macd':macd(rows),'rsi':rsi(rows),'trendline':lines[0] if lines else None,'trendlines':lines}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SRC.read_text(encoding='utf-8')); idx=[]
    for sym, obj in data.get('symbols',{}).items():
        rows=[{k:(float(v) if k!='time' else v) for k,v in r.items()} for r in obj.get('rows',[]) if r.get('time')]
        if len(rows)<30: continue
        for frame,suf in [('day',''),('week','_week'),('month','_month')]:
            fr=aggregate(rows,frame)
            if len(fr)<10: continue
            out=payload(sym,data.get('source'),fr,frame)
            (OUT/f'{sym}{suf}.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
            idx.append({'symbol':sym,'frame':frame,'rows':len(out['rows']),'path':f'/data/charts/{sym}{suf}.json'})
    (OUT/'index.json').write_text(json.dumps({'count':len(idx),'items':idx},ensure_ascii=False,indent=2),encoding='utf-8')
    print('charts',len(idx))
if __name__=='__main__': main()
