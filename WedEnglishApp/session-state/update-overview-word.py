from pathlib import Path
from docx import Document
from docx.shared import Cm,Pt
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

root=Path(__file__).resolve().parents[1]
doc=Document(root/'Bao_cao_NHK_English_times.docx')
ps=doc.paragraphs
caption=next(p for p in ps if p.style.name=='NHKFigureCaption' and 'Sơ đồ use case tổng quát' in p.text)
i=next(i for i,p in enumerate(ps) if p._p is caption._p)
pic=ps[i-1]
rid=pic._p.xpath('.//a:blip/@r:embed')[0]
doc.part.related_parts[rid]._blob=(root/'docs/use-cases/01-tong-quat.png').read_bytes()
for shape in doc.inline_shapes:
 if shape._inline.xpath('.//a:blip/@r:embed')==[rid]:
  shape.width=Cm(14.7);shape.height=Cm(14.7*2610/1900)
# The overview occupies its own readable page. Preserve the existing explanation.
ps[i+1].paragraph_format.page_break_before=True
anchor=next(p for p in ps if p.text.startswith('Hệ thống gồm 4 tác nhân chính:'))
e=OxmlElement('w:p');anchor._p.addnext(e);p=Paragraph(e,anchor._parent)
p.add_run('Sơ đồ tổng quát gồm 37 use case, thể hiện bốn tác nhân ở ngoài ranh giới hệ thống. Các chức năng chung về đăng nhập, đổi mật khẩu và đăng xuất được đặt ở giữa. Bốn quan hệ «include» lần lượt mô tả đăng ký khóa học phải gửi nguyện vọng lịch học, tạo hoặc chỉnh sửa lớp phải thiết lập lịch tuần, xếp lớp phải kiểm tra điều kiện và chấm bài phải nhập kết quả. Việc xác thực là điều kiện truy cập cho các chức năng được bảo vệ; xác nhận thu học phí vẫn độc lập với xác nhận xếp lớp.')
p.paragraph_format.first_line_indent=Cm(.65);p.paragraph_format.line_spacing=1.12;p.paragraph_format.space_after=Pt(2)
for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(13)
out=root/'docs/report-work/final-refresh/nhk-overview-draft.docx';doc.save(out)
# Use the detailed overview whenever the report diagrams are regenerated.
q=root/'docs/report-work/final-refresh/diagrams.cjs';s=q.read_text(encoding='utf-8')
start=s.index(' let s=start(1200,1050)');end=s.index(' // Core entity diagram.',start)
s=s[:start]+" require('../../use-cases/overview-nhk.cjs');\n let s;\n"+s[end:];q.write_text(s,encoding='utf-8')
print(out)
