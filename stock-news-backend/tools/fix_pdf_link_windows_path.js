const fs=require('fs'),path=require('path');
const f=path.resolve(__dirname,'..','firebase_public','stock-report.html');
let s=fs.readFileSync(f,'utf8');
const old="function renderOutputs(r){const link=u=>API+u;const nbErr=clean(r.notebooklm_error||'');";
const neu="function renderOutputs(r){const link=u=>{const raw=String(u||'').replace(/\\\\/g,'/');const name=raw.split('/').pop();return API+'/pipeline/model3/file/'+encodeURIComponent(name)};const nbErr=clean(r.notebooklm_error||'');";
if(!s.includes(old))throw new Error('renderOutputs marker not found');
s=s.replace(old,neu);
fs.writeFileSync(f,s,'utf8');
console.log('Sanitized artifact links in stock-report frontend');
