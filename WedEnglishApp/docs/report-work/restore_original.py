from pathlib import Path
from copy import deepcopy
import re,json
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent;A=ROOT/'assets'
SOURCE=Path('D:/LTUD/doanketthucmonWeb.docx')
d=Document(SOURCE)
original_paras=list(d.paragraphs)
original_text=[p.text for p in original_paras]
original_tables=[[[c.text for c in r.cells]for r in t.rows]for t in d.tables]
original_elements=list(d.element.body)[:-1]
for e in list(d.element.body):
    if e.tag==qn('w:sdt') and any('TOC 'in (x.text or'')for x in e.iter(qn('w:instrText'))):d.element.body.remove(e)

def el(tag,**attrs):
    e=OxmlElement(tag)
    for k,v in attrs.items():e.set(qn('w:'+k),str(v))
    return e
def fld(p,code,cache=''):
    p.add_run()._r.append(el('w:fldChar',fldCharType='begin'))
    t=el('w:instrText');t.set(qn('xml:space'),'preserve');t.text=' '+code+' ';p.add_run()._r.append(t)
    p.add_run()._r.append(el('w:fldChar',fldCharType='separate'));p.add_run(cache)
    p.add_run()._r.append(el('w:fldChar',fldCharType='end'))
def para(text='',style=None):
    p=d.add_paragraph(text,style)
    if not style:
        p.paragraph_format.first_line_indent=Cm(.75)
        p.paragraph_format.line_spacing=1.15
    return p
def h(text,level=2,newpage=False):
    p=para(text,'Heading '+str(level));p.paragraph_format.page_break_before=newpage
    np=el('w:numPr');np.append(el('w:numId',val=0));p._p.get_or_add_pPr().append(np)
    return p
def addpic(file,caption=None,width=15,maxheight=12):
    from PIL import Image
    f=A/file
    with Image.open(f)as im:width=min(width,maxheight*im.width/im.height)
    p=para();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0)
    p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(3)
    p.add_run().add_picture(str(f),width=Cm(width))
    if caption:
        c=para(caption,'HITCFigureCaption');c.alignment=WD_ALIGN_PARAGRAPH.CENTER
def move_new_before(anchor,fun):
    before=set(d.element.body)
    fun()
    added=[x for x in d.element.body if x not in before and x.tag!=qn('w:sectPr')]
    for x in added:anchor._p.addprevious(x)

# A4, standard headings and the source's paragraph content remain intact.
for name in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
    if name not in d.styles:d.styles.add_style(name,1)
    st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    for b in list(st.element.iter(qn('w:pBdr'))):b.getparent().remove(b)
d.styles['Normal'].font.size=Pt(13)
d.styles['Normal'].paragraph_format.line_spacing=1.25
d.styles['Normal'].paragraph_format.space_after=Pt(6)
for name,size in [('Heading 1',16),('Heading 2',14),('Heading 3',13)]:
    st=d.styles[name];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.keep_with_next=True
    st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(6)
d.styles['Caption'].font.size=Pt(11);d.styles['Caption'].font.italic=True
d.styles['Caption'].paragraph_format.line_spacing=1.05
d.styles['Caption'].paragraph_format.space_after=Pt(8)
if 'HITCFigureCaption'not in d.styles:d.styles.add_style('HITCFigureCaption',1)
d.styles['HITCFigureCaption'].base_style=d.styles['Caption']

# Correct heading structure without rewriting the author's paragraphs.
for i,p in enumerate(original_paras):
    text=p.text.strip()
    for br in list(p._p.iter(qn('w:br'))):
        if br.get(qn('w:type'))in['page','column']:br.getparent().remove(br)
    if not text and not any(p._p.iter(qn('w:drawing')))and not any(p._p.iter(qn('w:pict'))):
        if p._p.getparent()is not None:p._p.getparent().remove(p._p)
        continue
    p.paragraph_format.page_break_before=False
    if text.startswith('CHƯƠNG ')or text in ['MỞ ĐẦU','KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN']:
        p.style='Heading 1';p.paragraph_format.page_break_before=True
    elif 2<=i<=61 and re.match(r'^\d+\. ',text):p.style='Heading 2'
    elif 2<=i<=61 and re.match(r'^\d+\.\d+ ',text):p.style='Heading 3'
    if p.style.name.startswith('Heading')and text:
        # The source contains mixed numbering definitions; displayed numbers in its text are retained.
        pr=p._p.get_or_add_pPr();n=pr.find(qn('w:numPr'))
        if n is not None:pr.remove(n)
        np=el('w:numPr');np.append(el('w:numId',val=0));pr.append(np)
        for r in p.runs:r.font.color.rgb=RGBColor(0,0,0)

