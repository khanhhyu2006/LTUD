from pathlib import Path
import pypdfium2 as pdfium
import sys
from PIL import Image,ImageOps,ImageDraw
from pypdf import PdfReader
root=Path(__file__).resolve().parent
source=root/'qa'/(sys.argv[1]if len(sys.argv)>1 else'report.pdf')
qa=root/'qa'/(sys.argv[2]if len(sys.argv)>2 else'')
qa.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(str(source))
rows=[]
for i,page in enumerate(pdf):
    im=page.render(scale=1.5).to_pil().convert('RGB')
    im.save(qa/f'page-{i+1}.png')
    text=page.get_textpage().get_text_range()
    rows.append(f'\n### PAGE {i+1}\n'+text)
for start in range(0,len(pdf),12):
    sheet=Image.new('RGB',(4*310,3*450),'#d9dfe5')
    d=ImageDraw.Draw(sheet)
    for j in range(start,min(start+12,len(pdf))):
        im=Image.open(qa/f'page-{j+1}.png');im.thumbnail((296,420))
        x=(j-start)%4*310+7;y=(j-start)//4*450+24
        sheet.paste(im,(x,y));d.text((x,y-19),f'Page {j+1}',fill='black')
    sheet.save(qa/f'contact-{start//12+1}.png')
(qa/'pages.txt').write_text(''.join(rows),encoding='utf8')
print('Rendered',len(pdf),'pages')
for i,p in enumerate(PdfReader(str(source)).pages):
    t=p.extract_text()
    print(i+1,len(t),t.replace('\n',' ')[:95])
