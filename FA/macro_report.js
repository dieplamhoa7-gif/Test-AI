const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, Header, Footer, LevelFormat, VerticalAlign,
} = require("docx");
const fs = require("fs");

// ── helpers ─────────────────────────────────────────────────────────
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
    children: [new TextRun({
      text: String(text),
      bold: opts.bold || false,
      size: 18,
      font: "Arial",
      color: opts.color || "000000",
    })]
  })]
});

const hdr = (t1, t2, t3, t4) => new TableRow({ tableHeader: true, children: [
  cell(t1, { bold:true, bg:"1F3864", color:"FFFFFF", w:2600, align: AlignmentType.CENTER }),
  cell(t2, { bold:true, bg:"1F3864", color:"FFFFFF", w:2600, align: AlignmentType.CENTER }),
  cell(t3, { bold:true, bg:"1F3864", color:"FFFFFF", w:2600, align: AlignmentType.CENTER }),
  cell(t4, { bold:true, bg:"1F3864", color:"FFFFFF", w:1560, align: AlignmentType.CENTER }),
]});

const row2 = (a, b, c, d, altBg) => new TableRow({ children: [
  cell(a, { w:2600, bg: altBg }),
  cell(b, { w:2600, bg: altBg, align: AlignmentType.RIGHT }),
  cell(c, { w:2600, bg: altBg, align: AlignmentType.RIGHT }),
  cell(d, { w:1560, bg: altBg, align: AlignmentType.CENTER }),
]});

const row3 = (label, value, signal) => new TableRow({ children: [
  cell(label, { w:5200, bold: true }),
  cell(value, { w:3100, align: AlignmentType.RIGHT }),
  cell(signal, { w:1060, align: AlignmentType.CENTER,
    bg: signal.includes("↑") ? "D5E8D4" : signal.includes("↓") ? "FFD7CC" : "FFF2CC" }),
]});

const P = (text, opts = {}) => new Paragraph({
  heading: opts.h,
  alignment: opts.align,
  spacing: { before: opts.before || 0, after: opts.after || 120 },
  border: opts.borderBottom ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1F3864" } } : undefined,
  children: [new TextRun({ text, bold: opts.bold, size: opts.size || (opts.h ? undefined : 20), font: "Arial", color: opts.color || "000000" })]
});

