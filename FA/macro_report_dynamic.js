const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType,
  PageNumber, Header, Footer, VerticalAlign,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const DATA = path.join(ROOT, "data");
const REPORTS = path.join(ROOT, "reports");
fs.mkdirSync(REPORTS, { recursive: true });

// ── Data helpers ───────────────────────────────────────────────────
function readJson(p, fallback = {}) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return fallback; }
}
function latestHistory() {
  const dir = path.join(DATA, "history");
  const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter(f => /^\d{4}-\d{2}-\d{2}.*\.json$/.test(f)).sort() : [];
  if (!files.length) return {};
  return readJson(path.join(dir, files[files.length - 1]), {});
}
function n(v) { const x = Number(v); return Number.isFinite(x) ? x : null; }
function fmt(v, suffix = "", digits = 2) {
  const x = n(v); if (x === null) return "N/A";
  return x.toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: digits }) + suffix;
}
function fmt0(v, suffix = "") { const x = n(v); return x === null ? "N/A" : x.toLocaleString("en-US", { maximumFractionDigits: 0 }) + suffix; }
function pct(v) { return fmt(v, "%", 2); }
function val(obj, pathArr) {
  let cur = obj;
  for (const k of pathArr) { if (!cur || cur[k] === undefined) return null; cur = cur[k]; }
  return cur;
}
function signalRate(v) {
  const x = n(v); if (x === null) return "→ Thiếu dữ liệu";
  if (x >= 6) return "↓ Rủi ro";
  if (x >= 5) return "→ Chú ý";
  return "↑ Tốt";
}
function signalFx(usd) {
  const x = n(usd); if (x === null) return "→ Thiếu dữ liệu";
  if (x >= 26600) return "↓ Rủi ro";
  if (x >= 26200) return "→ Chú ý";
  return "↑ Ổn định";
}
function signalNet(v) {
  const x = n(v); if (x === null) return "→ Thiếu dữ liệu";
  if (x > 0) return "↑ Bơm ròng";
  if (x < 0) return "↓ Hút ròng";
  return "→ Trung tính";
}
function signalMarketChange(v) {
  const x = n(v); if (x === null) return "→ Theo dõi";
  if (x > 0) return "↑ Tích cực";
  if (x < 0) return "↓ Rủi ro";
  return "→ Trung tính";
}

const hist = latestHistory();
const liq = readJson(path.join(DATA, "sbv_liquidity", "latest.json"), {});
const pt = hist.pinetree || {};
const vcb = (hist.vcbFx && hist.vcbFx.raw) || {};
const vn = hist.vnMarket || {};
const global = hist.global || {};
const te = readJson(path.join(DATA, "tradingeconomics_visible_latest.json"), {});
const liqSummary = liq.summary || {};
const today = hist.date || new Date().toISOString().slice(0,10);

const interbankON = val(pt, ["interbankOvernight", "value"]);
const deposit12m = val(pt, ["deposit12m", "value"]);
const usdPinetree = val(pt, ["usdVnd", "value"]);
const usdVcbSell = val(vcb, ["USD", "sell"]);
const vnindex = val(pt, ["vnindex", "value"]) || val(vn, ["vnindex", "value"]);
const marketTurnover = val(pt, ["marketTurnoverBn", "value"]);
const foreignNet = val(pt, ["foreignNetBuyBn", "value"]);
const vix = val(pt, ["vix", "value"]) || val(global, ["vix", "value"]);
const brent = val(pt, ["brent", "value"]) || val(global, ["brent", "value"]);
const gold = val(pt, ["gold", "value"]) || val(global, ["gold", "value"]);
const sp500 = val(pt, ["sp500", "value"]) || val(global, ["sp500", "value"]);
const dxy = val(global, ["dxy", "value"]);
const us10y = val(global, ["us10y", "value"]);

const reverseRepoIssue = liqSummary.reverseRepoIssueBn;
const reverseRepoNet = liqSummary.reverseRepoNetBn;
const totalLiquidityNet = liqSummary.totalLiquidityNetBn;
const omoRate = liqSummary.omoRate;
const tbillIssue = liqSummary.tbillIssueBn;
const tbillNet = liqSummary.tbillNetBn;