# The original chapter 3 title was attached to the last paragraph of chapter 2.
title='CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG'
old206=original_paras[206]
if title in old206.text:
    old206.text=old206.text.replace(title,'')
    move_new_before(original_paras[207],lambda:h(title,1,True))

# Keep the original caption wording, removing only drafting wrappers around placeholders.
caption_indices=[86,98,209,276,294,311,320,331,343,351,359,364,371,381,389,397,402,406,417,422,425,428,431,440,443,447]
for i in caption_indices:
    p=original_paras[i]
    if p.text.startswith('(Vị trí chèn hình:')or p.text.startswith('(Hình '):
        text=p.text.replace('(Vị trí chèn hình:','',1).strip()
        if text.startswith('(Hình '):text=text[1:]
        p.text=text[:-1]if text.endswith(')')else text
    p.style='HITCFigureCaption';p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    np=el('w:numPr');np.append(el('w:numId',val=0));p._p.get_or_add_pPr().append(np)

# Move old screenshots to inline paragraphs while retaining the media and all original text.
for p in original_paras:
    drawings=list(p._p.iter(qn('w:drawing')))
    for drawing in drawings:
        anchor=drawing.find(qn('wp:anchor'))
        if anchor is not None:
            inline=OxmlElement('wp:inline')
            for k in ['distT','distB','distL','distR']:inline.set(k,'0')
            for tag in ['extent','effectExtent','docPr','cNvGraphicFramePr']:
                child=anchor.find(qn('wp:'+tag))
                if child is not None:inline.append(deepcopy(child))
            child=anchor.find(qn('a:graphic'))
            if child is not None:inline.append(deepcopy(child))
            drawing.replace(anchor,inline)
        extent=drawing.find('.//'+qn('wp:extent'))
        if extent is not None:
            cx,cy=int(extent.get('cx')),int(extent.get('cy'))
            scale=min(1,Cm(15.2)/cx,Cm(14)/cy)
            extent.set('cx',str(int(cx*scale)));extent.set('cy',str(int(cy*scale)))
        if p.text.strip():
            np=OxmlElement('w:p');pr=el('w:pPr');pr.append(el('w:jc',val='center'));pr.append(el('w:keepNext'));np.append(pr)
            run=el('w:r');run.append(deepcopy(drawing));np.append(run);p._p.addprevious(np)
            drawing.getparent().remove(drawing)
        else:p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True

move_new_before(original_paras[209],lambda:addpic('uc-overview.png',None,15.2,18))

