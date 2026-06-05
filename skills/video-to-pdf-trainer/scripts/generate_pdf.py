# -*- coding: utf-8 -*-
"""
Video → Training PDF Generator
Dùng bởi skill video-to-pdf-trainer
Chạy: python generate_pdf.py --title "..." --output "out.pdf" --content_json "content.json"
"""
import json, sys, argparse, html as _html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV",   FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FONT_DIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI",FONT_DIR + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-M", FONT_DIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B",
                               italic="DV-I", boldItalic="DV-BI")

# ── Colours ────────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#1B2B4B"); BLUE  = colors.HexColor("#2E5FA3")
RED   = colors.HexColor("#A31F34"); GOLD  = colors.HexColor("#C49A1B")
GREEN = colors.HexColor("#1B5E20"); LGRN  = colors.HexColor("#F0FFF4")
LGRAY = colors.HexColor("#F4F6FA"); GRAY  = colors.HexColor("#8A8B8C")
LGOLD = colors.HexColor("#FFFDE7"); WHITE = colors.white

_style_counter = 0
def mk(fn="DV", fs=10, ld=None, tc=colors.black, al=TA_JUSTIFY,
       sb=0, sa=4, li=0, ri=0, bg=None):
    global _style_counter
    _style_counter += 1
    kw = dict(fontName=fn, fontSize=fs, leading=ld or fs*1.5,
              textColor=tc, alignment=al, spaceBefore=sb, spaceAfter=sa,
              leftIndent=li, rightIndent=ri)
    if bg: kw["backColor"] = bg
    return ParagraphStyle(f"s{_style_counter}", **kw)

# Pre-built styles
sB   = mk()
sBb  = mk(fn="DV-B")
sBul = mk(li=14, sa=3)
sNt  = mk(fn="DV-I", fs=9, tc=colors.HexColor("#555"), li=10, sa=3)
sSec = mk(fn="DV-B", fs=13, tc=NAVY, al=TA_LEFT, sb=10, sa=5)
sSub = mk(fn="DV-B", fs=11, tc=BLUE, al=TA_LEFT, sb=6,  sa=4)
sTH  = mk(fn="DV-B", fs=18, tc=NAVY, al=TA_CENTER, sa=16)
sTC  = mk(fn="DV-B", fs=11, tc=NAVY, al=TA_LEFT, sb=7, sa=2)
sTI  = mk(fs=10, tc=colors.HexColor("#444"), al=TA_LEFT, li=16, sa=2)
sCL  = mk(fn="DV-B", fs=9,  tc=GOLD, al=TA_LEFT, sa=1)
sCT  = mk(fn="DV-B", fs=20, tc=WHITE, ld=26, al=TA_LEFT, sa=4)
sCS  = mk(fn="DV-I", fs=9.5, tc=colors.HexColor("#AACBF0"), al=TA_LEFT)
sCVT = mk(fn="DV-B", fs=30, tc=WHITE, ld=38, al=TA_CENTER, sa=6)
sCVS = mk(fn="DV-I", fs=15, tc=colors.HexColor("#D4E1F7"), ld=22, al=TA_CENTER, sa=4)
sCVI = mk(fs=10, tc=colors.HexColor("#AACBF0"), ld=16, al=TA_CENTER, sa=3)
sCVL = mk(fn="DV-B", fs=11, tc=GOLD, al=TA_CENTER, sa=8)

def sp(h=0.25): return Spacer(1, h*cm)
def hr(c=GRAY, t=0.5): return HRFlowable(width="100%", thickness=t, color=c,
                                          spaceAfter=4, spaceBefore=2)
def p(text):  return Paragraph(text, sB)
def pb(text): return Paragraph(text, sBb)
def bp(text): return Paragraph(f"•  {text}", sBul)

def ch_banner(num, title, sub=""):
    rows = [[Paragraph(f"MODULE {num}", sCL)], [Paragraph(title, sCT)]]
    if sub: rows.append([Paragraph(sub, sCS)])
    t = Table(rows, colWidths=["100%"])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("LEFTPADDING",(0,0),(-1,-1),18),("RIGHTPADDING",(0,0),(-1,-1),18),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14)]))
    return t

def lec_banner(num, title, who):
    lp = Paragraph(f"Lecture {num}  |  {title}", mk(fn="DV-B", fs=10, tc=WHITE))
    wp = Paragraph(who, mk(fn="DV-I", fs=9, tc=colors.HexColor("#AACBF0"), al=TA_RIGHT))
    t = Table([[lp, wp]], colWidths=["68%","32%"])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),BLUE),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

