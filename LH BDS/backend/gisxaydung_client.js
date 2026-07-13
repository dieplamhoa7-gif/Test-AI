const GIS_BASE = 'https://api-gisxaydung.tphcm.gov.vn/arcm/rest/services';

async function queryPoint(servicePath, lat, lng) {
  const url = `${GIS_BASE}/${servicePath}/query?` + new URLSearchParams({
    f: 'json',
    geometry: `${lng},${lat}`,
    geometryType: 'esriGeometryPoint',
    inSR: '4326',
    spatialRel: 'esriSpatialRelIntersects',
    outFields: '*',
    returnGeometry: 'false',
  });
  const r = await fetch(url, { headers: { accept: 'application/json' } });
  if (!r.ok) throw new Error(`${servicePath} HTTP ${r.status}`);
  const j = await r.json();
  if (j.error) throw new Error(`${servicePath}: ${j.error.message || JSON.stringify(j.error)}`);
  return j.features?.map(f => f.attributes || {}) || [];
}

function firstNonEmpty(...xs) {
  for (const x of xs) if (x !== null && x !== undefined && String(x).trim() !== '') return x;
  return null;
}

function toNum(v) {
  if (v === null || v === undefined || v === '') return null;
  const n = Number(String(v).replace(',', '.'));
  return Number.isFinite(n) ? n : null;
}

function normalizeOfficialPlanning(parcel, landRows, indicatorRows, provinceRows) {
  const land = landRows[0] || {};
  const ind = indicatorRows[0] || {};
  const prov = provinceRows[0] || {};
  const density = toNum(firstNonEmpty(ind.MatDoXayDung, ind.MatDoXayDungTrungBinh, land.MatDoXayDung, prov.MatDoXayDungTrungBinh));
  const far = toNum(firstNonEmpty(ind.HeSoSuDungDat, land.HeSoSuDungDat, prov.HeSoSuDungDat));
  return {
    ok: true,
    source: 'GIS Xây dựng TP.HCM',
    parcel: parcel ? {
      map_sheet: firstNonEmpty(parcel.SoTo, parcel.SoHieuToBanDoCu),
      parcel_no: firstNonEmpty(parcel.SoThua, parcel.SoThuTuThuaCu),
      area_m2: toNum(firstNonEmpty(parcel.DienTich, parcel.DienTichPhapLy)),
      land_code: firstNonEmpty(parcel.KyHieuLoaiDat, parcel.DMMucDichSuDungDat),
      land_use: firstNonEmpty(parcel.DMMucDichSuDungDat, parcel.KyHieuLoaiDat),
      address: firstNonEmpty(parcel.DiaChi, parcel.SoNhaMoi, parcel.SoNha),
      ward: firstNonEmpty(parcel.TenXaMoi, parcel.MaPhuongXaMoi, parcel.MaPhuongXa),
      district_code: parcel.MaQuanHuyen || null,
    } : null,
    planning: {
      land_use: firstNonEmpty(land.TenKhuChucNang, land.MucDichSDDTT12, land.MucDichSuDung, prov.MucDichSuDung),
      land_code: firstNonEmpty(land.MaQuyUoc, land.KyHieuTT12, land.KyHieuLoaiDat, prov.KyHieuLoaiDat),
      project_id: firstNonEmpty(land.MaDuAn, ind.MaDuAn, prov.MaDuAn),
      planning_type: firstNonEmpty(land.PhanLoaiQuyHoach, ind.PhanLoaiQuyHoach),
      construction_function: firstNonEmpty(ind.ChucNangCongTrinh, land.TenCongTrinhXayDung),
      height: firstNonEmpty(ind.TangCaoXayDung, ind.ChieuCao, land.TangCaoXayDung),
      density,
      far,
      population: firstNonEmpty(ind.DanSo, ind.QuyMoDanSo),
      area_m2: toNum(firstNonEmpty(ind.DienTich, land.DienTich)),
    },
    raw: { parcel, landRows, indicatorRows, provinceRows },
  };
}

async function lookupGisXayDung(lat, lng) {
  const [parcels, landRows, indicatorRows, provinceRows] = await Promise.all([
    queryPoint('HCM/ThuaDat/FeatureServer/0', lat, lng).catch(e => ({ __error: e.message })),
    queryPoint('HCM/SuDungDat_QHPK_HCM/FeatureServer/2', lat, lng).catch(e => ({ __error: e.message })),
    queryPoint('HCM/SuDungDat_QHPK_HCM/FeatureServer/3', lat, lng).catch(e => ({ __error: e.message })),
    queryPoint('HCM/QHCTinh_SDD_2025/FeatureServer/1', lat, lng).catch(e => ({ __error: e.message })),
  ]);
  const errors = [parcels, landRows, indicatorRows, provinceRows].filter(x => x && x.__error).map(x => x.__error);
  const result = normalizeOfficialPlanning(
    Array.isArray(parcels) ? parcels[0] : null,
    Array.isArray(landRows) ? landRows : [],
    Array.isArray(indicatorRows) ? indicatorRows : [],
    Array.isArray(provinceRows) ? provinceRows : [],
  );
  if (errors.length) result.errors = errors;
  result.ok = !!(result.parcel || result.planning?.land_use || result.planning?.height || result.planning?.density);
  return result;
}

module.exports = { lookupGisXayDung };
