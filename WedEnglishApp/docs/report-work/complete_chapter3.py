from pathlib import Path
from copy import deepcopy
from io import BytesIO
import json,re,hashlib
from lxml import etree
from PIL import Image
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

R=Path(__file__).resolve().parent;ROOT=R.parents[1];A=R/'chapter3-assets'
source=ROOT/'Bao_cao_LLUD_Khoi_phuc_noi_dung_goc.docx';d=Document(source)
schema=json.loads((ROOT/'session-state/report-live-schema.json').read_text(encoding='utf-8'))
ps=d.paragraphs;start=next(p for p in ps if p.style.name=='Heading 1' and p.text.startswith('CHƯƠNG 3'))
end=next(p for p in ps if p.style.name=='Heading 1' and p.text.startswith('CHƯƠNG 4'))
sidx=ps.index(start);eidx=ps.index(end)
body=d.element.body;children=list(body);a=children.index(start._p);b=children.index(end._p)
before=[etree.tostring(x,method='c14n') for x in children[:a]];after=[etree.tostring(x,method='c14n') for x in children[b:]]
saved={i:deepcopy(p._p) for i,p in enumerate(ps) if sidx<=i<eidx}
oldtables=[deepcopy(t._tbl) for t in d.tables if children.index(t._tbl)>a and children.index(t._tbl)<b]
original_text=[p.text for p in ps[sidx:eidx] if p.text and not p.style.name.startswith('Heading') and p.style.name!='HITCFigureCaption']
for x in children[a:b]:body.remove(x)
new=[];newtables=[]
def emit(el):
 if el.getparent() is body:body.remove(el)
 end._p.addprevious(el);new.append(el);return el
def para(text='',style='Normal',bold=False):
 p=d.add_paragraph(text,style);emit(p._p);f=p.paragraph_format
 f.space_after=Pt(3);f.space_before=Pt(0);f.line_spacing=1.12;f.first_line_indent=Cm(.65);f.widow_control=True
 if style.startswith('Heading'):
  f.keep_with_next=True;f.first_line_indent=Cm(0);f.space_before=Pt(8);f.space_after=Pt(5)
  f.page_break_before=style=='Heading 1'
  num=OxmlElement('w:numPr');nid=OxmlElement('w:numId');nid.set(qn('w:val'),'0');num.append(nid);p._p.get_or_add_pPr().append(num)
 else:p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
 if bold:f.keep_with_next=True
 for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(15 if style=='Heading 1' else 14 if style=='Heading 2' else 13);r.font.color.rgb=RGBColor(0,0,0);r.bold=bold or style.startswith('Heading')
 return p
def h(t,l=2):return para(t,'Heading '+str(l))
def tree(text):
 p=para(text);p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1;p.paragraph_format.keep_together=True
 for r in p.runs:r.font.name='Consolas';r.font.size=Pt(10.5)
 return p
def old(i,normal_heading=False,text=None):
 e=deepcopy(saved[i]);emit(e);p=Paragraph(e,d._body)
 if normal_heading:
  p.style='Normal';p.text=re.sub(r'^\d+(?:\.\d+)*\s*','',p.text);p.paragraph_format.keep_with_next=True
  for r in p.runs:r.bold=True;r.font.name='Times New Roman';r.font.size=Pt(13)
 if text is not None:p.text=text
 return p
def oldrange(i,j):
 for k in range(i,j):old(k,ps[k].style.name.startswith('Heading'))
def field(p,code,result):
 for tag,val in [('w:fldChar','begin'),('w:instrText',code),('w:fldChar','separate'),('w:t',str(result)),('w:fldChar','end')]:
  x=OxmlElement(tag)
  if tag=='w:fldChar':x.set(qn('w:fldCharType'),val)
  else:x.text=val
  p.add_run()._r.append(x)
def caption(title,number,sub=False):
 p=para('' if not sub else title,'Normal' if sub else 'HITCFigureCaption');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;f=p.paragraph_format;f.first_line_indent=Cm(0);f.line_spacing=1.05;f.space_after=Pt(6);f.keep_together=True
 if not sub:p.add_run('Hình ');field(p,' SEQ Hinh \\* ARABIC ',number);p.add_run('. '+title)
 for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(11);r.italic=True
 return p
def picture(path,title=None,number=None,width=14.7,maxheight=20):
 im=Image.open(path);w=width;hh=w*im.height/im.width
 if hh>maxheight:w*=maxheight/hh;hh=maxheight
 p=para();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1;p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(path),width=Cm(w),height=Cm(hh))
 if title:return caption(title,number)
def tc(text,num):
 p=para(f'Bảng {num}. {text}',bold=True);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.keep_with_next=True
 for r in p.runs:r.font.size=Pt(12)