const sectionTitle = (t) => new Paragraph({
  spacing: { before: 280, after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" } },
  children: [new TextRun({ text: t, bold: true, size: 26, font: "Arial", color: "1F3864" })]
});

const bulletPara = (text, indent = 360) => new Paragraph({
  spacing: { before: 40, after: 40 },
  indent: { left: indent, hanging: 240 },
  children: [new TextRun({ text: "•  " + text, size: 20, font: "Arial" })]
});

// Signal badge helper
const signalBadge = (s) => s.includes("↑") ? "TÍCH CỰC ↑" : s.includes("↓") ? "RỦI RO ↓" : "TRUNG TÍNH →";

// ── DOCUMENT ────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: "FFFFFF" },
        paragraph: { spacing: { before: 0, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6" } },
        spacing: { after: 80 },
        children: [new TextRun({ text: "BÁO CÁO VĨ MÔ HÀNG NGÀY  |  LH Investment  |  05/06/2026",
          size: 16, font: "Arial", color: "666666", italics: true })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" } },
        spacing: { before: 80 },
        children: [
          new TextRun({ text: "Trang ", size: 16, font: "Arial", color: "999999" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: "999999" }),
          new TextRun({ text: "  |  Tài liệu phân tích nội bộ – Không phải lời khuyên đầu tư cá nhân hóa", size: 16, font: "Arial", color: "999999" }),
        ]
      })] })
    },
    children: [

      // ── COVER BLOCK ──
      new Paragraph({
        shading: { fill: "1F3864", type: ShadingType.CLEAR },
        spacing: { before: 0, after: 0 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "BÁO CÁO VĨ MÔ HÀNG NGÀY", bold: true, size: 52, font: "Arial", color: "FFFFFF" })]
      }),
      new Paragraph({
        shading: { fill: "1F3864", type: ShadingType.CLEAR },
        spacing: { before: 0, after: 0 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Ngày 05/06/2026  |  Nguồn: FiinProX + Pinetree + LH Investment Research", size: 20, font: "Arial", color: "BDD7EE" })]
      }),
      new Paragraph({
        shading: { fill: "1F3864", type: ShadingType.CLEAR },
        spacing: { before: 0, after: 240 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "ĐÁNH GIÁ ẢNH HƯỞNG ĐẾN VNINDEX", bold: true, size: 28, font: "Arial", color: "FFD966" })]
      }),

      // ── EXECUTIVE SUMMARY ──
      sectionTitle("I. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)"),

      // Macro Regime Box
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [3900, 3846, 2000],
        rows: [
          new TableRow({ children: [
            cell("MACRO SCORE", { bold:true, bg:"1F3864", color:"FFFFFF", w:3900, align: AlignmentType.CENTER }),
            cell("REGIME", { bold:true, bg:"1F3864", color:"FFFFFF", w:3846, align: AlignmentType.CENTER }),
            cell("SIGNAL", { bold:true, bg:"1F3864", color:"FFFFFF", w:2000, align: AlignmentType.CENTER }),
          ]}),
          new TableRow({ children: [
            cell("43–48 / 100", { bold:true, bg:"FFF2CC", w:3900, align: AlignmentType.CENTER }),
            cell("Cuối chu kỳ / Phòng thủ", { bold:true, bg:"FFF2CC", w:3846, align: AlignmentType.CENTER }),
            cell("THẬN TRỌNG", { bold:true, bg:"FFD7CC", w:2000, align: AlignmentType.CENTER, color:"C00000" }),
          ]}),
        ]
      }),
      P(""),

      P("Tổng quan: Dữ liệu FiinProX (cập nhật 05/06/2026) cho thấy nền kinh tế Việt Nam duy trì đà tăng trưởng tốt về mặt thực (tín dụng +18% yoy, IIP +9%, FDI kỷ lục), nhưng áp lực thanh khoản và lãi suất đang gia tăng đáng kể trong tháng 5–6/2026. Lãi suất liên ngân hàng qua đêm tăng lên 6.97–7.80% cuối tháng 5, M2 tăng trưởng chậm (+6.4% yoy) trong khi tín dụng tăng 18% tạo ra gap thanh khoản hệ thống. VNIndex đang ở phase phòng thủ: tăng trưởng cơ bản hỗ trợ nhưng định giá chịu áp lực từ lãi suất tăng và khối ngoại bán ròng liên tục."),
      P(""),

      // Component Table
      sectionTitle("II. CÁC CHỈ SỐ VĨ MÔ CHÍNH"),

      P("2.1 Thanh khoản & Lãi suất hệ thống", { bold: true }),
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [5200, 3100, 1446],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Chỉ số", { bold:true, bg:"2E75B6", color:"FFFFFF", w:5200 }),
            cell("Giá trị mới nhất", { bold:true, bg:"2E75B6", color:"FFFFFF", w:3100, align: AlignmentType.RIGHT }),
            cell("Tín hiệu", { bold:true, bg:"2E75B6", color:"FFFFFF", w:1446, align: AlignmentType.CENTER }),
          ]}),
          row3("Lãi suất liên NH qua đêm (29/05/2026)", "6.97% (cao nhất T5: 7.80%)", "↓ Rủi ro"),
          row3("Lãi suất tiết kiệm 12T (Big 4)", "5.9% (T4/2026)", "↓ Nhẹ"),
          row3("Lãi suất tiết kiệm 12T (trung bình TT)", "5.86%  |  cao nhất: 7.5%", "↓ Nhẹ"),
          row3("Cho vay VND trung–dài hạn (thấp nhất)", "7.8% → đang tăng", "↓ Rủi ro"),
          row3("Cho vay VND trung–dài hạn (cao nhất)", "10.0% (T4/2026)", "↓ Rủi ro"),
          row3("M2 tăng trưởng yoy (T3/2026)", "+6.42% yoy  |  +0.98% YTD", "→ Chú ý"),
          row3("Tổng tín dụng yoy (T4/2026)", "+17.96% yoy  |  +4.42% YTD", "↑ Tốt"),
        ]
      }),
      P(""),
      P("Nhận xét: Lãi suất liên NH tăng mạnh từ ~3–4% (T2/2026) lên 6–8% (T5/2026) phản ánh gap M2 vs tín dụng đang được hệ thống điều tiết. Đây là signal quan trọng nhất cần theo dõi — nếu liên NH duy trì >6% qua Q3/2026, rủi ro margin call và áp lực bán cổ phiếu sẽ tăng cao.", { color: "C00000" }),
      P(""),

      P("2.2 Tỷ giá & Vàng", { bold: true }),
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [5200, 3100, 1446],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Chỉ số", { bold:true, bg:"2E75B6", color:"FFFFFF", w:5200 }),
            cell("Giá trị mới nhất", { bold:true, bg:"2E75B6", color:"FFFFFF", w:3100, align: AlignmentType.RIGHT }),
            cell("Tín hiệu", { bold:true, bg:"2E75B6", color:"FFFFFF", w:1446, align: AlignmentType.CENTER }),
          ]}),
          row3("USD/VND (VCB bán) – 29/05/2026", "26,395 VND", "→ Ổn định"),
          row3("USD/VND (Tự do) – 29/05/2026", "26,450 VND (+55 VND premium)", "→ Ổn định"),
          row3("Vàng SJC mua vào (05/06/2026)", "166,300,000 VND/lượng", "→ Phục hồi"),
          row3("Vàng SJC bán ra (05/06/2026)", "168,800,000 VND/lượng", "→ Phục hồi"),
          row3("Vàng SJC peak tháng 3/2026", "176,000,000 VND/lượng (bán ra)", "→ Đã giảm"),
        ]
      }),
      P(""),
      P("Nhận xét: USD/VND ổn định, premium tự do chỉ ~55 VND (~0.2%) — áp lực tỷ giá không đáng kể trong ngắn hạn. Vàng SJC giảm từ peak 176 triệu (T3/2026) xuống 157 triệu (T5/2026) rồi phục hồi lại 168.8 triệu hôm nay. Xu hướng vàng phục hồi có thể cạnh tranh dòng tiền với chứng khoán."),
      P(""),

      P("2.3 Tăng trưởng thực & Xuất nhập khẩu", { bold: true }),
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [5200, 3100, 1446],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Chỉ số", { bold:true, bg:"2E75B6", color:"FFFFFF", w:5200 }),
            cell("Giá trị mới nhất", { bold:true, bg:"2E75B6", color:"FFFFFF", w:3100, align: AlignmentType.RIGHT }),
            cell("Tín hiệu", { bold:true, bg:"2E75B6", color:"FFFFFF", w:1446, align: AlignmentType.CENTER }),
          ]}),
          row3("IIP – Sản xuất công nghiệp yoy (T5/2026)", "+8.79% yoy", "↑ Tốt"),
          row3("IIP – Sản xuất công nghiệp yoy (T4/2026)", "+9.3% yoy", "↑ Tốt"),
          row3("Tổng xuất khẩu (T5/2026)", "46,929 triệu USD (+8.3% mom ước)", "↑ Tốt"),
          row3("Tổng nhập khẩu (T5/2026)", "52,141 triệu USD", "→ Chú ý"),
          row3("Cán cân thương mại T5/2026", "Nhập siêu ~5,212 triệu USD", "↓ Chú ý"),
          row3("Cán cân thương mại T4/2026", "Nhập siêu ~3,994 triệu USD", "↓ Chú ý"),
          row3("Cán cân vãng lai Q3/2025", "+12,459 triệu USD (rất mạnh)", "↑ Tốt"),
          row3("Cán cân vãng lai Q4/2025", "+7,654 triệu USD", "↑ Tốt"),
        ]
      }),
      P(""),
      P("Nhận xét: Nhập siêu tháng 5 (~5.2 tỷ USD) là mức cao — tuy nhiên cần phân tích thêm cơ cấu. Nếu chủ yếu là nhập máy móc thiết bị (đầu tư sản xuất), tín hiệu này thực ra là bullish cho IIP và FDI disbursement Q3/2026. Cán cân vãng lai cả năm 2025 dương mạnh, hỗ trợ VND dài hạn."),
      P(""),

      P("2.4 FDI – Vốn đầu tư nước ngoài", { bold: true }),
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [5200, 3100, 1446],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Chỉ số", { bold:true, bg:"2E75B6", color:"FFFFFF", w:5200 }),
            cell("Giá trị (4T/2026 – YTD)", { bold:true, bg:"2E75B6", color:"FFFFFF", w:3100, align: AlignmentType.RIGHT }),
            cell("Tín hiệu", { bold:true, bg:"2E75B6", color:"FFFFFF", w:1446, align: AlignmentType.CENTER }),
          ]}),
          row3("FDI thực hiện (4T/2026)", "7,401 triệu USD", "↑ Tốt"),
          row3("FDI tổng đăng ký (4T/2026)", "18,728 triệu USD", "↑ Mạnh"),
          row3("FDI vốn cấp mới (4T/2026)", "12,279 triệu USD", "↑ Mạnh"),
          row3("FDI vốn tăng thêm (4T/2026)", "3,176 triệu USD", "↑ Tốt"),
          row3("FDI góp vốn mua CP (4T/2026)", "3,273 triệu USD", "↑ Tốt"),
          row3("FDI thực hiện full year 2025", "27,620 triệu USD (so sánh)", "↑ Baseline"),
        ]
      }),
      P(""),
      P("Nhận xét: FDI đăng ký 4T/2026 đạt 18,728 triệu USD — nếu duy trì pace này, cả năm 2026 có thể đạt ~56 tỷ USD đăng ký (vs 38.4 tỷ năm 2025). FDI thực hiện 7,401 triệu (4T/2026) trên pace cao. Đây là động lực tăng trưởng dài hạn tích cực cho nhóm KCN, logistics, utilities."),
      P(""),

      // ── SECTION III ──
      sectionTitle("III. PHÂN TÍCH TÁC ĐỘNG ĐẾN VNINDEX"),

      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [1500, 4500, 2246, 1500],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("YẾU TỐ", { bold:true, bg:"1F3864", color:"FFFFFF", w:1500, align: AlignmentType.CENTER }),
            cell("DIỄN GIẢI", { bold:true, bg:"1F3864", color:"FFFFFF", w:4500 }),
            cell("TÁC ĐỘNG NGẮN HẠN", { bold:true, bg:"1F3864", color:"FFFFFF", w:2246, align: AlignmentType.CENTER }),
            cell("TÁC ĐỘNG DÀI HẠN", { bold:true, bg:"1F3864", color:"FFFFFF", w:1500, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Lãi suất liên NH", { w:1500, bg:"FFD7CC", bold:true }),
            cell("6.97–7.80% cuối T5 → chi phí vốn tăng, áp lực margin, NIM bank thu hẹp", { w:4500, bg:"FFD7CC" }),
            cell("BEARISH – ảnh hưởng ngay định giá & room margin", { w:2246, bg:"FFD7CC", align: AlignmentType.CENTER }),
            cell("BEARISH → cần giám sát", { w:1500, bg:"FFD7CC", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("M2 vs Tín dụng", { w:1500, bg:"FFF2CC", bold:true }),
            cell("M2 +6.4% yoy vs Tín dụng +18% → gap thanh khoản hệ thống, lãi suất liên NH tăng là hệ quả", { w:4500, bg:"FFF2CC" }),
            cell("BEARISH – liquidity squeeze", { w:2246, bg:"FFF2CC", align: AlignmentType.CENTER }),
            cell("NEUTRAL nếu NHNN bơm vốn", { w:1500, bg:"FFF2CC", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("LSHD tăng", { w:1500, bg:"FFE6CC", bold:true }),
            cell("Tiết kiệm 12T trung bình 5.86% (+40–60bps so T2), cao nhất 7.5% → cạnh tranh kênh đầu tư", { w:4500, bg:"FFE6CC" }),
            cell("BEARISH NHẸ – dòng tiền có thể shift sang tiết kiệm", { w:2246, bg:"FFE6CC", align: AlignmentType.CENTER }),
            cell("BEARISH nếu lãi tiếp tục tăng", { w:1500, bg:"FFE6CC", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Tín dụng mạnh", { w:1500, bg:"D5E8D4", bold:true }),
            cell("+17.96% yoy (T4/2026) → tăng trưởng kinh tế, earnings doanh nghiệp được hỗ trợ", { w:4500, bg:"D5E8D4" }),
            cell("BULLISH – hỗ trợ EPS", { w:2246, bg:"D5E8D4", align: AlignmentType.CENTER }),
            cell("BULLISH", { w:1500, bg:"D5E8D4", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("IIP mạnh", { w:1500, bg:"D5E8D4", bold:true }),
            cell("+8–9% yoy → sản xuất công nghiệp tăng trưởng vững → doanh thu nhóm sản xuất/XK tốt", { w:4500, bg:"D5E8D4" }),
            cell("BULLISH – hỗ trợ ngành SX/XK", { w:2246, bg:"D5E8D4", align: AlignmentType.CENTER }),
            cell("BULLISH", { w:1500, bg:"D5E8D4", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("FDI kỷ lục", { w:1500, bg:"D5E8D4", bold:true }),
            cell("Đăng ký 18.7 tỷ USD trong 4T/2026, pace gấp đôi 2025 → đầu tư trực tiếp, KCN, logistics", { w:4500, bg:"D5E8D4" }),
            cell("BULLISH nhóm KCN, logistics, utilities", { w:2246, bg:"D5E8D4", align: AlignmentType.CENTER }),
            cell("BULLISH mạnh", { w:1500, bg:"D5E8D4", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Nhập siêu T5", { w:1500, bg:"FFF2CC", bold:true }),
            cell("Nhập siêu ~5.2 tỷ USD (T5/2026) → áp lực USD/VND tiềm tàng nếu kéo dài sang Q3", { w:4500, bg:"FFF2CC" }),
            cell("NEUTRAL → giám sát Q3", { w:2246, bg:"FFF2CC", align: AlignmentType.CENTER }),
            cell("BEARISH NHẸ nếu trend", { w:1500, bg:"FFF2CC", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Vàng phục hồi", { w:1500, bg:"FFF2CC", bold:true }),
            cell("Vàng SJC từ 157tr đáy tháng 5 phục hồi lên 168.8tr → risk-off partial, cạnh tranh dòng tiền", { w:4500, bg:"FFF2CC" }),
            cell("BEARISH NHẸ – cạnh tranh dòng tiền", { w:2246, bg:"FFF2CC", align: AlignmentType.CENTER }),
            cell("NEUTRAL", { w:1500, bg:"FFF2CC", align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Tỷ giá ổn định", { w:1500, bg:"D5E8D4", bold:true }),
            cell("Premium tự do chỉ 55 VND (~0.2%) → không có risk event tỷ giá trong ngắn hạn", { w:4500, bg:"D5E8D4" }),
            cell("BULLISH – yếu tố ổn định vĩ mô", { w:2246, bg:"D5E8D4", align: AlignmentType.CENTER }),
            cell("NEUTRAL", { w:1500, bg:"D5E8D4", align: AlignmentType.CENTER }),
          ]}),
        ]
      }),
      P(""),

      // ── SECTION IV: SECTOR ──
      sectionTitle("IV. ẢNH HƯỞNG THEO NHÓM NGÀNH"),

      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [2500, 4746, 2500],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("NGÀNH", { bold:true, bg:"1F3864", color:"FFFFFF", w:2500, align: AlignmentType.CENTER }),
            cell("LUẬN ĐIỂM", { bold:true, bg:"1F3864", color:"FFFFFF", w:4746 }),
            cell("QUAN ĐIỂM", { bold:true, bg:"1F3864", color:"FFFFFF", w:2500, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Ngân hàng (BID, VCB, CTG, MBB)", { w:2500, bold:true, bg:"FFD7CC" }),
            cell("Lãi suất liên NH cao → NIM thu hẹp trong Q2–Q3/2026. Margin call risk tăng nếu lãi suất duy trì. Tín dụng tăng mạnh hỗ trợ một phần. Net: áp lực ngắn hạn.", { w:4746, bg:"FFD7CC" }),
            cell("THẬN TRỌNG ↓", { w:2500, bg:"FFD7CC", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("KCN & Logistics (KBC, SZC, NLG, GMD)", { w:2500, bold:true, bg:"D5E8D4" }),
            cell("FDI đăng ký kỷ lục 18.7 tỷ USD trong 4T/2026, pace gấp đôi 2025. IIP mạnh → nhu cầu thuê đất KCN tăng. Logistics hưởng lợi từ nhập khẩu máy móc thiết bị.", { w:4746, bg:"D5E8D4" }),
            cell("TÍCH CỰC ↑", { w:2500, bg:"D5E8D4", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Xuất khẩu (dệt may, thủy sản, điện tử)", { w:2500, bold:true, bg:"D5E8D4" }),
            cell("IIP +8–9% yoy, xuất khẩu T5 đạt 46.9 tỷ USD. Tỷ giá USD/VND ổn định không gây thiệt hại. Hưởng lợi từ FDI manufacturing disbursement.", { w:4746, bg:"D5E8D4" }),
            cell("TÍCH CỰC ↑", { w:2500, bg:"D5E8D4", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Bất động sản nhà ở (VHM, NVL, PDR)", { w:2500, bold:true, bg:"FFD7CC" }),
            cell("Lãi suất cho vay trung–dài hạn tăng lên 7.8–10.0% → sức mua nhà giảm, chi phí vốn chủ đầu tư tăng. Tín dụng tổng tăng mạnh nhưng LSHD cao sẽ hút dòng tiền sang tiết kiệm.", { w:4746, bg:"FFD7CC" }),
            cell("THẬN TRỌNG ↓", { w:2500, bg:"FFD7CC", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Tiêu dùng & Bán lẻ (MWG, FRT, PNJ)", { w:2500, bold:true, bg:"FFF2CC" }),
            cell("Lãi suất cao → chi phí vay tiêu dùng tăng, thu nhập khả dụng bị ảnh hưởng. Vàng phục hồi có thể tạo wealth effect cho người nắm vàng. Net: trung tính đến tiêu cực nhẹ.", { w:4746, bg:"FFF2CC" }),
            cell("TRUNG TÍNH →", { w:2500, bg:"FFF2CC", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Utilities & Điện (POW, PC1, GEG)", { w:2500, bold:true, bg:"D5E8D4" }),
            cell("FDI manufacturing tăng → tăng nhu cầu điện công nghiệp. Tỷ giá ổn định giảm áp lực nhập khẩu than/khí. Ngành có cash flow ổn định, ít nhạy với lãi suất ngắn hạn.", { w:4746, bg:"D5E8D4" }),
            cell("TÍCH CỰC ↑", { w:2500, bg:"D5E8D4", bold:true, align: AlignmentType.CENTER }),
          ]}),

          new TableRow({ children: [
            cell("Vật liệu xây dựng (HPG, HSG, NKG)", { w:2500, bold:true, bg:"FFF2CC" }),
            cell("FDI cao → nhu cầu thép KCN/XD công nghiệp tốt. Nhưng BDS nhà ở chậm và lãi suất cao → nhu cầu từ BDS dân dụng yếu. Net: mixed, FDI bù một phần.", { w:4746, bg:"FFF2CC" }),
            cell("TRUNG TÍNH →", { w:2500, bg:"FFF2CC", bold:true, align: AlignmentType.CENTER }),
          ]}),
        ]
      }),
      P(""),

      // ── SECTION V ──
      sectionTitle("V. KHUYẾN NGHỊ HÀNH ĐỘNG"),

      P("5.1 Định hướng tổng thể cho danh mục", { bold: true }),
      bulletPara("Duy trì tỷ trọng cổ phiếu ở mức 50–60% (thấp hơn mức bình thường). Không mua đuổi."),
      bulletPara("Ưu tiên các mã có earnings visibility tốt, ít phụ thuộc vào lãi vay (ROE cao, D/E thấp)."),
      bulletPara("Tránh mở vị thế mới với margin trong giai đoạn lãi suất liên NH >6%."),
      bulletPara("Theo dõi lãi suất liên NH hằng ngày — nếu về dưới 5% trong 3 phiên liên tiếp, cân nhắc tăng tỷ trọng."),
      P(""),

      P("5.2 Ưu tiên sector", { bold: true }),
      bulletPara("OVERWEIGHT: KCN (KBC, SZC, LHG), Logistics (GMD, STG), Utilities/Điện (PC1, GEG, POW) — hưởng lợi FDI & IIP."),
      bulletPara("NEUTRAL: Xuất khẩu dệt may, thủy sản — tốt về fundamentals nhưng cần kiểm tra định giá hiện tại."),
      bulletPara("UNDERWEIGHT: Ngân hàng (áp lực NIM), BDS nhà ở (chi phí vốn cao)."),
      P(""),

      P("5.3 Ngưỡng trigger cần theo dõi", { bold: true }),
      new Table({
        width: { size: 9746, type: WidthType.DXA },
        columnWidths: [3500, 3246, 3000],
        rows: [
          new TableRow({ tableHeader: true, children: [
            cell("Chỉ số", { bold:true, bg:"1F3864", color:"FFFFFF", w:3500 }),
            cell("Ngưỡng cần theo dõi", { bold:true, bg:"1F3864", color:"FFFFFF", w:3246, align: AlignmentType.CENTER }),
            cell("Hành động", { bold:true, bg:"1F3864", color:"FFFFFF", w:3000, align: AlignmentType.CENTER }),
          ]}),
          new TableRow({ children: [
            cell("Lãi suất liên NH qua đêm", { w:3500 }),
            cell("< 4.5% trong 3 phiên liên tiếp", { w:3246, align: AlignmentType.CENTER, bg:"D5E8D4" }),
            cell("Tăng tỷ trọng, xem xét mở vị thế", { w:3000, bg:"D5E8D4" }),
          ]}),
          new TableRow({ children: [
            cell("Lãi suất liên NH qua đêm", { w:3500 }),
            cell("> 8.0% kéo dài > 5 phiên", { w:3246, align: AlignmentType.CENTER, bg:"FFD7CC" }),
            cell("Giảm tỷ trọng, ưu tiên tiền mặt", { w:3000, bg:"FFD7CC" }),
          ]}),
          new TableRow({ children: [
            cell("USD/VND tự do", { w:3500 }),
            cell("> 26,700 (+1.1% từ nay)", { w:3246, align: AlignmentType.CENTER, bg:"FFD7CC" }),
            cell("Cảnh báo áp lực tỷ giá", { w:3000, bg:"FFD7CC" }),
          ]}),
          new TableRow({ children: [
            cell("FDI thực hiện tháng (monthly)", { w:3500 }),
            cell("Giảm liên tiếp 2 tháng", { w:3246, align: AlignmentType.CENTER, bg:"FFF2CC" }),
            cell("Xem lại luận điểm KCN/logistics", { w:3000, bg:"FFF2CC" }),
          ]}),
          new TableRow({ children: [
            cell("IIP yoy", { w:3500 }),
            cell("< 5% trong 2 tháng liên tiếp", { w:3246, align: AlignmentType.CENTER, bg:"FFF2CC" }),
            cell("Cảnh báo suy giảm đà tăng trưởng", { w:3000, bg:"FFF2CC" }),
          ]}),
        ]
      }),
      P(""),

      // ── SECTION VI ──
      sectionTitle("VI. DỮ LIỆU CẦN CẬP NHẬT THÊM"),

      bulletPara("CPI tháng 5/2026 — chưa có trong FiinProX bản này. Cần cập nhật để đánh giá áp lực lạm phát và kỳ vọng điều hành lãi suất."),
      bulletPara("VNIndex OHLCV + khối ngoại giao dịch gần nhất — cần từ nguồn market data (Pinetree/VDSC/vnstock)."),
      bulletPara("PMI tháng 5/2026 — chỉ số sức khỏe sản xuất, bổ sung cho IIP."),
      bulletPara("OMO/bơm hút ròng NHNN — chưa có; cần WiData/WiFeed để đánh giá thanh khoản OMO chính xác hơn."),
      bulletPara("Credit growth phân ngành — cần biết tín dụng tập trung vào BDS/sản xuất/tiêu dùng tỷ lệ nào."),
      P(""),

      sectionTitle("VII. NGUỒN DỮ LIỆU"),
      bulletPara("FiinProX: Dữ liệu vĩ mô (DE), Lãi suất NHNN, Lãi suất huy động ngân hàng, Cán cân thương mại — cập nhật 05/06/2026"),
      bulletPara("Pinetree Morning Brief: Snapshot lãi suất liên NH, FX, global risk, VNINDEX — 04/05/2026 (bản test)"),
      bulletPara("LH Investment Research — tổng hợp và phân tích nội bộ"),
      P(""),

      new Paragraph({
        spacing: { before: 240, after: 0 },
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" } },
        children: [new TextRun({
          text: "DISCLAIMER: Báo cáo này là tài liệu phân tích nội bộ phục vụ quá trình ra quyết định đầu tư. Không phải lời khuyên đầu tư cá nhân hóa. Số liệu từ các nguồn công khai và có thể có độ trễ. Nhà đầu tư tự chịu trách nhiệm về quyết định của mình.",
          size: 16, font: "Arial", color: "999999", italics: true
        })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync("reports", { recursive: true });
  fs.writeFileSync("reports/ViMo_VNIndex_Claude_Code_20260605.docx", buf);
  console.log("OK reports/ViMo_VNIndex_Claude_Code_20260605.docx");
});