def fml(label, formula):
    lp = Paragraph(label, mk(fn="DV-B", fs=9, tc=BLUE, al=TA_LEFT))
    fp = Paragraph(_html.escape(formula), mk(fn="DV-M", fs=9.5, al=TA_LEFT))
    t = Table([[lp, fp]], colWidths=[4.5*cm, 12.5*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LGRAY),
        ("BOX",(0,0),(-1,-1),.4,GRAY),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

def ibox(text):
    lp = Paragraph("▶  ỨNG DỤNG ĐẦU TƯ THỰC TẾ", mk(fn="DV-B", fs=9, tc=GREEN))
    cp = Paragraph(text, mk(fs=10, ld=15))
    t = Table([[lp],[cp]], colWidths=["100%"])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LGRN),
        ("BOX",(0,0),(-1,-1),1.5,GREEN),("LINEBEFORE",(0,0),(0,-1),4,GREEN),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t

def kbox(items):
    lp = Paragraph("★  ĐIỂM MẤU CHỐT", mk(fn="DV-B", fs=9, tc=colors.HexColor("#7B4F00")))
    rows = [[lp]]
    for it in items:
        rows.append([Paragraph(f"✓  {it}", mk(fs=9.5, ld=14, sa=2))])
    t = Table(rows, colWidths=["100%"])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LGOLD),
        ("BOX",(0,0),(-1,-1),1,GOLD),("LINEBEFORE",(0,0),(0,-1),4,GOLD),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    return t

def tbl(headers, rows, widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"DV-B"),("FONTNAME",(0,1),(-1,-1),"DV"),
        ("FONTSIZE",(0,0),(-1,-1),9),("ALIGN",(0,0),(-1,-1),"LEFT"),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LGRAY]),
        ("GRID",(0,0),(-1,-1),.3,GRAY),
        ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    return t

def box_info(label, text, lc=BLUE, bg=LGRAY):
    lp = Paragraph(label, mk(fn="DV-B", fs=9, tc=lc, al=TA_LEFT))
    cp = Paragraph(text, mk(fs=10, ld=15))
    t = Table([[lp],[cp]], colWidths=["100%"])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
        ("BOX",(0,0),(-1,-1),1,lc),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return t

# ── Footer ─────────────────────────────────────────────────────────────────────
def make_footer(course_title):
    def footer(canvas, doc):
        canvas.saveState()
        w, h = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, w, 1.1*cm, fill=1, stroke=0)
        canvas.setFillColor(WHITE); canvas.setFont("DV", 7.5)
        canvas.drawString(1.5*cm, 0.4*cm, course_title[:80])
        canvas.drawRightString(w-1.5*cm, 0.4*cm, f"Trang {doc.page}")
        canvas.setFillColor(RED)
        canvas.rect(0, h-0.2*cm, w, 0.2*cm, fill=1, stroke=0)
        canvas.restoreState()
    return footer

# ── Cover ──────────────────────────────────────────────────────────────────────
def build_cover(data):
    s = []
    def crow(item): return Table([[item]], colWidths=["100%"], style=[
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("LEFTPADDING",(0,0),(-1,-1),40),("RIGHTPADDING",(0,0),(-1,-1),40),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)])
    items = [
        sp(2.5),
        Paragraph(data.get("date",""), sCVL),
        Paragraph(data.get("course_title","Khóa học"), sCVT),
        sp(0.3),
        Paragraph(data.get("subtitle","Training Guide"), sCVS),
        sp(0.5),
        Table([[HRFlowable(width="100%",thickness=1,
                           color=colors.HexColor("#FFFFFF44"))]],
              colWidths=["100%"], style=[("BACKGROUND",(0,0),(-1,-1),NAVY),
              ("PADDING",(0,0),(-1,-1),0)]),
        sp(0.4),
        Paragraph(data.get("instructors",""), sCVI),
        Paragraph(data.get("guest_lecturers",""), sCVI),
        sp(3.5),
    ]
    for it in items: s.append(crow(it))
    s.append(PageBreak())
    return s

# ── TOC ────────────────────────────────────────────────────────────────────────
def build_toc(modules):
    s = [Paragraph("MỤC LỤC", sTH), hr(NAVY,1.5), sp(0.3)]
    for mod in modules:
        s.append(Paragraph(f"Module {mod['number']}  –  {mod['title']}", sTC))
        for sec in mod.get("sections",[]):
            if sec.get("heading"):
                s.append(Paragraph(sec["heading"], sTI))
    s.append(PageBreak())
    return s