let macroScore = 50;
if (n(interbankON) !== null) macroScore += interbankON < 5 ? 8 : interbankON < 6 ? 0 : -10;
if (n(reverseRepoNet) !== null) macroScore += reverseRepoNet > 0 ? 5 : reverseRepoNet < 0 ? -7 : 0;
if (n(usdVcbSell || usdPinetree) !== null) macroScore += (usdVcbSell || usdPinetree) > 26600 ? -8 : 3;
if (n(foreignNet) !== null) macroScore += foreignNet > 0 ? 5 : -5;
if (n(vix) !== null) macroScore += vix < 18 ? 4 : vix > 25 ? -8 : 0;
macroScore = Math.max(0, Math.min(100, Math.round(macroScore)));
const regime = macroScore >= 65 ? "Risk-on / Thuận lợi" : macroScore >= 50 ? "Trung tính có chọn lọc" : "Phòng thủ / Thận trọng";
const regimeSignal = macroScore >= 65 ? "TÍCH CỰC" : macroScore >= 50 ? "TRUNG TÍNH" : "THẬN TRỌNG";

// ── DOCX helpers ───────────────────────────────────────────────────
const brd = (color = "CCCCCC") => ({ style: BorderStyle.SINGLE, size: 1, color });
const borders = (c) => { const b = brd(c); return { top:b, bottom:b, left:b, right:b }; };
const cell = (text, opts = {}) => new TableCell({
  borders: borders(opts.borderColor || "CCCCCC"),
  width: { size: opts.w || 1, type: WidthType.DXA },
  shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined,
  margins: { top: 80, bottom: 80, left: 160, right: 160 },
  verticalAlign: VerticalAlign.CENTER,
  children: [new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text: String(text), bold: opts.bold || false, size: opts.size || 18, font: "Arial", color: opts.color || "000000" })]
  })]
});
const P = (text, opts = {}) => new Paragraph({
  alignment: opts.align,
  spacing: { before: opts.before || 0, after: opts.after || 120 },
  border: opts.borderBottom ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1F3864" } } : undefined,
  children: [new TextRun({ text, bold: opts.bold, size: opts.size || 20, font: "Arial", color: opts.color || "000000", italics: opts.italics || false })]
});
const sectionTitle = (t) => new Paragraph({
  spacing: { before: 280, after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" } },
  children: [new TextRun({ text: t, bold: true, size: 26, font: "Arial", color: "1F3864" })]
});
const row3 = (label, value, signal) => new TableRow({ children: [
  cell(label, { w:5200, bold: true }),
  cell(value, { w:3000, align: AlignmentType.RIGHT }),
  cell(signal, { w:1546, align: AlignmentType.CENTER, bg: signal.includes("↑") ? "D5E8D4" : signal.includes("↓") ? "FFD7CC" : "FFF2CC" }),
]});
const table3 = (rows) => new Table({
  width: { size: 9746, type: WidthType.DXA },
  columnWidths: [5200, 3000, 1546],
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("Chỉ số", { bold:true, bg:"2E75B6", color:"FFFFFF", w:5200 }),
      cell("Giá trị động mới nhất", { bold:true, bg:"2E75B6", color:"FFFFFF", w:3000, align: AlignmentType.RIGHT }),
      cell("Tín hiệu", { bold:true, bg:"2E75B6", color:"FFFFFF", w:1546, align: AlignmentType.CENTER }),
    ]}),
    ...rows
  ]
});

const interpretation = `Dữ liệu động ngày ${today} cho thấy trạng thái vĩ mô hiện tại nghiêng về ${regime.toLowerCase()}. Trọng tâm chính sách tiền tệ là thanh khoản: lãi suất liên ngân hàng qua đêm ở ${pct(interbankON)}, lãi suất huy động 12T khoảng ${pct(deposit12m)}, OMO/Reverse Repo bơm ròng ${fmt0(reverseRepoNet, " tỷ")}. Điều này cho thấy NHNN đang điều tiết thanh khoản có kiểm soát: có bơm vốn qua OMO, nhưng chưa phải môi trường tiền rẻ rõ rệt.`;

