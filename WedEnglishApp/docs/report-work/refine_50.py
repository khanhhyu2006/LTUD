from pathlib import Path
import re,json
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parent
SOURCE=R.parent.parent/'Bao_cao_HITC_English_Giu_nguyen_noi_dung_goc.docx'
d=Document(SOURCE);o=Document('D:/LTUD/doanketthucmonWeb.docx')
def norm(s):return re.sub(r'\s+',' ',s).strip()
def clean(s):
    if s.startswith('(Vị trí chèn hình:'):s=s.replace('(Vị trí chèn hình:','',1).strip().removesuffix(')')
    elif s.startswith('(Hình '):s=s[1:].removesuffix(')')
    return s.replace('CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG','')
ps=list(d.paragraphs);mapped={};cursor=0
for i,p in enumerate(o.paragraphs):
    value=norm(clean(p.text))
    if not value:continue
    for j in range(cursor,len(ps)):
        if norm(ps[j].text)==value:mapped[i]=ps[j];cursor=j+1;break
assert len(mapped)>=490,len(mapped)

def el(tag,**attrs):
    x=OxmlElement(tag)
    for k,v in attrs.items():x.set(qn('w:'+k),str(v))
    return x
nums=d.part.numbering_part.element
an=el('w:abstractNum',abstractNumId=77);lv=el('w:lvl',ilvl=0)
lv.append(el('w:start',val=1));lv.append(el('w:numFmt',val='bullet'));lv.append(el('w:lvlText',val='•'))
lv.append(el('w:suff',val='tab'));an.append(lv);nums.append(an)
num=el('w:num',numId=77);num.append(el('w:abstractNumId',val=77));nums.append(num)
changes=[]
def newp(text,kind='b'):
    p=d.add_paragraph()
    if kind.startswith('h'):
        p.style='Heading '+kind[-1];p.add_run(text)
        p.paragraph_format.keep_with_next=True
        p.paragraph_format.page_break_before=kind=='h1'
        np=el('w:numPr');np.append(el('w:numId',val=0));p._p.get_or_add_pPr().append(np)
    else:
        p.style='Normal';p.paragraph_format.line_spacing=1.15;p.paragraph_format.space_after=Pt(5)
        if kind=='b':
            np=el('w:numPr');np.append(el('w:ilvl',val=0));np.append(el('w:numId',val=77));p._p.get_or_add_pPr().append(np)
            p.paragraph_format.left_indent=Cm(.5);p.paragraph_format.first_line_indent=Cm(-.25)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(.5))
        else:p.paragraph_format.first_line_indent=Cm(.75)
        if kind=='b' and ':'in text and len(text.split(':',1)[0])<55:
            label,body=text.split(':',1);p.add_run(label+':').bold=True;p.add_run(body)
        else:p.add_run(text)
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(13 if not kind.startswith('h')else 14 if kind=='h2'else 13);r.font.color.rgb=RGBColor(0,0,0)
    return p
def replace(start,end,entries):
    targets=[mapped[i]for i in range(start,end+1)if i in mapped and mapped[i]._p.getparent()is not None]
    if not targets:return
    anchor=targets[0]._p
    for kind,text in entries:anchor.addprevious(newp(text,kind)._p)
    for p in targets:
        if p._p.xpath('.//w:drawing'):continue
        if p.style.name=='HITCFigureCaption':continue
        p._p.getparent().remove(p._p)
    changes.append([start,end,len(entries)])
def B(*a):return [('b',s)for s in a]
def P(s):return [('p',s)]
def H(s,l=2):return [('h'+str(l),s)]

replace(2,61,
 H('1. Lý do chọn đề tài')+
 P('Việc quản lý hồ sơ, lớp học và học phí bằng sổ sách hoặc nhiều bảng tính rời rạc dễ gây trùng dữ liệu, cập nhật chậm và khó tổng hợp. Người học cần một kênh tra cứu chương trình, đăng ký và theo dõi lịch học thuận tiện. Đề tài HITC English được lựa chọn để vận dụng ASP.NET Core MVC và SQL Server vào bài toán này.')+
 H('2. Mục tiêu nghiên cứu')+
 B('Khách: Tra cứu chương trình, lớp mở, học phí; gửi yêu cầu tư vấn và đăng ký tài khoản.',
 'Học viên: Cập nhật hồ sơ, đăng ký lớp, xem lịch học và lịch thi, theo dõi học phí, in biên lai và gửi đánh giá.',
 'Giáo viên: Theo dõi lớp phụ trách, quản lý tài liệu, nhập kết quả kiểm tra được giao, xem phản hồi và bảng lương.',
 'Admin: Quản lý đào tạo, tài khoản, ghi danh, học phí, lịch thi, lương, banner, tư vấn và thùng rác.')+
 H('3. Đối tượng và phạm vi nghiên cứu')+
 B('Đối tượng: Quy trình tuyển sinh, ghi danh, tổ chức lớp, phân công giáo viên và quản lý học phí tại trung tâm ngoại ngữ.',
 'Công nghệ: ASP.NET Core MVC (.NET 8), C#, Razor, Entity Framework Core và SQL Server LocalDB.',
 'Phạm vi: Ứng dụng web với bốn tác nhân; ba vai trò tài khoản là Student, Teacher và Admin. Khách không phải một loại tài khoản.',
 'Giới hạn: Kiểm tra đầu vào hiện là đặt lịch và nhập kết quả; VietQR hỗ trợ thông tin chuyển khoản, chưa tự động đối soát ngân hàng; VNPay/MoMo đang mô phỏng.')+
 H('4. Phương pháp và bố cục nghiên cứu')+
 B('Nghiên cứu tài liệu: Tham khảo Microsoft Learn và tài liệu chính thức của các thư viện sử dụng.',
 'Khảo sát và phân tích: Tham khảo giao diện công khai của VUS, ILA; xác định tác nhân, use case, thực thể và các liên kết dữ liệu.',
 'Hiện thực và đánh giá: Lập trình MVC, tạo dữ liệu bằng EF Core, đối chiếu mã nguồn và quan sát các màn hình trên môi trường cục bộ.')+
 P('Báo cáo gồm bốn chương: tổng quan; cơ sở lý thuyết; phân tích và thiết kế; hiện thực và kiểm tra hệ thống. Phần cuối trình bày kết luận, hướng phát triển và tài liệu tham khảo.'))

