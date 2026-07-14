from pathlib import Path
p=Path('firebase_public/pattern-reco.html')
s=p.read_text(encoding='utf-8')
old="function addLineFor(key,points,color,title){if(!points||points.length<2)return;const s=chart.addLineSeries({color:rgba(color,.22),lineWidth:1,priceLineVisible:false,lastValueVisible:false,title:title||''});s.setData(points.map(p=>({time:p.time,value:+p.value})).filter(p=>p.time&&isFinite(p.value)));(overlayMap[key]||=[]).push({series:s,color})}"
new=old+"function addHorizontalLevel(key,label,value,color,rows){value=+value;if(!isFinite(value)||!rows||rows.length<2)return;addLineFor(key,[{time:rows[0].time,value},{time:rows[rows.length-1].time,value}],color,label)}function addEngineOverlay(key,pat,rows){const lv=pat.levels||{},dir=pat.direction||'',color=lineColor(dir);Object.entries(lv).forEach(([name,val])=>{if(typeof val==='number')addHorizontalLevel(key,name,val,color,rows)});['support','resistance','neckline','target','stop','breakout','lower','upper'].forEach(name=>{if(lv[name]!=null)addHorizontalLevel(key,name,lv[name],color,rows)});if(Object.keys(lv).length===0&&pat.price)addHorizontalLevel(key,pat.type,pat.price,color,rows)}function fmtLevels(lv){lv=lv||{};const ent=Object.entries(lv).filter(([k,v])=>typeof v==='number'||typeof v==='string');if(!ent.length)return '<div class=\"level-empty\">No explicit chart level</div>';return '<div class=\"level-grid\">'+ent.map(([k,v])=>`<span class=\"level-chip\"><b>${k}</b>${v}</span>`).join('')+'</div>'}"
if old not in s: raise SystemExit('addLineFor anchor not found')
s=s.replace(old,new)
old2="const enginePats=getPatterns(selected).map((p,i)=>({...p,_hoverKey:'engine'+i,_idx:i+1,_src:'engine'}));const pats=[...chartPats,...enginePats].slice(0,80);"
new2="const enginePats=getPatterns(selected).map((p,i)=>({...p,_hoverKey:'engine'+i,_idx:i+1,_src:'engine'}));enginePats.forEach(p=>addEngineOverlay(p._hoverKey,p,chartData.rows||[]));const pats=[...chartPats,...enginePats].slice(0,80);"
if old2 not in s: raise SystemExit('enginePats anchor not found')
s=s.replace(old2,new2)
old3='<div class="levels">${JSON.stringify(p.levels||{},null,1)}</div>'
new3='${fmtLevels(p.levels)}'
if old3 not in s: raise SystemExit('levels anchor not found')
s=s.replace(old3,new3)
css_anchor='.levels{font-family:ui-monospace,Consolas,monospace;color:#b9cbe0;font-size:11px;background:#061424;border:1px solid rgba(145,167,194,.12);border-radius:10px;padding:8px;margin-top:8px;white-space:pre-wrap}'
css_new=css_anchor+'.level-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:9px}.level-chip{display:flex;justify-content:space-between;gap:8px;align-items:center;border:1px solid rgba(145,167,194,.16);background:#061424;border-radius:10px;padding:7px 9px;color:#cfe3ff;font-size:12px}.level-chip b{color:#91a7c2;font-weight:700;text-transform:capitalize}.level-empty{margin-top:9px;color:#91a7c2;font-size:12px;border:1px dashed rgba(145,167,194,.18);border-radius:10px;padding:8px;background:#061424}'
if css_anchor not in s: raise SystemExit('css anchor not found')
s=s.replace(css_anchor,css_new)
p.write_text(s,encoding='utf-8')
print('patched')
