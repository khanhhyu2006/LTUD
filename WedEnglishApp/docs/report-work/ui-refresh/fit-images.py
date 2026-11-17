from docx import Document
from pathlib import Path
p=Path('docs/report-work/ui-refresh/updated-ui-draft.docx')
d=Document(p)
for shape in d.inline_shapes:
    rid=shape._inline.xpath('.//a:blip')[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
    if rid in [f'rId{i}' for i in range(21,52)]:shape.height=round(shape.width*820/1280)
d.save(p)
