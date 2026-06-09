const api='https://architects-non-skirts-learners.trycloudflare.com';
const body={lat:10.788423362693855,lon:106.69143208535428};
(async()=>{
 for (const path of ['/nvtc/k1-lookup','/planning/lookup']){
  const r=await fetch(api+path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
  const j=await r.json();
  console.log('\n--- '+path+' ---');
  console.log('ok:',j.ok,'status:',r.status);
  console.log('location:', j.location?.display_name);
  if(path.includes('nvtc')) {
    console.log('road:', j.k1?.match?.road);
    console.log('segment:', j.k1?.match?.segment);
    console.log('base:', j.k1?.calc?.baseThousandPerM2);
    console.log('K:', j.k1?.calc?.marketK);
    console.log('adjusted_million_m2:', j.k1?.calc?.adjustedMillionPerM2);
  } else {
    console.log('project:', j.planning?.planning_project?.TenDoAn);
    console.log('qh:', j.planning?.planning_project?.TenQH);
    console.log('soqd:', j.planning?.planning_project?.SoQD);
    console.log('ngay:', j.planning?.planning_project?.NgayDuyet);
    console.log('status:', j.planning?.planning_project?.TrangThai);
    const mixed=j.planning?.official_lot?.mixed?.[0] || j.planning?.official_lot?.mixedFirst || null;
    console.log('official_lot:', JSON.stringify(j.planning?.official_lot || null).slice(0,800));
  }
 }
 const prompt='Bạn là analyst R&D bất động sản cho LH Real Estate. Test tọa độ: 10.788423362693855, 106.69143208535428. Giao dịch: Mua. Loại tài sản: Đất/Nhà phố. MĐSDĐ: ODT. Đặc tính: Mặt tiền. Trả kết quả ngắn theo 5 mục: vị trí, comparable, pháp lý/quy hoạch, giá nếu có căn cứ, checklist. Không bịa số chính thức.';
 const r=await fetch(api+'/v1/chat/completions',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({model:'APIBDS',messages:[{role:'user',content:prompt}],max_tokens:1000})});
 const j=await r.json();
 console.log('\n--- /rd ai ---');
 console.log('ok status:',r.status);
 console.log(j.choices?.[0]?.message?.content || JSON.stringify(j,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