replace(64,81,H('1.1 Bài toán quản lý trung tâm ngoại ngữ')+
 P('Quy trình bắt đầu khi khách tra cứu khóa học và gửi tư vấn. Sau khi có tài khoản, học viên đặt lịch kiểm tra hoặc chọn lớp; quản trị viên tiếp nhận ghi danh, phân công giáo viên và xác nhận học phí. Giáo viên theo dõi lớp, tài liệu và kết quả kiểm tra được giao.')+
 B('Hạn chế của cách quản lý phân tán: Hồ sơ dễ trùng hoặc thất lạc; lịch học khó đồng bộ; tình trạng thu học phí khó tổng hợp.',
 'Giải pháp tập trung: Liên kết tài khoản, hồ sơ, chương trình, lớp, ghi danh và học phí trong một cơ sở dữ liệu.',
 'Phân quyền sử dụng: Các chức năng công khai dành cho mọi người; nghiệp vụ cá nhân và quản trị yêu cầu phiên đăng nhập đúng vai trò.',
 'Quy tắc cần kiểm soát: Sĩ số, lịch trùng, trạng thái ghi danh và quyền sở hữu bản ghi phải được kiểm tra tại bước ghi dữ liệu.'))
replace(82,85,H('1.2 Khảo sát các website tham khảo')+H('1.2.1 Website VUS',3)+P('VUS được tham khảo về cách giới thiệu thương hiệu, tổ chức chương trình theo nhóm tuổi và bố trí nút tư vấn. Hình dưới là tư liệu khảo sát trong bản báo cáo ban đầu.'))
replace(87,95,B('Điểm tham khảo: Danh mục rõ ràng, banner nổi bật, liên kết tư vấn dễ nhận biết và thông tin khóa học phân nhóm.',
 'Vận dụng cho HITC English: Dùng thanh điều hướng ngắn, thẻ chương trình và lời mời tư vấn; không sao chép nội dung thương hiệu.',
 'Giới hạn khảo sát: Giao diện công khai không đủ căn cứ kết luận về hệ thống nội bộ hoặc quy trình thanh toán của VUS.'))
replace(96,97,H('1.2.2 Website ILA',3))
replace(99,107,B('Điểm tham khảo: Phân nhóm chương trình, thông tin giáo viên và hệ thống cơ sở được trình bày rõ.',
 'Vận dụng cho HITC English: Đưa thông tin chương trình, lớp mở và liên hệ vào các điểm truy cập dễ tìm.',
 'Giới hạn khảo sát: Chỉ đánh giá cách tổ chức thông tin công khai; chưa đánh giá hiệu năng hoặc các chức năng yêu cầu tài khoản của ILA.'))
replace(108,119,H('1.3 Vấn đề cần giải quyết và giải pháp đề xuất')+
 B('Dữ liệu tuyển sinh: Lưu yêu cầu tư vấn và trạng thái xử lý để nhân viên theo dõi.',
 'Dữ liệu đào tạo: Tổ chức chương trình, lớp, ca học và giáo viên; hỗ trợ điều phối học viên.',
 'Dữ liệu tài chính: Ghi nhận học phí, đối soát thủ công, hiển thị lịch sử và biên lai; theo dõi lương giáo viên riêng.',
 'Dữ liệu vận hành: Cung cấp thống kê, banner và cơ chế xóa mềm, khôi phục phù hợp từng đối tượng.'))
replace(120,122,H('1.4 Đối tượng sử dụng'))
replace(123,129,H('1.5 Phạm vi và ý nghĩa thực tiễn')+
 B('Phạm vi sử dụng: Một trung tâm ngoại ngữ, dữ liệu trình diễn tại môi trường cục bộ; chưa đánh giá vận hành nhiều chi nhánh.',
 'Giá trị cho học viên: Chủ động tra cứu chương trình, hồ sơ, lịch học và tình trạng học phí.',
 'Giá trị cho trung tâm: Tập trung dữ liệu và giảm thao tác tổng hợp thủ công; tạo nền tảng mở rộng khi nghiệp vụ được kiểm thử đầy đủ.'))
replace(130,140,H('Kết chương 1')+P('Chương 1 xác định bài toán, nhóm người dùng và phạm vi của HITC English. Những yêu cầu này là cơ sở lựa chọn công nghệ và thiết kế chức năng ở các chương tiếp theo.'))

replace(142,206,
 H('2.1 Kiến trúc Client Server và ASP.NET Core MVC')+
 B('Client: Trình duyệt gửi yêu cầu HTTP và hiển thị HTML, CSS, JavaScript.',
 'Server: Kestrel hoặc IIS Express tiếp nhận yêu cầu; Controller truy vấn dữ liệu rồi trả Razor View.',
 'Model: Các thực thể và ViewModel biểu diễn dữ liệu; View kết xuất giao diện; Controller điều phối yêu cầu.',
 'Tổ chức dự án: Khu vực công khai nằm tại Controllers/Views; Admin và Teacher được tách bằng Areas. Chưa có hệ thống API riêng cho ứng dụng di động.')+
 H('2.2 C# và Entity Framework Core')+
 B('C#: Sử dụng lớp, kiểu dữ liệu và async/await cho các thao tác truy xuất dữ liệu bất đồng bộ.',
 'Entity Framework Core: Ánh xạ thực thể với bảng, truy vấn bằng LINQ và nạp dữ liệu liên quan bằng Include/ThenInclude.',
 'Migrations: Quản lý thay đổi lược đồ dữ liệu từ mô hình C#; ApplicationDbContext khai báo các tập thực thể và quan hệ.',
 'Tổ chức nghiệp vụ: Nhiều xử lý hiện nằm trong Controller; các dịch vụ tệp và ảnh hỗ trợ lưu dữ liệu tải lên. Chưa tách thành một tầng dịch vụ nghiệp vụ hoàn chỉnh.')+
 H('2.3 Công nghệ giao diện')+
 B('Razor: Kết hợp dữ liệu C# với HTML và tái sử dụng layout chung.',
 'Bootstrap 5: Cung cấp lưới, biểu mẫu, nút, bảng và hộp thoại; hỗ trợ bố cục thích ứng.',
 'JavaScript và Chart.js: Bổ sung tương tác tại trình duyệt và biểu đồ thống kê quản trị. Mỗi số liệu cần được diễn giải theo truy vấn thực tế, không chỉ theo nhãn giao diện.')+
 H('2.4 SQL Server và mô hình dữ liệu')+
 B('Lưu trữ: Dự án dùng SQL Server LocalDB với cơ sở dữ liệu EnglishCenterDb.',
 'Quan hệ: Khóa ngoại liên kết tài khoản, hồ sơ, lớp, ghi danh và học phí; email có chỉ mục duy nhất.',
 'Toàn vẹn dữ liệu: Restrict, Cascade hoặc SetNull được cấu hình theo quan hệ. Tài khoản và hồ sơ là các thực thể liên kết một–một, không phải kế thừa TPT.',
 'Giao dịch: Các bước tạo đăng ký và học phí cần được xử lý nhất quán; cần bổ sung transaction để tránh trạng thái dở dang khi có lỗi.')+
 H('2.5 Xác thực và phân quyền')+
 B('Cookie và claims: Lưu thông tin định danh sau khi kiểm tra tài khoản và mật khẩu.',
 'RoleCookieRouter: Chọn cookie AdminCookie, TeacherCookie hoặc StudentCookie theo đường dẫn và authRole, hỗ trợ các phiên vai trò tách biệt.',
 'BCrypt: Băm mật khẩu khi tạo hoặc đổi mật khẩu; Verify được dùng để đối chiếu.',
 'Bảo vệ thao tác: Authorize kiểm tra vai trò; ValidateAntiForgeryToken kiểm tra yêu cầu biểu mẫu. Quyền trên từng bản ghi vẫn phải được kiểm tra tại các action liên quan.')+
 H('2.6 VietQR và giới hạn tích hợp')+
 B('Hiển thị QR: Checkout nhúng ảnh VietQR với ngân hàng, tài khoản, số tiền và nội dung chuyển khoản.',
 'Đối soát: Có mã QR không đồng nghĩa giao dịch đã thành công; Admin kiểm tra trước khi xác nhận thu tiền.',
 'Phạm vi hiện tại: VNPay/MoMo đang mô phỏng; chưa có xác thực IPN. MailKit có trong phụ thuộc nhưng EmailService chưa được hiện thực đầy đủ.')+
 H('Kết chương 2')+P('Các công nghệ được lựa chọn tạo nền tảng cho ứng dụng MVC và dữ liệu quan hệ. Chương 3 phân tích cụ thể tác nhân, use case, dữ liệu và các điều kiện nghiệp vụ cần kiểm soát.'))

