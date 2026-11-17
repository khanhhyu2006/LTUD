from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from collections import Counter
import pypdfium2 as pdfium
import json
base=Path('D:/LTUD/7_NguyenKhanhHuy')
src=base/'16_NguyenKhanhHuy_baocaoLLUD.docx'
out=base/'16_NguyenKhanhHuy_baocaoLLUD_Muc_luc_tu_dong.docx'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def content(path):
 with ZipFile(path) as z:
  r=E.fromstring(z.read('word/document.xml'))
  ps=[]
  for p in r.xpath('//w:body/w:p | //w:body/w:tbl//w:p',namespaces=ns):
   style=p.xpath('./w:pPr/w:pStyle/@w:val',namespaces=ns)
   if style and style[0].lower().startswith('toc'):continue
   t=''.join(p.xpath('.//w:t/text()',namespaces=ns))
   if t.strip():ps.append(t)
  media={x:z.read(x) for x in z.namelist() if x.startswith('word/media/')}
  return ps,media,r
a,am,_=content(src);b,bm,r=content(out)
assert a==b,'Body content changed'
assert Counter(am.values())==Counter(bm.values()),'Images changed'
fields=[t for t in r.xpath('//w:instrText/text()',namespaces=ns) if t.strip().startswith('TOC ')]
assert len(fields)==3
pdf=pdfium.PdfDocument('docs/report-work/qa/user-toc.pdf')
qa=Path('docs/report-work/qa/user-toc');qa.mkdir(exist_ok=True)
from PIL import Image,ImageDraw
texts=[]
for i,page in enumerate(pdf):
 im=page.render(scale=1.25).to_pil().convert('RGB');im.save(qa/f'page-{i+1}.png')
 texts.append(page.get_textpage().get_text_range())
for start in range(0,len(pdf),12):
 sheet=Image.new('RGB',(1240,1350),'#d9dfe5');d=ImageDraw.Draw(sheet)
 for i in range(start,min(start+12,len(pdf))):
  im=Image.open(qa/f'page-{i+1}.png');im.thumbnail((296,420))
  x=(i-start)%4*310+7;y=(i-start)//4*450+24
  sheet.paste(im,(x,y));d.text((x,y-18),str(i+1),fill='black')
 sheet.save(qa/f'contact-{start//12+1}.png')
assert not any('Error! Bookmark' in t or 'Error! No table' in t for t in texts)
(qa/'pages.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{t}'for i,t in enumerate(texts)),encoding='utf8')
print(json.dumps({'pages':len(pdf),'automatic_lists':len(fields),'body_preserved':True,'images_preserved':True}))
