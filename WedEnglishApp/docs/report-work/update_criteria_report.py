from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table
from pathlib import Path
from PIL import Image
import json,re
R=Path('docs/report-work');d=Document('Bao_cao_LLUD_Ra_soat_hoan_chinh.docx');ps=list(d.paragraphs);start=next(i for i,p in enumerate(ps) if p.text=='MỞ ĐẦU' and p.style.name=='Heading 1');body=ps[start:]
evidence=json.loads(Path('session-state/criteria-data-evidence.json').read_text(encoding='utf-8-sig'));schema=json.loads(Path('session-state/report-criteria-schema.json').read_text(encoding='utf-8-sig'));tests=json.loads(Path('session-state/criteria-checks/results.json').read_text(encoding='utf-8-sig'))
def settext(p,t):p.clear();p.add_run(t)
rewrites={
'Quản trị người dùng và phân quyền bảo mật:':'Quản trị người dùng: Admin tạo, sửa hồ sơ và khóa/mở tài khoản học viên, giáo viên. Cookie được kiểm tra lại theo trạng thái tài khoản ở mỗi yêu cầu; tài khoản bị khóa hoặc xóa mềm không tiếp tục dùng phiên cũ.',
'Thống kê quản trị:':'Thống kê quản trị: Dashboard lấy số liệu từ SQL Server theo năm được chọn. Doanh thu có đủ 12 tháng; biểu đồ ghi danh tổng hợp số đơn theo chương trình. Admin xem báo cáo chi tiết, xuất CSV và in/lưu PDF bằng trình duyệt.',
'Chart.js được dùng tại trang quản trị':'Chart.js hiển thị doanh thu theo tháng và số ghi danh theo chương trình từ truy vấn tổng hợp [8]. Các tháng không có khoản thu nhận giá trị 0; không còn sử dụng chuỗi số liệu mẫu viết cố định trong View.',
'Mô hình có 16 bảng nghiệp vụ':'Mô hình gồm 16 bảng nghiệp vụ chính và TeacherActivities lưu hoạt động giáo viên, tổng cộng 17 bảng ứng dụng. Sơ đồ tổng quát thể hiện các khóa ngoại; hai sơ đồ nhóm phía sau trình bày các quan hệ chính của đào tạo và hỗ trợ.',
'Thiết kế được đối chiếu với metadata':'Thiết kế được đối chiếu với SQL Server sau nâng cấp: 17 bảng ứng dụng, 157 cột và 22 ràng buộc khóa ngoại. TeacherActivities lưu nhật ký nghiệp vụ giáo viên. Các bảng lịch sử triển khai và __EFMigrationsHistory không tính vào số bảng này; Models/Class.cs và Models/Program.cs rỗng không tạo thêm thực thể.',
'Luồng xử lý: Giáo viên mở phân hệ tài liệu':'Luồng xử lý: Giáo viên chọn lớp mình phụ trách, nhập tiêu đề và tải tệp hợp lệ. Tệp mới được lưu riêng trong App_Data/ClassDocuments; bảng ClassDocuments lưu định danh tệp, trạng thái công bố và thời điểm cập nhật. Giáo viên có thể sửa, thay tệp, công bố/ẩn, tải về hoặc xóa.',
'Kết quả: Tài liệu gắn với lớp':'Kết quả: Tài liệu được quản lý theo lớp và được kiểm tra quyền ở từng thao tác. Học viên chỉ xem/tải tài liệu đã công bố của lớp được xếp Confirmed. Hoạt động của giáo viên được lưu cùng giao dịch và vẫn còn sau khi tài liệu bị xóa.',
'Lưu ý về dữ liệu thời gian:':'Dữ liệu thời gian: Khoản thu mới lưu ConfirmedAt ở lần xác nhận đầu tiên; cập nhật có điều kiện tránh ghi đè khi yêu cầu được gửi lặp. Khoản đã Paid từ trước giữ nguyên dữ liệu, ConfirmedAt để NULL; báo cáo và biên lai dùng PaymentDate làm mốc lịch sử khi chưa có ConfirmedAt. Việc xác nhận thu không thay đổi ClassId hoặc trạng thái xếp lớp.',
'Biên lai nội bộ hiển thị':'Biên lai nội bộ hiển thị mã #PAY-{id}, học viên, chương trình, lớp nếu đã xếp và số tiền. Chỉ khoản đã Paid mới mở trang in. Ngày hiển thị ưu tiên ConfirmedAt, sau đó PaymentDate của dữ liệu cũ; nhãn “đã thu tiền” không phải chữ ký số được chứng thực.',
'Hiển thị chi tiết: Tên khóa học':'Hiển thị lớp, khóa học, phòng, giáo viên và lịch tuần; đơn chờ xếp có khu vực nguyện vọng riêng. Liên kết Tài liệu học tập mở danh sách tài liệu đã công bố cho lớp của học viên. Máy chủ kiểm tra ghi danh Confirmed trước khi cho tải từng tệp.',
'Danh sách học phí hiển thị':'Danh sách học phí hiển thị mã, phương thức, số tiền và trạng thái. Thời điểm xác nhận mới được lưu ở ConfirmedAt; các khoản thu cũ vẫn dùng PaymentDate đang lưu để đối chiếu lịch sử.',
'Biểu đồ Chart.js minh họa':'Biểu đồ Chart.js dùng dữ liệu thật theo năm: số tiền của Payments Paid được cộng theo tháng; phân bổ chương trình được tính từ đơn chưa hủy, chưa xóa trong năm. Tháng không có thu nhận 0; dữ liệu tiền cũ dùng PaymentDate, dữ liệu mới ưu tiên ConfirmedAt.',
'View nhận một số tổng số':'Dashboard và báo cáo tài chính dùng chung ReportingService. View nhận nhãn và giá trị được tuần tự hóa JSON; tổng doanh thu trên báo cáo đã được đối chiếu với truy vấn SQL trong kiểm thử.',
'Quản lý Giảng viên (TeacherManager):':'Quản lý giáo viên: Admin tạo tài khoản với mật khẩu băm BCrypt, sửa chuyên môn và hồ sơ, khóa/mở hoặc xóa mềm. Khóa có hiệu lực với phiên đang mở ở yêu cầu tiếp theo; mở lại cho phép đăng nhập bình thường.',
'Các phần cần hoàn thiện trong ứng dụng gồm':'Các phần còn cần phát triển gồm lưu điểm danh theo buổi, gửi thư tự động và đối soát ngân hàng tự động. Quản lý tài liệu đã có CRUD, công bố/ẩn, tải xuống theo quyền và giới hạn tệp; báo cáo đã dùng dữ liệu tổng hợp thật.',
'Thanh toán còn cần Admin đối soát;':'Thanh toán còn cần Admin đối soát; chưa có callback ngân hàng để tự động ghi nhận kết quả. ConfirmedAt lưu thời điểm xác nhận cho khoản mới; dữ liệu cũ không được suy diễn thêm ngày xác nhận.',
'Phân hệ Admin quản lý đào tạo':'Phân hệ Admin quản lý đào tạo, nhân sự, ghi danh, học phí, tư vấn và banner. Dashboard và báo cáo tổng hợp dữ liệu thực theo năm, có xuất CSV và in/lưu PDF; không dùng số liệu biểu đồ viết cố định.',
}
for p in body:
 if p._p.xpath('.//w:instrText') or p._p.xpath('.//w:drawing'):continue
 for prefix,new in rewrites.items():
  if p.text.startswith(prefix):settext(p,new);break
 else:
  t=p.text.replace('Quản trị 16 bảng nghiệp vụ','Quản trị 17 bảng ứng dụng').replace('Thiết kế 16 bảng nghiệp vụ gồm','Thiết kế 16 bảng nghiệp vụ chính gồm')
  if t.startswith('Sơ đồ thực thể kết hợp (ERD):'):t+=' Bảng TeacherActivities bổ sung nhật ký giáo viên, đưa tổng số bảng ứng dụng lên 17.'
  if 'liên kết đặc tả nghiệp vụ với 16 bảng dữ liệu' in t:t=t.replace('16 bảng dữ liệu','17 bảng ứng dụng')
  if t!=p.text:settext(p,t)