# New chapter 3 content is inserted before chapter 4. Nothing from the old chapter is removed.
def chapter3():
    h('3.2 Phân rã use case theo từng tác nhân',2)
    para('Các sơ đồ phân rã bổ sung làm rõ những mục tiêu sử dụng của từng nhóm. Website có bốn tác nhân nhưng chỉ có ba vai trò tài khoản được lưu trong UserAccount là Student, Teacher và Admin. Khách là người chưa đăng nhập. Mỗi sơ đồ sử dụng khung hệ thống, tác nhân và các use case tương ứng; các chức năng công khai vẫn có thể được truy cập khi người dùng đã đăng nhập.')
    for subtitle,img,caption,text in [
      ('3.2.1 Tác nhân khách','uc-guest.png','Hình 3.2: Sơ đồ use case khách chưa đăng nhập','Khách xem trang chủ, chương trình đào tạo, thông tin lớp mở và liên hệ. Tìm kiếm, lọc theo cấp độ hoặc mức học phí giúp thu hẹp lựa chọn. Khách có thể gửi yêu cầu tư vấn và đăng ký tài khoản; tài khoản mới được gán vai trò Student. Các chức năng này được hiện thực tại HomeController, ProgramController, ConsultationController và AccountController.'),
      ('3.2.2 Tài khoản học viên','uc-student.png','Hình 3.3: Sơ đồ use case tài khoản học viên','Học viên đăng nhập để cập nhật hồ sơ, đăng ký lớp, xem lịch học, học phí và biên lai. Khi ghi danh, học viên có thể cung cấp ảnh hồ sơ, giáo viên mong muốn và ghi chú. Học viên đặt lịch kiểm tra đầu vào, xem điểm cùng cấp độ được đề xuất và gửi đánh giá khóa học. Các thao tác cá nhân xác định người dùng thông qua thông tin định danh trong cookie.'),
      ('3.2.3 Tài khoản giáo viên','uc-teacher.png','Hình 3.4: Sơ đồ use case tài khoản giáo viên','Giáo viên theo dõi bảng điều khiển, lớp phụ trách, danh sách học viên và lịch giảng dạy. Giáo viên quản lý tài liệu lớp học, chấm các bài kiểm tra được phân công và nhập cấp độ đề xuất. Phân hệ còn cung cấp phản hồi của học viên, cập nhật ảnh hồ sơ và bảng lương theo kỳ. Chức năng được tổ chức trong Area Teacher.'),
      ('3.2.4 Tài khoản quản trị viên','uc-admin.png','Hình 3.5: Sơ đồ use case tài khoản quản trị viên','Admin quản lý chương trình, lớp học, hồ sơ học viên và giáo viên; điều phối ghi danh, phân công giảng dạy và lịch kiểm tra. Admin xác nhận học phí, quản lý bảng lương, thống kê, banner, tư vấn và thùng rác. Các thao tác cùng mục tiêu được gộp trong sơ đồ để giữ khả năng đọc; chi tiết được thể hiện qua các Controller thuộc Area Admin.')]:
        h(subtitle,3,not subtitle.startswith('3.2.1'));para(text);addpic(img,caption,15.6,18)
    h('3.3 Đặc tả các use case tiêu biểu',2,True)
    specs=[
      ('3.3.1 Đăng ký tài khoản và đăng nhập','Khách hoặc người dùng có tài khoản.','Email chưa được sử dụng khi đăng ký; tài khoản phải hoạt động khi đăng nhập.','Người dùng nhập thông tin biểu mẫu. Hệ thống kiểm tra tính hợp lệ, kiểm tra email và băm mật khẩu khi đăng ký. Khi đăng nhập, mật khẩu được đối chiếu bằng BCrypt; thông tin định danh và vai trò được lưu trong phiên cookie.','Đăng ký tạo UserAccount và Student. Đăng nhập thành công điều hướng đến khu vực tương ứng; thông tin không hợp lệ được thông báo trên biểu mẫu.'),
      ('3.3.2 Đăng ký lớp học','Học viên.','Có phiên Student và chọn lớp tồn tại; có ảnh hồ sơ hoặc tải ảnh hợp lệ.','Học viên xem Checkout, cung cấp nguyện vọng giáo viên và ghi chú, chọn phương thức thanh toán rồi xác nhận. Hệ thống tạo Registration và bản ghi Payment tương ứng với học phí của chương trình.','Đơn mới có trạng thái Pending. Với VietQR, học phí chờ đối soát; học viên theo dõi đơn tại Lớp học của tôi.'),
      ('3.3.3 Xác nhận học phí','Quản trị viên.','Có phiên Admin; bản ghi học phí tồn tại và đã được kiểm tra chứng từ thu tiền.','Admin mở danh sách học phí, kiểm tra khoản thu và thực hiện xác nhận. Hệ thống cập nhật trạng thái thanh toán và trạng thái đơn ghi danh liên quan theo logic nghiệp vụ.','Học phí được ghi nhận Paid; thông tin được sử dụng để xem hoặc in biên lai nội bộ.'),
      ('3.3.4 Đặt lịch và chấm kiểm tra xếp lớp','Học viên, Admin và giáo viên.','Học viên có tài khoản; lịch kiểm tra được tạo và giáo viên được phân công trước khi chấm.','Học viên chọn ngày và ca. Admin điều chỉnh lịch, phòng và phân công giáo viên. Giáo viên xem bài được giao, nhập điểm và cấp độ đề xuất. Hệ thống cập nhật kết quả để học viên tra cứu.','Bài kiểm tra chuyển Completed khi nhập kết quả; điểm và cấp độ được hiển thị trong lịch sử kiểm tra.'),
      ('3.3.5 Quản lý tài liệu lớp học','Giáo viên.','Có phiên Teacher; xác định lớp, tiêu đề và tệp tài liệu.','Giáo viên mở phân hệ tài liệu, chọn lớp và tải tệp lên. Tệp được lưu trong thư mục uploads/documents và đường dẫn được ghi vào ClassDocument. Danh sách cung cấp liên kết tải về và thao tác xóa.','Tài liệu gắn với lớp được lưu để quản lý; quyền sở hữu lớp và tệp cần được kiểm tra ở mọi thao tác thay đổi.'),
      ('3.3.6 Xóa mềm và khôi phục dữ liệu','Quản trị viên.','Có phiên Admin; đối tượng thuộc nhóm dữ liệu hỗ trợ xóa mềm.','Thao tác xóa mềm cập nhật IsDeleted và DeletedAt. Admin xem mục đã xóa trong thùng rác, chọn khôi phục hoặc xóa vĩnh viễn. Việc xóa vĩnh viễn cần kiểm tra các liên kết còn phụ thuộc.','Khôi phục đưa bản ghi trở lại danh sách. Xóa vĩnh viễn loại bỏ bản ghi và không có thao tác khôi phục thông thường.')]
    for title,actor,pre,flow,post in specs:
        h(title,3);para('Tác nhân: '+actor);para('Điều kiện trước: '+pre);para('Luồng xử lý: '+flow);para('Kết quả: '+post)
    h('3.4 Thiết kế cơ sở dữ liệu',2,True)
    para('Đối chiếu ApplicationDbContext cho thấy mô hình hiện tại khai báo 14 tập thực thể: UserAccount, Student, Teacher, Program, Class, Registration, Payment, PlacementTest, Consultation, ClassSchedule, ClassDocument, CourseFeedback, Banner và TeacherSalary. Hình dưới tổng hợp các bảng và trường khóa, còn quan hệ giữa chúng được mô tả ở mục tiếp theo.')
    addpic('data-model.png','Hình 3.6: Mô hình các bảng dữ liệu và trường khóa',15.6,16)
    h('3.4.1 Nhóm tài khoản và hồ sơ',3)
    para('UserAccount lưu AccountId, họ tên, email, mật khẩu băm, vai trò và trạng thái tài khoản. Student và Teacher có khóa chính riêng và liên kết tới tài khoản bằng AccountId. Email có chỉ mục duy nhất. Student bổ sung thông tin liên hệ, ngày sinh và ảnh hồ sơ; Teacher bổ sung chuyên môn, bằng cấp, tiểu sử và ảnh. Quan hệ tài khoản–hồ sơ là quan hệ dữ liệu một–một tùy chọn theo vai trò.')
    h('3.4.2 Nhóm đào tạo và ghi danh',3)
    para('Một Program có nhiều Class; mỗi lớp thuộc một chương trình và có thể chưa có giáo viên phụ trách. ClassSchedule lưu các ca của lớp và ClassDocument lưu tài liệu. Registration liên kết Student với Class, đồng thời lưu giáo viên mong muốn, ngày đăng ký, ghi chú và trạng thái. Payment có khóa ngoại duy nhất RegistrationId để gắn tối đa một bản ghi học phí với mỗi đơn.')
    h('3.4.3 Nhóm hỗ trợ và quản trị',3)
    para('PlacementTest liên kết học viên với lịch, điểm, cấp độ đề xuất và giáo viên chấm có thể để trống trước khi phân công. CourseFeedback gắn đánh giá học viên với lớp. TeacherSalary ghi nhận các kỳ lương và trạng thái chi trả của giáo viên. Consultation lưu yêu cầu tư vấn; Banner quản lý hình ảnh quảng bá và thứ tự hiển thị. ClassStatus là thuộc tính trạng thái của lớp trong phiên bản hiện tại, không phải bảng độc lập.')
    h('3.5 Ràng buộc và luồng dữ liệu',2)
    para('Các khóa ngoại bảo đảm dữ liệu ghi danh tham chiếu đúng học viên và lớp, học phí tham chiếu đúng đơn, lịch học và tài liệu tham chiếu đúng lớp. ApplicationDbContext sử dụng Restrict ở các liên kết cần tránh xóa đối tượng cha khi còn dữ liệu con; một số liên kết tùy chọn đến giáo viên dùng SetNull. Những dữ liệu hỗ trợ thùng rác có IsDeleted và DeletedAt để theo dõi xóa mềm.')
    para('Luồng ghi danh kết nối các bước tra cứu chương trình, chọn lớp, tạo đăng ký, tạo học phí và theo dõi trạng thái. Luồng kiểm tra đầu vào kết nối đặt lịch, phân công, nhập kết quả và tra cứu. Luồng lương tách khỏi học phí học viên, gồm lập kỳ lương, tính các thành phần và xác nhận chi trả. Các luồng cần kiểm tra dữ liệu đầu vào và quyền của người đang thao tác trước khi ghi dữ liệu.')
    h('3.6 Đối chiếu thiết kế với phạm vi hiện thực',2)
    para('Phần phân tích nghiệp vụ xác định mục tiêu của hệ thống; mức độ hiện thực phải đối chiếu với mã nguồn. Trong phiên bản hiện tại, PlacementTest thực hiện đặt lịch và nhập kết quả bởi người chấm, chưa có bộ câu hỏi Listening/Reading tự chấm. Checkbox điểm danh chưa có thao tác lưu chuyên cần theo buổi. EmailService và các lớp VnPayService còn trống; VNPay/MoMo được mô phỏng trong luồng ghi danh, còn VietQR hiển thị ảnh chuyển khoản và chờ xác nhận nội bộ.')
    para('Cần hoàn thiện kiểm tra sĩ số, chống đăng ký trùng ở bước Confirm, kiểm tra xung đột lịch và quyền sở hữu bản ghi đối với tài liệu hoặc phản hồi. Việc tạo đơn và học phí nên được xử lý trong một giao dịch dữ liệu. Chức năng tải tài liệu riêng cho học viên, gửi thư tư vấn và khóa/mở tài khoản giáo viên chưa có luồng hoàn chỉnh tương ứng trong mã nguồn hiện tại.')
    para('Các sơ đồ bổ sung mô tả đăng nhập như một chức năng riêng và điều kiện trước của nghiệp vụ được bảo vệ. Đường nối tác nhân với use case không thể hiện thứ tự thao tác; các quan hệ include hoặc extend chỉ phù hợp khi có hành vi bắt buộc dùng lại hoặc mở rộng được xác định rõ. Cách biểu diễn này giúp phân biệt mục tiêu nghiệp vụ, điều kiện truy cập và mức độ đã triển khai.')
    h('3.7 Kết chương 3',2)
    para('Chương 3 bổ sung sơ đồ use case tổng quát và sơ đồ cho từng tác nhân, đặc tả các luồng chính, mô hình bảng dữ liệu và các ràng buộc. Thiết kế tạo cơ sở liên kết nội dung lý thuyết với các màn hình ở Chương 4, đồng thời xác định những phần cần tiếp tục hoàn thiện trước khi triển khai thực tế.')