replace(210,215,H('3.1.1 Tác nhân và cách đọc sơ đồ',3)+
 B('Bốn tác nhân: Khách, học viên, giáo viên và quản trị viên; chỉ ba nhóm sau có vai trò tài khoản.',
 'Ký hiệu: Người que là tác nhân; elip là mục tiêu chức năng; khung là ranh giới hệ thống. Đường liền biểu diễn tương tác.',
 'Điều kiện truy cập: Đăng nhập là điều kiện trước của nghiệp vụ được bảo vệ. Chỉ dùng include/extend khi xác định rõ hành vi dùng lại hoặc mở rộng; không dùng để biểu diễn thứ tự màn hình.'))

replace(219,255,H('4.1.1 Môi trường phát triển và triển khai',3)+
 B('Nền tảng: Windows, .NET 8 và Visual Studio; ứng dụng chạy trên Kestrel hoặc IIS Express.',
 'Cơ sở dữ liệu: SQL Server LocalDB; cấu hình trong appsettings.json; mô hình và dữ liệu ban đầu tại ApplicationDbContext, Migrations và DbInitializer.',
 'Tổ chức mã: Models/ViewModels cho dữ liệu; Controllers/Views cho giao diện công khai và học viên; Areas/Admin, Areas/Teacher cho các cổng theo vai trò.',
 'Tệp tải lên: Ảnh hồ sơ, banner và tài liệu được lưu dưới wwwroot/uploads theo chức năng.',
 'Điều kiện triển khai: Cần kiểm tra cấu hình kết nối, quyền ghi thư mục, khóa bảo mật, sao lưu và dữ liệu kiểm thử trước khi vận hành.'))
replace(259,265,H('4.1.3 Đường ống xử lý yêu cầu',3)+
 B('Khởi tạo: Đăng ký DbContext, MVC và cơ chế xác thực; cấu hình định tuyến Areas và tuyến mặc định.',
 'Tiếp nhận: Middleware phục vụ tệp tĩnh và xác định tuyến xử lý.',
 'Kiểm soát truy cập: UseAuthentication nhận diện người dùng; UseAuthorization kiểm tra quyền trước khi action chạy.',
 'Kết xuất: Controller xử lý yêu cầu, truy vấn hoặc cập nhật dữ liệu rồi trả View hoặc chuyển hướng.'))
replace(267,272,P('Giao diện được chia theo nhóm sử dụng, với layout chung, thanh điều hướng và các biểu mẫu Bootstrap. Các hình dưới gồm ảnh trong tài liệu ban đầu và ảnh chụp bổ sung từ website cục bộ; số liệu hiển thị là dữ liệu trình diễn.'))
replace(274,274,H('A. Trang chủ công khai',3))
replace(277,291,B('Giao diện: Logo, thanh điều hướng, banner, khóa học nổi bật và điểm truy cập tư vấn.',
 'Dữ liệu: HomeController lấy banner đang hiển thị, chương trình và lớp liên quan rồi đóng gói trong HomeViewModel.',
 'Tư vấn: Biểu mẫu gửi POST qua ConsultationController; yêu cầu hợp lệ được lưu Pending và hiển thị thông báo. Chưa có chức năng gửi nội dung trả lời tự động.'))
replace(292,292,H('B. Trang chủ sau đăng nhập',3))
replace(295,301,B('Cá nhân hóa: Tên và ảnh người dùng thay cho nút đăng nhập; menu dẫn đến hồ sơ, lớp, học phí, đổi mật khẩu và đăng xuất.',
 'Phiên làm việc: Cookie Student nhận diện học viên; RoleCookieRouter duy trì ngữ cảnh của từng vai trò.',
 'Ghi danh: Liên kết đăng ký dẫn đến Checkout; thông tin cá nhân được lấy từ hồ sơ hiện có.'))
replace(302,309,H('C. Danh mục khóa học',3)+B('Chức năng: Tìm theo từ khóa, lọc cấp độ và khoảng học phí; xem danh sách chương trình cùng thời lượng, mức phí.',
 'Xử lý: ProgramController nhận tham số lọc, truy vấn chương trình hợp lệ và phân trang kết quả.'))
replace(312,318,H('D. Chi tiết chương trình',3)+B('Thông tin: Mô tả chương trình, chuẩn đầu ra, thời lượng, học phí và các lớp liên quan.',
 'Điều hướng: Người dùng chọn lớp để đăng ký; chương trình không hợp lệ được xử lý bằng NotFound.'))
replace(321,329,H('E. Đặt lịch kiểm tra đầu vào',3)+B('Học viên: Chọn ngày, ca kiểm tra và xem lịch sử điểm, cấp độ đề xuất.',
 'Xử lý: BookTest kiểm tra ngày hợp lệ và tạo PlacementTest ở trạng thái Pending.',
 'Giới hạn: Giáo viên hoặc Admin nhập kết quả; chưa có đề thi trực tuyến tự chấm và email xác nhận tự động.'))