def normal(t,anchor,bold=False,style='Normal'):
 p=d.add_paragraph(style=style);anchor._p.addprevious(p._p);p.add_run(t);p.paragraph_format.space_after=Pt(4);p.paragraph_format.line_spacing=1.12
 if style.startswith('Heading'):
  n=OxmlElement('w:numPr');v=OxmlElement('w:numId');v.set(qn('w:val'),'0');n.append(v);p._p.get_or_add_pPr().append(n);p.paragraph_format.keep_with_next=True
 for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(13);r.font.bold=bold or style.startswith('Heading');r.font.color.rgb=RGBColor(0,0,0)
 return p
def field(p,code,cache):
 for typ,txt in [('begin',None),('code',code),('separate',None),('text',cache),('end',None)]:
  r=OxmlElement('w:r');e=OxmlElement('w:instrText' if typ=='code' else 'w:t' if typ=='text' else 'w:fldChar')
  if txt is not None:e.text=txt
  else:e.set(qn('w:fldCharType'),typ)
  r.append(e);p._p.append(r)
def caption(t,anchor,kind='Bang',num=1):
 p=normal('',anchor,style='NHKTableCaption' if kind=='Bang' else 'NHKFigureCaption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=(kind=='Bang');p.add_run('Bảng ' if kind=='Bang' else 'Hình ');field(p,'SEQ '+kind+' '+chr(92)+'* ARABIC',str(num));p.add_run('. '+t);return p
def table(headers,rows,anchor,title,num):
 caption(title,anchor,num=num);t=d.add_table(rows=1, cols=len(headers));anchor._p.addprevious(t._tbl);t.style='Table Grid'
 for c,txt in zip(t.rows[0].cells,headers):c.text=txt
 for row in rows:
  for c,txt in zip(t.add_row().cells,row):c.text=str(txt)
 fmt(t);return t
def fmt(t):
 for i,row in enumerate(t.rows):
  if i==0:
   row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
  for cell in row.cells:
   pr=cell._tc.get_or_add_tcPr();borders=pr.find(qn('w:tcBorders'))
   if borders is None:borders=OxmlElement('w:tcBorders');pr.append(borders)
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D6DBDF');borders.append(e)
   for p in cell.paragraphs:
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.04;p.paragraph_format.keep_with_next=False
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10.5);r.bold=(i==0)
def rowsadd(t,rows):
 for vals in rows:
  for cell,value in zip(t.add_row().cells,vals):cell.text=value
 fmt(t)
