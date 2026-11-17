from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
import json

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
OUTPUT=ROOT/'report-draft.docx'
doc=Document()
figures=[]
pending_page=False

def xml(tag, **attrs):
    e=OxmlElement(tag)
    for k,v in attrs.items(): e.set(qn('w:'+k),str(v))
    return e

def field(p,code,cached=''):
    r=p.add_run();r._r.append(xml('w:fldChar',fldCharType='begin'))
    r=p.add_run();t=xml('w:instrText');t.set(qn('xml:space'),'preserve');t.text=' '+code+' ';r._r.append(t)
    p.add_run()._r.append(xml('w:fldChar',fldCharType='separate'))
    p.add_run(cached)
    p.add_run()._r.append(xml('w:fldChar',fldCharType='end'))

def paragraph(text='',style=None,bold=False):
    p=doc.add_paragraph(style=style)
    p.add_run(text).bold=bold
    if style is None:p.paragraph_format.first_line_indent=Cm(.75)
    return p

def page():
    global pending_page
    pending_page=True

def heading(text,level=1,numbered=True):
    global pending_page
    p=doc.add_paragraph(text,'Heading '+str(level))
    if pending_page:p.paragraph_format.page_break_before=True;pending_page=False
    np=xml('w:numPr');np.append(xml('w:ilvl',val=level-1));np.append(xml('w:numId',val=42 if numbered else 0));p._p.get_or_add_pPr().append(np)
    return p