def table(headers,rows,widths,size=11):
 t=d.add_table(rows=1,cols=len(headers));emit(t._tbl);t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for i,w in enumerate(widths):t.columns[i].width=Cm(w)
 for j,values in enumerate([headers]+rows):
  row=t.rows[0] if j==0 else t.add_row();pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
  if j==0:pr.append(OxmlElement('w:tblHeader'))
  for i,v in enumerate(values):
   c=row.cells[i];c.width=Cm(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;c.text=str(v)
   cp=c._tc.get_or_add_tcPr();mar=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    vmar=OxmlElement('w:'+side);vmar.set(qn('w:w'),'70');vmar.set(qn('w:type'),'dxa');mar.append(vmar)
   cp.append(mar)
   if j==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EDF2');cp.append(sh)
   for p in c.paragraphs:
    p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.line_spacing=1.04;p.paragraph_format.space_before=Pt(1);p.paragraph_format.space_after=Pt(2)
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(size);r.bold=j==0;r.font.color.rgb=RGBColor(0,0,0)
 borders=OxmlElement('w:tblBorders')
 for side in ['top','left','bottom','right','insideH','insideV']:
  z=OxmlElement('w:'+side);z.set(qn('w:val'),'single');z.set(qn('w:sz'),'4');z.set(qn('w:color'),'D9D9D9');borders.append(z)
 t._tbl.tblPr.append(borders);newtables.append(t);return t
def ot(i):emit(deepcopy(oldtables[i]))

h('CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG',1)
para('Chương này trình bày các tác nhân và đặc tả nghiệp vụ của NHK English times, thiết kế cơ sở dữ liệu, luồng đăng ký và thanh toán, cùng kiến trúc và tổ chức mã nguồn. Các nội dung được đối chiếu với ứng dụng ASP.NET Core MVC và cấu trúc SQL Server LocalDB đang sử dụng; phần phân tích đã có được giữ lại và sắp xếp theo các mục tương ứng.')
h('3.1 Phân tích chức năng và đặc tả Use Case')
oldrange(382,386)
h('3.1.1 Sơ đồ Use Case tổng quát và phạm vi tác nhân',3).paragraph_format.page_break_before=True
picture(ROOT/'docs/use-cases/01-tong-quat.png','Sơ đồ use case tổng quát hệ thống NHK English times',3,maxheight=19.7)
h('3.1.2 Phân rã chức năng theo từng tác nhân',3)
old(387,text=ps[387].text.replace('mục 3.2','mục 3.1.2').replace('mục 3.3','các bảng đặc tả tiếp theo'))
old(389)
caption('Các sơ đồ use case phân rã theo bốn tác nhân',4)
for label,head,desc,img in [('a',390,391,392),('b',394,395,396),('c',398,399,400),('d',402,403,404)]:
 old(head,True);old(desc);pp=old(img)
 role={'a':'guest','b':'student','c':'teacher','d':'admin'}[label]
 rid=pp._p.xpath('.//a:blip/@r:embed')[0];d.part.related_parts[rid]._blob=(R/'final-refresh/assets'/f'uc-{role}.png').read_bytes()
 caption(f'Hình 4{label}. '+ps[img+1].text.split('. ',1)[1],4,True)
h('3.1.3 Đặc tả chi tiết Use Case của khách và học viên',3)
para('Bảng 2 ghi nhận điều kiện trước, các bước xử lý và kết quả của những chức năng công khai và chức năng học viên. Các use case cần đăng nhập còn kiểm tra quyền sở hữu theo AccountId hoặc StudentId; không chỉ kiểm tra vai trò ở giao diện.')
student=[
 ['HV01\nTra cứu khóa học','Khách hoặc học viên; chương trình đang hoạt động.','Mở danh mục; nhập từ khóa, cấp độ; xem nội dung, học phí và lớp tham khảo.','Chỉ hiển thị chương trình không bị xóa và đang hoạt động; không chọn lớp khi ghi danh.'],
 ['HV02\nĐăng ký và đăng nhập','Email hợp lệ; email chưa tồn tại khi tạo tài khoản.','Nhập thông tin; kiểm tra dữ liệu; băm BCrypt; tạo UserAccount và Student. Đăng nhập xác minh mật khẩu, cấp cookie theo vai trò.','Email trùng, tài khoản khóa/xóa hoặc sai mật khẩu bị từ chối; đăng nhập thành công chuyển đúng phân hệ.'],
 ['HV03\nĐăng ký khóa học','Student đang hoạt động; khóa mở tuyển sinh; chưa có đơn hoạt động cùng khóa.','Chọn khóa; nhập ngày bắt đầu không ở quá khứ, buổi, nhóm 246/357, ghi chú và Cash/VietQR. Lưu đơn và học phí trong một transaction.','Registration Pending, ClassId NULL; Payment Pending; lỗi dữ liệu hoặc đăng ký trùng không tạo đơn mới.'],
 ['HV04\nTheo dõi đơn và lịch','Student sở hữu đơn hoặc lớp được xác nhận.','Mở lớp của tôi; theo dõi đơn chờ, nguyện vọng, lớp Admin đã xếp; xem lịch học và thi theo tuần.','Chỉ thấy dữ liệu cá nhân. Đơn chờ không được thể hiện như đã thuộc một lớp chính thức.'],
 ['HV05\nHọc phí và biên lai','Student sở hữu Registration và Payment; đơn chưa bị xóa/hủy khi mở hướng dẫn.','Xem số tiền lấy từ Programs; chọn VietQR hoặc nộp tại trung tâm; theo dõi trạng thái và mở trang in biên lai.','Hiển thị QR không tự chuyển Paid. Biên lai phản ánh dữ liệu thu được Admin xác nhận; không tự xếp lớp.'],
 ['HV06\nKiểm tra xếp lớp','Student đăng nhập; chưa có yêu cầu kiểm tra đang chờ xử lý theo quy tắc hiện tại.','Gửi ngày và khung giờ mong muốn; theo dõi phòng thi sau khi Admin xếp; xem điểm và cấp độ do giáo viên nhập.','Không tự chọn phòng/người chấm; chưa có bộ đề trực tuyến tự chấm bốn kỹ năng.'],
 ['HV07\nHồ sơ và đánh giá','Student có quyền với hồ sơ; đã được xếp vào lớp khi gửi phản hồi.','Cập nhật liên hệ, ngày sinh, ảnh; chọn số sao 1–5 và nhận xét; kiểm tra dữ liệu trước khi lưu.','Ảnh không hợp lệ bị từ chối; đánh giá phải thuộc lớp hợp lệ của học viên.'],
 ['HV08\nTư vấn hai chiều','Khách có cookie/liên kết riêng hợp lệ; hoặc Student là chủ hội thoại.','Gửi câu hỏi, nhận phản hồi, gửi thêm tin và xem lịch sử; hệ thống cập nhật tin và trạng thái đã đọc.','Không đọc/sửa hội thoại người khác. Cuộc Closed chặn gửi thêm đến khi Admin mở lại.']]
tc('Đặc tả chi tiết Use Case',2);table(['Mã và nghiệp vụ','Điều kiện trước','Luồng xử lý chính','Kết quả và ngoại lệ'],student,[2.4,3.5,6.0,4.1])
oldrange(407,417)
h('3.1.4 Đặc tả các nghiệp vụ quản trị của giáo viên',3)
teacher=[
 ['GV01\nHồ sơ cá nhân','Teacher đang hoạt động.','Xem bảng điều khiển; cập nhật ảnh; đổi mật khẩu qua AccountController.','Không đổi vai trò hoặc hồ sơ người khác; tệp ảnh phải qua kiểm tra.'],
 ['GV02\nLớp và học viên','Lớp được phân công cho TeacherId hiện tại.','Mở danh sách lớp; xem học viên và thông tin liên hệ trong lớp được giao.','Lớp ngoài phân công bị chặn; checkbox điểm danh hiện chưa lưu chuyên cần theo buổi.'],
 ['GV03\nLịch dạy và thi','Có lớp giảng dạy hoặc ca thi được giao.','Đọc ClassSchedules trong khoảng ngày của lớp; kết hợp ExamSessions được phân công.','Không xem phân công riêng của giáo viên khác; lớp chưa có lịch được thông báo rõ.'],
 ['GV04\nTài liệu lớp','Teacher phụ trách lớp; tệp hợp lệ.','Chọn lớp, nhập tiêu đề; tải tệp; lưu ClassDocuments; xem, tải về hoặc xóa theo chức năng của phân hệ.','Tài liệu phải gắn đúng lớp; chức năng tải tài liệu riêng cho học viên cần tiếp tục hoàn thiện.'],
 ['GV05\nChấm lớp thi','Ca thi có TeacherId hiện tại; bài chưa bị xóa.','Mở ca thi; xem thí sinh; nhập Score 0–10 và RecommendedLevel không rỗng, tối đa 100 ký tự; lưu kết quả.','PlacementTest Completed; ca thi Completed khi mọi bài hợp lệ đã chấm; bài ngoài phân công bị chặn.'],
 ['GV06\nPhản hồi học viên','Teacher có lớp liên quan.','Tra cứu đánh giá và nhận xét học viên đối với các lớp mình phụ trách.','Chỉ đọc dữ liệu thuộc phạm vi phụ trách; không sửa đánh giá thay học viên.'],
 ['GV07\nBảng lương','Teacher đăng nhập.','Xem lương tháng, số giờ, đơn giá, thưởng, khấu trừ và trạng thái chi trả của mình.','Không tự lập, sửa hoặc xác nhận đã trả lương; nghiệp vụ đó thuộc Admin.']]
tc('Đặc tả chi tiết các nghiệp vụ quản trị của giáo viên',3);table(['Mã và nghiệp vụ','Điều kiện trước','Luồng xử lý chính','Kết quả và ngoại lệ'],teacher,[2.4,3.5,6.0,4.1]);oldrange(424,434)
h('3.1.5 Đặc tả các nghiệp vụ quản trị Admin',3)
admin=[
 ['AD01\nChương trình học','Admin; dữ liệu chương trình hợp lệ.','Thêm, sửa học phí, thời lượng, trình độ, mô tả; bật/tắt tuyển sinh hoặc xóa mềm.','Không xóa vật lý khi quan hệ còn ràng buộc; học phí không âm.'],
 ['AD02\nLớp và lịch tuần','Chương trình hợp lệ; ngày kết thúc không trước ngày bắt đầu.','Nhập lớp, phòng, sĩ số; chọn 246/357 và giờ bắt đầu/kết thúc; ClassSchedulePlanner kiểm tra và tạo ba lịch tuần.','Lịch xuất hiện theo ngày thực tế trong thời khóa biểu; kiểm tra phòng, giáo viên và các xung đột áp dụng.'],
 ['AD03\nXếp và chuyển lớp','Đơn chưa hủy/xóa; lớp đúng chương trình và còn hoạt động.','CourseClassAssignment kiểm tra ngày khai giảng từ EarliestStartDate trở đi, sĩ số và lịch trùng; gán ClassId, chuyển Confirmed trong transaction.','Buổi/thứ là nguyện vọng tham khảo. Lớp chưa có lịch không bị chặn chỉ vì thiếu lịch; Payment giữ nguyên.'],
 ['AD04\nTrạng thái ghi danh','Đơn tồn tại; Admin có quyền xử lý.','Xem danh sách theo khóa; xếp/chuyển lớp, trả về chờ, hủy hoặc xóa mềm theo điều kiện nghiệp vụ.','Liên kết lớp thay đổi theo trạng thái; không tự đổi Paid về Pending hoặc xóa lịch sử thu tiền.'],
 ['AD05\nXác nhận học phí','Payment gắn với đơn chưa xóa/hủy; đã đối soát chứng từ.','Xem tiền, phương thức và mã giao dịch; POST ConfirmPayment; gán Paid; sinh mã thủ công nếu chưa có; lưu và in biên lai.','Không tự gán ClassId hay xác nhận xếp lớp. Không có callback VietQR ngân hàng tự động trong phiên bản này.'],
 ['AD06\nPhòng và lớp thi','Phòng, ngày, giờ, sức chứa hợp lệ.','Tạo ExamSession; chọn nhiều yêu cầu; xếp thí sinh; phân công một giáo viên chấm cả ca.','Kiểm tra sức chứa, ngày yêu cầu và lịch trùng; không đổi người chấm hoặc đưa bài đã có điểm về chờ trái quy tắc.'],
 ['AD07\nTài khoản và hồ sơ','Admin; email và thông tin hợp lệ.','Tạo/sửa giáo viên; quản lý học viên, khóa/mở học viên; xóa mềm và khôi phục hồ sơ theo chức năng có sẵn.','Giáo viên chưa có action khóa/mở riêng như học viên; mật khẩu lưu dưới dạng băm.'],
 ['AD08\nLương giáo viên','Kỳ lương và TeacherId hợp lệ.','Lập/sửa lương; tính lương cơ bản + giờ × đơn giá + thưởng − khấu trừ; xác nhận chi trả.','Status Pending/Paid và ngày trả lương là dữ liệu riêng, không đồng nhất với thu học phí.'],
 ['AD09\nHộp thư tư vấn','Hội thoại tồn tại và chưa bị xóa.','Xem tin chưa đọc; trả lời; đánh dấu đã xem; kết thúc hoặc mở lại hội thoại.','Tin được kiểm tra nội dung và CSRF; khách/học viên chỉ truy cập qua quyền sở hữu hợp lệ.'],
 ['AD10\nThống kê và lưu trữ','Admin; đối tượng được thao tác hợp lệ.','Xem doanh thu, quy mô; quản lý banner; khôi phục, xóa vĩnh viễn hoặc dọn thùng rác khi cần.','Ràng buộc dữ liệu vẫn áp dụng với xóa vật lý; không suy ra các chỉ số thống kê là số liệu khảo sát thị trường.']]
tc('Đặc tả chi tiết các nghiệp vụ quản trị Admin',4);table(['Mã và nghiệp vụ','Điều kiện trước','Luồng xử lý chính','Kết quả và ngoại lệ'],admin,[2.4,3.5,6.0,4.1]);oldrange(417,424);oldrange(434,442)

h('3.2 Thiết kế Cơ sở dữ liệu')
old(443)
para('Thiết kế được đối chiếu với metadata của SQL Server: 16 bảng nghiệp vụ và 149 cột, bao gồm tên trường, kiểu dữ liệu, khả năng nhận NULL, khóa chính, khóa ngoại, chỉ mục và CHECK. Các bảng nhật ký nâng cấp và __EFMigrationsHistory phục vụ triển khai, không được tính là thực thể nghiệp vụ. Hai lớp Models/Class.cs và Models/Program.cs đang rỗng và không phải hai bảng bổ sung.')
h('3.2.1 Sơ đồ quan hệ giữa các thực thể',3)
picture(A/'erd-full.png','Sơ đồ quan hệ giữa các thực thể của NHK English times',5,maxheight=20.8)
para('UserAccounts liên kết một–một tùy chọn với Students hoặc Teachers; một chương trình có nhiều lớp và nhiều đơn. Registrations có thể chưa có lớp nhưng phải có chương trình; khóa ngoại ghép (ClassId, ProgramId) bảo đảm lớp được xếp thuộc đúng chương trình đã đăng ký. Payments có RegistrationId duy nhất, nên mỗi đơn có tối đa một bản ghi học phí.')
para('Teachers liên kết với Classes, ExamSessions, PlacementTests và TeacherSalaries. Một ca thi có nhiều bài PlacementTests; Students còn liên kết với phản hồi và các bài kiểm tra. Consultations liên kết người sở hữu nếu là học viên, còn khách được nhận diện bằng mã truy cập băm; ConsultationMessages lưu các tin nhắn của từng hội thoại. Banners là bảng cấu hình hiển thị độc lập.')
old(444);caption('Hình 5a. Lược đồ nhóm tài khoản đào tạo và học phí',5,True)
old(446);caption('Hình 5b. Lược đồ nhóm kiểm tra tư vấn và hỗ trợ',5,True)
oldrange(448,454)
h('3.2.2 Thiết kế chi tiết các bảng dữ liệu',3)
old(455);tc('Tổng hợp các bảng và trường dữ liệu chính',5);ot(0)
para('Trong các bảng chi tiết dưới đây, NULL nghĩa là được để trống; NOT NULL nghĩa là bắt buộc có giá trị ở mức lưu trữ. PK là khóa chính, FK là khóa ngoại vật lý đã có trong SQL Server. Quy tắc bắt buộc của biểu mẫu có thể chặt hơn NULL của cột để tương thích dữ liệu cũ. ID tự tăng không được học viên tự gửi để xác lập quyền sở hữu.')
descs={
'AccountId':'Mã tài khoản đăng nhập.','FullName':'Họ tên người dùng.','Email':'Email đăng nhập; chỉ mục duy nhất.','PasswordHash':'Chuỗi băm BCrypt; không lưu mật khẩu rõ.','Role':'Admin, Teacher hoặc Student.','AvatarUrl':'Đường dẫn ảnh đại diện.','IsActive':'Trạng thái được sử dụng hoặc hiển thị.','IsDeleted':'Cờ xóa mềm; không đồng nghĩa xóa vật lý.','DeletedAt':'Thời điểm đưa vào thùng rác.','CreatedAt':'Thời điểm tạo bản ghi.',
'StudentId':'Mã học viên.','PhoneNumber':'Số điện thoại liên hệ.','Address':'Địa chỉ liên hệ.','PhotoUrl':'Đường dẫn ảnh hồ sơ.','DateOfBirth':'Ngày sinh.','TeacherId':'Mã giáo viên.','Specialization':'Chuyên môn giảng dạy.','Bio':'Giới thiệu giáo viên.','Degree':'Học vị hoặc bằng cấp.',
'ProgramId':'Mã chương trình đào tạo.','ProgramName':'Tên khóa học hiển thị.','Level':'Trình độ đầu vào hoặc phân loại.','DurationWeeks':'Thời lượng tính theo tuần; từ 1 đến 100.','TuitionFee':'Học phí niêm yết; không âm.','Description':'Mô tả chương trình.','LearningOutcomes':'Chuẩn đầu ra dự kiến.','ImageUrl':'Đường dẫn ảnh hiển thị.','ClassId':'Mã lớp học.','ClassName':'Tên hoặc mã lớp.','Room':'Tên phòng học hoặc phòng thi.','MaxStudents':'Sĩ số tối đa; từ 1 đến 100.','StartDate':'Ngày khai giảng.','EndDate':'Ngày bế giảng; không trước ngày khai giảng.',
'RegistrationId':'Mã đơn đăng ký khóa học.','RegistrationDate':'Thời điểm tạo đơn.','DesiredTeacherId':'Cột tương thích dữ liệu cũ; không còn chọn trên biểu mẫu; hiện không có FK vật lý.','Notes':'Ghi chú và nguyện vọng bổ sung.','EarliestStartDate':'Ngày sớm nhất có thể bắt đầu; biểu mẫu mới yêu cầu nhập.','PreferredSession':'Morning, Afternoon, Evening hoặc Any.','PreferredDays':'Nhóm thứ dạng 2,4,6 hoặc 3,5,7.',
'PaymentId':'Mã bản ghi học phí.','Amount':'Số tiền của đơn; lấy từ khóa học tại lúc đăng ký.','PaymentDate':'Thời điểm ghi nhận trong bản ghi học phí hiện tại.','PaymentMethod':'Đơn mới dùng Cash hoặc VietQR; dữ liệu lịch sử có thể có phương thức cũ.','TransactionCode':'Mã nội dung chuyển khoản hoặc mã giao dịch.','ExamSessionId':'Mã ca/lớp thi.','Name':'Tên ca thi; có chỉ mục duy nhất.','ExamDate':'Ngày diễn ra ca thi.','StartTime':'Giờ bắt đầu; phải trước giờ kết thúc.','EndTime':'Giờ kết thúc ca học hoặc ca thi.','Capacity':'Số chỗ tối đa của ca thi.','TestId':'Mã yêu cầu/bài kiểm tra.','EvaluatedByTeacherId':'Giáo viên chấm bài; có thể chưa được phân công.','TestDate':'Ngày thi chính thức hoặc giá trị đang lưu của yêu cầu.','TestTime':'Chuỗi giờ thi được hiển thị.','Score':'Điểm 0–10; NULL khi chưa chấm.','RecommendedLevel':'Trình độ/khóa học đề xuất sau kiểm tra.','RequestedDate':'Ngày mong muốn do học viên gửi.','RequestedTime':'Khung giờ mong muốn do học viên gửi.',
'ConsultationId':'Mã cuộc tư vấn.','ContactName':'Họ tên người liên hệ.','ContactEmail':'Email liên hệ của khách hoặc học viên.','Question':'Câu hỏi khởi tạo cuộc tư vấn.','OwnerAccountId':'Chủ tài khoản nếu là học viên; khách để NULL.','GuestAccessHash':'Băm SHA-256 của mã truy cập riêng; không lưu mã thô.','LastMessageAt':'Thời điểm tin mới nhất.','AdminLastReadMessageId':'Mốc tin Admin đã đọc; không phải FK vật lý.','CustomerLastReadMessageId':'Mốc tin khách/học viên đã đọc; không phải FK vật lý.','MessageId':'Mã tin nhắn.','SenderRole':'Nhóm người gửi, ví dụ Customer hoặc Admin.','SenderAccountId':'Tài khoản gửi nếu có; khách có thể NULL.','Body':'Nội dung tin, tối đa 2.000 ký tự.','SentAt':'Thời điểm gửi tin.',
'ScheduleId':'Mã ca học theo tuần.','DayOfWeek':'2 đến 8: Thứ Hai đến Chủ Nhật.','DocumentId':'Mã tài liệu lớp.','Title':'Tiêu đề hiển thị.','FilePath':'Đường dẫn tệp được lưu trên máy chủ.','UploadedAt':'Thời điểm tải tài liệu.','FeedbackId':'Mã phản hồi học viên.','Rating':'Số sao từ 1 đến 5.','Comment':'Nhận xét chất lượng lớp học.','BannerId':'Mã banner.','Subtitle':'Phụ đề của banner.','LinkUrl':'Địa chỉ điều hướng khi bấm banner.','ButtonText':'Nhãn nút trên banner.','DisplayOrder':'Thứ tự ưu tiên hiển thị.','SalaryId':'Mã bảng lương.','Month':'Tháng của kỳ lương.','Year':'Năm của kỳ lương.','BaseSalary':'Lương cơ bản.','TotalTeachingHours':'Số giờ dùng để tính lương.','HourlyRate':'Đơn giá theo giờ.','Bonus':'Khoản thưởng.','Deduction':'Khoản khấu trừ.','TotalSalary':'Tổng lương được tính và lưu.','Note':'Ghi chú của kỳ lương.'}
statuses={'Classes':'Planning, InProgress, Completed hoặc Cancelled.','Registrations':'Pending, Confirmed hoặc Cancelled; độc lập học phí.','Payments':'Pending, Paid hoặc Failed.','ExamSessions':'Trạng thái tổ chức ca thi; Planning, InProgress, Completed.','PlacementTests':'Pending khi chờ xử lý; Completed khi đã nhập kết quả.','Consultations':'Pending, Replied hoặc Closed.','TeacherSalaries':'Pending hoặc Paid, phản ánh chi trả lương.'}
purposes={'UserAccounts':'Quản lý định danh và phân quyền đăng nhập.','Students':'Lưu hồ sơ bổ sung cho tài khoản học viên.','Teachers':'Lưu chuyên môn, bằng cấp và hồ sơ giáo viên.','Programs':'Danh mục các chương trình đào tạo và mức học phí.','Classes':'Các lớp được trung tâm mở cho từng chương trình.','Registrations':'Đơn đăng ký khóa học và nguyện vọng trước khi Admin xếp lớp.','Payments':'Thông tin học phí gắn riêng với mỗi đơn đăng ký.','ClassSchedules':'Các ca học lặp theo tuần của lớp trong khoảng ngày mở lớp.','ExamSessions':'Tổ chức lớp thi, phòng thi, sức chứa và người chấm.','PlacementTests':'Yêu cầu và kết quả kiểm tra xếp lớp của từng học viên.','Consultations':'Thông tin chủ hội thoại, quyền truy cập và trạng thái tư vấn.','ConsultationMessages':'Lịch sử tin nhắn hai chiều của cuộc tư vấn.','ClassDocuments':'Tài liệu giảng dạy do giáo viên quản lý theo lớp.','CourseFeedbacks':'Đánh giá và nhận xét lớp học của học viên.','TeacherSalaries':'Dữ liệu lương theo giáo viên và kỳ tính lương.','Banners':'Thông tin quảng bá và điều hướng trên trang chủ.'}
order=list(purposes)
for k,name in enumerate(order):
 para(f'{chr(97+k)}) Bảng {name}',bold=True);para(purposes[name]).paragraph_format.keep_with_next=True;rows=[]
 cols=[c for c in schema['columns'] if c['table']==name]
 for c in cols:
  typ=c['type']
  if typ in ('nvarchar','varchar'):typ+=f"({('max' if c['max_length']==-1 else c['max_length']//(2 if typ=='nvarchar' else 1))})"
  elif typ=='decimal':typ+=f"({c['precision']},{c['scale']})"
  elif typ in ('datetime2','time'):typ+=f"({c['scale']})"
  fks=[f for f in schema['foreign_keys'] if f['source_table']==name and f['source_column']==c['name']]
  tags=(['PK'] if c['is_pk'] else [])+(['IDENTITY'] if c['is_identity'] else [])+(['FK'] if fks else [])+['NULL' if c['is_nullable'] else 'NOT NULL']
  desc=statuses.get(name,'Trạng thái nghiệp vụ.') if c['name']=='Status' else descs.get(c['name'],c['name'])
  if name=='TeacherSalaries' and c['name']=='PaymentDate':desc='Ngày chi trả lương; NULL khi chưa thanh toán.'
  if fks:desc+=' Tham chiếu '+', '.join(sorted({f["target_table"]+'.'+f['target_column'] for f in fks}))+'.'
  rows.append([c['name'],typ,'; '.join(tags),desc])
 tc(f'Thiết kế chi tiết bảng {name}',6+k);table(['Tên trường','Kiểu SQL Server','Ràng buộc','Ý nghĩa sử dụng'],rows,[4.3,3.0,2.5,6.2],10.5)
 idx=[x for x in schema['indexes'] if x['table']==name and x['is_unique'] and not x['is_primary_key']]
 if idx:para('Chỉ mục duy nhất: '+'; '.join(x['columns'] for x in idx)+'.')
 if name=='Registrations':para('Khóa ngoại ghép (ClassId, ProgramId) tham chiếu Classes; khi ClassId NULL, đơn vẫn tham chiếu Programs qua ProgramId. DesiredTeacherId là cột cũ không có khóa ngoại vật lý trong database được đối chiếu, dù model còn khai báo thuộc tính điều hướng.')
 if name=='TeacherSalaries':para('Công thức: TotalSalary = BaseSalary + TotalTeachingHours × HourlyRate + Bonus − Deduction. Bảng lương là nghiệp vụ riêng với khoản thu học phí.')
oldrange(456,459);tc('Các quan hệ và hành vi khi xóa',22);ot(1)

h('3.3 Phân tích luồng xử lý và Biểu đồ nghiệp vụ')
oldrange(460,462)
h('3.3.1 Biểu đồ Hoạt động – Quy trình đặt khóa học',3)
para('Trong hệ thống này, đặt khóa học là gửi đơn đăng ký chương trình kèm nguyện vọng, không phải giữ trước một lớp học. Biểu đồ hoạt động phân rõ trách nhiệm Học viên, Hệ thống và Admin; dữ liệu sai quay về biểu mẫu, còn lớp chưa phù hợp tiếp tục ở trạng thái chờ.')
picture(A/'activity-enrollment.png','Biểu đồ hoạt động Quy trình đăng ký khóa học',6,maxheight=19)
para('Hệ thống kiểm tra dữ liệu trước và trong transaction để hạn chế đơn trùng khi có yêu cầu đồng thời. Ngày khai giảng lớp được chọn phải bằng hoặc sau ngày học viên có thể bắt đầu. Sĩ số và lịch trùng là điều kiện kiểm tra thực tế; buổi và nhóm thứ dùng làm nguyện vọng tham khảo cho Admin.')
old(462);caption('Hình 6a. Luồng đăng ký xếp lớp và xác nhận học phí độc lập',6,True)
oldrange(464,469);tc('Trạng thái và điều kiện chuyển bước',23);ot(2)
h('3.3.2 Biểu đồ Tuần tự – Luồng xử lý Thanh toán',3)
para('Luồng thanh toán hiện tại sử dụng hướng dẫn VietQR hoặc đóng tại trung tâm và được Admin đối soát. EnrollmentController tạo Payment Pending cùng Registration trong transaction; PaymentAdminController.ConfirmPayment mới ghi nhận Paid. Vì chưa có API callback ngân hàng, sơ đồ không mô tả VNPay, MoMo hay email xác nhận tự động như một tích hợp đã hoàn thành.')
picture(A/'sequence-payment.png','Biểu đồ tuần tự Luồng xử lý thanh toán học phí',7,maxheight=18)
para('Sau khi tiếp nhận đơn, Razor View hiển thị số tiền và nội dung chuyển khoản. Người học thực hiện giao dịch ngoài ứng dụng; Admin kiểm tra chứng từ rồi gửi yêu cầu xác nhận có mã chống CSRF. Máy chủ kiểm tra Payment và Registration, cập nhật trạng thái và trả thông báo. Học viên tra cứu theo quyền sở hữu của chính mình, tránh truy cập hóa đơn của tài khoản khác bằng cách đổi ID.')
para('Lưu ý về dữ liệu thời gian: ConfirmPayment hiện không cập nhật lại PaymentDate khi chuyển Paid; cột này có thể phản ánh thời điểm tạo bản ghi. Báo cáo không coi đó là dấu thời gian đối soát ngân hàng chính xác. Nếu cần truy vết thu tiền khi vận hành, nên bổ sung trường xác nhận và nhật ký thay vì sửa ngầm ý nghĩa dữ liệu cũ.')
oldrange(469,477);tc('Phân quyền theo vai trò và từng bản ghi',24);ot(3)

h('3.4 Kiến trúc hệ thống và Tổ chức thư mục nguồn')
h('3.4.1 Kiến trúc phân tầng ứng dụng',3)
para('NHK English times sử dụng ASP.NET Core MVC trên .NET 8 trong một dự án WedEnglishApp. Giao diện Razor được dựng ở máy chủ; các phân hệ Admin và Teacher được tổ chức bằng Areas. Có sự phân chia trách nhiệm giữa trình bày, điều phối, nghiệp vụ và dữ liệu, nhưng đây không phải kiến trúc hai ứng dụng Spring Boot và Next.js triển khai riêng.')
picture(A/'architecture.png','Kiến trúc phân tầng ứng dụng NHK English times',8,maxheight=15.8)
para('Tầng trình bày gồm Views, Areas/*/Views và tài nguyên wwwroot. Controllers nhận yêu cầu, kiểm tra ModelState và quyền, chuẩn bị ViewModel, sau đó trả View hoặc JSON. Services tập trung các quy tắc dễ dùng lại như CourseClassAssignment, ClassSchedulePlanner, ExamSessionPlanner, ConsultationAccess và ConsultationMessaging. ApplicationDbContext ánh xạ Models sang SQL Server qua EF Core.')
para('Một số controller vẫn truy vấn ApplicationDbContext trực tiếp; dự án chưa có lớp Repository hoặc Unit of Work tự định nghĩa tách biệt. DbContext cung cấp theo dõi thay đổi và SaveChanges; các thao tác nhiều bước dùng transaction tại vị trí nghiệp vụ tương ứng. Phân tầng ở đây mô tả cách mã nguồn đang được tổ chức, không khẳng định đã áp dụng Clean Architecture đầy đủ.')
h('3.4.2 Cấu trúc thư mục mã nguồn dự án thực tế',3)
para('A. Cấu trúc thư mục phân tầng Backend ASP.NET Core MVC',bold=True)
para('Backend xử lý HTTP, nghiệp vụ, quyền truy cập và lưu trữ. Các mục dưới đây được lấy từ thư mục dự án thực tế; tên lớp và đường dẫn giữ nguyên để có thể đối chiếu mã nguồn.')
tree('WedEnglishApp/\n|-- Controllers/\n|   |-- AccountController.cs\n|   |-- EnrollmentController.cs\n|   `-- ConsultationController.cs\n|-- Areas/\n|   |-- Admin/Controllers/\n|   `-- Teacher/Controllers/\n|-- Services/\n|-- Models/\n|-- ViewModels/\n|-- Data/\n|   |-- ApplicationDbContext.cs\n|   |-- DbInitializer.cs\n|   `-- Sql/\n|-- Migrations/\n|-- Properties/launchSettings.json\n|-- Program.cs\n|-- appsettings.json\n`-- WedEnglishApp.csproj')
backend=[
 ('Controllers/','AccountController, EnrollmentController, StudentController, ProgramController, ConsultationController và các controller công khai.'),
 ('Areas/Admin/Controllers/','ClassManagerController, RegistrationAdminController, PaymentAdminController, PlacementTestAdminController và các chức năng quản trị khác.'),
 ('Areas/Teacher/Controllers/','TeachingClassController, TeacherTestController, DocumentController, FeedbackController, TeacherSalaryController.'),
 ('Services/','CourseClassAssignment, ClassSchedulePlanner, ExamSessionPlanner, EnrollmentSchedule, ConsultationAccess, ConsultationMessaging và kiểm tra/tổ chức tệp tải lên.'),
 ('Models/','16 thực thể nghiệp vụ được ApplicationDbContext sử dụng. Các lớp rỗng Class và Program không tạo thêm bảng nghiệp vụ.'),
 ('ViewModels/','Auth, Enrollment, Admin, Student, Home, Program và Consultation; định dạng dữ liệu của biểu mẫu và màn hình.'),
 ('Data/ và Data/Sql/','ApplicationDbContext, DbInitializer, các lớp nâng cấp schema và script SQL cho ghi danh, lịch học, phòng thi, tư vấn.'),
 ('Migrations/','Các tệp EF Core migrations đã có; schema mới còn được bổ sung bằng script SQL, không chỉ thông qua migrations.'),
 ('Program.cs và appsettings.json','Đăng ký DI, SQL Server, cookie theo vai trò, pipeline và routing; cấu hình chuỗi kết nối và logging.'),
 ('Properties/launchSettings.json và WedEnglishApp.csproj','Profile chạy cục bộ, cổng phục vụ, framework .NET 8 và các PackageReference.')]
for p,t in backend:para(p+' — '+t).alignment=WD_ALIGN_PARAGRAPH.LEFT
para('B. Cấu trúc thư mục Frontend Razor Views',bold=True)
para('Frontend là tập View và tài nguyên tĩnh cùng nằm trong dự án MVC. Tuyến trang do controller/action xác định; ứng dụng không có thư mục app/ hoặc cơ chế App Router của Next.js.')
tree('WedEnglishApp/\n|-- Views/\n|   |-- Shared/\n|   |-- Home/\n|   |-- Program/\n|   |-- Account/\n|   |-- Enrollment/\n|   |-- Student/\n|   |-- PlacementTest/\n|   `-- Consultation/\n|-- Areas/\n|   |-- Admin/Views/\n|   `-- Teacher/Views/\n`-- wwwroot/\n    |-- css/\n    |-- js/\n    `-- uploads/')
frontend=[
 ('Views/Shared/','_Layout.cshtml dùng chung cho trang công khai/học viên; _RegistrationPayment.cshtml hiển thị hướng dẫn học phí.'),
 ('Views/Home/ và Views/Program/','Trang chủ, liên hệ/tư vấn, danh mục và chi tiết chương trình đào tạo.'),
 ('Views/Account/, Views/Enrollment/ và Views/Student/','Đăng nhập/đăng ký, đăng ký khóa học, hướng dẫn học phí, hồ sơ, lớp, lịch và biên lai.'),
 ('Views/PlacementTest/ và Views/Consultation/','Đăng ký kiểm tra xếp lớp và các màn hình theo dõi hội thoại riêng.'),
 ('Areas/Admin/Views/','Màn hình quản trị theo từng controller; Shared/_AdminLayout.cshtml là bố cục riêng cho Admin.'),
 ('Areas/Teacher/Views/','Màn hình giảng viên; Shared/_TeacherLayout.cshtml là bố cục riêng của phân hệ.'),
 ('wwwroot/css/ và wwwroot/js/','portal-layout.css, consultation-chat.css, consultation-chat.js và tài nguyên giao diện dùng chung.'),
 ('wwwroot/uploads/','Ảnh avatars, banners, teachers, students và tệp documents do ứng dụng quản lý.'),
 ('Views/_ViewImports.cshtml và Views/_ViewStart.cshtml','Khai báo dùng chung, Tag Helpers và lựa chọn layout theo phạm vi Views.')]
for p,t in frontend:para(p+' — '+t).alignment=WD_ALIGN_PARAGRAPH.LEFT
para('Tài nguyên Bootstrap, Font Awesome, Google Fonts và Chart.js được các layout tham chiếu theo cấu hình đang có. JavaScript dùng fetch ở luồng tư vấn để gửi/nhận JSON và cập nhật giao diện theo chu kỳ; điều đó không làm ứng dụng trở thành một frontend Next.js riêng.')
para('KẾT CHƯƠNG 3',bold=True)
para('Chương 3 đã liên kết đặc tả nghiệp vụ với 16 bảng dữ liệu, các biểu đồ xử lý và mã nguồn thực tế. Thiết kế tách đăng ký khóa học, xếp lớp và xác nhận học phí; phân rõ quyền của khách, học viên, giáo viên và Admin. Các chức năng chưa hoàn thiện được ghi nhận để tiếp tục phát triển.').paragraph_format.keep_together=True

# Preserve all nodes outside chapter 3 exactly during authoring.
current=list(body);na=current.index(new[0]);nb=current.index(end._p)
assert before==[etree.tostring(x,method='c14n')for x in current[:na]]
assert after==[etree.tostring(x,method='c14n')for x in current[nb:]]
newtexts=[''.join(e.itertext())for e in new]
all_chapter='\n'.join(''.join(e.xpath('.//w:t/text()'))for e in new)
missing=[t for t in original_text if t not in all_chapter and t!=ps[387].text]
assert not missing,missing
out=R/'chapter3-completed-draft.docx';d.save(out)
audit={'source':str(source),'original_body_paragraphs_retained':len(original_text),'missing_original_body_paragraphs':missing,'outside_chapter3_xml_unchanged':True,'business_tables':16,'detailed_columns':len(schema['columns']),'use_case_rows':{'student_guest':len(student),'teacher':len(teacher),'admin':len(admin)},'new_tables':len(newtables),'old_chapter_tables_retained':len(oldtables),'figures_total':len(d.inline_shapes)}
(R/'chapter3-preservation-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False));print(out)