replace(332,341,H('F. Đăng ký lớp và học phí',3)+B('Checkout: Xem lớp, học phí, gửi ảnh hồ sơ, nguyện vọng giáo viên và ghi chú; chọn cách thanh toán.',
 'Ghi dữ liệu: Confirm tạo Registration và Payment. VietQR chờ đối soát; VNPay/MoMo hiện là lựa chọn mô phỏng.',
 'Cần hoàn thiện: Kiểm tra trùng đăng ký, sĩ số và transaction ở bước xác nhận; không mặc định coi ảnh QR là bằng chứng đã thu tiền.'))
replace(344,350,H('G. Biên lai học phí',3)+B('Hiển thị: Mã biên lai, học viên, lớp, số tiền và thời điểm thu; hỗ trợ in hoặc lưu PDF bằng trình duyệt.',
 'Kiểm soát: Truy vấn hóa đơn theo người dùng và áp dụng CSS khi in. Biên lai dùng trong quản trị nội bộ, không phải tích hợp hóa đơn thuế.'))
replace(352,358,H('H. Lớp của tôi và thời khóa biểu',3)+B('Lớp học: Xem đăng ký, chương trình, giảng viên và trạng thái liên quan.',
 'Lịch tuần: Theo dõi ca học, phòng và lịch kiểm tra đầu vào; chuyển tuần để tra cứu.',
 'Dữ liệu: StudentController xác định học viên từ phiên và truy vấn các bản ghi liên quan.'))
replace(360,363,H('I. Lịch sử học phí',3)+B('Thông tin: Mã học phí, số tiền, ngày, phương thức và trạng thái thanh toán.',
 'Tra cứu: Liên kết đến mẫu biên lai; số liệu chỉ phản ánh bản ghi đã lưu trong hệ thống.'))
replace(365,370,H('J. Hồ sơ học viên',3)+B('Cập nhật: Họ tên, số điện thoại, ngày sinh, địa chỉ và ảnh hồ sơ.',
 'Lưu ảnh: Kiểm tra tệp hợp lệ và ghi đường dẫn ảnh tại hồ sơ, tài khoản. Điểm xếp lớp được xem tại lịch sử kiểm tra, không phải một bảng điểm bốn kỹ năng trong hồ sơ.'))
replace(373,380,H('Bảng điều khiển quản trị',3)+B('Phạm vi: Area Admin yêu cầu phiên Admin; sidebar dẫn đến các nhóm đào tạo, nhân sự và tài chính.',
 'Thống kê: Tổng hợp các truy vấn liên quan đến học phí, lớp và người dùng; truyền dữ liệu sang biểu đồ Chart.js.',
 'Diễn giải: Các con số là dữ liệu trình diễn, cần kiểm chứng truy vấn trước khi dùng làm báo cáo quản trị thực tế.'))
replace(382,388,H('Quản lý banner',3)+B('Danh sách: Xem ảnh, tiêu đề, liên kết, thứ tự và trạng thái hiển thị.',
 'Thao tác: Tạo, sửa, bật/tắt hoặc xóa mềm; ảnh tải lên được lưu trong thư mục banners.'))
replace(390,396,H('Quản lý chương trình và lớp',3)+B('Chương trình: Thêm, sửa, thay đổi trạng thái tuyển sinh, cập nhật thời lượng và học phí.',
 'Lớp: Tổ chức lịch, phòng, thời gian và phân công giáo viên; điều phối học viên theo đăng ký.',
 'Ràng buộc: MaxStudents là thông tin sĩ số tối đa; cần bảo đảm kiểm tra giới hạn tại mọi thao tác thêm học viên.'))
replace(398,401,H('Quản lý ghi danh và học phí',3)+B('Ghi danh: Xem đơn, xếp hoặc chuyển lớp; cập nhật Pending, Confirmed, Cancelled theo nghiệp vụ.',
 'Học phí: Admin đối soát trước khi xác nhận thu; bản ghi được dùng để in biên lai.',
 'Tư vấn: Tiếp nhận thông tin công khai và đổi trạng thái xử lý; chưa có chức năng gửi thư trả lời tích hợp.'))
replace(403,405,H('Quản lý giáo viên và học viên',3)+B('Giáo viên: Tạo tài khoản, sửa bằng cấp, chuyên môn, ảnh và xóa mềm; chưa có action khóa/mở riêng.',
 'Học viên: Xem, sửa thông tin và khóa/mở tài khoản theo chức năng hiện có.'))
replace(407,416,H('Thùng rác và xóa mềm',3)+B('Xóa mềm: Các đối tượng hỗ trợ được đánh dấu IsDeleted và ghi thời điểm DeletedAt.',
 'Khôi phục: Đưa bản ghi trở lại phạm vi dữ liệu đang hoạt động.',
 'Xóa vĩnh viễn: Kiểm tra bản ghi phụ thuộc trước khi xóa; thao tác này không thể khôi phục bằng luồng thông thường.'))
replace(419,421,H('Bảng điều khiển giáo viên',3)+B('Phạm vi: Area Teacher cung cấp lớp phụ trách, thông tin cá nhân và các chỉ số hỗ trợ công việc.',
 'Theo dõi: Xem lớp, lịch dạy và kiểm tra được phân công; số liệu cần được hiểu theo phạm vi truy vấn của từng thẻ thống kê.'))
replace(423,424,H('Theo dõi lớp và học viên',3)+B('Tra cứu: Xem lớp được phân công và danh sách học viên tương ứng.',
 'Điểm danh: Hiện có checkbox giao diện; chưa lưu chuyên cần theo buổi hoặc các trạng thái đi trễ, vắng có phép.'))
replace(426,427,H('Chấm kiểm tra xếp lớp',3)+B('Phân công: Giáo viên chỉ xem các bài kiểm tra được giao theo danh sách.',
 'Kết quả: Nhập điểm và RecommendedLevel, cập nhật Completed. Phiên bản hiện tại không lưu bảng điểm riêng cho cả bốn kỹ năng.'))
replace(429,430,H('Tài liệu và phản hồi',3)+B('Tài liệu: Chọn lớp, nhập tiêu đề và tải tệp; danh sách có liên kết tải về và xóa.',
 'Phản hồi: Xem đánh giá học viên thuộc lớp phụ trách. Chưa có luồng tải học liệu riêng được hoàn thiện trong khu vực Student.'))