def figure(file,caption,width=15.2,maxheight=None,source=None):
    f=ASSETS/file
    if not f.exists():raise FileNotFoundError(f)
    if maxheight:
        with Image.open(f) as im: width=min(width,maxheight*im.width/im.height)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after=Pt(3);p.paragraph_format.keep_with_next=True
    p.add_run().add_picture(str(f),width=Cm(width))
    cap=doc.add_paragraph(style='Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    cap.add_run('Hình ');field(cap,'SEQ Hình \\* ARABIC',str(len(figures)+1));cap.add_run('  '+caption)
    if source:cap.add_run(' ('+source+')')
    figures.append(caption)

def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for i,h in enumerate(headers):t.rows[0].cells[i].text=h
    for row in rows:
        cells=t.add_row().cells
        for i,txt in enumerate(row):cells[i].text=str(txt)
    for ri,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr()
        trpr.append(xml('w:cantSplit'))
        if ri==0:trpr.append(xml('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            if widths:c.width=Cm(widths[ci])
            tcpr=c._tc.get_or_add_tcPr();tcpr.append(xml('w:vAlign',val='center'))
            mar=xml('w:tcMar')
            for side in ['top','left','bottom','right']:mar.append(xml('w:'+side,w=75,type='dxa'))
            tcpr.append(mar)
            edges=xml('w:tcBorders')
            for side in ['top','left','bottom','right']:edges.append(xml('w:'+side,val='single',sz=4,color='D9D9D9'))
            tcpr.append(edges)
            if ri==0:tcpr.append(xml('w:shd',fill='E8EEF5'))
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.1
                for r in p.runs:r.font.size=Pt(11);r.bold=ri==0
    doc.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def footer(sec,fmt='decimal',start=1):
    sec.footer.is_linked_to_previous=False
    p=sec.footer.paragraphs[0];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field(p,'PAGE',str(start))
    for r in p.runs:r.font.size=Pt(11)
    pn=sec._sectPr.find(qn('w:pgNumType'))
    if pn is None:pn=xml('w:pgNumType');sec._sectPr.append(pn)
    pn.set(qn('w:fmt'),fmt);pn.set(qn('w:start'),str(start))

def link(p,label,url):
    rel=p.part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rel)
    r=OxmlElement('w:r');rp=xml('w:rPr');rp.append(xml('w:color',val='000000'));r.append(rp)
    text=xml('w:t');text.text=label;r.append(text);h.append(r);p._p.append(h)

# A4 and the conventional Vietnamese student-report typography.
sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.left_margin=Cm(3);sec.right_margin=Cm(2);sec.top_margin=Cm(2);sec.bottom_margin=Cm(2)
sec.header_distance=Cm(1);sec.footer_distance=Cm(1)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    st.element.get_or_add_rPr().append(xml('w:rFonts',ascii='Times New Roman',hAnsi='Times New Roman',eastAsia='Times New Roman',cs='Times New Roman'))
normal=doc.styles['Normal'];normal.font.size=Pt(13)
normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
normal.paragraph_format.line_spacing=1.3;normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size in [('Heading 1',16),('Heading 2',14),('Heading 3',13)]:
    st=doc.styles[name];st.font.size=Pt(size);st.font.bold=True
    st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(8);st.paragraph_format.keep_with_next=True
doc.styles['Heading 1'].paragraph_format.page_break_before=True
doc.styles['Caption'].font.size=Pt(11);doc.styles['Caption'].font.italic=True
doc.styles['Caption'].paragraph_format.space_after=Pt(8)
doc.styles['Caption'].paragraph_format.line_spacing=1.05
for st in doc.styles:
    for border in list(st.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
for name in ['TOC 1','TOC 2','TOC 3','Table of Figures']:
    if name not in doc.styles:doc.styles.add_style(name,1)
    st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(12);st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.space_after=Pt(3);st.paragraph_format.line_spacing=1.05

# Multilevel heading numbering is native Word numbering, so TOC numbers follow edits.
numbering=doc.part.numbering_part.element
an=xml('w:abstractNum',abstractNumId=42);an.append(xml('w:multiLevelType',val='multilevel'))
for i,fmt in enumerate(['CHƯƠNG %1','%1.%2','%1.%2.%3']):
    lvl=xml('w:lvl',ilvl=i);lvl.append(xml('w:start',val=1));lvl.append(xml('w:numFmt',val='decimal'));lvl.append(xml('w:lvlText',val=fmt));lvl.append(xml('w:suff',val='space'));an.append(lvl)
numbering.append(an);num=xml('w:num',numId=42);num.append(xml('w:abstractNumId',val=42));numbering.append(num)

doc.core_properties.title='Xây dựng website quản lý trung tâm ngoại ngữ HITC English'
doc.core_properties.author='Nguyễn Khánh Huy'
doc.core_properties.subject='Báo cáo đồ án môn Lập trình ứng dụng'
doc.core_properties.keywords='ASP.NET Core, SQL Server, HITC English, use case'

# Cover follows the supplied visual structure with a white page and black text.
borders=xml('w:pgBorders',offsetFrom='page')
for side in ['top','left','bottom','right']:borders.append(xml('w:'+side,val='double',sz=6,space=24,color='000000'))
sec._sectPr.append(borders)
def coverline(text,size=13,bold=False,after=10):
    global pending_page
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_after=Pt(after)
    if pending_page:p.paragraph_format.page_break_before=True;pending_page=False
    r=p.add_run(text);r.font.size=Pt(size);r.bold=bold;return p
coverline('TRƯỜNG CAO ĐẲNG CÔNG THƯƠNG TP HỒ CHÍ MINH',13,True)
coverline('KHOA CÔNG NGHỆ THÔNG TIN',13,True,34)
coverline('BÁO CÁO ĐỒ ÁN KẾT THÚC MÔN',16,True,8)
coverline('LẬP TRÌNH ỨNG DỤNG',16,True,18)
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(ASSETS/'hitc-logo.png'),width=Cm(2.8));p.paragraph_format.space_after=Pt(20)
p=doc.add_paragraph(style='Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('XÂY DỰNG WEBSITE QUẢN LÝ\nTRUNG TÂM NGOẠI NGỮ HITC ENGLISH');r.font.size=Pt(18);r.bold=True
p.paragraph_format.space_after=Pt(26)
coverline('Sinh viên thực hiện   Nguyễn Khánh Huy',14,True,6)
coverline('Mã số sinh viên   2124110269',13,False,6)
coverline('Lớp   ................................',13,False,18)
coverline('Giảng viên hướng dẫn   Nguyễn Minh Nhứt',14,True,38)
coverline('TP Hồ Chí Minh tháng 11 năm 2026',13,False,0)

# Front matter is excluded from the chapter numbering.
front=doc.add_section(WD_SECTION_START.NEW_PAGE)
pb=front._sectPr.find(qn('w:pgBorders'))
if pb is not None:front._sectPr.remove(pb)
footer(front,'lowerRoman',1)
coverline('MỤC LỤC',16,True,18)
p=doc.add_paragraph();field(p,'TOC \\o "1-2" \\h \\z \\u')
page();coverline('DANH MỤC HÌNH',16,True,18)
p=doc.add_paragraph();field(p,'TOC \\h \\z \\c "Hình"')
main=doc.add_section(WD_SECTION_START.NEW_PAGE);footer(main,'decimal',1)

heading('MỞ ĐẦU',1,False)
heading('Lý do chọn đề tài',2,False)
paragraph('Nhu cầu tra cứu khóa học, đăng ký lớp và theo dõi học phí đặt ra yêu cầu quản lý dữ liệu tập trung tại các trung tâm ngoại ngữ. Khi thông tin được lưu bằng nhiều bảng tính rời rạc, nhân viên khó cập nhật đồng bộ hồ sơ, lịch học và tình trạng thanh toán; người học cũng thiếu một kênh tự tra cứu thuận tiện.')
paragraph('Đề tài xây dựng website HITC English bằng ASP.NET Core MVC và SQL Server nhằm hỗ trợ các nghiệp vụ tuyển sinh, đào tạo và quản trị trên cùng một hệ thống. Sản phẩm tập trung vào tra cứu chương trình, đặt lịch kiểm tra đầu vào, đăng ký lớp, theo dõi học phí và cung cấp cổng làm việc riêng cho học viên, giáo viên, quản trị viên.')
heading('Mục tiêu và phạm vi',2,False)
paragraph('Mục tiêu là vận dụng kiến thức lập trình web, thiết kế dữ liệu và phân quyền để tạo một ứng dụng có thể trình diễn các luồng nghiệp vụ chính. Website phục vụ bốn nhóm tác nhân, trong đó chỉ có ba vai trò tài khoản là Student, Teacher và Admin; khách truy cập sử dụng các chức năng công khai.')
paragraph('Phạm vi thực hiện gồm quản lý chương trình, lớp học, hồ sơ, ghi danh, lịch kiểm tra xếp lớp, học phí, tài liệu, phản hồi, lương giáo viên, banner và thùng rác. Kiểm tra đầu vào hiện là quy trình đặt lịch và nhập kết quả bởi người chấm. VietQR hỗ trợ hiển thị thông tin chuyển khoản; việc đối soát học phí thuộc quản trị viên.')
heading('Phương pháp và bố cục báo cáo',2,False)
paragraph('Đề tài kết hợp tham khảo tài liệu kỹ thuật chính thức, khảo sát giao diện công khai của VUS và ILA, phân tích nghiệp vụ bằng use case, thiết kế cơ sở dữ liệu và hiện thực bằng C#. Việc đánh giá dựa trên đối chiếu mã nguồn cùng thao tác mở trang, đăng nhập và quan sát giao diện trên môi trường cục bộ.')
paragraph('Báo cáo gồm bốn chương: tổng quan bài toán; cơ sở lý thuyết và công nghệ; phân tích và thiết kế; hiện thực và kiểm tra hệ thống. Phần cuối trình bày kết quả, hạn chế, hướng phát triển và tài liệu tham khảo.')

heading('TỔNG QUAN ĐỀ TÀI')
heading('Bài toán quản lý trung tâm ngoại ngữ',2)
paragraph('Quy trình nghiệp vụ bắt đầu khi khách tìm hiểu chương trình và gửi yêu cầu tư vấn. Sau khi có tài khoản, học viên có thể đặt lịch kiểm tra trình độ hoặc chọn lớp phù hợp. Bộ phận quản lý tiếp nhận đơn, xếp lớp và xác nhận học phí. Giáo viên theo dõi các lớp được giao, cung cấp tài liệu và nhập kết quả kiểm tra đầu vào.')
paragraph('Dữ liệu lớp học cần liên kết với chương trình đào tạo, giáo viên và lịch học. Đơn đăng ký liên kết học viên với lớp; bản ghi thanh toán ghi nhận học phí và trạng thái thu tiền. Cách tổ chức này giúp hạn chế nhập lặp dữ liệu và tạo cơ sở tổng hợp hoạt động của trung tâm.')
heading('Khảo sát các website tham khảo',2)
paragraph('Website VUS tổ chức thông tin chương trình theo nhóm tuổi và mục tiêu học tập, đồng thời bố trí các điểm truy cập tư vấn nổi bật. Website ILA cung cấp danh mục khóa học, thông tin giáo viên và hệ thống cơ sở. Hai website được dùng làm tham khảo cho cách tổ chức nội dung và điều hướng công khai [1], [2].')
figure('original-image1.png','Trang chủ VUS được dùng để tham khảo bố cục',width=15.2,source='VUS [1]')
figure('original-image2.png','Trang chủ ILA được dùng để tham khảo điều hướng',width=15.2,source='ILA [2]')
paragraph('Từ khảo sát giao diện, HITC English lựa chọn thanh điều hướng ngắn, banner giới thiệu, thẻ khóa học và biểu mẫu tư vấn dễ nhận biết. Báo cáo không suy diễn về quy trình thanh toán hay hệ thống quản trị nội bộ của VUS và ILA từ các trang công khai.')
heading('Đối tượng sử dụng và yêu cầu chính',2)
table(['Tác nhân','Nhu cầu chính'],[
['Khách','Xem chương trình và lớp mở; tìm kiếm, lọc; gửi tư vấn; đăng ký tài khoản.'],
['Học viên','Cập nhật hồ sơ; ghi danh; xem lớp, lịch học, lịch thi, học phí; in biên lai; phản hồi.'],
['Giáo viên','Xem lớp và lịch dạy; xem học viên; quản lý tài liệu; chấm thi được giao; xem phản hồi và lương.'],
['Admin','Quản lý đào tạo, tài khoản, ghi danh, học phí, lịch thi, lương, tư vấn, banner và thùng rác.']],[3.1,12.9])
paragraph('Giao diện cần thống nhất theo vai trò, các biểu mẫu có kiểm tra dữ liệu và các chức năng cá nhân yêu cầu đăng nhập. Dữ liệu tài khoản phải tránh trùng email; mỗi bản ghi nghiệp vụ sử dụng khóa chính và khóa ngoại để xác định liên kết.')

heading('CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ')
heading('Kiến trúc ASP.NET Core MVC',2)
paragraph('MVC phân chia ứng dụng thành Model, View và Controller. Model biểu diễn dữ liệu; View kết xuất giao diện; Controller tiếp nhận yêu cầu và phối hợp xử lý. ASP.NET Core hỗ trợ định tuyến, liên kết dữ liệu biểu mẫu và cơ chế tiêm phụ thuộc để cung cấp các thành phần dùng chung [3].')
paragraph('Trong dự án, trình duyệt gửi yêu cầu đến Kestrel hoặc IIS Express. Controller truy vấn ApplicationDbContext rồi truyền Model hoặc ViewModel cho Razor View. Các phân hệ Admin và Teacher được tổ chức bằng Areas. Phần lớn nghiệp vụ hiện nằm trong Controller; dự án chưa tách thành một tầng dịch vụ nghiệp vụ đầy đủ và chưa xây dựng API riêng cho ứng dụng di động.')
heading('Entity Framework Core và SQL Server',2)
paragraph('Entity Framework Core là công cụ ánh xạ dữ liệu quan hệ cho .NET, cho phép thao tác qua các lớp thực thể, DbContext và truy vấn LINQ. Migrations quản lý thay đổi lược đồ khi mô hình dữ liệu phát triển [4].')
paragraph('ApplicationDbContext ánh xạ 14 tập thực thể. Dữ liệu được lưu trong SQL Server LocalDB với cơ sở dữ liệu EnglishCenterDb. Fluent API thiết lập chỉ mục email duy nhất, các liên kết một–một, một–nhiều và hành vi khi xóa. Quan hệ tài khoản với hồ sơ học viên hoặc giáo viên được triển khai bằng khóa ngoại; đây không phải quan hệ kế thừa lớp TPT.')
heading('Giao diện và trực quan hóa dữ liệu',2)
paragraph('Razor kết hợp HTML với dữ liệu C# phía máy chủ. Bootstrap cung cấp hệ thống lưới và các thành phần biểu mẫu, bảng, nút, hộp thoại để xây dựng giao diện thích ứng [7]. JavaScript bổ sung tương tác tại trình duyệt; Chart.js được dùng để thể hiện các chuỗi thống kê trên bảng điều khiển quản trị [8].')
paragraph('Dự án dùng layout chung cho khu vực công khai, Admin và Teacher. Các thành phần lặp như thanh điều hướng, thanh bên và thông báo được đặt trong layout để giảm trùng mã và duy trì cách trình bày nhất quán.')
heading('Xác thực và phân quyền',2)
paragraph('Xác thực bằng cookie duy trì danh tính sau khi đăng nhập; claims chứa các thông tin định danh cần thiết. Phân quyền theo vai trò giới hạn quyền truy cập chức năng thông qua thuộc tính Authorize [5], [6]. Trong dự án, RoleCookieRouter chọn cookie AdminCookie, TeacherCookie hoặc StudentCookie theo đường dẫn và tham số authRole.')
paragraph('Mật khẩu được băm bằng BCrypt.Net-Next và đối chiếu bằng hàm Verify [9]. Các biểu mẫu thay đổi dữ liệu chủ yếu dùng ValidateAntiForgeryToken để kiểm tra token chống giả mạo yêu cầu. Những cơ chế này là nền tảng bảo vệ; vẫn cần kiểm tra quyền sở hữu bản ghi và xác thực dữ liệu tại từng thao tác.')
heading('Hỗ trợ thanh toán bằng VietQR',2)
paragraph('VietQR.io cung cấp công cụ và đường dẫn ảnh để nhúng mã chuyển khoản vào ứng dụng [10]. Checkout của dự án truyền thông tin ngân hàng, số tài khoản, số tiền và nội dung chuyển khoản cho ảnh QR. Hiển thị mã QR giúp nhập sẵn thông tin giao dịch nhưng không chứng minh giao dịch đã thành công.')
paragraph('Học phí qua VietQR được tạo ở trạng thái Pending và cần Admin xác nhận. Các lựa chọn VNPay/MoMo hiện được xử lý mô phỏng trong EnrollmentController; chưa có luồng gọi cổng, xác thực chữ ký hay nhận IPN. MailKit có trong danh sách phụ thuộc nhưng EmailService còn trống, nên chưa được xem là chức năng gửi email đã hoàn thiện.')

heading('PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG')
heading('Phân tích tác nhân và sơ đồ use case tổng quát',2)
paragraph('Sơ đồ tổng quát thể hiện các mục tiêu chính của bốn tác nhân. Các sơ đồ tiếp theo phân rã theo phạm vi sử dụng của từng nhóm. Đường liền nối tác nhân với use case biểu diễn tương tác; hình elip là chức năng và khung chữ nhật là ranh giới website.')
paragraph('Đăng nhập là điều kiện trước cho nghiệp vụ được bảo vệ, không phải thao tác phải gọi lại trong mỗi use case. Vì vậy, sơ đồ không gắn quan hệ include đến đăng nhập một cách máy móc. Các chức năng công khai có thể được sử dụng khi đã có tài khoản mà không cần lặp lại toàn bộ trên mỗi sơ đồ vai trò.')
figure('uc-overview.png','Sơ đồ use case tổng quát hệ thống',width=15.8,maxheight=19.2)
for title,file,desc in [
('Use case khách chưa đăng nhập','uc-guest.png','Khách tra cứu chương trình, xem lớp mở và thông tin liên hệ, gửi yêu cầu tư vấn, đăng ký tài khoản học viên hoặc đăng nhập. Tài khoản được đăng ký công khai có vai trò Student; tài khoản giáo viên do Admin tạo.'),
('Use case tài khoản học viên','uc-student.png','Học viên quản lý hồ sơ cá nhân, đăng ký lớp, theo dõi lịch học và học phí, đặt lịch thi, xem điểm do người chấm nhập và gửi phản hồi. Khi ghi danh, hệ thống tiếp nhận ảnh hồ sơ, nguyện vọng giáo viên và ghi chú.'),
('Use case tài khoản giáo viên','uc-teacher.png','Giáo viên theo dõi lớp, lịch giảng dạy và các bài kiểm tra được phân công; quản lý tài liệu, nhập điểm và xem phản hồi cùng bảng lương. Checkbox điểm danh hiện chưa có luồng lưu dữ liệu nên không được mô hình hóa như một nghiệp vụ hoàn chỉnh.'),
('Use case tài khoản quản trị viên','uc-admin.png','Admin quản lý chương trình, lớp, tài khoản, ghi danh, lịch thi và tài chính; đồng thời cập nhật banner, trạng thái tư vấn và xử lý thùng rác. Sơ đồ gom các thao tác cùng mục tiêu để giữ khả năng đọc; danh sách thao tác chi tiết được đối chiếu ở phần hiện thực.')]:
    page();heading(title,2);paragraph(desc);figure(file,title,width=15.8,maxheight=19.0)

page();heading('Thiết kế dữ liệu',2)
paragraph('Mô hình hiện tại gồm 14 bảng nghiệp vụ. UserAccount lưu thông tin xác thực; Student và Teacher lưu hồ sơ chuyên biệt. Program và Class tổ chức đào tạo; Registration nối học viên với lớp; Payment gắn với đơn đăng ký. Các bảng còn lại bổ sung lịch, kiểm tra đầu vào, học liệu, phản hồi, lương và nội dung công khai.')
figure('data-model.png','Các bảng dữ liệu và trường khóa chính trong hệ thống',width=15.8,maxheight=15.0)
paragraph('Consultation và Banner là các danh mục độc lập trong mô hình hiện tại. ClassStatus là thuộc tính trạng thái của lớp, không phải một bảng riêng. Hai lớp Program.cs và Class.cs trống trong thư mục Models không tương đương hai bảng bổ sung; các thực thể sử dụng thực tế là CourseProgram và CourseClass.')
heading('Các quan hệ và ràng buộc dữ liệu chính',2).paragraph_format.page_break_before=True
table(['Quan hệ','Bội số','Ý nghĩa'],[
['UserAccount – Student / Teacher','1 – 0..1','Mỗi hồ sơ có một tài khoản; loại hồ sơ phụ thuộc vai trò.'],
['Program – Class','1 – N','Một chương trình có nhiều lớp.'],
['Teacher – Class','0..1 – N','Lớp có thể chưa được phân công giáo viên.'],
['Student / Class – Registration','1 – N','Đơn ghi danh xác định học viên tham gia lớp.'],
['Registration – Payment','1 – 0..1','Mỗi đơn có tối đa một bản ghi học phí.'],
['Class – Schedule / Document','1 – N','Lớp có nhiều ca học và tài liệu.'],
['Student / Teacher – PlacementTest','1 – N / 0..1 – N','Bài thi thuộc học viên và có thể chưa có giáo viên chấm.'],
['Student / Class – CourseFeedback','1 – N','Phản hồi gắn với học viên và lớp.'],
['Teacher – TeacherSalary','1 – N','Một giáo viên có nhiều kỳ lương.']],[5.6,2.4,8.0])
paragraph('Email có chỉ mục duy nhất. Các khóa ngoại của Registration sử dụng Restrict để tránh xóa hồ sơ hoặc lớp khi còn đơn liên kết. Một số liên kết tùy chọn tới giáo viên dùng SetNull. Các đối tượng có IsDeleted và DeletedAt được đưa vào thùng rác trước khi xóa vĩnh viễn; điều kiện xóa cần được kiểm tra cùng các bản ghi phụ thuộc.')
heading('Đặc tả các luồng nghiệp vụ tiêu biểu',2)
table(['Luồng','Điều kiện và các bước chính','Kết quả'],[
['Đăng ký lớp','Học viên đăng nhập; xem Checkout; gửi ảnh hoặc dùng ảnh hồ sơ; chọn cách thanh toán và xác nhận.','Tạo Registration và Payment; VietQR ở trạng thái chờ đối soát.'],
['Xác nhận học phí','Admin xem danh sách học phí; chọn xác nhận cho khoản đã thu.','Payment chuyển Paid; đơn tương ứng được xác nhận theo logic hiện tại.'],
['Kiểm tra xếp lớp','Học viên đặt ngày, ca; Admin phân công lịch và giáo viên; giáo viên nhập điểm, cấp độ.','PlacementTest chuyển Completed; học viên xem kết quả trong lịch sử kiểm tra.'],
['Xử lý thùng rác','Admin xem đối tượng đã xóa mềm; chọn khôi phục hoặc xóa vĩnh viễn sau kiểm tra ràng buộc.','Khôi phục IsDeleted hoặc xóa bản ghi khỏi dữ liệu.']],[3.0,8.1,4.9])

heading('HIỆN THỰC VÀ KIỂM TRA HỆ THỐNG')
heading('Môi trường và tổ chức mã nguồn',2)
paragraph('Dự án nhắm đến .NET 8, sử dụng ASP.NET Core MVC, Entity Framework Core và SQL Server LocalDB. Các thư viện trong tệp dự án gồm BCrypt.Net-Next 4.0.3, MailKit 4.18.1 và Swashbuckle 6.6.2. EF Core và provider SQL Server đang khai báo các phiên bản 8.0.x khác nhau; cần đồng bộ khi chuẩn bị bản phát hành.')
table(['Thành phần','Vị trí','Vai trò'],[
['Khởi động','Program.cs','Đăng ký DbContext, cookie theo vai trò, MVC và định tuyến.'],
['Dữ liệu','Models, Data, Migrations','Thực thể, quan hệ dữ liệu, thay đổi lược đồ và nạp dữ liệu ban đầu.'],
['Công khai và học viên','Controllers, Views','Tra cứu, xác thực, hồ sơ, ghi danh, lịch và học phí.'],
['Quản trị và giáo viên','Areas/Admin, Areas/Teacher','Tách các cổng làm việc theo vai trò.'],
['Tệp tải lên','wwwroot/uploads','Ảnh hồ sơ, banner và tài liệu lớp học.']],[3.1,5.0,7.9])
paragraph('Ảnh giao diện trong chương này được chụp từ website chạy cục bộ và dữ liệu hiện có. Số lượng học viên, lớp, doanh thu hoặc kỳ lương trên màn hình là dữ liệu trình diễn tại thời điểm chụp; chúng không phải số liệu khảo sát hoạt động của một trung tâm đang vận hành.')

def ui_pair(title,text,items):
    page();heading(title,2);paragraph(text)
    for file,cap in items:figure(file+'.jpg',cap,width=15.0)

ui_pair('Trang chủ và danh mục khóa học','Trang chủ tập trung banner, các điểm truy cập nhanh và khóa học nổi bật. Trang chương trình bổ sung tìm kiếm, lọc theo cấp độ và học phí, giúp người dùng thu hẹp lựa chọn trước khi xem lớp mở.',[
('ui-home','Trang chủ HITC English'),('ui-programs','Danh mục chương trình và bộ lọc khóa học')])
ui_pair('Chi tiết khóa học và liên hệ','Trang chi tiết trình bày mô tả, thời lượng, mức phí và các lớp thuộc chương trình. Trang liên hệ cung cấp thông tin trung tâm cùng biểu mẫu tư vấn; yêu cầu được tiếp nhận ở trạng thái Pending.',[
('ui-detail','Thông tin chi tiết chương trình học'),('ui-contact','Thông tin liên hệ và biểu mẫu yêu cầu tư vấn')])
ui_pair('Đăng nhập và đăng ký tài khoản','Đăng nhập kiểm tra email, mật khẩu và tình trạng tài khoản rồi điều hướng theo vai trò. Đăng ký công khai tạo tài khoản Student và hồ sơ học viên tương ứng; dữ liệu nhập được kiểm tra bằng ViewModel.',[
('ui-login','Giao diện đăng nhập đa vai trò'),('ui-register','Biểu mẫu đăng ký tài khoản học viên')])
ui_pair('Hồ sơ và bảo vệ tài khoản','Học viên có thể cập nhật họ tên, thông tin liên hệ, ngày sinh và ảnh hồ sơ. Đổi mật khẩu yêu cầu mật khẩu hiện tại và xác nhận mật khẩu mới. Các ảnh minh họa chỉ thể hiện biểu mẫu, không thực hiện thay đổi thông tin khi chụp.',[
('ui-profile','Cập nhật hồ sơ học viên'),('ui-change-password','Biểu mẫu đổi mật khẩu')])
ui_pair('Lớp đã đăng ký và lịch học','Lớp của tôi hiển thị chương trình, giảng viên, lịch học và trạng thái đăng ký. Trang thời khóa biểu hỗ trợ chuyển tuần và trình bày lịch học cùng lịch kiểm tra đầu vào để học viên theo dõi tập trung.',[
('ui-myclasses','Danh sách lớp đã đăng ký của học viên'),('ui-schedule','Thời khóa biểu và lịch thi của học viên')])
ui_pair('Đăng ký lớp và thông tin chuyển khoản','Checkout tiếp nhận thông tin ghi danh, nguyện vọng giáo viên, ghi chú và lựa chọn thanh toán. Ảnh QR hỗ trợ chuyển khoản đúng thông tin; hệ thống chưa nhận thông báo ngân hàng tự động. Việc chụp minh họa không xác nhận hoặc thực hiện giao dịch.',[
('ui-checkout','Biểu mẫu xác nhận đăng ký khóa học'),('ui-qr','Vùng chọn phương thức thanh toán và mã VietQR')])
ui_pair('Theo dõi học phí và in biên lai','Lịch sử học phí hiển thị số tiền, phương thức, thời gian và trạng thái. Mẫu biên lai được kết xuất từ bản ghi học phí và đơn đăng ký, hỗ trợ lệnh in của trình duyệt hoặc lưu PDF; đây là biên lai nội bộ.',[
('ui-payments','Lịch sử thanh toán học phí'),('ui-receipt','Mẫu biên lai thu học phí')])
ui_pair('Đặt lịch và quản lý kiểm tra đầu vào','Học viên chọn ngày, ca và xem lịch sử kết quả. Admin phân công phòng, lịch và giáo viên chấm. Website chưa có bộ câu hỏi trắc nghiệm Listening/Reading tự chấm; kết quả được nhập qua chức năng của giáo viên hoặc quản trị viên.',[
('ui-test','Đặt lịch kiểm tra và xem kết quả xếp lớp'),('ui-admin-tests','Quản trị lịch kiểm tra và phân công giáo viên')])
ui_pair('Bảng điều khiển và lớp giảng dạy','Cổng giáo viên trình bày thông tin cá nhân, các chỉ số hỗ trợ và các lớp được giao. Danh sách lớp liên kết đến học viên và lịch giảng dạy. Số liệu trên bảng điều khiển cần được diễn giải theo phạm vi truy vấn của từng chỉ số.',[
('ui-teacher-dashboard','Bảng điều khiển giáo viên'),('ui-teacher-classes','Các lớp giáo viên được phân công')])
ui_pair('Danh sách học viên và lịch giảng dạy','Giáo viên tra cứu danh sách học viên và lịch dạy theo tuần, đồng thời xem lịch kiểm tra được giao. Cột điểm danh hiện là checkbox giao diện; chưa có bảng và thao tác lưu lịch sử chuyên cần theo buổi học.',[
('ui-teacher-students','Danh sách học viên trong lớp của giáo viên'),('ui-teacher-schedule','Lịch giảng dạy và các ca kiểm tra được giao')])
ui_pair('Chấm kiểm tra và quản lý tài liệu','Giáo viên xem các bài kiểm tra được phân công và nhập điểm, cấp độ đề xuất. Phân hệ tài liệu cho phép tải lên, xem liên kết tải về và xóa tài liệu lớp. Ảnh trang tài liệu có thể hiển thị danh sách trống theo dữ liệu của giáo viên được chọn.',[
('ui-teacher-tests','Danh sách bài kiểm tra và thao tác chấm điểm'),('ui-teacher-documents','Quản lý tài liệu và bài giảng của giáo viên')])
ui_pair('Phản hồi và thu nhập giáo viên','Giáo viên xem phản hồi học viên của các lớp phụ trách và các khoản lương theo kỳ. Bảng lương thể hiện các thành phần tính và trạng thái chi trả; việc duyệt chi do quản trị viên thực hiện.',[
('ui-teacher-feedback','Danh sách phản hồi dành cho giáo viên'),('ui-teacher-salary','Bảng lương và thu nhập của giáo viên')])
ui_pair('Điều hành và quản lý chương trình học','Bảng điều khiển quản trị tổng hợp quy mô đào tạo, học phí và biểu đồ. Chương trình học được thêm, sửa, thay đổi trạng thái tuyển sinh hoặc xóa mềm. Dữ liệu thống kê là dữ liệu trình diễn, chưa được dùng để kết luận hiệu quả kinh doanh.',[
('ui-admin-dashboard','Bảng điều khiển và thống kê quản trị'),('ui-admin-programs','Quản lý chương trình đào tạo')])
ui_pair('Quản lý lớp và điều phối ghi danh','Admin tổ chức các lớp theo chương trình và phân công giáo viên. Danh sách ghi danh hỗ trợ theo dõi trạng thái và điều phối học viên sang lớp phù hợp. Cần bổ sung kiểm tra sĩ số và lịch trùng đầy đủ ở các bước ghi dữ liệu.',[
('ui-admin-classes','Quản lý lớp mở và phân công giáo viên'),('ui-admin-registrations','Quản lý ghi danh và điều phối lớp')])
ui_pair('Quản lý học phí và lương','Admin đối soát các khoản học phí trước khi xác nhận thu tiền. Phân hệ lương hỗ trợ lập và điều chỉnh lương theo tháng, lọc danh sách, xác nhận chi trả và xóa bảng lương. Hai quy trình phục vụ theo dõi tài chính nội bộ.',[
('ui-admin-payments','Quản lý và xác nhận thanh toán học phí'),('ui-admin-salaries','Quản lý bảng lương giáo viên')])
ui_pair('Quản lý hồ sơ học viên và giáo viên','Admin cập nhật hồ sơ học viên và khóa hoặc mở tài khoản học viên. Hồ sơ giáo viên hỗ trợ thêm mới, chỉnh sửa, ảnh hồ sơ và xóa mềm. Mã hiện tại chưa có thao tác khóa/mở riêng cho tài khoản giáo viên.',[
('ui-admin-students','Quản lý học viên và trạng thái tài khoản'),('ui-admin-teachers','Quản lý hồ sơ giáo viên')])
ui_pair('Quản lý tư vấn và banner','Danh sách tư vấn cho phép xem nội dung, đổi trạng thái đã xử lý và xóa mềm. Banner được quản lý theo hình ảnh, thứ tự và trạng thái hiển thị. Thao tác đổi trạng thái tư vấn không đồng nghĩa với gửi thư trả lời tự động.',[
('ui-admin-consultations','Quản lý yêu cầu tư vấn tuyển sinh'),('ui-admin-banners','Quản lý banner trên trang chủ')])
page();heading('Thùng rác và phục hồi dữ liệu',2)
paragraph('Thùng rác tập trung các bản ghi được xóa mềm. Admin có thể khôi phục hoặc xóa vĩnh viễn tùy loại đối tượng và điều kiện liên kết dữ liệu. Ảnh minh họa giữ nguyên trạng thái hiện có; không tạo hoặc xóa dữ liệu chỉ để phục vụ chụp hình.')
figure('ui-admin-trash.jpg','Thùng rác và trạng thái dữ liệu đã xóa mềm',width=15.2)
heading('Phạm vi và kết quả kiểm tra',2)
paragraph('Đợt kiểm tra giao diện mở 33 địa chỉ trang ở các vai trò bằng trình duyệt tự động, nhận HTTP 200 và quan sát được nội dung tương ứng. Việc đăng nhập dùng ba tài khoản mẫu có sẵn. Hai kiểm tra truy cập Admin được ghi lại riêng; kết quả được trình bày dưới đây.')
table(['Nội dung','Quan sát thực tế','Phạm vi kết luận'],[
['Mở các trang công khai và có đăng nhập','33/33 địa chỉ chụp chính trả HTTP 200, có tiêu đề và giao diện tương ứng.','Xác nhận khả năng mở trang trong phiên kiểm tra.'],
['Đăng nhập theo vai trò','Student, Teacher, Admin vào được các trang tương ứng.','Xác nhận luồng đăng nhập với tài khoản mẫu.'],
['Khách mở /Admin/Dashboard','Chuyển đến /Account/Login kèm ReturnUrl.','Không hiển thị trang quản trị khi thiếu phiên Admin.'],
['Student mở /Admin/Dashboard','Chuyển đến trang đăng nhập Admin vì router chọn cookie Admin riêng.','Không mặc định kết luận trả HTTP 403.']],[4.0,7.0,5.0])
heading('Các điểm cần hoàn thiện sau kiểm tra',2)
paragraph('Đối chiếu mã nguồn cho thấy cần hoàn thiện kiểm soát sĩ số, chống đăng ký trùng tại bước xác nhận, kiểm tra xung đột lịch và quyền sở hữu dữ liệu trong các thao tác tài liệu hoặc phản hồi. Quy trình tạo đăng ký cùng học phí cần được xem xét dùng giao dịch dữ liệu để tránh trạng thái dở dang khi có lỗi.')
paragraph('Các ca thử thay đổi dữ liệu như tạo lớp, xác nhận học phí, chi trả lương, khôi phục và xóa vĩnh viễn cần thực hiện trên cơ sở dữ liệu kiểm thử riêng. Đợt chụp giao diện không thay thế kiểm thử toàn bộ nghiệp vụ; chưa có số đo tải, độ trễ, bảo mật hoặc tỷ lệ thành công để kết luận sẵn sàng vận hành thực tế.')

heading('KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN',1,False)
heading('Kết quả đạt được',2,False)
paragraph('Đề tài đã xây dựng được ứng dụng ASP.NET Core MVC phục vụ các nhóm tác nhân của trung tâm ngoại ngữ, tổ chức dữ liệu trên SQL Server và triển khai cơ chế cookie theo vai trò. Các phân hệ hiện có bao quát tra cứu chương trình, hồ sơ, ghi danh, học phí, lịch học, kiểm tra đầu vào, tài liệu, phản hồi và quản trị nội bộ.')
paragraph('Bộ sơ đồ use case cùng mô hình bảng dữ liệu mô tả phạm vi chức năng và liên kết giữa các thành phần. Ảnh giao diện cho thấy các màn hình chính có thể mở trong môi trường cục bộ; việc tách Areas giúp phân biệt cổng quản trị, giáo viên và khu vực học viên.')
heading('Hạn chế và hướng phát triển',2,False)
paragraph('Sản phẩm vẫn cần hoàn thiện nghiệp vụ và kiểm thử trước khi triển khai thực tế. Những phần chưa hoàn chỉnh gồm điểm danh lưu theo buổi, thi trực tuyến tự chấm, học liệu dành riêng cho học viên, gửi email và đối soát ngân hàng tự động. Các lựa chọn thanh toán mô phỏng phải được tách rõ khỏi trạng thái giao dịch thật.')
paragraph('Ưu tiên phát triển tiếp theo là bổ sung kiểm tra quyền trên từng bản ghi; dùng giao dịch cho ghi danh và học phí; kiểm soát sĩ số, lịch trùng và xóa dữ liệu có liên kết. Sau đó có thể triển khai IPN có xác thực chữ ký, bộ kiểm thử nghiệp vụ, nhật ký thao tác và sao lưu dữ liệu. Các mở rộng như lớp học trực tuyến hoặc ứng dụng di động chỉ nên thực hiện sau khi các luồng cốt lõi ổn định.')

heading('TÀI LIỆU THAM KHẢO',1,False)
refs=[
('VUS','Website Anh văn Hội Việt Mỹ','https://vus.edu.vn/'),
('ILA Vietnam','Website trung tâm Anh ngữ ILA','https://ila.edu.vn/'),
('Microsoft','Overview of ASP.NET Core MVC','https://learn.microsoft.com/en-us/aspnet/core/mvc/overview?view=aspnetcore-8.0'),
('Microsoft','Entity Framework Core','https://learn.microsoft.com/en-us/ef/core/'),
('Microsoft','Use cookie authentication without ASP.NET Core Identity','https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie?view=aspnetcore-8.0'),
('Microsoft','Role based authorization in ASP.NET Core','https://learn.microsoft.com/en-us/aspnet/core/security/authorization/roles?view=aspnetcore-8.0'),
('Bootstrap','Get started with Bootstrap 5.3','https://getbootstrap.com/docs/5.3/getting-started/introduction/'),
('Chart.js','Chart.js Documentation','https://www.chartjs.org/docs/latest/'),
('BCrypt.Net','BCrypt.Net source and usage documentation','https://github.com/BcryptNet/bcrypt.net'),
('Casso','VietQR Payment Kit và Quick Link','https://www.vietqr.io/'),
]
for i,(author,title,url) in enumerate(refs,1):
    p=paragraph(f'[{i}] {author}. {title}. ')
    link(p,url,url);p.add_run('. Truy cập ngày 03/11/2026.')
    p.paragraph_format.first_line_indent=Cm(0);p.paragraph_format.space_after=Pt(8)
paragraph('Nguồn nội bộ: mã nguồn dự án WedEnglishApp, gồm Program.cs, ApplicationDbContext, Models, Controllers, Areas, Views và các tệp cấu hình; tài liệu báo cáo ban đầu và ảnh khảo sát VUS, ILA đi kèm. Các hình use case và mô hình bảng dữ liệu được xây dựng từ mã nguồn; ảnh giao diện HITC English được chụp từ bản chạy cục bộ.')

# Encourage update on open without locking the live field results.
settings=doc.settings.element
settings.append(xml('w:updateFields',val='true'))
doc.save(OUTPUT)
(ROOT/'figure-index.json').write_text(json.dumps(figures,ensure_ascii=False,indent=2),encoding='utf8')
print(OUTPUT)
print('Figures:',len(figures),'Paragraphs:',len(doc.paragraphs),'Tables:',len(doc.tables))
