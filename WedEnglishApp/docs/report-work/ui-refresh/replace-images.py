from pathlib import Path
from docx import Document
from lxml import etree
from PIL import Image,ImageDraw
import zipfile,io,json
root=Path(__file__).resolve().parent
src=Path('D:/Wold/Bao_cao_LLUD.docx')
names=['home','home-student','programs','detail','test','qr','receipt','myclasses','schedule','payments','profile','admin-dashboard','admin-banners','admin-programs','admin-classes','admin-registrations','admin-payments','admin-teachers','admin-students','admin-trash','teacher-dashboard','teacher-classes','teacher-students','teacher-tests','teacher-documents','teacher-feedback','teacher-salary','admin-salaries','login','register','change-password']
doc=Document(src);patch={};audit=[]
for rid,name in zip(range(21,52),names):
    part=doc.part.related_parts[f'rId{rid}'];target=str(part.partname).lstrip('/');p=root/'assets'/f'ui-{name}.png'
    im=Image.open(p).convert('RGB');buf=io.BytesIO();fmt='JPEG' if target.lower().endswith(('.jpg','.jpeg')) else 'PNG';im.save(buf,format=fmt,**({'quality':94,'dpi':(144,144)} if fmt=='JPEG' else {}));patch[target]=buf.getvalue();audit.append({'relationship':f'rId{rid}','media':target,'screenshot':str(p)})
out=root/'updated-ui-draft.docx'
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as w:
    for item in z.infolist():w.writestr(item,patch.get(item.filename,z.read(item.filename)))
new=Document(out);assert [p.text for p in new.paragraphs]==[p.text for p in doc.paragraphs];assert len(new.inline_shapes)==len(doc.inline_shapes)
(root/'replacement-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
for start in range(0,len(names),8):
    sheet=Image.new('RGB',(1600,1000),'#dddddd');d=ImageDraw.Draw(sheet)
    for j,name in enumerate(names[start:start+8]):
        im=Image.open(root/'assets'/f'ui-{name}.png').convert('RGB');im.thumbnail((790,450));x=j%2*800;y=j//2*250;im.thumbnail((790,225));sheet.paste(im,(x,y+22));d.text((x+5,y+4),name,fill='black')
    sheet.save(root/f'screens-{start//8+1}.png')
print('Replaced',len(patch),'images; text and image count unchanged',out)