replace(433,439,H('Đăng nhập theo vai trò',3)+B('Biểu mẫu: Nhập email, mật khẩu và lựa chọn ghi nhớ.',
 'Xử lý: Kiểm tra tài khoản, trạng thái hoạt động, mật khẩu BCrypt; cấp cookie tương ứng và điều hướng theo vai trò.',
 'Giới hạn: Liên kết quên mật khẩu chưa chứng minh đã có quy trình đặt lại mật khẩu hoàn chỉnh.'))
replace(441,442,H('Đăng ký tài khoản học viên',3)+B('Dữ liệu: Họ tên, email, số điện thoại, mật khẩu và xác nhận mật khẩu.',
 'Kết quả: Kiểm tra email, băm mật khẩu, tạo UserAccount vai trò Student và hồ sơ Student.'))
replace(444,446,H('Đổi mật khẩu và kiểm soát truy cập',3)+B('Đổi mật khẩu: Xác minh mật khẩu hiện tại trước khi lưu mã băm mới.',
 'Truy cập Admin: Với cookie riêng cho từng vai trò, người chưa có phiên Admin có thể được chuyển về đăng nhập; không mặc định mọi tình huống đều trả trang 403.'))

replace(449,461,H('4.3.1 Mục tiêu và phương pháp kiểm tra',3)+B('Mục tiêu: Kiểm tra giao diện, luồng đăng nhập, điều hướng và đối chiếu các chức năng với mã nguồn.',
 'Quan sát thực tế: Đã mở 33 địa chỉ trang bằng các tài khoản mẫu, nhận HTTP 200 và chụp giao diện; đăng nhập được ở ba vai trò.',
 'Truy cập trái vai trò: Khách hoặc Student mở Admin/Dashboard được chuyển đến trang đăng nhập Admin trong cấu hình cookie hiện tại.',
 'Giới hạn: Chưa kiểm thử tải, chưa đo độ trễ và chưa chạy đầy đủ các thao tác ghi/xóa dữ liệu. Các bảng dưới là kế hoạch kiểm thử cần thực hiện trên dữ liệu riêng.'))
replace(470,477,H('Kết chương 4')+P('Chương 4 trình bày môi trường, các màn hình theo vai trò và kế hoạch kiểm thử. Kết quả quan sát xác nhận khả năng mở các trang trong phiên kiểm tra; chưa đủ căn cứ kết luận toàn bộ nghiệp vụ đạt 100% hoặc hệ thống sẵn sàng vận hành thực tế.'))
replace(480,512,H('1. Kết quả đạt được')+B('Kiến trúc: Xây dựng ứng dụng ASP.NET Core MVC, dùng Areas để tổ chức cổng Admin và Teacher.',
 'Dữ liệu: Thiết kế mô hình 14 bảng nghiệp vụ, quan hệ và ràng buộc trên SQL Server.',
 'Chức năng: Triển khai tra cứu, hồ sơ, ghi danh, lịch học, học phí, đặt lịch kiểm tra, tài liệu, phản hồi và các mục quản trị.',
 'Tài liệu: Bổ sung sơ đồ use case, đặc tả nghiệp vụ, mô hình bảng dữ liệu và ảnh giao diện đối chiếu.')+
 H('2. Hạn chế')+B('Nghiệp vụ: Chưa hoàn thiện điểm danh theo buổi, thi trực tuyến tự chấm, tải học liệu riêng cho học viên và gửi email.',
 'Thanh toán: VietQR chưa tự đối soát ngân hàng; VNPay/MoMo cần được tách rõ khỏi giao dịch thật.',
 'Kiểm soát dữ liệu: Cần bổ sung kiểm tra sĩ số, đăng ký trùng, lịch trùng, quyền sở hữu bản ghi và transaction.',
 'Đánh giá: Chưa có kết quả kiểm thử tải hoặc đo hiệu năng đủ căn cứ.')+
 H('3. Hướng phát triển')+B('Ưu tiên trước: Hoàn thiện quyền truy cập từng bản ghi, tính nhất quán của ghi danh/học phí và kiểm thử nghiệp vụ tự động.',
 'Thanh toán: Tích hợp cổng có xác thực chữ ký và IPN, nhật ký đối soát và xử lý giao dịch lặp.',
 'Vận hành: Bổ sung sao lưu, nhật ký thao tác, môi trường kiểm thử và quy trình phục hồi dữ liệu.',
 'Mở rộng sau: Lớp học trực tuyến, ứng dụng di động và phân tích dữ liệu khi các luồng cốt lõi đã ổn định.'))

# Shorten redundant captions and normalize numbering consistently across figures.
count=0
for p in d.paragraphs:
    if p.style.name=='HITCFigureCaption':
        if not p.text.strip():continue
        # Group captions duplicated after two individually captioned screenshots add no new information.
        if any(norm(p.text)==norm(clean(o.paragraphs[i].text))for i in [359,397,402,406,425,431]):
            p._p.getparent().remove(p._p);continue
        text=re.sub(r'^(?:Hình|Hi\u0300nh)\s*[^:]*:\s*','',p.text.strip(),flags=re.I)
        text=text.replace('Biểu đồ Use Case tổng quan hệ thống Dang ky khoa hc','Sơ đồ use case tổng quát hệ thống')
        text=text.replace('Giao diện Hồ sơ cá nhân và Kết quả thi xếp lớp của học viên','Hồ sơ cá nhân học viên').replace('Giao diện Đổi mật khẩu và Thông báo từ chối truy cập 403','Giao diện đổi mật khẩu')
        count+=1;p.text=f'Hình {count}. {text}'
        p.paragraph_format.space_after=Pt(5)
        p.paragraph_format.keep_with_next=False
        for r in p.runs:r.bold=False;r.font.name='Times New Roman';r.font.size=Pt(11)

# Condense the newly added chapter 3 into bullets without changing its detailed scope.
for p in list(d.paragraphs):
    if p.text.startswith('3.7 Kết chương 3'):
        following=p._p.getnext();p._p.getparent().remove(p._p)
        if following is not None and following.tag==qn('w:p'):following.getparent().remove(following)
    if p.text.startswith(('Tác nhân:','Điều kiện trước:','Luồng xử lý:','Kết quả:')):
        pr=p._p.get_or_add_pPr();old=pr.find(qn('w:numPr'))
        if old is not None:pr.remove(old)
        np=el('w:numPr');np.append(el('w:ilvl',val=0));np.append(el('w:numId',val=77));pr.append(np)
        p.paragraph_format.left_indent=Cm(.5);p.paragraph_format.first_line_indent=Cm(-.25)
        p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(4)

# Keep all screenshots and diagrams; tighten oversized original images to fit report pages.
for shape in d.inline_shapes:
    scale=min(1,Cm(15.2)/shape.width,Cm(12)/shape.height)
    shape.width=int(shape.width*scale);shape.height=int(shape.height*scale)

