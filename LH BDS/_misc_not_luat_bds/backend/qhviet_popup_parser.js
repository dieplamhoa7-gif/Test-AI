// Lightweight parser for QH Viet popup text captured from browser automation.
// Parses deterministic fields only; no AI interpretation.

function parseQhVietPopupText(text) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  const out = {
    source: 'QH Viet popup',
    parcel: {},
    planning: [],
    raw_text: t,
  };

  let m;
  if ((m = t.match(/Số\s*tờ\s*(\d+)\s*Số\s*thửa\s*(\d+)/i))) {
    out.parcel.map_sheet = m[1];
    out.parcel.parcel_no = m[2];
  }
  if ((m = t.match(/Diện\s*tích\s*(?:thửa)?\s*([\d.,]+)\s*m(?:2|²)?/i))) {
    out.parcel.area_m2 = normalizeNumber(m[1]);
  }

  const landRows = [];
  const codes = 'ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD|HCD|HH';
  const landRegex = new RegExp(`\\b(${codes})\\b\\s*([^\\d]*?Đất[^\\d]*?)(?:\\s+([\\d.,]+)\\s*m(?:2|²)?)?(?=\\s+(?:${codes})\\b|\\s+Khu vực|\\s+Thông tin|$)`, 'ig');
  while ((m = landRegex.exec(t))) {
    landRows.push({
      code: m[1].toUpperCase(),
      land_use: (m[2] || '').trim(),
      area_m2: m[3] ? normalizeNumber(m[3]) : null,
    });
  }
  if (landRows.length) {
    out.parcel.land_rows = landRows;
    out.parcel.land_code = landRows[0].code;
    out.parcel.land_use = landRows[0].land_use;
    out.parcel.land_area_m2 = landRows[0].area_m2;
    out.planning = landRows.map(r => ({ area_m2: r.area_m2, land_use: r.land_use, code: r.code }));
  }

  if ((m = t.match(/Khu\s*vực\s*cũ\s*:?\s*([^]+?)(?:\s+Khu\s*vực\s*mới|\s+Thông tin|\s+Xem quy hoạch|$)/i))) {
    out.old_area_name = cleanQhValue(m[1]);
  }
  const newMatches = [...t.matchAll(/Khu\s*vực\s*mới\s*:?\s*([^]+?)(?=\s+page:\s*\d+|\s+parcel:\s*\d+|\s+new_ward_id|\s+Tọa\s*độ|\s+Khu\s*vực\s*cũ|\s+Thông tin|\s+Xem quy hoạch|\s+Quy hoạch|\s+Loại\s*đất|\s+Ký\s*hiệu|\s+Đất\s+\S+|$)/ig)];
  if (newMatches.length) {
    out.area_name = cleanQhValue(newMatches[newMatches.length - 1][1]);
  }
  if (!out.area_name && (m = t.match(/Khu\s*vực\s*:?\s*([^]+?)(?=\s+Tọa\s*độ|\s+Khu\s*vực\s+cũ|$)/i))) {
    out.area_name = cleanQhValue(m[1]);
  }
  if ((m = t.match(/(Quyết\s*định\s+[^]+?)(?=\s+Làm\s+mờ\s+nền|\s+Giao\s+thông|\s+Thông\s+tin\s+quy\s+hoạch|$)/i))) {
    out.plan_name = cleanQhValue(m[1]);
    out.planning.push({ source: 'QH Việt', plan_name: out.plan_name });
  }

  if ((m = t.match(/(?:Quy\s*hoạch|Loại\s*đất)\s*:\s*([^]+?)(?=\s+Loại\s*đất\s*:|\s+Ký\s*hiệu|\s+Hê\S*\s+s\S*\s+s\S*\s*d\S*ng|\s+M\S*t\s+đ\S*\s+x\S*y\s+d\S*ng|\s+Tên\s+khu|\s+Mô\s*ta\S*|$)/i))) {
    out.parcel.land_use = m[1].trim();
  }
  if ((m = t.match(/Ký\s*hiệu\s*loại\s*đất\s*:?\s*([A-Z0-9]+)/i))) {
    out.parcel.land_code = m[1].toUpperCase();
  }
  if ((m = t.match(/Hê\S*\s*s\S*\s*s\S*\s*d\S*ng\s*:?\s*([\d.,]+)/i))) {
    out.far = normalizeNumber(m[1]);
  }
  if ((m = t.match(/M\S*t\s+đ\S*\s+x\S*y\s+d\S*ng\s*:?\s*([\d.,]+)/i))) {
    out.density = normalizeNumber(m[1]);
  }
  if ((m = t.match(/T\S*ng\s+cao\s+x\S*y\s+d\S*ng\s*:?\s*([\d.,]+\s*-\s*[\d.,]+|[\d.,]+)/i))) {
    out.height = String(m[1]).replace(/\s+/g, '');
  }
  if ((m = t.match(/Tên\s*khu\s*ch(?:ứ|ứ)c\s*năng\s*:?\s*([^]+?)(?=\s+Mô\s*tả|\s+Mô\s*tả|$)/i))) {
    out.functional_area = cleanQhValue(m[1]);
  }
  if ((m = t.match(/Mô\s*ta\S*\s*:?\s*([^]+?)(?=\s+Hiện\s+thửa|\s+Lưu\s+điểm|\s+Mã\s+chia|\s+Tọa\s+độ\s+ranh|\s+Xem quy hoạch|$)/i))) {
    out.description = cleanQhValue(m[1]);
  }
  // If the page body repeated the ward after parcel fields, trim the area name back to the administrative label.
  if (out.area_name) out.area_name = out.area_name.replace(/\s+\d+(?:[.,]\d+)?\s*m\s*2.*$/i, '').trim();

  if (out.parcel.land_code || out.parcel.land_use || out.far || out.density || out.height || out.functional_area) {
    const qvPlan = {
      source: 'QH Việt',
      code: out.parcel.land_code || null,
      land_use: out.parcel.land_use || out.functional_area || null,
      far: out.far ?? null,
      density: out.density ?? null,
      height: out.height || null,
      functional_area: out.functional_area || null,
      description: out.description || null,
    };
    out.planning.unshift(qvPlan);
  }

  return out;
}

