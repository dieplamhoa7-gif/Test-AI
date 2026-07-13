function normalizeNumber(s) {
  if (s == null) return null;
  const raw = String(s).trim();
  if (raw.includes(',') && raw.includes('.')) return Number(raw.replace(/\./g, '').replace(',', '.'));
  if (raw.includes(',')) return Number(raw.replace(',', '.'));
  return Number(raw);
}

function stripGulandDisclaimer(text) {
  return String(text || '')
    .replace(/Dữ liệu chỉ có giá trị tham khảo:.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Guland chỉ đăng theo thông tin đang được lưu hành.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Vui lòng phân biệt quy hoạch theo màu.*?(?=(?:\d+[\d.,]*\s*m(?:2|²)|\b(?:ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO)\b|Thông tin quy hoạch|Dữ liệu chính|$))/gi, ' ')
    .replace(/Hãy kiểm tra và xác thực lại với cơ quan nhà nước trước khi giao dịch\.?/gi, ' ');
}

function cleanLandUse(s) {
  return String(s || '')
    .replace(/^[\s\-:]+|[\s\-:]+$/g, '')
    .replace(/^(?:-|–|—)\s*/, '')
    .trim();
}

function parseGulandPopupText(text) {
  const t = stripGulandDisclaimer(text).replace(/\s+/g, ' ').trim();
  const out = { source: 'Guland popup/browser', parcel: {}, planning: [], raw_text: t };
  let m;

  // Tờ / Thửa
  if ((m = t.match(/Tờ\s*(\d+)\s*Thửa\s*(\d+)/i))) {
    out.parcel.map_sheet = m[1];
    out.parcel.parcel_no = m[2];
  }

  // Diện tích thửa
  if ((m = t.match(/(?:Diện tích(?:\s*thửa)?|Thửa\s*\d+\s*,\s*Diện tích)\s*([\d.,]+)\s*m(?:2|²)?/i))) {
    out.parcel.area_m2 = normalizeNumber(m[1]);
  }

  const codes = 'ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH|CTC|CCDVO';

  // Land use codes
  const landRegex = new RegExp(`\\b(${codes})\\b\\s*(?:[-–—]\\s*)?([^\\d]*đất[^\\d]*?)(?:\\s+([\\d.,]+)\\s*m(?:2|²)?)?(?=\\s+(?:[\\d.,]+\\s*m(?:2|²)\\s*)?(?:${codes})\\b|\\s+Khu vực|\\s+Thông tin|$)`, 'ig');
  while ((m = landRegex.exec(t))) {
    out.planning.push({ 
      code: m[1].toUpperCase(), 
      land_use: cleanLandUse(m[2]), 
      area_m2: m[3] ? normalizeNumber(m[3]) : null 
    });
  }

  // Guland often renders rows as: "391.6 m² DGT - Đất giao thông".
  const areaCodeRegex = new RegExp(`([\\d.,]+)\\s*m(?:2|²)?\\s*\\b(${codes})\\b\\s*(?:[-–—]\\s*)?([^\\d]*đất[^\\d]*?)(?=\\s+[\\d.,]+\\s*m(?:2|²)?\\s*\\b(?:${codes})\\b|\\s+Thông tin|\\s+Dữ liệu|$)`, 'ig');
  while ((m = areaCodeRegex.exec(t))) {
    const code = m[2].toUpperCase();
    const area_m2 = normalizeNumber(m[1]);
    const land_use = cleanLandUse(m[3]);
    if (!out.planning.some(r => r.code === code && r.area_m2 === area_m2 && r.land_use === land_use)) {
      out.planning.push({ code, land_use, area_m2 });
    }
  }

  // Fallback for planning
  if (!out.planning.length && (m = t.match(new RegExp(`\\b(${codes})\\b\\s*(?:[\\d.,]+\\s*m(?:2|²)?)?\\s*([^]+?)(?=\\s+Thông tin quy hoạch|\\s+Dữ liệu chính|$)`, 'i')))) {
    out.planning.push({ code: m[1].toUpperCase(), land_use: cleanLandUse(m[2]), area_m2: out.parcel.area_m2 || null });
  }

  // Quy hoạch xây dựng
  if ((m = t.match(/Thông tin quy hoạch xây dựng\s*([\d.,]+)\s*m(?:2|²)?\s*([^]+?)(?=\s+Dữ liệu chính|\s+Xem đầy đủ|$)/i))) {
    const first = (m[2] || '').trim();
    const parts = [];
    const firstUse = cleanLandUse(first.replace(/\s*Tổng\s*:.*$/i, '')); 
    if (firstUse) parts.push({ code: null, land_use: firstUse, area_m2: normalizeNumber(m[1]), kind: 'construction_planning' });
    const traffic = first.match(/([\d.,]+)\s*m(?:2|²)?\s*(đất\s+giao\s+thông)/i);
    if (traffic) parts.push({ code: 'DGT', land_use: cleanLandUse(traffic[2]), area_m2: normalizeNumber(traffic[1]), kind: 'construction_planning' });
    out.planning.push(...parts);
  }

  if ((m = t.match(/Tầng\s*:\s*([^;]+?)(?:;|\s*Mặt|$)/i))) out.height = m[1].trim();
  if ((m = t.match(/Mật\s*độ\s*xây\s*dựng\s*:?\s*([\d.,]+)\s*%?/i))) out.density = normalizeNumber(m[1]);
  if ((m = t.match(/Hệ số sử dụng đất\s*:\s*([\d.,]+)/i))) out.far = normalizeNumber(m[1]);
  if ((m = t.match(/Độ rộng đường\s*([\d.,]+)\s*m/i))) out.road_width_m = normalizeNumber(m[1]);
  if ((m = t.match(/Hướng mặt tiền\s*([^]+?)(?=\s+Dữ liệu|$)/i))) out.frontage_direction = m[1].trim();

  if (out.planning.length) {
    out.parcel.land_rows = out.planning;
    out.parcel.land_code = out.planning[0].code;
    out.parcel.land_use = out.planning[0].land_use;
    out.planning = out.planning.map((r, idx) => idx === 0 ? { ...r, height: out.height || null, density: out.density ?? null, far: out.far ?? null } : r);
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
