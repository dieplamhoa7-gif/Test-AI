from pathlib import Path
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

REPORTS=Path('reports')
files=[
'MIT_18_642_Chuong_01_Lecture_1_VI.md',
'MIT_18_642_Chuong_02_Linear_Algebra_Probability_VI.md',
'MIT_18_642_Chuong_03_Regression_TimeSeries_PCA_VI.md',
'MIT_18_642_Chuong_04_Portfolio_Risk_Volatility_VI.md',
'MIT_18_642_Chuong_05_Derivatives_BlackScholes_CW_VI.md',
'MIT_18_642_Chuong_06_MachineLearning_StochasticCalculus_Roadmap_VI.md',
'MIT_18_642_Chuong_07_Ke_Hoach_Trien_Khai_LH_Investment_VI.md',
]
combined=['# MIT 18.642 - Hướng dẫn học và áp dụng vào LH Investment (Bản đầy đủ)\n', 'Bản tiếng Việt cho Hòa Đại ka: học tài chính định lượng theo hướng biến thành feature, backtest, risk rule, portfolio và CW scoring.\n']
for f in files:
    combined.append((REPORTS/f).read_text(encoding='utf-8'))
combined_path=REPORTS/'MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment_v2.md'
combined_path.write_text('\n\n---\n\n'.join(combined), encoding='utf-8')

font='Helvetica'
for fp in [r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\calibri.ttf', r'C:\Windows\Fonts\segoeui.ttf']:
    if Path(fp).exists():
        pdfmetrics.registerFont(TTFont('VNFont', fp)); font='VNFont'; break
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='VNTitle', parent=styles['Title'], fontName=font, fontSize=20, leading=26, spaceAfter=16))
styles.add(ParagraphStyle(name='VNH1', parent=styles['Heading1'], fontName=font, fontSize=16, leading=22, spaceBefore=14, spaceAfter=8))
styles.add(ParagraphStyle(name='VNH2', parent=styles['Heading2'], fontName=font, fontSize=13, leading=18, spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name='VNBody', parent=styles['BodyText'], fontName=font, fontSize=10, leading=14, spaceAfter=5, alignment=TA_LEFT))
styles.add(ParagraphStyle(name='VNCode', parent=styles['Code'], fontName=font, fontSize=8, leading=10, leftIndent=12, backColor='#f3f4f6'))

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
story=[]; in_code=False; code=[]
for line in combined_path.read_text(encoding='utf-8').splitlines():
    if line.strip().startswith('```'):
        if not in_code: in_code=True; code=[]
        else:
            if code: story.append(Paragraph(esc('\n'.join(code)).replace('\n','<br/>'), styles['VNCode'])); story.append(Spacer(1,5))
            in_code=False
        continue
    if in_code: code.append(line); continue
    if line.startswith('# '): story.append(Paragraph(esc(line[2:]), styles['VNTitle']))
    elif line.startswith('## '): story.append(Paragraph(esc(line[3:]), styles['VNH1']))
    elif line.startswith('### '): story.append(Paragraph(esc(line[4:]), styles['VNH2']))
    elif line.strip()=='---': story.append(PageBreak())
    elif line.startswith('- [ ]'): story.append(Paragraph('☐ '+esc(line[5:].strip()), styles['VNBody']))
    elif line.startswith('- '): story.append(Paragraph('• '+esc(line[2:]), styles['VNBody']))
    elif re.match(r'^\d+\. ', line): story.append(Paragraph(esc(line), styles['VNBody']))
    elif line.strip(): story.append(Paragraph(esc(line), styles['VNBody']))
    else: story.append(Spacer(1,4))
pdf_path=REPORTS/'MIT_18_642_Huong_Dan_Hoc_Va_Ap_Dung_LH_Investment_v2.pdf'
doc=SimpleDocTemplate(str(pdf_path),pagesize=A4,rightMargin=1.4*cm,leftMargin=1.4*cm,topMargin=1.4*cm,bottomMargin=1.4*cm)
doc.build(story)
print(combined_path, combined_path.stat().st_size)
print(pdf_path, pdf_path.stat().st_size)