move_new_before(original_paras[217],chapter3)

shots={
351:['ui-receipt'],359:['ui-myclasses','ui-schedule'],364:['ui-payments'],371:['ui-profile'],381:['ui-admin-dashboard'],389:['ui-admin-banners'],397:['ui-admin-programs','ui-admin-classes'],402:['ui-admin-registrations','ui-admin-payments'],406:['ui-admin-teachers','ui-admin-students'],417:['ui-admin-trash'],422:['ui-teacher-dashboard'],425:['ui-teacher-classes','ui-teacher-students'],428:['ui-teacher-tests'],431:['ui-teacher-documents','ui-teacher-feedback'],440:['ui-login'],443:['ui-register'],447:['ui-change-password']}
for i,files in shots.items():
    def insert(files=files,i=i):
        for j,f in enumerate(files):
            label=None
            base=re.search(r'Hình\s+4\.\d+',original_paras[i].text)
            if len(files)>1:label=(base.group(0)if base else'Hình 4')+chr(97+j)+': '+{'ui-schedule':'Lịch học và lịch thi theo tuần','ui-myclasses':'Các lớp học viên đã đăng ký','ui-admin-programs':'Chương trình đào tạo','ui-admin-classes':'Lớp học và phân công','ui-admin-registrations':'Đăng ký và xếp lớp','ui-admin-payments':'Quản lý học phí','ui-admin-teachers':'Hồ sơ giáo viên','ui-admin-students':'Hồ sơ học viên','ui-teacher-classes':'Các lớp được phân công','ui-teacher-students':'Danh sách học viên của lớp','ui-teacher-documents':'Quản lý tài liệu lớp','ui-teacher-feedback':'Phản hồi của học viên'}.get(f,f)
            addpic(f+'.jpg',label,15,10)
    move_new_before(original_paras[i],insert)

