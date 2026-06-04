from pathlib import Path
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

src=Path('skills/mit-18-642-transcript-trained-lh-model/SKILL.md')
text=src.read_text(encoding='utf-8')
out_md=Path('reports/MIT_18_642_Full_Skill_LH_Model.md')
out_pdf=Path('reports/MIT_18_642_Full_Skill_LH_Model.pdf')
out_md.write_text(text,encoding='utf-8')
font='Helvetica'
for fp in [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\calibri.ttf', r'C:\Windows\Fonts\segoeui.ttf']:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFont', fp)); font='VNFont'; break
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='VNTitle', parent=styles['Title'], fontName=font, fontSize=18, leading=23, spaceAfter=14))
styles.add(ParagraphStyle(name='VNH1', parent=styles['Heading1'], fontName=font, fontSize=14, leading=19, spaceBefore=12, spaceAfter=7))
styles.add(ParagraphStyle(name='VNH2', parent=styles['Heading2'], fontName=font, fontSize=12, leading=16, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name='VNBody', parent=styles['BodyText'], fontName=font, fontSize=9.5, leading=13, spaceAfter=4, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='VNCode', parent=styles['Code'], fontName=font, fontSize=7.5, leading=9, leftIndent=10, backColor='#f3f4f6'))
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
story=[]; in_code=False; code=[]
for line in text.splitlines():
    if line.strip().startswith('```'):
        if not in_code: in_code=True; code=[]
        else:
            if code: story.append(Paragraph(esc('\n'.join(code)).replace('\n','<br/>'), styles['VNCode'])); story.append(Spacer(1,4))
            in_code=False
        continue
    if in_code: code.append(line); continue
    if line.startswith('# '): story.append(Paragraph(esc(line[2:]), styles['VNTitle']))
    elif line.startswith('## '): story.append(PageBreak()); story.append(Paragraph(esc(line[3:]), styles['VNH1']))
    elif line.startswith('### '): story.append(Paragraph(esc(line[4:]), styles['VNH2']))
    elif line.startswith('#### '): story.append(Paragraph('<b>'+esc(line[5:])+'</b>', styles['VNBody']))
    elif line.strip()=='---': story.append(Spacer(1,8))
    elif line.startswith('- '): story.append(Paragraph('• '+esc(line[2:]), styles['VNBody']))
    elif re.match(r'^\d+\. ', line): story.append(Paragraph(esc(line), styles['VNBody']))
    elif line.strip(): story.append(Paragraph(esc(line), styles['VNBody']))
    else: story.append(Spacer(1,3))
SimpleDocTemplate(str(out_pdf), pagesize=A4, rightMargin=1.25*cm, leftMargin=1.25*cm, topMargin=1.25*cm, bottomMargin=1.25*cm).build(story)
print(out_md, out_md.stat().st_size)
print(out_pdf, out_pdf.stat().st_size)