function cleanQhValue(s) {
  return String(s || '').replace(/\s+page:\s*\d+.*$/i, '').replace(/\s+parcel:\s*\d+.*$/i, '').replace(/\s+new_ward_id.*$/i, '').replace(/\s+/g, ' ').trim();
}

function normalizeNumber(s) {
  if (s == null) return null;
  const raw = String(s).trim();
  if (raw.includes(',') && raw.includes('.')) return Number(raw.replace(/\./g, '').replace(',', '.'));
  if (raw.includes(',')) return Number(raw.replace(',', '.'));
  return Number(raw);
}

function formatQhVietPopup(parsed, sourceUrl) {
  return [
    'Nguồn QH Việt popup:',
    sourceUrl ? `- Link: ${sourceUrl}` : null,
    parsed.parcel.map_sheet ? `- Tờ/thửa: ${parsed.parcel.map_sheet}/${parsed.parcel.parcel_no}` : null,
    parsed.parcel.area_m2 ? `- Diện tích thửa: ${parsed.parcel.area_m2} m²` : null,
    parsed.parcel.land_code ? `- Quy hoạch: ${parsed.parcel.land_code} - ${parsed.parcel.land_use || ''}` : null,
    parsed.area_name ? `- Khu vực: ${parsed.area_name}` : null,
    '- Ghi chú: dữ liệu QH Việt là nguồn tham khảo/đối chiếu.',
  ].filter(Boolean).join('\n');
}

module.exports = { parseQhVietPopupText, formatQhVietPopup };

if (require.main === module) {
  const input = process.argv.slice(2).join(' ');
  const parsed = parseQhVietPopupText(input);
  console.log(JSON.stringify(parsed, null, 2));
  console.log(formatQhVietPopup(parsed));
}