def bycaption(name):
 p=next(p for p in d.paragraphs if p.style.name=='NHKTableCaption' and p.text.endswith(name));x=p._p.getnext()
 while x is not None and x.tag!=qn('w:tbl'):x=x.getnext()
 return Table(x,d._body)
rowsadd(bycaption('Thiết kế chi tiết bảng Payments'),[['ConfirmedAt','datetime2(7)','NULL','Thời điểm xác nhận đầu tiên của khoản thu mới; NULL cho chứng từ cũ chưa có mốc xác nhận.']])
rowsadd(bycaption('Thiết kế chi tiết bảng ClassDocuments'),[['IsPublished','bit','NOT NULL; DEFAULT 1','Trạng thái công bố cho học viên đã xếp vào lớp; bản ghi mới theo lựa chọn trên biểu mẫu.'],['UpdatedAt','datetime2(7)','NULL','Lần sửa nội dung hoặc thay đổi công bố gần nhất.']])
rowsadd(bycaption('Tổng hợp các bảng và trường dữ liệu chính'),[['TeacherActivities','PK ActivityId; FK TeacherId; Kind, Description, OccurredAt','Nhật ký thao tác tài liệu, chấm bài và ảnh hồ sơ của giáo viên.']])
relations=bycaption('Các quan hệ và hành vi khi xóa');rowsadd(relations,[['Teacher – TeacherActivity','1 – N','Nhật ký gắn giáo viên; xóa vật lý giáo viên dùng Cascade. Xóa tài liệu không xóa nhật ký vì không có FK đến tài liệu.']])
anchor=next(p for p in d.paragraphs if p.text=='Các quan hệ và hành vi khi xóa')
normal('q) Bảng TeacherActivities',anchor,True)
table(['Tên trường','Kiểu SQL Server','Ràng buộc','Ý nghĩa'],[['ActivityId','int','PK; IDENTITY; NOT NULL','Mã nhật ký.'],['TeacherId','int','FK; NOT NULL','Giáo viên thực hiện thao tác; tham chiếu Teachers.TeacherId.'],['Kind','nvarchar(30)','NOT NULL','Loại thao tác tài liệu, chấm thi hoặc hồ sơ.'],['Description','nvarchar(300)','NOT NULL','Mô tả do máy chủ tạo; hiển thị dưới dạng văn bản.'],['OccurredAt','datetime2(7)','NOT NULL','Thời điểm ghi nhận thao tác mới; không tạo nhật ký giả cho quá khứ.']],anchor,'Thiết kế chi tiết bảng TeacherActivities',22)
gv=bycaption('Đặc tả chi tiết các nghiệp vụ quản trị của giáo viên')
for r in gv.rows:
 if r.cells[0].text.startswith('GV04'):
  for c,t in zip(r.cells,['GV04\nQuản lý tài liệu','Teacher phụ trách lớp; tệp PDF/DOCX/PPTX/XLSX/TXT hợp lệ, không quá 10 MB.','Thêm, sửa tiêu đề/thay tệp, xóa, công bố/ẩn, tải về. Lưu tệp riêng; cập nhật dữ liệu và nhật ký cùng giao dịch.','Kiểm tra quyền tại từng action. Học viên chỉ tải bản đã công bố của lớp được xếp; URL tệp tĩnh cũ bị chặn.']):c.text=t