const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 20 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" } },
      spacing: { after: 80 },
      children: [new TextRun({ text: `BÁO CÁO VĨ MÔ ĐỘNG | LH Investment | ${today}`, size: 16, font: "Arial", color: "666666", italics: true })]
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" } },
      spacing: { before: 80 },
      children: [new TextRun({ text: "Trang ", size: 16, font: "Arial", color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: "999999" }), new TextRun({ text: " | Phân tích nội bộ – không phải lời khuyên đầu tư cá nhân hóa", size: 16, font: "Arial", color: "999999" })]
    })] }) },
    children: [
      new Paragraph({ shading: { fill: "1F3864", type: ShadingType.CLEAR }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "BÁO CÁO VĨ MÔ ĐỘNG", bold: true, size: 52, font: "Arial", color: "FFFFFF" })] }),
      new Paragraph({ shading: { fill: "1F3864", type: ShadingType.CLEAR }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: `Ngày ${today} | Data tự đọc từ FA/data`, size: 20, font: "Arial", color: "BDD7EE" })] }),
      new Paragraph({ shading: { fill: "1F3864", type: ShadingType.CLEAR }, spacing: { after: 240 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TRỌNG TÂM: CHÍNH SÁCH TIỀN TỆ & THANH KHOẢN", bold: true, size: 26, font: "Arial", color: "FFD966" })] }),

      sectionTitle("I. TÓM TẮT ĐIỀU HÀNH"),
      new Table({ width: { size: 9746, type: WidthType.DXA }, columnWidths: [3200, 4200, 2346], rows: [
        new TableRow({ children: [cell("MACRO SCORE", { bold:true, bg:"1F3864", color:"FFFFFF", w:3200, align: AlignmentType.CENTER }), cell("REGIME", { bold:true, bg:"1F3864", color:"FFFFFF", w:4200, align: AlignmentType.CENTER }), cell("SIGNAL", { bold:true, bg:"1F3864", color:"FFFFFF", w:2346, align: AlignmentType.CENTER })] }),
        new TableRow({ children: [cell(`${macroScore} / 100`, { bold:true, bg:"FFF2CC", w:3200, align: AlignmentType.CENTER }), cell(regime, { bold:true, bg:"FFF2CC", w:4200, align: AlignmentType.CENTER }), cell(regimeSignal, { bold:true, bg: macroScore >= 65 ? "D5E8D4" : macroScore >= 50 ? "FFF2CC" : "FFD7CC", w:2346, align: AlignmentType.CENTER, color: macroScore < 50 ? "C00000" : "000000" })] })
      ]}),
      P(""), P(interpretation),

      sectionTitle("II. CHÍNH SÁCH TIỀN TỆ & THANH KHOẢN HỆ THỐNG"),
      table3([
        row3("Lãi suất liên NH qua đêm", pct(interbankON), signalRate(interbankON)),
        row3("Lãi suất tiết kiệm 12T", pct(deposit12m), signalRate(deposit12m)),
        row3("Reverse Repo / OMO phát hành", fmt0(reverseRepoIssue, " tỷ"), signalNet(reverseRepoIssue)),
        row3("Bơm/hút ròng Reverse Repo", fmt0(reverseRepoNet, " tỷ"), signalNet(reverseRepoNet)),
        row3("Tổng bơm/hút ròng NHNN", fmt0(totalLiquidityNet, " tỷ"), signalNet(totalLiquidityNet)),
        row3("Lãi suất OMO", pct(omoRate), signalRate(omoRate)),
        row3("Tín phiếu phát hành", tbillIssue === null || tbillIssue === undefined ? "Chưa có số public" : fmt0(tbillIssue, " tỷ"), tbillIssue ? signalNet(-tbillIssue) : "→ Thiếu dữ liệu"),
        row3("Bơm/hút ròng tín phiếu", tbillNet === null || tbillNet === undefined ? "Chưa có số public" : fmt0(tbillNet, " tỷ"), tbillNet ? signalNet(tbillNet) : "→ Thiếu dữ liệu"),
      ]),
      P("Nhận xét: Nếu lãi suất liên ngân hàng giữ trên 6% trong nhiều phiên, thị trường thường bước vào trạng thái phòng thủ vì chi phí vốn và rủi ro margin tăng. OMO bơm ròng là tín hiệu hỗ trợ, nhưng cần theo dõi đồng thời tín phiếu vì tín phiếu có thể hút ngược thanh khoản.", { color: "C00000" }),

      sectionTitle("III. TỶ GIÁ, ĐỐI NGOẠI & RÀNG BUỘC CHÍNH SÁCH"),
      table3([
        row3("USD/VND Pinetree", fmt0(usdPinetree), signalFx(usdPinetree)),
        row3("USD/VND VCB bán", fmt0(usdVcbSell), signalFx(usdVcbSell)),
        row3("DXY", fmt(dxy, "", 2), n(dxy) && dxy > 105 ? "↓ Rủi ro" : "→ Theo dõi"),
        row3("US 10Y", pct(us10y), n(us10y) && us10y > 4.5 ? "↓ Rủi ro" : "→ Theo dõi"),
      ]),
      P("Nhận xét: Tỷ giá là ràng buộc lớn nhất của NHNN. Nếu USD/VND và DXY ổn định, NHNN có dư địa bơm OMO để làm dịu liên ngân hàng. Nếu tỷ giá căng, ưu tiên chính sách sẽ chuyển sang bảo vệ VND, khiến thanh khoản chứng khoán kém thuận lợi hơn."),

      sectionTitle("IV. THỊ TRƯỜNG & KHẨU VỊ RỦI RO"),
      table3([
        row3("VNINDEX", fmt(vnindex, "", 2), "→ Theo dõi"),
        row3("Thanh khoản thị trường", fmt0(marketTurnover, " tỷ"), n(marketTurnover) && marketTurnover > 20000 ? "↑ Tốt" : "→ Theo dõi"),
        row3("Khối ngoại mua/bán ròng", fmt0(foreignNet, " tỷ"), signalMarketChange(foreignNet)),
        row3("VIX", fmt(vix, "", 2), n(vix) && vix < 18 ? "↑ Tốt" : n(vix) && vix > 25 ? "↓ Rủi ro" : "→ Theo dõi"),
        row3("S&P 500", fmt(sp500, "", 2), "→ Theo dõi"),
      ]),

      sectionTitle("V. HÀNG HÓA & DÒNG TIỀN THAY THẾ"),
      table3([
        row3("Dầu Brent", fmt(brent, "", 2), n(brent) && brent > 95 ? "↓ Áp lực lạm phát" : "→ Theo dõi"),
        row3("Vàng", fmt(gold, "", 2), "→ Cạnh tranh dòng tiền"),
      ]),

      sectionTitle("VI. KẾT LUẬN HÀNH ĐỘNG"),
      P("1. Trạng thái hiện tại nên là thận trọng/có chọn lọc, không dùng margin cao khi liên ngân hàng còn cao."),
      P("2. Chỉ chuyển sang risk-on rõ hơn nếu liên NH ON hạ dưới 5%, OMO tiếp tục bơm ròng, USD/VND ổn định và khối ngoại giảm bán."),
      P("3. Ưu tiên nhóm hưởng lợi tăng trưởng thực như KCN, logistics, xuất khẩu, điện công nghiệp; tránh doanh nghiệp đòn bẩy cao khi lãi suất còn căng."),
      P("4. Tín phiếu NHNN hiện chưa có số public ổn định trên trang SBV visible; báo cáo giữ trạng thái thiếu dữ liệu thay vì tự bịa số."),

      P("Nguồn dữ liệu động", { bold: true, before: 240 }),
      P(`History: ${path.join("FA", "data", "history")}`),
      P(`SBV liquidity: ${path.join("FA", "data", "sbv_liquidity", "latest.json")}`),
      P(`Pinetree: ${pt.url || "FA/data/pinetree_archive"}`),
      P("DISCLAIMER: Báo cáo này là tài liệu phân tích nội bộ, không phải lời khuyên đầu tư cá nhân hóa.", { italics: true, color: "666666" }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  const out = path.join(REPORTS, `ViMo_VNIndex_Dynamic_${today}.docx`);
  fs.writeFileSync(out, buf);
  const meta = { out, today, macroScore, regime, fields: { interbankON, deposit12m, usdPinetree, usdVcbSell, reverseRepoIssue, reverseRepoNet, totalLiquidityNet, omoRate, tbillIssue, tbillNet, vnindex, marketTurnover, foreignNet, vix, dxy, us10y, brent, gold } };
  fs.writeFileSync(path.join(REPORTS, `ViMo_VNIndex_Dynamic_${today}.json`), JSON.stringify(meta, null, 2));
  console.log(JSON.stringify(meta, null, 2));
});
