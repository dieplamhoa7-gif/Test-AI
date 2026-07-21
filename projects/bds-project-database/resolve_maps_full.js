const fs=require('fs');
const links=[
'https://maps.app.goo.gl/D8GuCY5LefTH8JVq9',
'https://maps.app.goo.gl/GdiSL1z7fBFtk3tr8',
'https://maps.app.goo.gl/ioqJ9N2mKRyMdiAe6',
'https://maps.app.goo.gl/oHEYY6H9GGykdD9C6',
'https://maps.app.goo.gl/qDbb6mJHvwhXw4Az6',
'https://maps.app.goo.gl/t178LDzcrFtjxgEz9'];
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
 fs.writeFileSync('C:/Users/HoaD-CVDT/.openclaw/workspace/projects/bds-project-database/map_link_resolution_full.json',JSON.stringify(out,null,2),'utf8');
 console.log(JSON.stringify(out,null,2));
})();