rowsadd(gv,[['GV08\nThống kê và báo cáo','Teacher đăng nhập; khoảng ngày hợp lệ.','Lọc kỳ; tổng hợp lớp, sĩ số hiện tại, kết quả bài thi được giao và số hoạt động; xuất CSV hoặc in/lưu PDF.','Phạm vi lấy theo TeacherId của phiên; CSV có BOM UTF-8 và xử lý ô bắt đầu bằng ký tự công thức.']])
ad=bycaption('Đặc tả chi tiết các nghiệp vụ quản trị Admin')
for r in ad.rows:
 if r.cells[0].text.startswith('AD07'):r.cells[2].text='Tạo/sửa hồ sơ giáo viên, học viên; khóa/mở tài khoản, xóa mềm và khôi phục theo chức năng.';r.cells[3].text='Tài khoản bị khóa không đăng nhập hoặc dùng tiếp cookie cũ; mật khẩu lưu dưới dạng băm.'
 if r.cells[0].text.startswith('AD10'):r.cells[2].text='Lọc năm, xem biểu đồ và báo cáo dữ liệu thật, xuất CSV, in/lưu PDF; quản lý banner và thùng rác.'
fmt(ad)
# Replace the changed diagrams and current screenshots, keeping captions and other material.
figure_files={'4a':'docs/diagrams-clear/Use_case_Guest_criteria.png','4b':'docs/diagrams-clear/Use_case_Student_criteria.png','4c':'docs/diagrams-clear/Use_case_Teacher_criteria.png','4d':'docs/diagrams-clear/Use_case_Admin_criteria.png',7:'docs/diagrams-clear/sequence-payment-criteria.png',3:'docs/diagrams-clear/Use_case_tong_quat_du_tieu_chi.png',5:'docs/diagrams-clear/So_do_CSDL_17_bang.png',21:'session-state/criteria-checks/live-admin-dashboard.png',28:'session-state/criteria-checks/live-admin-teachers.png',35:'session-state/criteria-checks/live-teacher-dashboard.png',39:'session-state/criteria-checks/live-teacher-documents.png'}
figure_files={str(k):v for k,v in figure_files.items()}
for p in body:
 m=re.match(r'^Hình (\d+[a-z]?)\.',p.text)
 if not m or m[1] not in figure_files:continue
 path=Path(figure_files[m[1]]);prev=p._p.getprevious()
 while prev is not None and not prev.xpath('.//w:drawing'):prev=prev.getprevious()
 if prev is None:continue
 for b in prev.xpath('.//a:blip'):d.part.related_parts[b.get(qn('r:embed'))]._blob=path.read_bytes()
 im=Image.open(path);w=Cm(15.4);h=int(w*im.height/im.width);maxh=Cm(20.5 if m[1]=='3' or m[1].startswith('4') else 16)
 if h>maxh:w=int(w*maxh/h);h=maxh
 for e in prev.xpath('.//wp:extent')+prev.xpath('.//a:xfrm/a:ext'):e.set('cx',str(w));e.set('cy',str(h))
