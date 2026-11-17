from pathlib import Path
from docx import Document
from docx.shared import Pt,Cm
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parent
source=R.parent.parent/'Bao_cao_HITC_English_50_trang.docx'
d=Document(source)
texts=[p.text for p in d.paragraphs]
main=False;count=0;references=False
for p in d.paragraphs:
    if p.style.name.startswith('Heading')and p.text=='MỞ ĐẦU':main=True
    if p.style.name.startswith('Heading')and p.text=='TÀI LIỆU THAM KHẢO':references=True
    if not main:continue
    pr=p._p.get_or_add_pPr()
    for n in list(pr.findall(qn('w:numPr'))):pr.remove(n)
    np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);pr.append(np)
    if p.style.name.startswith('Heading'):
        p.paragraph_format.keep_with_next=True
        p.paragraph_format.space_before=Pt(12);p.paragraph_format.space_after=Pt(7)
        continue
    if p._p.xpath('.//w:drawing'):
        p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(4)
        p.paragraph_format.keep_with_next=True
        continue
    if p.style.name=='HITCFigureCaption':
        p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(7)
        p.paragraph_format.first_line_indent=Cm(0)
        continue
    if not p.text.strip():continue
    p.paragraph_format.left_indent=Cm(0);p.paragraph_format.right_indent=Cm(0)
    p.paragraph_format.first_line_indent=Cm(.75)
    p.paragraph_format.line_spacing=1.15 if references else 1.5
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(6 if references else 8)
    p.paragraph_format.keep_with_next=False;p.paragraph_format.keep_together=False
    p.paragraph_format.widow_control=True
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(13)
    count+=1
for t in d.tables:
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                pr=p._p.get_or_add_pPr()
                for n in list(pr.findall(qn('w:numPr'))):pr.remove(n)
                np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);pr.append(np)
                p.paragraph_format.line_spacing=1.1
                p.paragraph_format.space_after=Pt(3)
assert texts==[p.text for p in d.paragraphs],'Paragraph content changed unexpectedly'
out=R/'no-markers-body50-v2.docx';d.save(out)
print('Text retained, markers removed; body paragraphs formatted:',count)
print(out)
