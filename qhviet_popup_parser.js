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
  const codes = 'ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD';
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

  if ((m = t.match(/Khu\s*vực\s*mới\s*([^]+?)(?:\s+Thông tin|$)/i))) {
    out.area_name = m[1].trim();
  }

  return out;
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