# Keep the sequence diagram aligned with confirmation timestamps.
svg=Path('docs/report-work/chapter3-assets/sequence-payment.svg').read_text(encoding='utf8').replace('SaveChanges','ConfirmedAt');Path('docs/diagrams-clear/sequence-payment-criteria.svg').write_text(svg,encoding='utf8')
# The additional evidence sits inside chapter 4, before its existing conclusion.
anchor=next(p for p in d.paragraphs if p.text=='KẾT CHƯƠNG 4')
normal('4.7 Hoàn thiện và đối chiếu tiêu chí đánh giá',anchor,style='Heading 2')
normal('Phiên bản cập nhật bổ sung nghiệp vụ quản lý tài liệu đầy đủ cho giáo viên, hoạt động gần đây, báo cáo theo kỳ, biểu đồ dữ liệu thật và khóa/mở giáo viên. Phần này ghi nhận chức năng và minh chứng thực hiện; không tự quy đổi thành điểm chấm.',anchor)
normal('4.7.1 Phạm vi dữ liệu và các tình huống mẫu',anchor,style='Heading 3')
normal('Cơ sở dữ liệu ứng dụng có 17 bảng và 157 trường sau nâng cấp. Bảng dưới ghi số bản ghi thực tại ngày 05/11/2026, gồm dữ liệu cũ và xóa mềm. Hai tài liệu mẫu được ghi nhãn rõ, gồm bản nháp và bản công bố. Các ca thay đổi dữ liệu để kiểm thử chạy riêng trong EnglishCenterCriteriaTest.',anchor)
table(['Bảng dữ liệu','Số bản ghi'],[[c['Table'],c['Records']] for c in evidence['counts']],anchor,'Độ bao phủ dữ liệu tại thời điểm hoàn thiện',31)
normal('Trạng thái ghi danh: '+', '.join(f"{x['Status']}: {x['Records']}" for x in evidence['registration_states'])+'. Trạng thái học phí: '+', '.join(f"{x['Status']}: {x['Records']}" for x in evidence['payment_states'])+'. Số bản ghi không thay thế số ca kiểm thử.',anchor)
normal('4.7.2 Đối chiếu các hạng mục đã bổ sung',anchor,style='Heading 3')
table(['Hạng mục trong phiếu','Hiện thực','Minh chứng'],[
 ['Nhân viên: hoạt động gần đây','TeacherActivities lưu thao tác tài liệu, chấm bài và ảnh hồ sơ.','TeacherDashboard: 10 hoạt động mới nhất của chính giáo viên.'],
 ['Nhân viên: thêm/sửa/xóa/trạng thái','DocumentController có Upload, Edit, Delete và SetPublished.','Tài liệu có hai trạng thái: bản nháp và công bố; có thể thay tệp.'],
 ['Nhân viên: thống kê/báo cáo','Báo cáo theo khoảng ngày, lớp phụ trách, kết quả thi và hoạt động.','/Teacher/Report; xuất CSV và in/lưu PDF qua trình duyệt.'],
 ['Admin: thống kê/báo cáo','Truy vấn thu theo 12 tháng và số ghi danh theo chương trình trong năm.','/Admin/Dashboard và /Admin/Report dùng chung ReportingService.'],
 ['Admin: kích hoạt/vô hiệu hóa','ToggleStatus cho giáo viên; cookie kiểm tra lại trạng thái tài khoản.','Khóa chặn đăng nhập và thu hồi phiên cũ ở yêu cầu tiếp theo.'],
 ['UI/UX: kiểm tra và lỗi','Kiểm tra quyền sở hữu, tiêu đề, loại tệp, nội dung, kích thước và ngày báo cáo.','Sai quyền trả 404; CSRF/biểu mẫu trạng thái sai bị từ chối; lỗi tệp được thông báo.']],anchor,'Đối chiếu hạng mục chức năng với tiêu chí đánh giá',32)
