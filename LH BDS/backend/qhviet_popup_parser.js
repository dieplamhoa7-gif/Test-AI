// Lightweight parser for QH Viet popup text captured from browser automation.
// Parses deterministic fields only; no AI interpretation.

function stripHtml(s) {
  return String(s || '').replace(/<[^>]+>/g, ' ').replace(/\+/g, '').replace(/\"/g, '"').replace(/\s+/g, ' ').trim();
}

function extractQhVietHtmlFields(raw) {
  const fields = {};
  const str = String(raw || '');
  try {
    const obj = JSON.parse(str.split('\n')[0]);
    const html = obj?.feature?.properties?.html || [];
    for (const h of html) {
      const lab = (String(h).match(/<div class="label">([^<]+)<\/div>/i) || [])[1];
      const val = (String(h).match(/<div class="value">([\s\S]*?)<\/div>/i) || [])[1];
      if (lab) fields[stripHtml(lab)] = stripHtml(val || '');
    }
  } catch {}
  return fields;
}

function parseQhVietPopupText(text) {
  const fields = extractQhVietHtmlFields(text);
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  const out = {
    source: 'QH Viet popup',
    parcel: {},
    planning: [],
    raw_text: t,
  };

  let m;
  if (fields['Khu vực cũ']) out.old_area_name = fields['Khu vực cũ'];
  if (fields['Khu vực mới']) out.area_name = fields['Khu vực mới'];
  if (fields['Tọa độ']) out.coordinate_text = fields['Tọa độ'];
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

  if (!out.old_area_name && (m = t.match(/Khu\s*vực\s*cũ\s*:?\s*([^]+?)(?:\s+Khu\s*vực\s*mới|\s+Thông tin|\s+Xem quy hoạch|$)/i))) {
    out.old_area_name = m[1].trim();
  }
  const newMatches = [...t.matchAll(/Khu\s*vực\s*mới\s*:?\s*([^]+?)(?=\s+Tọa\s*độ|\s+Khu\s*vực\s*cũ|\s+Thông tin|\s+Xem quy hoạch|\s+Quy hoạch|\s+Loại\s*đất|\s+Ký\s*hiệu|\s+Đất\s+\S+|$)/ig)];
  if (!out.area_name && newMatches.length) {
    out.area_name = newMatches[newMatches.length - 1][1].trim();
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
  if ((m = t.match(/Tên\s*khu\s*ch(?:ứ|ứ)c\s*năng\s*:?\s*([^]+?)(?=\s+Mô\s*tả|\s+Mô\s*tả|$)/i))) {
    out.functional_area = m[1].trim();
  }
  if ((m = t.match(/Mô\s*ta\S*\s*:?\s*([^]+?)(?=\s+Hiện\s+thửa|\s+Lưu\s+điểm|\s+Mã\s+chia|\s+Tọa\s+độ\s+ranh|\s+Xem quy hoạch|$)/i))) {
    out.description = m[1].trim();
  }
  if (out.parcel.land_code || out.parcel.land_use) {
    out.planning = out.planning.length ? out.planning : [{ code: out.parcel.land_code || null, land_use: out.parcel.land_use || null, far: out.far ?? null, density: out.density ?? null }];
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
      ].filter(Boolean).join('\n');
}

module.exports = { parseQhVietPopupText, formatQhVietPopup };

if (require.main === module) {
  const input = process.argv.slice(2).join(' ');
  const parsed = parseQhVietPopupText(input);
  console.log(JSON.stringify(parsed, null, 2));
  console.log(formatQhVietPopup(parsed));
}
