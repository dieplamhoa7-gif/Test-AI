function normalizeNumber(s) {
  if (s == null) return null;
  const raw = String(s).trim();
  if (raw.includes(',') && raw.includes('.')) return Number(raw.replace(/\./g, '').replace(',', '.'));
  if (raw.includes(',')) return Number(raw.replace(',', '.'));
  return Number(raw);
}

const CODES = 'ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO';
const CODE_RE = new RegExp(`\\b(${CODES})\\b`, 'i');

function stripGulandDisclaimer(text) {
  return String(text || '')
    .replace(/Dữ liệu chỉ có giá trị tham khảo:.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Guland chỉ đăng theo thông tin đang được lưu hành.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Vui lòng phân biệt quy hoạch theo màu.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Hãy kiểm tra và xác thực lại với cơ quan nhà nước trước khi giao dịch\.?/gi, ' ');
}
function cleanLandUse(s) {
  return String(s || '')
    .replace(/Tên chủ:.*$/i, '')
    .replace(/Tầng\s*:.*$/i, '')
    .replace(/Mật độ\s*:.*$/i, '')
    .replace(/Loại đất quy hoạch.*$/i, '')
    .replace(/Thông tin mô tả thửa.*$/i, '')
    .replace(/thông tin quy hoạch chi tiết.*$/i, '')
    .replace(/Thu gọn thông tin.*$/i, '')
    .replace(/^[\s\-–—:]+|[\s\-–—:]+$/g, '')
    .trim();
}
function uniqueRows(rows) {
  const seen = new Set();
  return rows.filter(r => {
    const k = [r.kind||'', r.code||'', r.land_use||'', r.area_m2||''].join('|');
    if (seen.has(k)) return false; seen.add(k); return true;
  });
}
function parseGulandPopupText(text) {
  const full = stripGulandDisclaimer(text).replace(/\s+/g, ' ').trim();
  const out = { source: 'Guland popup/browser', parcel: {}, planning: [], raw_text: full };
  let m;
  const parcelMatch = full.match(/Tờ\s*(\d+)\s*Thửa\s*(\d+)\s*,\s*Diện tích\s*([\d.,]+)\s*m(?:2|²)?/i);
  if (parcelMatch) {
    out.parcel.map_sheet = parcelMatch[1];
    out.parcel.parcel_no = parcelMatch[2];
    out.parcel.area_m2 = normalizeNumber(parcelMatch[3]);
  } else {
    if ((m = full.match(/Tờ\s*(\d+)\s*Thửa\s*(\d+)/i))) { out.parcel.map_sheet=m[1]; out.parcel.parcel_no=m[2]; }
    if ((m = full.match(/Diện tích\s*([\d.,]+)\s*m(?:2|²)?/i))) out.parcel.area_m2 = normalizeNumber(m[1]);
  }

  let parcelSeg = full;
  if (parcelMatch) parcelSeg = full.slice(parcelMatch.index + parcelMatch[0].length);
  parcelSeg = parcelSeg.split(/Thông tin quy hoạch xây dựng/i)[0];
  parcelSeg = parcelSeg.split(/Tên chủ:/i)[0];
  const landRows = [];
  const rowRe = new RegExp(`\\b(${CODES})\\b\\s*([\\d.,]+)\\s*m(?:2|²)?\\s*([^]+?)(?=\\s+\\b(?:${CODES})\\b\\s*[\\d.,]+\\s*m(?:2|²)?|$)`, 'ig');
  while ((m = rowRe.exec(parcelSeg))) landRows.push({ code:m[1].toUpperCase(), area_m2:normalizeNumber(m[2]), land_use:cleanLandUse(m[3]) });
  const areaCodeRe = new RegExp(`([\\d.,]+)\\s*m(?:2|²)?\\s*\\b(${CODES})\\b\\s*(?:[-–—]\\s*)?([^]+?)(?=\\s+[\\d.,]+\\s*m(?:2|²)?\\s*\\b(?:${CODES})\\b|$)`, 'ig');
  while ((m = areaCodeRe.exec(parcelSeg))) landRows.push({ code:m[2].toUpperCase(), area_m2:normalizeNumber(m[1]), land_use:cleanLandUse(m[3]) });

  const buildMatch = full.match(/Thông tin quy hoạch xây dựng\s*([\d.,]+)\s*m(?:2|²)?\s*([^]+?)(?=\s+Thông tin mô tả thửa|\s+Dữ liệu chính|\s+Xem đầy đủ|$)/i);
  if (buildMatch) {
    const seg = buildMatch[2];
    const landUse = cleanLandUse(seg.replace(/Tầng\s*:.*$/i,''));
    const r = { code:null, land_use:landUse, area_m2:normalizeNumber(buildMatch[1]), kind:'construction_planning' };
    if ((m = seg.match(/Tầng\s*:\s*([^;]+?)(?:;|$)/i))) { out.height=m[1].trim(); r.height=out.height; }
    if ((m = seg.match(/Mật\s*độ\s*:?\s*([\d.,]+)\s*%?/i))) { out.density=normalizeNumber(m[1]); r.density=out.density; }
    if ((m = seg.match(/Hệ số sử dụng đất\s*:?\s*([\d.,]+)/i))) { out.far=normalizeNumber(m[1]); r.far=out.far; }
    if (r.land_use) landRows.push(r);
  }
  if ((m = full.match(/Độ rộng đường\s*([\d.,]+)\s*m/i))) out.road_width_m = normalizeNumber(m[1]);
  if ((m = full.match(/Hướng mặt tiền\s*([^]+?)(?=\s+thông tin quy hoạch|\s+Thu gọn|$)/i))) out.frontage_direction = cleanLandUse(m[1]);

  out.planning = uniqueRows(landRows.filter(r => r.land_use || r.code || r.area_m2));
  if (out.planning.length) {
    out.parcel.land_rows = out.planning.filter(r => r.kind !== 'construction_planning');
    const first = out.parcel.land_rows[0] || out.planning[0];
    out.parcel.land_code = first.code || null;
    out.parcel.land_use = first.land_use || null;
    out.planning = out.planning.map((r, idx) => idx===0 ? {...r, height:out.height||r.height||null, density:out.density??r.density??null, far:out.far??r.far??null} : r);
  }
  return out;
}
function formatGulandPopup(parsed, sourceUrl) {
  return [
    'Nguồn Guland popup/browser:',
    sourceUrl ? `- Link: ${sourceUrl}` : null,
    parsed.parcel.map_sheet ? `- Tờ/thửa: ${parsed.parcel.map_sheet}/${parsed.parcel.parcel_no}` : null,
    parsed.parcel.area_m2 ? `- Diện tích thửa: ${parsed.parcel.area_m2} m²` : null,
    parsed.parcel.land_code ? `- Quy hoạch: ${parsed.parcel.land_code} - ${parsed.parcel.land_use || ''}` : null,
  ].filter(Boolean).join('\n');
}
module.exports = { parseGulandPopupText, formatGulandPopup };