# Add figures for the salary feature without replacing the user's other content.
def salaries():
    addpic('ui-teacher-salary.jpg','Hình 4.20a: Bảng lương của giáo viên',15,10)
    addpic('ui-admin-salaries.jpg','Hình 4.20b: Quản lý lương tại trang Admin',15,10)
move_new_before(original_paras[432],salaries)

# Retain every original table, applying only readable, consistent borders.
for ti,t in enumerate(d.tables):
    t.autofit=False
    props=t._tbl.tblPr
    for tag in ['tblW','tblInd','tblpPr','jc']:
        for node in list(props.findall(qn('w:'+tag))):props.remove(node)
    props.append(el('w:tblW',w=9071,type='dxa'))
    props.append(el('w:tblInd',w=0,type='dxa'))
    props.append(el('w:jc',val='left'))
    count=len(t.columns)
    widths={1:[16],2:[4.4,11.6],4:[3,4,2,7],5:[1.4,2.6,3.2,4.5,4.3],6:[1.4,2.5,3.1,4,3.4,1.6]}.get(count,[16/count]*count)
    for ci,column in enumerate(t.columns):column.width=Cm(widths[ci])
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):c.width=Cm(widths[ci])
        if ri==0:row._tr.get_or_add_trPr().append(el('w:tblHeader'))
        for c in row.cells:
            tcpr=c._tc.get_or_add_tcPr();border=el('w:tcBorders')
            for side in ['top','bottom','left','right']:border.append(el('w:'+side,val='single',sz=4,color='D9D9D9'))
            tcpr.append(border)
            if ri==0:tcpr.append(el('w:shd',fill='E8EEF5'))
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.05
                for r in p.runs:r.font.size=Pt(10.5)