# Revise old test assertions into a concise, honest test plan.
statuses=['Cần chạy lại','Đã quan sát đăng nhập','Cần chạy lại','Đã quan sát chuyển hướng','Đã quan sát các phiên']
for ti,t in enumerate(d.tables):
    if ti==0:
        vals=[
          'Xem chương trình, lớp mở; gửi tư vấn và đăng ký tài khoản.',
          'Quản lý hồ sơ; xem lớp, lịch, học phí, biên lai và kết quả kiểm tra.',
          'Theo dõi lớp; quản lý tài liệu; nhập kết quả kiểm tra được giao; xem lương.',
          'Quản lý đào tạo, người dùng, ghi danh, học phí và các mục quản trị.']
        for row,text in zip(t.rows[1:],vals):row.cells[1].text=text
    if ti==1:
        t.rows[0].cells[0].text='SQL Server LocalDB — cơ sở dữ liệu EnglishCenterDb; cấu hình kết nối tại appsettings.json.'
    if ti==2:
        t.rows[0].cells[-1].text='Vai trò trong dự án'
        desc=['Nền tảng MVC và các Areas.','Truy vấn LINQ, ánh xạ dữ liệu và migrations.','Băm, đối chiếu mật khẩu.','Duy trì phiên riêng theo vai trò.','Phụ thuộc đã khai báo; dịch vụ gửi thư còn trống.','Kết xuất giao diện từ dữ liệu.','Lưới và các thành phần giao diện.','Biểu tượng và phông chữ.','Giao diện mô tả và thử endpoint trong môi trường phát triển.']
        for row,text in zip(t.rows[1:],desc):row.cells[-1].text=text
    if ti>=3:
        # Keep the original scenario IDs and test intent, while removing unsupported PASS claims.
        headers=[c.text for c in t.rows[0].cells]
        actual=next((i for i,x in enumerate(headers)if'Kết quả thực tế'in x),None)
        evaluation=next((i for i,x in enumerate(headers)if'Đánh giá'in x),None)
        if actual is not None:t.rows[0].cells[actual].text='Trạng thái kiểm tra'
        for ri,row in enumerate(t.rows[1:]):
            ident=row.cells[0].text
            if actual is not None:
                value='Chưa chạy lại; đối chiếu mã nguồn trước khi đánh giá.'
                if 'TC-AUTH-02'in ident:value='Đã quan sát đăng nhập bằng tài khoản mẫu.'
                if 'TC-AUTH-04'in ident:value='Đã quan sát chuyển về trang đăng nhập Admin khi thiếu phiên Admin.'
                if 'TC-AUTH-05'in ident:value='Đã mở các trang ở ba phiên vai trò.'
                row.cells[actual].text=value
            if evaluation is not None:row.cells[evaluation].text='Theo phạm vi nêu trên'
            # Remove device timings and claims not part of the implemented functionality.
            for c in row.cells:
                c.text=c.text.replace('dịch vụ MailKit gửi email xác nhận lịch thi tự động cho học viên.','lưu thông tin chờ phân công lịch và người chấm.').replace('học viên trong lớp có thể tải về.','giáo viên có liên kết tải về.').replace('Hệ thống lưu trữ dữ liệu điểm danh, cập nhật tỷ lệ chuyên cần của học viên trong lớp.','Chức năng cần bổ sung lưu chuyên cần; hiện mới có checkbox giao diện.')
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(2)
                p.paragraph_format.keep_with_next=False
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10.5)

def compact_table(headers,rows,widths):
    t=d.add_table(rows=1,cols=len(headers));t.autofit=False
    t._tbl.tblPr.append(el('w:tblW',w=9071,type='dxa'));t._tbl.tblPr.append(el('w:jc',val='left'))
    for i,x in enumerate(headers):t.rows[0].cells[i].text=x
    for values in rows:
        for c,v in zip(t.add_row().cells,values):c.text=v
    for ci,col in enumerate(t.columns):col.width=Cm(widths[ci])
    for ri,row in enumerate(t.rows):
        row._tr.get_or_add_trPr().append(el('w:cantSplit'))
        if ri==0:row._tr.get_or_add_trPr().append(el('w:tblHeader'))
        for ci,c in enumerate(row.cells):
            c.width=Cm(widths[ci]);pr=c._tc.get_or_add_tcPr()
            border=el('w:tcBorders')
            for side in ['top','bottom','left','right']:border.append(el('w:'+side,val='single',sz=4,color='D9D9D9'))
            pr.append(border);pr.append(el('w:vAlign',val='center'))
            margins=el('w:tcMar')
            for side in ['top','bottom','left','right']:margins.append(el('w:'+side,w=65,type='dxa'))
            pr.append(margins)
            if ri==0:pr.append(el('w:shd',fill='E8EEF5'))
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3);p.paragraph_format.line_spacing=1.1
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(11);r.bold=ri==0
    return t

plans=[
 [('AUTH-01','Đăng ký email đã có','Báo email đã được sử dụng; không tạo trùng.','Chưa chạy lại'),
  ('AUTH-02','Đăng nhập đúng','Cấp phiên và điều hướng theo vai trò.','Đã quan sát tài khoản mẫu'),
  ('AUTH-03','Mật khẩu sai','Từ chối xác thực và báo lỗi.','Chưa chạy lại'),
  ('AUTH-04','Student/khách mở Admin','Chặn nội dung quản trị; chuyển đến đăng nhập Admin.','Đã quan sát chuyển hướng'),
  ('AUTH-05','Các phiên vai trò','Các cookie được chọn đúng ngữ cảnh.','Đã mở trang ở ba phiên')],
 [('CUST-01','Gửi tư vấn','Lưu Pending khi dữ liệu hợp lệ; báo kết quả.','Chưa chạy lại'),
  ('CUST-02','Đặt lịch đầu vào','Ngày hợp lệ; lưu lịch chờ phân công.','Chưa chạy lại'),
  ('CUST-03','Đăng ký lớp','Tạo đơn và học phí đúng học viên/lớp.','Chưa chạy lại'),
  ('CUST-04','Lớp đã đủ sĩ số','Từ chối ghi danh vượt giới hạn tại bước ghi.','Cần hoàn thiện mã và kiểm thử'),
  ('CUST-05','Đối soát và biên lai','Chỉ xác nhận thu khi có căn cứ; biên lai đúng dữ liệu.','Chưa chạy lại giao dịch')],
 [('TEACH-01','Điểm danh theo buổi','Cần thiết kế lưu ngày, buổi và trạng thái chuyên cần.','Chưa hiện thực đầy đủ'),
  ('TEACH-02','Chấm bài được giao','Lưu điểm/cấp độ đúng bài và đúng người chấm.','Chưa chạy lại thao tác ghi'),
  ('TEACH-03','Tải tài liệu lên','Lưu tệp và liên kết đúng lớp; kiểm tra quyền sở hữu.','Chưa chạy lại thao tác ghi')],
 [('ADM-01','Thêm banner','Lưu ảnh, trạng thái và thứ tự; hiển thị theo cấu hình.','Chưa chạy lại'),
  ('ADM-02','Xóa mềm chương trình','Đánh dấu xóa; không xóa ngay dữ liệu gốc.','Chưa chạy lại'),
  ('ADM-03','Khôi phục dữ liệu','Bỏ trạng thái xóa và kiểm tra liên kết dữ liệu.','Chưa chạy lại'),
  ('ADM-04','Xóa vĩnh viễn','Chỉ xóa đối tượng hợp lệ và có kiểm tra phụ thuộc.','Chưa chạy lại'),
  ('ADM-05','Xóa khi còn liên kết','Từ chối hoặc xử lý liên kết theo quy tắc được thiết kế.','Chưa chạy lại')]
]
old_tests=list(d.tables)[3:7]
for old,rows in zip(old_tests,plans):
    t=compact_table(['Mã ca','Tình huống','Kết quả cần kiểm tra','Trạng thái'],rows,[2,3.4,6.4,4.2])
    old._tbl.addprevious(t._tbl);old._tbl.getparent().remove(old._tbl)

