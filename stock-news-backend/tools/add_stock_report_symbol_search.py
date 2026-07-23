from pathlib import Path
import re
p=Path('firebase_public/stock-report.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Add datalist to ticker input so SSI and other symbols are searchable/selectable.
s=s.replace('<input id="ticker" placeholder="MWG" value="MWG"/>', '<input id="ticker" list="tickerOptions" placeholder="Nhập mã: SSI, MWG..." value="MWG" autocomplete="off"/><datalist id="tickerOptions"></datalist>')
js = r"""
async function loadTickerOptions(){
  const dl=document.getElementById('tickerOptions');
  if(!dl)return;
  try{
    const r=await fetch('/data/market_symbols.json?t='+Date.now(),{cache:'no-store'});
    const data=await r.json();
    const arr=Array.isArray(data)?data:(data.symbols||data.data||data.items||[]);
    const rows=arr.map(x=>typeof x==='string'?{symbol:x}:x).filter(Boolean);
    const html=rows.map(x=>{
      const sym=String(x.symbol||x.ticker||x.code||x.Symbol||'').toUpperCase().trim();
      if(!sym)return '';
      const name=String(x.name||x.company_name||x.fullname||x.exchange||'').replace(/"/g,'&quot;');
      return `<option value="${sym}" label="${name}"></option>`;
    }).join('');
    if(html)dl.innerHTML=html;
  }catch(e){
    try{
      const r=await fetch('/data/market_data.json?t='+Date.now(),{cache:'no-store'});
      const data=await r.json();
      const rows=Array.isArray(data)?data:(data.stocks||data.data||data.items||[]);
      dl.innerHTML=rows.map(x=>{
        const sym=String(x.symbol||x.ticker||x.code||'').toUpperCase().trim();
        const name=String(x.name||x.company_name||'').replace(/"/g,'&quot;');
        return sym?`<option value="${sym}" label="${name}"></option>`:'';
      }).join('');
    }catch(_){ }
  }
}
loadTickerOptions();
"""
if 'function loadTickerOptions()' not in s:
    s=s.replace("$('ticker').addEventListener('keydown'", js+"\n$('ticker').addEventListener('keydown'")
p.write_text(s,encoding='utf-8')
