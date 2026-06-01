// Minimal Guland popup parser.
// Works with rough browser text fallback: deterministic extraction only.

function normalizeNumber(s) {
  if (s == null) return null;
  const raw = String(s).trim();
  if (raw.includes(',') && raw.includes('.')) return Number(raw.replace(/\./g, '').replace(',', '.'));
  if (raw.includes(',')) return Number(raw.replace(',', '.'));
  return Number(raw);
}

function parseGulandPopupText(text) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  const out = { source: 'Guland popup/browser', parcel: {}, planning: [], raw_text: t };
  let m;
  if ((m = t.match(/Tờ\s*(\d+)\s*Thửa\s*(\d+)/i))) {
    out.parcel.map_sheet = m[1];
    out.parcel.parcel_no = m[2];
  }
  if ((m = t.match(/Diện\s*tích\s*(?:thửa)?\s*([\d.,]+)\s*m(?:2|²)?/i))) {
    out.parcel.area_m2 = normalizeNumber(m[1]);
  }
  const codes = 'ODT|ONT|CLN|LUA|SKC|TMD|TMDV|DGT|DKV|DHT|DTT|DVH|TMN|SON|HNK|BHK|NTS|RSX|RPH|RDD';
  const landRegex = new RegExp(`\\b(${codes})\\b\\s*([^\\d]*?Đất[^\\d]*?)(?:\\s+([\\d.,]+)\\s*m(?:2|²)?)?(?=\\s+(?:${codes})\\b|\\s+Khu vực|\\s+Thông tin|$)`, 'ig');
  while ((m = landRegex.exec(t))) {
    out.planning.push({ code: m[1].toUpperCase(), land_use: (m[2] || '').trim(), area_m2: m[3] ? normalizeNumber(m[3]) : null });
  }
  if (out.planning.length) {
    out.parcel.land_rows = out.planning;
    out.parcel.land_code = out.planning[0].code;
    out.parcel.land_use = out.planning[0].land_use;
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
    '- Ghi chú: dữ liệu browser/popup Guland là nguồn đối chiếu, cần so với nguồn chính thống nếu có.'
  ].filter(Boolean).join('\n');
}

module.exports = { parseGulandPopupText, formatGulandPopup };
