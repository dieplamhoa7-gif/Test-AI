from pathlib import Path
p=Path('firebase_public/pattern-reco.html')
s=p.read_text(encoding='utf-8')
old="(d.patterns||[]).forEach((p,i)=>{const key='p'+i,color=lineColor(p.direction);(p.lines||[]).forEach(l=>addLineFor(key,l.points,color,p.type));if(p.time)markerBase.push({key,time:p.time,position:String(p.direction).includes('bear')?'aboveBar':'belowBar',baseColor:color,color,shape:String(p.direction).includes('bear')?'arrowDown':'arrowUp',shortText:String(i+1),fullText:`${i+1}. ${p.type}`})});"
new="(d.patterns||[]).forEach((p,i)=>{const key='p'+i,color=lineColor(p.direction);let pointNo={top:0,bottom:0,peak:0,trough:0,high:0,low:0};(p.lines||[]).forEach(l=>{const nm=String(l.name||l.type||'').toLowerCase();if(l.type==='point'||(l.points||[]).length===1){const pt=(l.points||[])[0];if(!pt)return;const isBottom=nm.includes('bottom')||nm.includes('trough')||nm==='low';const base=isBottom?'Đáy':'Đỉnh';const bucket=isBottom?'bottom':'top';pointNo[bucket]=(pointNo[bucket]||0)+1;markerBase.push({key,time:pt.time,position:isBottom?'belowBar':'aboveBar',baseColor:color,color,shape:isBottom?'arrowUp':'arrowDown',shortText:`${base} ${pointNo[bucket]}`,fullText:`${base} ${pointNo[bucket]} • ${p.type}`});}else addLineFor(key,l.points,color,p.type)});if(p.time)markerBase.push({key,time:p.time,position:String(p.direction).includes('bear')?'aboveBar':'belowBar',baseColor:color,color,shape:String(p.direction).includes('bear')?'circle':'circle',shortText:String(i+1),fullText:`${i+1}. ${p.type}`})});"
if old not in s:
    raise SystemExit('pattern loop anchor not found')
s=s.replace(old,new)
old2="candleSeries.setMarkers(markerBase.map(m=>({...m,text:m.shortText})).slice(-60));"
new2="candleSeries.setMarkers(markerBase.map(m=>({...m,text:m.shortText})).slice(-120));"
s=s.replace(old2,new2)
p.write_text(s,encoding='utf-8')
print('patched peak/bottom annotations')