def insert_before_prefix(prefix,fn):
    anchor=next(p for p in d.paragraphs if p.style.name.startswith('Heading')and p.text.startswith(prefix))
    before=set(d.element.body);fn()
    for x in [x for x in d.element.body if x not in before and x.tag!=qn('w:sectPr')]:anchor._p.addprevious(x)

def data_details():
    p=newp('3.4.4 Từ điển dữ liệu chính','h3');p.paragraph_format.page_break_before=False
    newp('Bảng sau tập trung các trường dùng để nhận diện và liên kết nghiệp vụ. PK là khóa chính; FK là khóa ngoại. Trường có thể để trống được nêu tại cột ràng buộc để phân biệt dữ liệu bắt buộc với thông tin chờ phân công.','p')
    compact_table(['Bảng','Khóa và trường tiêu biểu','Ý nghĩa và ràng buộc'],[
      ('UserAccount','PK AccountId; Email, PasswordHash, Role','Email duy nhất; Role là Student, Teacher hoặc Admin.'),
      ('Student','PK StudentId; FK AccountId; PhoneNumber, DateOfBirth','Hồ sơ học viên; tài khoản liên kết duy nhất.'),
      ('Teacher','PK TeacherId; FK AccountId; Specialization, Degree','Hồ sơ chuyên môn của giáo viên.'),
      ('Program','PK ProgramId; ProgramName, Level, TuitionFee','Chương trình học và mức học phí niêm yết.'),
      ('Class','PK ClassId; FK ProgramId, TeacherId','Lớp thuộc chương trình; TeacherId có thể trống.'),
      ('Registration','PK RegistrationId; FK StudentId, ClassId, DesiredTeacherId','Ghi danh học viên vào lớp; nguyện vọng giáo viên là tùy chọn.'),
      ('Payment','PK PaymentId; FK RegistrationId; Amount, Status','Tối đa một học phí cho mỗi đơn; theo dõi tình trạng thu.'),
      ('PlacementTest','PK TestId; FK StudentId, EvaluatedByTeacherId','Lịch, điểm, cấp độ; có thể chưa phân công người chấm.'),
      ('ClassSchedule','PK ScheduleId; FK ClassId; DayOfWeek, StartTime, EndTime','Một lớp có nhiều ca học.'),
      ('ClassDocument','PK DocumentId; FK ClassId; Title, FilePath','Liên kết học liệu với lớp và vị trí lưu tệp.'),
      ('CourseFeedback','PK FeedbackId; FK StudentId, ClassId; Rating, Comment','Đánh giá gắn với người gửi và lớp được nhận xét.'),
      ('TeacherSalary','PK SalaryId; FK TeacherId; Month, Year, TotalSalary','Kỳ lương, các thành phần và trạng thái chi trả.'),
      ('Consultation','PK ConsultationId; ContactName, Question, Status','Thông tin liên hệ và trạng thái xử lý tư vấn.'),
      ('Banner','PK BannerId; ImageUrl, LinkUrl, DisplayOrder','Nội dung hiển thị và thứ tự quảng bá.')],[3.2,6.1,6.7])
    newp('3.4.5 Các quan hệ và hành vi khi xóa','h3').paragraph_format.page_break_before=True
    compact_table(['Quan hệ','Bội số','Quy tắc dữ liệu'],[
      ('Tài khoản – Hồ sơ','1 – 0..1','Student và Teacher tham chiếu tài khoản; xóa tài khoản có thể kéo theo hồ sơ theo cấu hình.'),
      ('Program – Class','1 – N','Lớp tham chiếu chương trình; Restrict ngăn xóa khi còn lớp liên quan.'),
      ('Teacher – Class','0..1 – N','Lớp có thể chưa có giáo viên; SetNull giữ lớp khi liên kết giáo viên bị xóa.'),
      ('Student/Class – Registration','1 – N','Restrict bảo vệ đơn ghi danh khi còn tham chiếu tới học viên hoặc lớp.'),
      ('Registration – Payment','1 – 0..1','RegistrationId trong Payment là duy nhất; bản ghi học phí theo đơn.'),
      ('Class – Schedule/Document','1 – N','Ca học và tài liệu thuộc lớp; được cấu hình Cascade theo lớp.'),
      ('Student/Teacher – PlacementTest','1 – N; 0..1 – N','Bài kiểm tra thuộc học viên; người chấm là liên kết tùy chọn.'),
      ('Student/Class – Feedback','1 – N','Phản hồi thuộc người gửi và lớp; cần kiểm tra quyền gửi theo đăng ký.'),
      ('Teacher – TeacherSalary','1 – N','Một giáo viên có nhiều kỳ lương; điều kiện nghiệp vụ cần kiểm tra trước khi xóa.')],[5.1,2.4,8.5])
    newp('Xóa mềm: IsDeleted và DeletedAt giữ thông tin đối tượng để phục hồi; đây là thao tác nghiệp vụ, khác với hành vi khóa ngoại khi xóa vật lý.','b')
    newp('Nhất quán: Các thao tác liên quan nhiều bảng cần được xử lý trong transaction và có thông báo rõ khi ràng buộc không cho phép thực hiện.','b')
insert_before_prefix('3.5 Ràng buộc',data_details)

