import importlib.util
for m in ['weasyprint','playwright','pdfkit','xhtml2pdf','reportlab']:
    print(m, bool(importlib.util.find_spec(m)))
