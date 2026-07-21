const fs=require('fs');
const text=fs.readFileSync('C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database/teams_candidate_chunks.md','utf8');
const links=[...new Set([...text.matchAll(/https:\/\/maps\.app\.goo\.gl\/[A-Za-z0-9]+/g)].map(m=>m[0]))].sort();
(async()=>{
 let out=[];
 for(const url of links){
  try{
   const r=await fetch(url,{redirect:'manual'});
   let loc=r.headers.get('location')||'';
   let m=loc.match(/(?:search\/|@)(-?\d+\.\d+),\+?\s*(-?\d+\.\d+)/);
   if(!m) m=loc.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/);
   out.push({url,status:r.status,location:loc,lat:m?.[1]||'',lng:m?.[2]||''});
  }catch(e){out.push({url,error:String(e)});}
 }
 fs.writeFileSync('C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database/map_link_resolution_all.json',JSON.stringify(out,null,2),'utf8');
 console.log(JSON.stringify(out,null,2));
})();