def controls():
    newp('3.5.1 Trạng thái và điều kiện chuyển bước','h3').paragraph_format.page_break_before=True
    compact_table(['Đối tượng','Trạng thái chính','Điều kiện cần kiểm soát'],[
      ('Đơn đăng ký','Pending, Confirmed, Cancelled','Kiểm tra lớp, học viên, sĩ số và trùng đăng ký trước khi xác nhận hoặc chuyển lớp.'),
      ('Học phí','Pending, Paid','Admin đối soát trước khi xác nhận; giao dịch mô phỏng không được coi là thu tiền thật.'),
      ('Kiểm tra đầu vào','Pending, Completed','Phân công đúng người chấm; điểm và cấp độ được nhập trước khi hoàn tất.'),
      ('Lớp học','Planning, InProgress, Completed, Cancelled','Kiểm tra ngày bắt đầu/kết thúc, lịch, phòng và giáo viên khi lập hoặc điều chỉnh lớp.'),
      ('Lương','Pending, Paid','Đúng giáo viên, tháng/năm và thành phần tính; xác nhận chi trả là thao tác của Admin.'),
      ('Tư vấn','Pending, Replied','Đổi trạng thái sau xử lý; trạng thái Replied không đồng nghĩa đã gửi email từ website.')],[3.0,4.4,8.6])
    for s in ['Tạo đơn và học phí: Hoàn tất cả hai hoặc hoàn tác toàn bộ khi phát sinh lỗi; tránh đơn không có khoản học phí tương ứng.',
      'Xác nhận lặp: Cần kiểm tra trạng thái hiện tại để tránh cộng doanh thu hoặc xử lý cùng một giao dịch nhiều lần.',
      'Điều chỉnh lớp: Kiểm tra sĩ số và xung đột lịch ở phía máy chủ, kể cả khi giao diện đã ẩn lựa chọn không phù hợp.',
      'Dữ liệu đã xóa: Kiểm tra trạng thái đối tượng được tham chiếu trước khi khôi phục, sửa hoặc tạo quan hệ mới.']:newp(s,'b')
    newp('3.5.2 Phân quyền theo vai trò và từng bản ghi','h3').paragraph_format.page_break_before=True
    compact_table(['Tác nhân','Phạm vi dữ liệu','Kiểm tra trước khi thay đổi'],[
      ('Khách','Chương trình, lớp và thông tin công khai.','Kiểm tra dữ liệu biểu mẫu tư vấn/đăng ký; không cấp quyền quản trị.'),
      ('Học viên','Hồ sơ, đăng ký, học phí và kiểm tra của chính mình.','Đối chiếu AccountId/StudentId từ phiên; không tin ID do người dùng tự gửi.'),
      ('Giáo viên','Lớp và bài kiểm tra được phân công; bảng lương của mình.','Đối chiếu TeacherId ở cả thao tác xem, tải lên, sửa, xóa và chấm điểm.'),
      ('Admin','Các nghiệp vụ quản trị theo chức năng được cấp.','Xác thực hành động, dữ liệu liên kết và trạng thái; ghi nhận thao tác quan trọng.')],[2.6,6.0,7.4])
    for s in ['Hai lớp kiểm tra: Authorize giới hạn vai trò; truy vấn có điều kiện sở hữu giới hạn bản ghi. Có quyền vào màn hình chưa đủ để sửa mọi ID.',
      'Tệp tải lên: Kiểm tra loại, kích thước, tên lưu và quyền đối với lớp; tránh dùng tên tệp người gửi làm định danh tin cậy.',
      'Dữ liệu biểu mẫu: Kiểm tra ModelState, khoảng điểm, mức phí, ngày và tham chiếu hợp lệ trước khi SaveChanges.',
      'Theo dõi vận hành: Cần nhật ký thao tác, sao lưu và quy trình phục hồi; không suy ra mức độ an toàn chỉ từ việc có cookie hoặc BCrypt.',
      'Phạm vi đánh giá: Các quy tắc trên là yêu cầu kiểm soát để hoàn thiện; mức đã triển khai được nêu rõ ở mục 3.6 và kế hoạch kiểm thử.']:newp(s,'b')
insert_before_prefix('3.6 Đối chiếu',controls)

# Keep the last data-dictionary row with the rest of its compact table.
for t in d.tables:
    if len(t.rows[0].cells)>1 and 'Khóa và trường tiêu biểu'in t.rows[0].cells[1].text:
        for row in t.rows:
            for c in row.cells:
                for side in c._tc.get_or_add_tcPr().iter():
                    if side.tag in [qn('w:top'),qn('w:bottom')]and side.getparent().tag==qn('w:tcMar'):side.set(qn('w:w'),'35')
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(2)
                    for r in p.runs:r.font.size=Pt(10.5)

for p in d.paragraphs:
    if p.style.name=='Title':
        for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(18)

# Fix the source's duplicated test-section label and connect references to the discussion.
seen_student_test=False
for p in d.paragraphs:
    if p.text.startswith('2. Kiểm thử Phân hệ Khách hàng'):
        if seen_student_test:p.text='3. Kiểm thử phân hệ giáo viên'
        seen_student_test=True
    elif p.text.startswith('3. Kiểm thử Phân hệ Quản trị viên'):p.text='4. Kiểm thử phân hệ quản trị viên'
    citations=[('VUS được tham khảo','[1]'),('Phân nhóm chương trình, thông tin giáo viên','[2]'),
      ('Model: Các thực thể','[3]'),('Entity Framework Core: Ánh xạ','[4]'),
      ('Cookie và claims:','[5], [6]'),('BCrypt: Băm mật khẩu','[9]'),
      ('Bootstrap 5: Cung cấp','[7]'),('JavaScript và Chart.js:','[8]'),('Hiển thị QR: Checkout','[10]')]
    for phrase,cite in citations:
        if phrase in p.text:p.add_run(' '+cite)

# Refresh the TOC for two levels; a dedicated caption style keeps the figure list automatic.
for x in d.element.iter(qn('w:instrText')):
    if 'TOC 'in(x.text or'')and '\\o'in(x.text or''):x.text=' TOC \\o "1-2" \\h \\z \\u '
d.core_properties.title='Báo cáo đồ án HITC English bản hoàn thiện khoảng 50 trang'
out=R/'refined-50-draft.docx';d.save(out)
(R/'refinement-log.json').write_text(json.dumps({'source':str(SOURCE),'revised_blocks':changes,'figures':count,'tables':len(d.tables),'images':len(d.inline_shapes)},ensure_ascii=False,indent=2),encoding='utf8')
print(out);print('Revised blocks',len(changes),'figures',count,'images',len(d.inline_shapes))
