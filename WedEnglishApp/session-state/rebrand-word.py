from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import hashlib,json,re
from docx import Document

root=Path(__file__).resolve().parents[1]
src=root/'Bao_cao_LLUD_Khoi_phuc_noi_dung_goc.docx'
out=root/'docs/report-work/final-refresh/nhk-brand-draft.docx'
assets=root/'docs/report-work/final-refresh/assets'
manifest=json.loads((root/'session-state/rebrand-media-before.json').read_text())
source_doc=Document(src)
forced={str(source_doc.part.related_parts[rid].partname).lstrip('/'):name for rid,name in {
 'rId16':'uc-guest.png','rId17':'uc-student.png','rId18':'uc-teacher.png',
 'rId19':'uc-admin.png','rId20':'data-model.png','rId23':'ui-home.png'}.items()}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
patterns=[(re.compile(r'contact@hitc\.edu\.vn',re.I),'contact@nhkenglishtimes.vn'),
 (re.compile(r'tuyensinh@hitc\.edu\.vn',re.I),'tuyensinh@nhkenglishtimes.vn'),
 (re.compile(r'HITC(?:[ \t]+ENGLISH(?:[ \t]+CENTER)?)?',re.I),'NHK English times')]
media=[];edits=0
def change_nodes(nodes):
 global edits
 for pattern,new in patterns:
  text=''.join(n.text or '' for n in nodes)
  for m in reversed(list(pattern.finditer(text))):
   offsets=[];pos=0
   for n in nodes:
    s=n.text or '';offsets.append((n,pos,pos+len(s)));pos+=len(s)
   touched=[x for x in offsets if x[1]<m.end() and x[2]>m.start()]
   for j,(n,a,b) in enumerate(touched):
    s=n.text or '';left=max(0,m.start()-a);right=min(len(s),m.end()-a)
    n.text=s[:left]+(new if j==0 else '')+s[right:]
    n.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
   edits+=1
with ZipFile(src) as zin,ZipFile(out,'w',ZIP_DEFLATED) as zout:
 for info in zin.infolist():
  data=zin.read(info.filename)
  if info.filename.startswith('word/media/'):
   name=forced.get(info.filename) or manifest.get(hashlib.sha256(data).hexdigest())
   if name and name.startswith(('ui-','uc-','data-','enrollment-')):
    data=(assets/name).read_bytes();media.append(name)
  elif info.filename.endswith('.xml'):
   x=etree.fromstring(data)
   for p in x.xpath('//w:p',namespaces=ns):change_nodes(p.xpath('.//w:t',namespaces=ns))
   if info.filename.startswith('docProps/'):
    for e in x.iter():
     if e.text:
      for pat,new in patterns:e.text=pat.sub(new,e.text)
   data=etree.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
   data=data.replace(b'HITCFigureCaption',b'NHKFigureCaption')
  zout.writestr(info,data)
audit={'source':str(src),'output':str(out),'text_edits':edits,'updated_media':media,'media_count':len(media)}
(root/'session-state/nhk-word-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('Text changes:',edits,'Images updated:',len(media));print(out)