# ── Section renderer ──────────────────────────────────────────────────────────
def render_section(sec, s):
    if sec.get("heading"):
        # Detect heading level: "1.1 ..." = sub-section, "1.1.1 ..." = sub-sub
        dots = sec["heading"].count(".")
        if dots >= 2:
            s.append(Paragraph(sec["heading"], sSub))
        else:
            s.append(Paragraph(sec["heading"], sSec))

    if sec.get("body"):
        s.append(p(sec["body"]))
        s.append(sp(0.2))

    for fm in sec.get("formulas", []):
        s.append(fml(fm["label"], fm["formula"]))

    if sec.get("formulas"):
        s.append(sp(0.2))

    for b in sec.get("bullets", []):
        s.append(bp(b))

    if sec.get("bullets"):
        s.append(sp(0.2))

    tb = sec.get("table")
    if tb and tb.get("headers") and tb.get("rows"):
        s.append(tbl(tb["headers"], tb["rows"], tb.get("widths")))
        if tb.get("note"):
            s.append(Paragraph(tb["note"], sNt))
        s.append(sp(0.2))

    if sec.get("info_box"):
        ib = sec["info_box"]
        s.append(box_info(ib.get("label","INFO"), ib.get("text",""),
                          uid=ib.get("label","x")))
        s.append(sp(0.2))

# ── Module renderer ───────────────────────────────────────────────────────────
def render_module(mod, s):
    s.append(ch_banner(mod["number"], mod["title"], mod.get("subtitle","")))
    s.append(sp())

    for lec in mod.get("lectures", []):
        s.append(lec_banner(lec.get("number",""),
                             lec.get("title",""),
                             lec.get("instructor","")))
        s.append(sp(0.2))

    for sec in mod.get("sections", []):
        render_section(sec, s)

    if mod.get("invest_box"):
        s.append(ibox(mod["invest_box"]))
        s.append(sp(0.2))

    if mod.get("key_takeaways"):
        s.append(kbox(mod["key_takeaways"]))
        s.append(sp(0.2))

    s.append(PageBreak())

# ── Formula Summary ───────────────────────────────────────────────────────────
def build_formula_summary(formula_summary, s):
    if not formula_summary:
        return
    s.append(Paragraph("BẢNG TỔNG HỢP CÔNG THỨC", sTH))
    s.append(hr(NAVY, 1.5)); s.append(sp(0.3))
    data = [["Tên / Chủ đề", "Công thức"]] + formula_summary
    t = Table(data, colWidths=[5*cm, 12*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"DV-B"),
        ("FONTNAME",(0,1),(-1,-1),"DV"),("FONTNAME",(1,1),(1,-1),"DV-M"),
        ("FONTSIZE",(0,0),(-1,-1),8.5),("ALIGN",(0,0),(-1,-1),"LEFT"),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LGRAY]),
        ("GRID",(0,0),(-1,-1),.3,GRAY),
        ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]))
    s.append(t)
    s.append(PageBreak())

# ── References ────────────────────────────────────────────────────────────────
def build_references(refs, s):
    if not refs:
        return
    s.append(Paragraph("TÀI LIỆU THAM KHẢO", sSec))
    s.append(hr(NAVY, 1))
    for r in refs:
        s.append(bp(f"<b>{r.get('name','')}</b>:  {r.get('url','')}"))

# ── Main build ────────────────────────────────────────────────────────────────
def build_doc(data):
    story = []
    story += build_cover(data)
    story += build_toc(data.get("modules", []))
    for mod in data.get("modules", []):
        render_module(mod, story)
    build_formula_summary(data.get("formula_summary", []), story)
    build_references(data.get("references", []), story)
    return story

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Video → Training PDF Generator")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--content_json", required=True, help="Path to content JSON file")
    parser.add_argument("--title", default="Training Guide", help="Course title override")
    args = parser.parse_args()

    with open(args.content_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.title != "Training Guide":
        data["course_title"] = args.title

    course_title = data.get("course_title", args.title)
    footer_fn = make_footer(f"{course_title}  |  Training Guide")

    doc = SimpleDocTemplate(
        args.output, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.8*cm,
        title=course_title,
        author="Video-to-PDF Trainer Skill",
        subject="Training Guide"
    )

    story = build_doc(data)
    n = len(story)
    doc.build(story, onFirstPage=footer_fn, onLaterPages=footer_fn)
    print(f"✓ PDF saved → {args.output}  ({n} flowable elements)")

if __name__ == "__main__":
    main()
