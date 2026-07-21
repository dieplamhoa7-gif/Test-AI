const fs=require('fs');
const base='C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database';
const masters=JSON.parse(fs.readFileSync(base+'/project_master_curated_deduped.json','utf8'));
let existing=[]; try{existing=JSON.parse(fs.readFileSync(base+'/map_link_resolution_all.json','utf8'));}catch{}
const byUrl=new Map(existing.map(x=>[x.url,x]));
const re=/https?:\/\/(?:maps\.app\.goo\.gl|goo\.gl\/maps|www\.google\.com\/maps)[^\s)>\]]+/ig;
const urls=[...new Set(masters.flatMap(r=>[...(r.map_urls||'').matchAll(re)].map(m=>m[0].replace(/[.,;)]+$/,''))))];
function coordsFrom(loc){
  loc=decodeURIComponent(loc||'');
  let m=loc.match(/[?&]ll=(-?\d+\.\d+),\s*(-?\d+\.\d+)/); if(m)return [m[1],m[2]];
  m=loc.match(/[?&]q=(-?\d+\.\d+),\s*(-?\d+\.\d+)/); if(m)return [m[1],m[2]];
  m=loc.match(/(?:search\/|@)(-?\d+\.\d+),\+?\s*(-?\d+\.\d+)/); if(m)return [m[1],m[2]];
  m=loc.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/); if(m)return [m[1],m[2]];
  return ['',''];
}
(async()=>{
 let changed=0;
 for(const url of urls){
  if(byUrl.has(url) && byUrl.get(url).lat && byUrl.get(url).lng) continue;
  try{
   let loc=url;
   let status='direct';
   if(url.includes('maps.app.goo.gl')||url.includes('goo.gl/maps')){
    const r=await fetch(url,{redirect:'manual'}); status=r.status; loc=r.headers.get('location')||'';
   }
   const [lat,lng]=coordsFrom(loc||url);
   byUrl.set(url,{url,status,location:loc,lat,lng}); changed++;
  }catch(e){byUrl.set(url,{url,error:String(e),lat:'',lng:''});}
 }
 const out=[...byUrl.values()].sort((a,b)=>a.url.localeCompare(b.url));
 fs.writeFileSync(base+'/map_link_resolution_all.json',JSON.stringify(out,null,2),'utf8');
 console.log(JSON.stringify({urls:urls.length,total:out.length,resolved:out.filter(x=>x.lat&&x.lng).length,changed},null,2));
})();