normal('Vai trò giáo viên được dùng để đối chiếu nhóm “Nhân viên” trong đề tài trung tâm ngoại ngữ. Việc chấp thuận cách quy đổi vai trò và cách chia điểm thuộc đánh giá của giảng viên.',anchor)
normal('4.7.3 Các tính năng bổ sung có thể trình diễn',anchor,style='Heading 3')
table(['Nhóm tính năng','Cách trình diễn','Phạm vi'],[
 ['Mã QR học phí','Mở hướng dẫn VietQR theo đơn.','Admin vẫn đối soát; chưa có callback tự động.'],
 ['Tải tệp và học liệu riêng','Tạo bản nháp, sửa, công bố và tải bằng tài khoản đã xếp lớp.','Tệp lưu ngoài wwwroot; quyền được kiểm tra ở máy chủ.'],
 ['Tư vấn hai chiều','Khách/học viên và Admin gửi, nhận tin trong hội thoại riêng.','Lấy tin định kỳ; không mô tả như WebSocket.'],
 ['Biểu đồ từ dữ liệu thật','Chọn năm và đối chiếu biểu đồ với báo cáo thu.','Không sử dụng chuỗi giá trị viết cố định.'],
 ['Xuất báo cáo','Tải CSV UTF-8 hoặc chọn In/Lưu PDF trên báo cáo.','PDF được lưu qua hộp thoại in của trình duyệt, không phải API tạo PDF riêng.'],
 ['Bảo vệ truy cập','Thử sai quyền, thiếu CSRF hoặc khóa giáo viên đang đăng nhập.','BCrypt, cookie theo vai trò, kiểm tra tài khoản và quyền từng bản ghi.']],anchor,'Các nhóm tính năng bổ sung và phạm vi trình diễn',33)
normal('Phiếu nêu các ví dụ tính năng bổ sung, không yêu cầu triển khai mọi ví dụ. Có thể chọn năm nhóm phù hợp để trình diễn; không mặc định tính lặp điểm cho chức năng đã thuộc nhóm chính.',anchor)
normal('4.7.4 Kiểm thử phiên bản hoàn thiện',anchor,style='Heading 3')
normal('Bản ứng dụng biên dịch thành công, không có cảnh báo hoặc lỗi biên dịch. Bộ kiểm thử tự động ghi nhận '+str(tests['total'])+' kiểm tra đạt trên database riêng. Ba vai trò Admin, Teacher và Student còn được kiểm tra mở trang báo cáo/học liệu trên database chính; thao tác đọc này không sửa ghi danh hoặc học phí.',anchor)
table(['Nhóm kiểm tra','Tình huống chính','Kết quả'],[
 ['Tài liệu','Thêm, sửa/thay tệp, xóa, nháp/công bố; kiểm tra dữ liệu lưu.','Đạt trong bộ kiểm thử.'],
 ['Phân quyền học liệu','Giáo viên khác không sửa/xóa/tải; học viên ngoài lớp hoặc bản nháp không tải.','Đạt; URL tệp tĩnh trực tiếp bị chặn.'],
 ['Tệp và CSRF','EXE, PDF/Office giả, trên 10 MB, thiếu token, trạng thái không hợp lệ.','Bị từ chối; không tạo tài liệu sai.'],
 ['Báo cáo','Giới hạn đúng giáo viên; khoảng ngày/năm sai; CSV bắt đầu bằng công thức.','Đạt; CSV bảo vệ ô công thức.'],
 ['Học phí và biểu đồ','Tổng báo cáo khớp SQL; đủ 12 tháng; xác nhận lặp không đổi mốc đầu tiên.','Đạt; xác nhận không tự xếp lớp.'],
 ['Khóa/mở giáo viên','Khóa phiên đang mở, chặn đăng nhập, kích hoạt lại.','Đạt.'],
 ['Responsive','Các trang tài liệu, báo cáo, dashboard và quản lý giáo viên ở 390/1024/1440 px.','Không tràn ngang toàn trang trong kiểm tra.']],anchor,'Tổng hợp kiểm thử các hạng mục bổ sung',34)