def reference():
    h('TÀI LIỆU THAM KHẢO',1,True)
    refs=[('VUS','Website Anh văn Hội Việt Mỹ','https://vus.edu.vn/'),('ILA Vietnam','Website trung tâm Anh ngữ ILA','https://ila.edu.vn/'),('Microsoft','Overview of ASP.NET Core MVC','https://learn.microsoft.com/en-us/aspnet/core/mvc/overview?view=aspnetcore-8.0'),('Microsoft','Entity Framework Core','https://learn.microsoft.com/en-us/ef/core/'),('Microsoft','Use cookie authentication without ASP.NET Core Identity','https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie?view=aspnetcore-8.0'),('Microsoft','Role based authorization in ASP.NET Core','https://learn.microsoft.com/en-us/aspnet/core/security/authorization/roles?view=aspnetcore-8.0'),('Bootstrap','Bootstrap 5.3 Documentation','https://getbootstrap.com/docs/5.3/getting-started/introduction/'),('Chart.js','Documentation','https://www.chartjs.org/docs/latest/'),('BCrypt.Net','Source and documentation','https://github.com/BcryptNet/bcrypt.net'),('Casso','VietQR Payment Kit','https://www.vietqr.io/')]
    for i,(a,title,url)in enumerate(refs,1):para(f'[{i}] {a}. {title}. {url}. Truy cập ngày 03/11/2026.')
    para('Nguồn nội bộ: mã nguồn dự án WedEnglishApp; báo cáo doanketthucmonWeb.docx; ảnh khảo sát VUS, ILA trong tài liệu ban đầu. Các hình giao diện bổ sung được chụp từ website HITC English chạy cục bộ; sơ đồ bổ sung được xây dựng từ các chức năng và mô hình dữ liệu của dự án.')
reference()

# Build cover and front matter in the same package, then move them ahead of the source body.
body_before_front=set(d.element.body)
def center(text,size=13,bold=False,after=10):
    p=para(text);p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.space_after=Pt(after)
    for r in p.runs:r.font.size=Pt(size);r.bold=bold
    return p
