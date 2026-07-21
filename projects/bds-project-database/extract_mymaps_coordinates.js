const fs=require('fs');
const base='C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database';
const masters=JSON.parse(fs.readFileSync(base+'/project_popup_master_clean.json','utf8'));
const mids=[...new Set(masters.flatMap(r=>[...(r.map_urls||'').matchAll(/mid=([A-Za-z0-9_-]+)/g)].map(m=>m[1])) )];
function coordsFromKml(txt){
 const out=[]; const re=/<Placemark[\s\S]*?<\/Placemark>/g; let m;
 while((m=re.exec(txt))){ const block=m[0]; const name=(block.match(/<name>([\s\S]*?)<\/name>/)||[])[1]?.replace(/<!\[CDATA\[|\]\]>/g,'').trim()||''; const cm=block.match(/<coordinates>([\s\S]*?)<\/coordinates>/); if(!cm) continue; const first=cm[1].trim().split(/\s+/)[0]; const [lng,lat]=first.split(','); if(lat&&lng) out.push({name,lat,lng}); }
 return out;
}
(async()=>{
 const results=[];
 for(const mid of mids){
  const url=`https://www.google.com/maps/d/kml?mid=${mid}&forcekml=1`;
  try{const r=await fetch(url); const txt=await r.text(); const pts=coordsFromKml(txt); results.push({mid,status:r.status,points:pts.slice(0,200),count:pts.length});}
  catch(e){results.push({mid,error:String(e),points:[],count:0});}
 }
 fs.writeFileSync(base+'/mymaps_kml_points.json',JSON.stringify(results,null,2),'utf8');
 console.log(JSON.stringify({mids:mids.length,total_points:results.reduce((a,x)=>a+x.count,0),with_points:results.filter(x=>x.count).length},null,2));
})();
