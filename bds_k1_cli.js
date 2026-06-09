const { lookupHcmPlanning, summarize } = require('./bds_planning_checker');
const { lookupK1LandFee } = require('./k1_land_fee_lookup');
(async()=>{
  const lat=Number(process.argv[2]), lon=Number(process.argv[3]);
  const landUse=process.argv[4]||'ODT';
  const position=process.argv[5]||'VT1';
  if(!Number.isFinite(lat)||!Number.isFinite(lon)) throw new Error('lat lon required');
  const raw=await lookupHcmPlanning(lat, lon);
  const sum=summarize(raw);
  const k1=await lookupK1LandFee({lat, lon, geoLocation:sum.location||{}, text:'', landUse, position, planningMultiplier:1});
  console.log(JSON.stringify({ok:true, location:sum.location||{}, k1}, null, 2));
})().catch(e=>{console.log(JSON.stringify({ok:false,error:String(e&&e.message||e)})); process.exit(1);});