normal('Database đã được sao lưu trước khi nâng cấp. So sánh SHA-256 trên các trường cũ của toàn bộ Payments và Registrations cho kết quả không đổi sau khi thêm cột và bảng. Các đơn và biên lai đã Paid, kể cả các ghi danh trùng trong lịch sử, được giữ nguyên. Các kiểm tra này không thay thế kiểm thử tải hoặc đánh giá bảo mật độc lập.',anchor)
def picture(path,title,num):
 p=normal('',anchor);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
 im=Image.open(path);w=Cm(16);h=int(w*im.height/im.width);maxh=Cm(15.2)
 if h>maxh:w=int(w*maxh/h)
 p.add_run().add_picture(str(path),width=w);caption(title,anchor,'Hinh',num)
picture(Path('session-state/criteria-checks/live-teacher-report-word.png'),'Báo cáo giảng dạy theo kỳ và xuất dữ liệu',46)
picture(Path('session-state/criteria-checks/live-admin-report-word.png'),'Báo cáo thu học phí theo năm từ dữ liệu thực',47)
# Repair claims in the final conclusion without removing the original sections.
for p in body:
 if p.text.startswith('Đánh giá và kiểm thử:'):settext(p,'Các luồng mới được kiểm tra trên database riêng; bộ hoàn thiện tiêu chí có 64 kiểm tra đạt. Kết quả tư vấn trước đó ghi nhận 31 kiểm tra. Phần kiểm thử nêu rõ môi trường, tình huống và phạm vi; chưa có kiểm thử tải hoặc số đo độ trễ để bảo đảm hiệu năng vận hành.')
 if p.text.startswith('Các luồng mới đã được kiểm tra'):settext(p,'Các chức năng bổ sung đã được kiểm tra riêng trên dữ liệu thử, gồm 64 kiểm tra cho tài liệu, phân quyền, báo cáo, CSV, học phí, khóa tài khoản và responsive. Kết quả kiểm thử tư vấn trước đó vẫn được trình bày riêng; không cộng hai bộ để suy ra tỷ lệ bao phủ toàn hệ thống.')
for tab in d.tables:
 for row in tab.rows:
  for cell in row.cells:
   t=cell.text.replace('Luồng học liệu riêng cho học viên cần bổ sung.','Học viên chỉ tải tài liệu đã công bố khi có ghi danh Confirmed.').replace('chức năng tải tài liệu riêng cho học viên cần tiếp tục hoàn thiện.','học viên tải bản đã công bố qua action có kiểm tra quyền.')
   if t!=cell.text:cell.text=t
ref=d.add_paragraph('[11] Phiếu tiêu chí đánh giá đồ án cuối kỳ (100 điểm). Tài liệu “Project _ Tieu chi cham diem_.docx” dùng để đối chiếu yêu cầu.');ref.alignment=WD_ALIGN_PARAGRAPH.LEFT
for run in ref.runs:run.font.name='Times New Roman';run.font.size=Pt(12)
for p in body:
 if p.text.startswith('Kiểm thử và đánh giá:'):
  settext(p,'Kiểm thử: Kiểm tra đăng nhập, phân quyền, ghi danh, xếp lớp, lịch, thi và tư vấn trên dữ liệu riêng. Bảng ca thử phân biệt kết quả đã kiểm tra với ca chưa chạy lại; chưa có kiểm thử tải hoặc bảo mật chuyên sâu.')
k=next(i for i,p in enumerate(body) if p.text=='KẾT CHƯƠNG 4');end=next(i for i,p in enumerate(body[k+1:],k+1) if p.style.name=='Heading 1')
body[k].paragraph_format.page_break_before=True
for i in range(k,end):
 body[i].paragraph_format.keep_with_next=(i<end-1)
 body[i].paragraph_format.keep_together=True
# Keep every original body paragraph/table; only add descriptions and evidence.
assert all(p._p.getparent() is d._element.body for p in body)
d.core_properties.title='Báo cáo NHK English times hoàn thiện tiêu chí đánh giá';d.core_properties.author='Nguyễn Khánh Huy'
out=R/'criteria-report-draft.docx';d.save(out)
print(out,'tables',len(d.tables),'images',len(d.inline_shapes))