center('TRƯỜNG CAO ĐẲNG CÔNG THƯƠNG TP HỒ CHÍ MINH',13,True)
center('KHOA CÔNG NGHỆ THÔNG TIN',13,True,30)
center('BÁO CÁO ĐỒ ÁN KẾT THÚC MÔN',16,True)
center('LẬP TRÌNH ỨNG DỤNG',16,True,20)
addpic('hitc-logo.png',None,2.8,3)
p=center('XÂY DỰNG WEBSITE QUẢN LÝ\nTRUNG TÂM NGOẠI NGỮ HITC ENGLISH',18,True,30);p.style='Title'
center('Sinh viên thực hiện   Nguyễn Khánh Huy',14,True,6)
center('MSSV   2124110269',13,False,6)
center('Lớp   ................................',13,False,18)
center('Giảng viên hướng dẫn   Nguyễn Minh Nhứt',14,True,30)
center('TP Hồ Chí Minh tháng 11 năm 2026',13)
cover_section=d.sections[0]
front_section=d.add_section(WD_SECTION_START.NEW_PAGE)
center('MỤC LỤC',16,True,14);fld(para(),'TOC \\o "1-3" \\h \\z \\u')
p=center('DANH MỤC HÌNH',16,True,14);p.paragraph_format.page_break_before=True
fld(para(),'TOC \\h \\z \\t "HITCFigureCaption,1"')
main_section=d.add_section(WD_SECTION_START.NEW_PAGE)
front_nodes=[x for x in d.element.body if x not in body_before_front and x.tag!=qn('w:sectPr')]
for i,x in enumerate(front_nodes):d.element.body.insert(i,x)
for sec in d.sections:
    sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.left_margin=Cm(3);sec.right_margin=Cm(2);sec.top_margin=Cm(2);sec.bottom_margin=Cm(2)
    for node in list(sec._sectPr.findall(qn('w:pgBorders'))):sec._sectPr.remove(node)
    for node in list(sec._sectPr.findall(qn('w:footerReference'))):sec._sectPr.remove(node)
    sec.header.is_linked_to_previous=False;sec.footer.is_linked_to_previous=False
    for p in sec.header.paragraphs:p.clear()
    for p in sec.footer.paragraphs:p.clear()
    sec.different_first_page_header_footer=False
# Reacquire sections after moving the boundary paragraphs.
secs=list(d.sections)
for idx,sec in enumerate(secs):
    pg=el('w:pgNumType',fmt='lowerRoman'if idx==1 else'decimal',start=1);old=sec._sectPr.find(qn('w:pgNumType'))
    if old is not None:sec._sectPr.remove(old)
    sec._sectPr.append(pg)
    if idx>0:
        p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER;fld(p,'PAGE','1')
border=el('w:pgBorders',offsetFrom='page')
for side in ['top','bottom','left','right']:border.append(el('w:'+side,val='double',sz=6,space=24,color='000000'))
secs[0]._sectPr.append(border)
d.core_properties.author='Nguyễn Khánh Huy';d.core_properties.title='Báo cáo website HITC English bản giữ nguyên nội dung gốc'
d.settings.element.append(el('w:updateFields',val='true'))
out=ROOT/'original-preserved-draft.docx';d.save(out)

# Content preservation gate: all narrative paragraphs and all seven original tables remain.
final=[p.text for p in d.paragraphs]
missing=[]
for i,text in enumerate(original_text):
    if not text.strip():continue
    if i==206:expected=text.replace(title,'')
    elif i in caption_indices:
        expected=text.replace('(Vị trí chèn hình:','',1).strip()
        if expected.startswith('(Hình '):expected=expected[1:]
        if text.startswith('(')and expected.endswith(')'):expected=expected[:-1]
    else:expected=text
    if expected.strip() not in [x.strip()for x in final]:missing.append({'paragraph':i,'text':expected})
tables_after=[[[c.text for c in r.cells]for r in t.rows]for t in d.tables]
assert not missing,missing
assert original_tables==tables_after,'Original table content changed'
audit={'source_paragraphs':len(original_text),'preserved_nonempty_paragraphs':sum(bool(t.strip())for t in original_text),'missing_paragraphs':missing,'original_tables_preserved':len(original_tables),'output':str(out),'total_images':len(d.inline_shapes)}
(ROOT/'preservation-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(audit,ensure_ascii=False))
