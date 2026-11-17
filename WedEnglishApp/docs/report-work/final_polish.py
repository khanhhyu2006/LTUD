from pathlib import Path
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy
import re,json,hashlib
R=Path('docs/report-work');d=Document('Bao_cao_LLUD_Hoan_thien_Chuong_3.docx');ps=list(d.paragraphs);edits=[]
def replace(p,t):
 old=p.text
 if old==t:return
 p.clear();p.add_run(t);edits.append({'old':old,'new':t})
def unnumber(p):
 pr=p._p.get_or_add_pPr();n=pr.find(qn('w:numPr'))
 if n is not None:pr.remove(n)
 n=OxmlElement('w:numPr');v=OxmlElement('w:numId');v.set(qn('w:val'),'0');n.append(v);pr.append(n)
def style(name,size=13,bold=False):
 s=d.styles[name] if name in d.styles else d.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
 s.base_style=d.styles['Normal'];s.font.name='Times New Roman';s.font.size=Pt(size);s.font.bold=bold;s.font.color.rgb=RGBColor(0,0,0)
 s.paragraph_format.space_after=Pt(6);s.paragraph_format.space_before=Pt(0);s.paragraph_format.line_spacing=1.12
 return s
style('FrontMatterHeading',14,True);style('NHKTableCaption',12,True);style('NHKFigureCaption',12);style('NHKSubFigureCaption',12)
style('ReportCode',9)
for name in ['NHKTableCaption','NHKFigureCaption','NHKSubFigureCaption']:
 d.styles[name].paragraph_format.keep_with_next=(name=='NHKTableCaption')
 d.styles[name].paragraph_format.keep_together=True
for name in ['Heading 1','Heading 2','Heading 3']:
 s=d.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0);s.font.size=Pt(14 if name=='Heading 1' else 13);s.font.bold=True
 s.paragraph_format.keep_with_next=True;s.paragraph_format.keep_together=True
# Targeted content edits preserve scope and paragraph locations.
fix={
162:'Nhu cầu học tiếng Anh phục vụ học tập và công việc đặt ra yêu cầu quản lý thông tin rõ ràng tại các trung tâm ngoại ngữ. Người học cần tra cứu chương trình, đăng ký kiểm tra đầu vào, gửi nguyện vọng lịch học và theo dõi học phí trên website. Với trung tâm, các thao tác này cần được liên kết để hạn chế nhập liệu nhiều lần và thuận tiện khi xếp lớp.',
167:'Thiếu công cụ tiếp nhận yêu cầu kiểm tra đầu vào, tổ chức phòng thi và lưu kết quả để tư vấn trình độ phù hợp.',
168:'Đề tài lựa chọn ASP.NET Core MVC trên .NET 8, ngôn ngữ C#, Entity Framework Core và SQL Server. Các công nghệ này phù hợp với ứng dụng web quản lý dữ liệu quan hệ và cho phép tổ chức giao diện, xử lý yêu cầu và truy cập dữ liệu trong cùng dự án.',
169:'Từ những yêu cầu trên, đề tài “Xây dựng website quản lý trung tâm ngoại ngữ NHK English times” được thực hiện để hỗ trợ tư vấn, đăng ký khóa học, xếp lớp, quản lý lịch học và đối soát học phí. Báo cáo trình bày thiết kế, chức năng đã triển khai và những phần cần tiếp tục hoàn thiện.',
171:'Mục tiêu của đề tài là xây dựng ứng dụng web quản lý trung tâm ngoại ngữ theo mô hình ASP.NET Core MVC. Ứng dụng cung cấp khu vực sử dụng theo vai trò, lưu dữ liệu tập trung và hỗ trợ các bước từ đăng ký nguyện vọng đến xếp lớp, theo dõi lịch và học phí.',
180:'Hướng dẫn đóng học phí: Hiển thị số tiền, nội dung chuyển khoản và mã VietQR theo đơn đăng ký, hoặc hướng dẫn đóng tại trung tâm. Admin đối soát chứng từ rồi xác nhận khoản thu; quét mã không tự làm thay đổi trạng thái học phí.',
186:'Chấm kiểm tra đầu vào: Nhập điểm và cấp độ đề xuất cho thí sinh trong ca thi được phân công. Phiên bản hiện tại chưa có bảng điểm quá trình riêng cho từng khóa học.',
192:'Thống kê quản trị: Bảng điều khiển dùng Chart.js để minh họa doanh thu và cơ cấu chương trình. Tổng khoản thu đã xác nhận được lấy từ dữ liệu; chuỗi tháng và tỷ trọng trên một số biểu đồ còn là dữ liệu mẫu, cần hoàn thiện trước khi dùng cho báo cáo vận hành.',
199:'Phạm vi nghiệp vụ: Tư vấn tuyển sinh, đăng ký kiểm tra đầu vào, tổ chức ca thi, ghi danh theo nguyện vọng, xếp lớp, lập lịch học, phân công giáo viên và theo dõi học phí tại một trung tâm ngoại ngữ.',
201:'Môi trường phát triển: ASP.NET Core MVC (.NET 8), C#, Razor Views, HTML, CSS, JavaScript và Bootstrap 5. Bố cục được điều chỉnh theo kích thước màn hình; mức độ tương thích cần được kiểm tra trên các thiết bị dự kiến sử dụng.',
205:'Về thanh toán: Ứng dụng hiển thị hướng dẫn VietQR theo số tài khoản, số tiền và mã đơn hoặc cho phép chọn đóng tại trung tâm. Admin kiểm tra chứng từ và xác nhận đã thu trước khi học viên in biên lai nội bộ. Chưa tích hợp callback ngân hàng để tự động đối soát.',
214:'Khảo sát giao diện và phân tích nghiệp vụ: Tham khảo các trang công khai của VUS, ILA và mô hình tổ chức lớp học để xác định nhóm thông tin cần trình bày. Phần khảo sát không bao gồm quyền truy cập hệ thống quản trị nội bộ của các đơn vị này.',
219:'Hiện thực mã nguồn: Sử dụng Visual Studio và Visual Studio Code để xây dựng ứng dụng C#. Cơ sở dữ liệu được quản lý bằng EF Core cùng các script SQL nâng cấp; dữ liệu mẫu phục vụ chạy thử các nghiệp vụ.',
220:'Kiểm thử và đánh giá: Kiểm tra đăng nhập, phân quyền, đăng ký khóa học, xếp lớp, lập lịch, tổ chức ca thi và tư vấn trên dữ liệu thử. Các bảng kiểm thử phân biệt tình huống đã quan sát với ca chưa chạy lại; kết quả không thay thế kiểm thử tải hoặc đánh giá bảo mật chuyên sâu.',
224:'Ở mô hình quản lý thủ công, thông tin đăng ký, thu học phí và lịch giảng dạy thường được ghi trong sổ hoặc các bảng tính riêng. Khi số lớp tăng, cách lưu trữ phân tán có thể dẫn đến những khó khăn sau:',
228:'Website quản lý tập trung được đề xuất để hạn chế các vấn đề trên:',
235:'Hệ thống có bốn nhóm người sử dụng. Trong đó, Student, Teacher và Admin là ba vai trò tài khoản; Guest là người truy cập chưa đăng nhập:',
241:'Phần khảo sát tham khảo giao diện công khai của VUS (Anh văn Hội Việt Mỹ) và ILA Vietnam qua các hình trong tài liệu ban đầu [1], [2]. Nhận xét dưới đây phục vụ lựa chọn bố cục và cách giới thiệu khóa học, không đánh giá hệ thống quản trị nội bộ của hai đơn vị.',
245:'Hình 1. Trang chủ VUS',248:'Bố cục trang chủ: Khu vực banner, nhóm khóa học và nút tư vấn được đặt rõ ràng trong hình khảo sát. Báo cáo chưa đo tốc độ tải hoặc đánh giá SEO của website.',
251:'Tiện ích hỗ trợ người học: Các liên kết kiểm tra trình độ và tư vấn gợi ý cách tổ chức điểm vào cho người dùng mới; chức năng nội bộ không nằm trong phạm vi khảo sát.',
253:'Thông tin học phí: Hình khảo sát chưa thể hiện đủ học phí từng chương trình, nên người xem cần tìm thêm thông tin hoặc liên hệ tư vấn để so sánh.',
258:'Hình 2. Trang chủ ILA Vietnam',
259:'Mô tả hình ảnh: Trang chủ ILA trong hình khảo sát ưu tiên hình ảnh lớp học, các chương trình đào tạo và thông tin cơ sở. Cách trình bày này giúp phụ huynh và người học tiếp cận thông tin trước khi liên hệ tư vấn.',
263:'Nội dung giới thiệu: Trang trình bày chương trình và phương pháp giảng dạy để người học tham khảo. Báo cáo không kiểm chứng chất lượng đào tạo từ nội dung quảng bá.',
265:'Giới hạn quan sát: Các điểm điều hướng trong hình khảo sát chủ yếu phục vụ tìm hiểu chương trình và gửi thông tin tư vấn; chưa có căn cứ kết luận toàn bộ website không hỗ trợ ghi danh trực tuyến.',
266:'Thanh toán: Phần giao diện được khảo sát chưa thể hiện đầy đủ quy trình thanh toán. Vì không thực hiện giao dịch, báo cáo không đánh giá các kênh thanh toán của đơn vị.',
276:'Hiển thị VietQR theo đơn đăng ký, kèm số tiền và nội dung chuyển khoản để hỗ trợ đối chiếu. Admin xác nhận khoản thu sau khi kiểm tra chứng từ.',
277:'Cung cấp chức năng xem và in biên lai học phí nội bộ (PrintReceipt); mẫu trình diễn không thay thế hóa đơn điện tử hoặc chứng từ được cơ quan có thẩm quyền chứng nhận.',
288:'Chương 1 xác định nhu cầu quản lý tập trung và phạm vi website NHK English times.',
289:'Các nội dung chính gồm:',291:'Phân tích nguy cơ trùng thông tin, xung đột phòng và khó đối soát khi sử dụng sổ sách, bảng tính riêng. Hệ thống đề xuất lưu tập trung đơn đăng ký, lớp, lịch và học phí; lưu chuyên cần theo buổi còn cần bổ sung.',
293:'Tham khảo cách giới thiệu khóa học và bố trí điểm liên hệ trên giao diện công khai của VUS, ILA. Các nhận xét không thay thế khảo sát vận hành thực tế tại trung tâm.',
295:'Đề xuất website NHK English times để tiếp nhận tư vấn, kiểm tra đầu vào, đăng ký nguyện vọng, xếp lớp, quản lý lịch dạy và đối soát học phí.',
297:'Xác định phạm vi sử dụng của khách, học viên, giáo viên và Admin. Hiệu quả tiết kiệm thời gian cần được đo khi có điều kiện triển khai thực tế.',
299:'2.1 Kiến trúc Client–Server và ASP.NET Core MVC',
301:'Ứng dụng vận hành theo mô hình Client–Server. Razor dựng phần lớn giao diện ở máy chủ; JavaScript cập nhật một số khu vực bằng dữ liệu JSON:',
303:'Phía Server: Kestrel hoặc IIS tiếp nhận yêu cầu HTTP/HTTPS, thực hiện kiểm tra nghiệp vụ và truy vấn SQL Server. Các action MVC trả giao diện Razor hoặc JSON tùy chức năng; dự án chưa có backend Web API độc lập.',
305:'ASP.NET Core MVC chia mã nguồn theo dữ liệu, giao diện và bộ điều khiển [3]:',
307:'Model: Các thực thể như Student, Teacher, CourseClass và Payment mô tả dữ liệu nghiệp vụ. ViewModel định dạng dữ liệu gửi tới giao diện hoặc nhận từ biểu mẫu.',
315:'ASP.NET Core trên .NET 8: Nền tảng web mã nguồn mở, hỗ trợ Dependency Injection trong Program.cs. Các dịch vụ được đăng ký với vòng đời phù hợp để controller có thể sử dụng qua hàm khởi tạo.',
316:'Entity Framework Core 8: Ánh xạ thực thể C# sang dữ liệu quan hệ và hỗ trợ truy vấn LINQ, theo dõi thay đổi, giao dịch và migrations [4]. Include/ThenInclude nạp dữ liệu liên quan; hiệu quả truy vấn vẫn phụ thuộc cách sử dụng và lượng dữ liệu. Dự án còn dùng script SQL để nâng cấp schema.',
317:'2.3 Công nghệ giao diện Razor Views, Bootstrap và JavaScript',
319:'Bootstrap 5 và CSS tùy chỉnh: Sử dụng lưới 12 cột và các thành phần Navbar, Card, Modal, Badge, Alert, Table để xây dựng bố cục theo kích thước màn hình [7]. Các bảng nhiều cột cần vùng cuộn và kiểm tra riêng trên màn hình nhỏ.',
322:'Chart.js được dùng tại trang quản trị để vẽ biểu đồ [8]. Một số chuỗi dữ liệu đang phục vụ minh họa; cần thay bằng truy vấn tổng hợp theo kỳ trước khi dùng làm báo cáo quản lý.',
325:'Microsoft SQL Server/LocalDB: Lưu trữ dữ liệu quan hệ, hỗ trợ giao dịch và các ràng buộc khóa chính, khóa ngoại, duy nhất, CHECK. Hành vi khi xóa được cấu hình theo từng quan hệ; không áp dụng Cascade cho mọi bảng.',
326:'Hướng dẫn chuyển khoản VietQR: Giao diện hiển thị QR kèm số tiền và nội dung theo mã đăng ký [10]. Người học thực hiện chuyển tiền qua ứng dụng ngân hàng; Admin kiểm tra chứng từ rồi cập nhật trạng thái thu trong hệ thống.',
328:'Cookie Authentication: Program.cs đăng ký ba lược đồ cookie cho Admin, Teacher và Student. RoleCookieRouter chọn lược đồ phù hợp theo khu vực truy cập; thông tin phiên được ASP.NET Core bảo vệ [5].',
329:'Claims và phân quyền theo vai trò: ClaimTypes.NameIdentifier, Name và Role nhận diện tài khoản. Authorize giới hạn các controller/action tương ứng [6]:',
333:'Băm mật khẩu bằng BCrypt: Hệ thống lưu chuỗi băm kèm salt thay cho mật khẩu dạng rõ [9]. BCrypt không thay thế giới hạn số lần đăng nhập, quản lý mật khẩu và bảo vệ phiên.',
349:'Chương 2 trình bày nền tảng công nghệ và cách áp dụng trong dự án.',350:'Những nội dung được sử dụng để triển khai gồm:',
352:'Client–Server và MVC phân chia giao diện, dữ liệu và điều phối yêu cầu. Việc tổ chức này hỗ trợ bảo trì nhưng vẫn cần tránh đưa quá nhiều quy tắc nghiệp vụ vào controller.',
355:'ASP.NET Core trên .NET 8 và C# hỗ trợ xây dựng ứng dụng web; DI và Areas được dùng để tổ chức dịch vụ và hai khu vực quản trị.',
356:'EF Core và SQL Server hỗ trợ truy vấn dữ liệu, giao dịch và kiểm tra quan hệ. Migrations cùng script SQL được sử dụng để quản lý thay đổi lược đồ.',
358:'Razor dựng HTML ở máy chủ. Một số tương tác dùng fetch để gửi, nhận JSON và cập nhật khu vực giao diện mà không tải lại toàn trang.',
359:'Bootstrap, Font Awesome và Plus Jakarta Sans cung cấp lưới bố cục, biểu tượng và phông chữ. Bảng dữ liệu và thanh điều hướng được điều chỉnh để sử dụng trên các kích thước màn hình đã kiểm tra.',
364:'Chương này trình bày tác nhân và đặc tả nghiệp vụ của NHK English times, cơ sở dữ liệu, luồng đăng ký và thanh toán, cùng cách tổ chức mã nguồn ASP.NET Core MVC. Các bảng và sơ đồ được đối chiếu với mô hình dữ liệu đang sử dụng.',
429:'Luồng xử lý: Xóa mềm cập nhật IsDeleted và DeletedAt. Admin xem mục đã xóa trong thùng rác, chọn khôi phục hoặc xóa vĩnh viễn. Trước khi xóa vật lý, hệ thống cần kiểm tra các quan hệ còn phụ thuộc.',
435:'Mô hình có 16 bảng nghiệp vụ phục vụ tài khoản, đào tạo, ghi danh, học phí, kiểm tra, tư vấn và quản trị. Sơ đồ tổng quát thể hiện các quan hệ; hai sơ đồ nhóm phía sau giúp đọc rõ nhóm đào tạo và nhóm hỗ trợ.',
478:'Khóa ngoại ghép (ClassId, ProgramId) tham chiếu Classes; khi ClassId NULL, đơn vẫn tham chiếu Programs qua ProgramId. DesiredTeacherId là cột tương thích dữ liệu cũ, hiện không có khóa ngoại vật lý trong cơ sở dữ liệu được đối chiếu, dù model còn khai báo thuộc tính điều hướng.',
520:'3.3.1 Biểu đồ hoạt động – Quy trình đăng ký khóa học',
550:'NHK English times sử dụng ASP.NET Core MVC trên .NET 8 trong dự án WedEnglishApp. Razor dựng giao diện ở máy chủ; Admin và Teacher được tổ chức bằng Areas. Mã nguồn phân chia trách nhiệm trình bày, điều phối, nghiệp vụ và truy cập dữ liệu.',
560:'Ứng dụng được phát triển và chạy thử trên Windows với .NET 8, SQL Server LocalDB và IIS Express/Kestrel. Phần này ghi nhận các công cụ, cấu hình và bước khởi tạo của dự án; chưa mô tả một môi trường production đã được nghiệm thu.',
569:'Visual Studio Code: Hỗ trợ chỉnh sửa giao diện tĩnh, kiểm tra mã nguồn và chạy lệnh CLI.',
571:'Kestrel và IIS Express: Phục vụ ứng dụng cục bộ theo các profile trong launchSettings.json. HTTPS dùng chứng chỉ phát triển; địa chỉ truy cập thực tế phụ thuộc profile được chọn.',
575:'Git: Theo dõi thay đổi mã nguồn trong quá trình phát triển. Sao lưu dữ liệu và quản lý thông tin cấu hình cần có quy trình riêng.',
596:'Các thành phần sau được sử dụng trong dự án. Phiên bản được đối chiếu từ tệp cấu hình gói và các tài nguyên giao diện:',
598:'Thứ tự chính trong Program.cs là phục vụ HTTPS và tệp tĩnh, định tuyến, xác thực, phân quyền, sau đó ánh xạ endpoint. Swagger được bật trong môi trường phát triển:',
599:'HTTPS và tệp tĩnh: UseHttpsRedirection chuyển hướng yêu cầu phù hợp sang HTTPS; UseStaticFiles phục vụ CSS, JavaScript và hình ảnh trong wwwroot.',
600:'Định tuyến: UseRouting đối sánh URL với các tuyến; bước này chạy sau cấu hình HTTPS và tệp tĩnh trong mã nguồn hiện tại.',
611:'Các màn hình công khai và cá nhân của học viên được trình bày theo thứ tự thao tác dưới đây.',
621:'2. Cách xử lý dữ liệu:',637:'2. Cách xử lý dữ liệu:',
646:'Action Index nhận search, level, minFee, maxFee và page; kết quả được phân trang theo sáu chương trình mỗi trang.',
647:'Truy vấn chỉ lấy chương trình đang hoạt động, chưa xóa; tìm từ khóa trong tên hoặc mô tả, lọc cấp độ và khoảng học phí trước khi phân trang.',
655:'Action Detail(int id) lấy chương trình hợp lệ và các lớp chưa xóa, có trạng thái Planning hoặc InProgress, chưa kết thúc; nạp lịch tuần để hiển thị tham khảo.',
652:'Trình bày mục tiêu, thời lượng, học phí và chuẩn đầu ra theo nội dung từng chương trình. Các mức điểm mục tiêu là thông tin của khóa học, không phải cam kết kết quả cho mọi học viên.',
671:'1. Giao diện đăng ký theo nguyện vọng (Views/Enrollment/Checkout.cshtml)',
684:'Biên lai nội bộ hiển thị mã #PAY-{id}, học viên, chương trình, lớp nếu đã xếp và khoản thu. Nhãn “đã thu tiền” là thành phần giao diện, không phải chữ ký số được chứng thực. Ngày hiển thị lấy từ PaymentDate và có giới hạn dữ liệu đã nêu ở mục 3.3.2.',
705:'Danh sách học phí hiển thị mã, thời điểm đang lưu, phương thức, số tiền và trạng thái Pending hoặc Paid. PaymentDate chưa phản ánh riêng thời điểm Admin xác nhận; cần phân biệt khi đối soát.',
725:'Các thẻ tổng quan được tổng hợp từ dữ liệu tài khoản, lớp và khoản học phí đã xác nhận. Những chỉ số trình diễn cần được phân biệt với số liệu vận hành của một trung tâm thực tế.',
726:'Biểu đồ Chart.js minh họa xu hướng và cơ cấu chương trình. Chuỗi tháng có các giá trị mẫu, biểu đồ tỷ trọng đang dùng tỷ lệ cố định; chưa thể sử dụng như báo cáo doanh thu theo tháng đã kiểm chứng.',
729:'View nhận một số tổng số từ controller và dựng biểu đồ trên phần tử canvas. Cần thay các giá trị mẫu bằng truy vấn theo kỳ và kiểm tra lại trước khi triển khai.',
766:'Quản lý học viên (StudentManager): Xem hồ sơ, thông tin liên hệ, đăng ký và học phí theo tài khoản; khóa hoặc kích hoạt học viên theo chức năng hiện có. Phiên bản này chưa có hồ sơ phụ huynh độc lập.',
779:'Các danh sách hoạt động lọc IsDeleted ở các nhóm có hỗ trợ xóa mềm. Quy tắc này cần được áp dụng nhất quán ở cả truy vấn hiển thị và thao tác thay đổi.',
781:'Xóa vĩnh viễn (PermanentDelete): Loại bỏ bản ghi khi được phép và không còn ràng buộc cản trở; dữ liệu đã xóa vật lý không thể khôi phục bằng chức năng thùng rác.',
827:'Giao diện đăng nhập gồm Email, Mật khẩu và liên kết sang đăng ký tài khoản. Chức năng khôi phục mật khẩu tự động qua email cần được hoàn thiện cùng dịch vụ gửi thư.',
844:'Kiểm thử tập trung vào kết quả thao tác, quyền truy cập và tính nhất quán dữ liệu. Phạm vi dưới đây gồm các ca đã quan sát, kiểm tra riêng trên dữ liệu thử và ca cần chạy lại; chưa có kiểm thử tải hoặc đánh giá bảo mật toàn diện.',
847:'Kiểm tra nghiệp vụ chính: Tạo tài khoản, đăng ký kiểm tra, gửi nguyện vọng khóa học, xếp lớp, theo dõi VietQR, xác nhận thu, chấm thi, banner và thùng rác. Điểm danh theo buổi chưa có phần lưu dữ liệu nên được ghi nhận là hạn chế.',
848:'Kiểm tra phân quyền: Ba vai trò tài khoản Admin, Teacher và Student; khách chưa đăng nhập chỉ sử dụng chức năng công khai. Kiểm tra cookie theo vai trò khi mở nhiều khu vực trong cùng trình duyệt.',
860:'Kiểm thử phân hệ khách và học viên',861:'Kiểm thử phân hệ giáo viên',
864:'Chương 4 trình bày môi trường chạy, các màn hình và phạm vi kiểm thử của website NHK English times.',
865:'Các kết quả chính gồm:',
866:'Môi trường và công nghệ: ASP.NET Core MVC trên .NET 8, EF Core và SQL Server LocalDB; BCrypt bảo vệ mật khẩu lưu trữ, cookie quản lý phiên và mã CSRF bảo vệ biểu mẫu. VietQR hỗ trợ hướng dẫn chuyển khoản; MailKit mới là phụ thuộc cho hướng phát triển gửi thư.',
867:'Giao diện và nghiệp vụ: Các màn hình công khai, học viên, giáo viên và Admin hỗ trợ tra cứu, ghi danh, xếp lớp, lịch học, ca thi và học phí. Những phần chưa hoàn thiện được nêu cùng từng chức năng.',
869:'Thùng rác: Các nhóm dữ liệu có hỗ trợ xóa mềm được lưu để khôi phục; xóa vĩnh viễn vẫn phải tuân thủ ràng buộc quan hệ.',
873:'Đề tài đã xây dựng website NHK English times với các chức năng chính về tư vấn, đăng ký nguyện vọng, xếp lớp, lịch học, kiểm tra đầu vào và học phí. Sản phẩm đáp ứng phạm vi chạy thử của đồ án; một số chức năng và điều kiện vận hành còn cần hoàn thiện.',
876:'Ứng dụng ASP.NET Core MVC trên .NET 8 kết hợp EF Core để tổ chức giao diện, xử lý yêu cầu và truy cập SQL Server. Các dịch vụ nghiệp vụ được tách ở những phần cần tái sử dụng; một số controller vẫn truy vấn trực tiếp DbContext.',
878:'RoleCookieRouter chọn cookie theo vai trò để hỗ trợ sử dụng các khu vực Admin, Teacher và Student trên cùng trình duyệt. Phân quyền còn được kiểm tra tại controller và theo từng bản ghi.',
879:'BCrypt lưu mật khẩu dưới dạng băm; các biểu mẫu được bảo vệ bằng mã CSRF ở những action tương ứng. VietQR hỗ trợ hướng dẫn đóng học phí; gửi thư tự động chưa hoàn thiện.',
881:'Giao diện gồm các khu vực cho khách, học viên, giáo viên và Admin. Các màn hình được xây dựng bằng Razor, Bootstrap và CSS tùy chỉnh, cần tiếp tục kiểm tra khả năng sử dụng khi mở rộng dữ liệu.',
884:'Phân hệ Admin quản lý đào tạo, nhân sự, ghi danh, học phí, tư vấn và banner. Tổng khoản thu có dữ liệu thực; một số chuỗi trên biểu đồ Chart.js còn là dữ liệu mẫu nên cần hoàn thiện báo cáo theo kỳ.',
885:'Xóa mềm cho phép khôi phục các bản ghi thuộc nhóm hỗ trợ. Chức năng này hạn chế mất dữ liệu do thao tác nhầm nhưng không thay thế sao lưu và phục hồi cơ sở dữ liệu.',
889:'Thanh toán còn cần Admin đối soát; chưa có callback ngân hàng hoặc cổng thanh toán để tự động ghi nhận kết quả. PaymentDate chưa có trường riêng ghi thời điểm xác nhận thu.',
893:'Các hướng mở rộng dưới đây được đề xuất theo nhu cầu sử dụng. Trước khi thêm tích hợp, cần hoàn thiện chức năng nền tảng và kiểm tra với dữ liệu thực tế:',
895:'Nghiên cứu tích hợp cổng thanh toán có callback/IPN, kiểm tra chữ ký, số tiền, mã đơn và xử lý thông báo lặp trước khi chuyển Payment sang Paid. Trạng thái xếp lớp vẫn được quản lý độc lập.',
}
for i,t in fix.items():replace(ps[i],t)
# Light copy-edit across body; preserve paragraph formatting and nontext objects.
subs={'giao diện giao diện':'giao diện','I LA':'ILA','tc)hùng rác':'thùng rác','Vãng khách':'Khách vãng lai','hoàn hảo trên mọi kích thước màn hình':'phù hợp với các kích thước màn hình được kiểm tra','hiệu năng hàng đầu thế giới':'khả năng xử lý yêu cầu web','đảm bảo tuyệt đối':'hỗ trợ bảo đảm','giải quyết triệt để':'hạn chế','mạnh mẽ':'phù hợp','Luồng xử lý ngầm (Under-the-hood)':'Cách xử lý dữ liệu','chuẩn muối hóa (Salting) an toàn':'kèm salt','mã băm chống giả mạo @Html.AntiForgeryToken()':'token chống giả mạo @Html.AntiForgeryToken()'}
for p in d.paragraphs[160:]:
 if p._p.xpath('.//w:drawing') or p._p.xpath('.//w:instrText'):continue
 t=p.text
 for a,b in subs.items():t=t.replace(a,b)
 if t!=p.text:replace(p,t)
 if p.style.name.startswith('Heading'):unnumber(p)
# Keep the introductory screenshot label before the image.
ps[256]._p.addprevious(ps[257]._p)
ps[257].paragraph_format.keep_with_next=True
# Full role summary aligns with implemented functions.
t=d.tables[0]
roletexts=[('Khách vãng lai','• Tra cứu chương trình, học phí và lớp tham khảo.\n• Gửi và theo dõi tư vấn bằng quyền truy cập riêng.\n• Đăng ký tài khoản học viên.'),('Học viên','• Gửi nguyện vọng khóa học và đăng ký kiểm tra đầu vào.\n• Theo dõi đơn, lớp được xếp, lịch học và kết quả kiểm tra.\n• Xem học phí, biên lai và trao đổi tư vấn.'),('Giáo viên','• Xem lớp, danh sách học viên và lịch dạy được phân công.\n• Chấm bài kiểm tra đầu vào trong ca được giao.\n• Quản lý tài liệu, xem phản hồi và bảng lương cá nhân.\n• Điểm danh hiện mới có giao diện minh họa.'),('Quản trị viên','• Quản lý chương trình, lớp, lịch và hồ sơ người dùng.\n• Xếp học viên, tổ chức phòng thi và phân công chấm.\n• Xác nhận học phí, trả lời tư vấn, quản lý lương và banner.\n• Theo dõi thống kê và dữ liệu xóa mềm.')]
for row,(a,b) in zip(t.rows[1:],roletexts):row.cells[0].text=a;row.cells[1].text=b
# Fix table wording and inconsistent schema-summary names.
mapnames={'UserAccount':'UserAccounts','Student':'Students','Teacher':'Teachers','Program':'Programs','Class':'Classes','Registration':'Registrations','Payment':'Payments','PlacementTest':'PlacementTests','ClassSchedule':'ClassSchedules','ClassDocument':'ClassDocuments','CourseFeedback':'CourseFeedbacks','TeacherSalary':'TeacherSalaries','Consultation':'Consultations','Banner':'Banners','ExamSession':'ExamSessions','ConsultationMessage':'ConsultationMessages'}
for row in d.tables[4].rows[1:]:
 c=row.cells[0]
 if c.text in mapnames:c.text=mapnames[c.text]
d.tables[25].rows[2].cells[2].text='EF Core 8.0.30; SQL Server/Tools 8.0.10'
d.tables[25].rows[3].cells[3].text='Băm mật khẩu kèm salt; không lưu mật khẩu dạng rõ. Không thay thế kiểm soát đăng nhập và bảo vệ phiên.'
d.tables[25].rows[6].cells[3].text='Dựng HTML ở máy chủ bằng Razor, kết hợp tương tác JavaScript tại trình duyệt.'
d.tables[25].rows[8].cells[1].text='Font Awesome 6.5 và Google Fonts (Plus Jakarta Sans)'
d.tables[2].rows[4].cells[1].text='Thiết kế yêu cầu Teacher phụ trách lớp; danh sách hiện lọc theo giáo viên.'
d.tables[2].rows[4].cells[3].text='Cần bổ sung kiểm tra sở hữu tại Upload/Delete và giới hạn loại, kích thước tệp. Tải học liệu riêng cho học viên chưa hoàn thiện.'
d.tables[28].rows[1].cells[2].text='Giáo viên chọn lớp và đánh dấu checkbox Có mặt; chưa có phần lưu trạng thái theo buổi.'
d.tables[26].rows[4].cells[1].text='Ngăn truy cập khu vực trái quyền'
# Table captions use SEQ fields and a dedicated style.
def field(p,instr,cache=''):
 instr=instr.replace(chr(92)*2,chr(92))
 for tag,txt in [('begin',None),('instr',instr),('separate',None),('text',cache),('end',None)]:
  r=OxmlElement('w:r')
  if tag=='instr':x=OxmlElement('w:instrText');x.set(qn('xml:space'),'preserve');x.text=' '+txt+' '
  elif tag=='text':x=OxmlElement('w:t');x.text=txt
  else:x=OxmlElement('w:fldChar');x.set(qn('w:fldCharType'),tag)
  r.append(x);p._p.append(r)
def cap(p,num,title):
 p.clear();p.style=d.styles['NHKTableCaption'];unnumber(p);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.add_run('Bảng ');field(p,'SEQ Bang \\* ARABIC',str(num));p.add_run('. '+title)
 p.paragraph_format.keep_with_next=True
cap(ps[281].insert_paragraph_before(),1,'Các nhóm người sử dụng và nhu cầu chính')
# Move first caption directly before the first table (it sits between 280 and 281).
p=d.paragraphs[-1] if False else None
for node in list(d._element.body):
 if node.tag==qn('w:p') and ''.join(node.xpath('.//w:t/text()')).startswith('Bảng 1.'):
  t._tbl.addprevious(node);break
for p in ps[160:]:
 m=re.match(r'^Bảng (\d+)\.\s*(.*)',p.text)
 if m:cap(p,int(m[1]),m[2])
extra={25:'Các công nghệ và thư viện sử dụng',26:'Kiểm thử xác thực và quyền truy cập',27:'Kiểm thử chức năng khách và học viên',28:'Kiểm thử chức năng giáo viên',29:'Kiểm thử chức năng quản trị viên'}
for idx,title in extra.items():
 from docx.text.paragraph import Paragraph
 n=OxmlElement('w:p');d.tables[idx]._tbl.addprevious(n);cap(Paragraph(n,d._body),idx,title)
# Standardize table layout without forcing whole tables onto single pages.
for tab in d.tables:
 for ri,row in enumerate(tab.rows):
  if ri==0 and len(tab.rows)>1:
   trpr=row._tr.get_or_add_trPr()
   if trpr.find(qn('w:tblHeader')) is None:trpr.append(OxmlElement('w:tblHeader'))
  for c in row.cells:
   for p in c.paragraphs:
    p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.keep_with_next=False;p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(2);p.paragraph_format.line_spacing=1.03
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10.5 if len(tab.columns)>3 else 11);r.font.color.rgb=RGBColor(0,0,0)
# Figure captions include subfigures in the automatic list. Keep existing SEQ fields.
for p in ps[160:]:
 if re.match(r'^Hình \d+[a-z]?\.',p.text):
  match=re.match(r'^Hình (\d+)\.\s*(.*)',p.text)
  if match:
   n,title=match.groups();p.clear();p.add_run('Hình ');field(p,'SEQ Hinh '+chr(92)+'* ARABIC',n);p.add_run('. '+title)
  p.style=d.styles['NHKSubFigureCaption' if re.match(r'^Hình \d+[a-z]\.',p.text) else 'NHKFigureCaption'];unnumber(p)
  p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_together=True;p.paragraph_format.keep_with_next=False
  for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(12);r.font.color.rgb=RGBColor(0,0,0);r.font.italic=(p.style.name=='NHKSubFigureCaption')
# The first subfigure advances the sequence for the four-part figure 4.
p=ps[379];p.clear();p.add_run('Hình ');field(p,'SEQ Hinh '+chr(92)+'* ARABIC','4');p.add_run('a. Sơ đồ use case khách chưa đăng nhập')
for run in p.runs:run.italic=True
# Replace screenshots from the latest actual app captures; keep school logo and survey images.
assets=R/'final-refresh/assets'
figassets={9:'home',10:'home-student',11:'programs',12:'detail',13:'test',14:'checkout',15:'receipt',16:'myclasses',17:'schedule',18:'payments',19:'profile',20:'contact',21:'admin-dashboard',22:'admin-banners',23:'admin-programs',24:'admin-classes',25:'class-create',26:'admin-registrations',27:'admin-payments',28:'admin-teachers',29:'admin-students',30:'admin-trash',31:'exam-create',32:'admin-tests',33:'admin-consultations',34:'consultation-thread',35:'teacher-dashboard',36:'teacher-classes',37:'teacher-students',38:'teacher-tests',39:'teacher-documents',40:'teacher-feedback',41:'teacher-salary',42:'admin-salaries',43:'login',44:'register',45:'change-password'}
replacedimages=[]
for i,p in enumerate(ps[160:],160):
 m=re.match(r'^Hình (\d+)\.',p.text)
 if not m or int(m[1]) not in figassets:continue
 a=assets/('ui-'+figassets[int(m[1])]+'.png')
 for prev in reversed(ps[max(160,i-4):i]):
  blips=prev._p.xpath('.//a:blip')
  if blips:
   for b in blips:
    rid=b.get(qn('r:embed'));part=d.part.related_parts[rid];part._blob=a.read_bytes()
   replacedimages.append(int(m[1]));break
# Restore requested directory section from the prior completed draft, without changing current paragraphs.
old=Document(R/'chapter3-completed-draft.docx');ops=list(old.paragraphs)
start=next(i for i,p in enumerate(ops) if p.text.startswith('3.4.2 Cấu trúc thư mục'))
end=next(i for i,p in enumerate(ops[start:],start) if p.text=='KẾT CHƯƠNG 3')
for p in ops[start:end]:
 x=deepcopy(p._p);ps[555]._p.addprevious(x)
for p in d.paragraphs:
 if p.text.startswith('Frontend là tập View'):
  replace(p,'Frontend gồm Razor Views và tài nguyên tĩnh trong cùng dự án MVC. Controller và action xác định tuyến trang; các View dùng layout chung theo từng khu vực.')
 elif p.text.startswith('Tài nguyên Bootstrap, Font Awesome, Google Fonts'):
  replace(p,'Các layout tham chiếu Bootstrap, Font Awesome, Google Fonts và Chart.js. Ở phân hệ tư vấn, JavaScript dùng fetch để gửi, nhận JSON và cập nhật tin nhắn theo chu kỳ.')
# Rebuild front matter, preserving section boundary and cover.
body=d._element.body
first=ps[16]._p;last=ps[159]._p
nodes=list(body);a=nodes.index(first);b=nodes.index(last)
for x in nodes[a:b]:body.remove(x)
anchor=last
from docx.text.paragraph import Paragraph
def front(text='',sty='Normal',breakbefore=False):
 x=OxmlElement('w:p');anchor.addprevious(x);p=Paragraph(x,d._body);p.style=d.styles[sty];p.add_run(text);unnumber(p)
 p.paragraph_format.page_break_before=breakbefore
 return p
p=front('LỜI CẢM ƠN','FrontMatterHeading');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
for t in ['Em xin cảm ơn thầy Nguyễn Minh Nhứt đã hướng dẫn môn Lập trình ứng dụng, giúp em có cơ sở để thực hiện đề tài website quản lý trung tâm ngoại ngữ NHK English times.',
'Qua việc xây dựng ứng dụng và viết báo cáo, em có dịp vận dụng kiến thức về lập trình web, thiết kế cơ sở dữ liệu và phân tích nghiệp vụ vào một sản phẩm cụ thể. Em cũng nhận ra những phần cần tiếp tục cải thiện, nhất là kiểm thử, quản lý dữ liệu và cách trình bày kết quả.',
'Báo cáo còn có thể có thiếu sót do kinh nghiệm thực hiện của em còn hạn chế. Em mong nhận được góp ý của thầy để hoàn thiện kiến thức và sản phẩm. Em xin chân thành cảm ơn.']:
 p=front(t);p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY;p.paragraph_format.first_line_indent=Cm(1)
p=front('Sinh viên thực hiện\nNguyễn Khánh Huy');p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for title,instr in [
 ('MỤC LỤC','TOC \\o "1-3" \\t "FrontMatterHeading,1" \\h \\z'),
 ('DANH MỤC CÁC BẢNG','TOC \\h \\z \\t "NHKTableCaption,1"'),
 ('DANH MỤC CÁC HÌNH','TOC \\h \\z \\t "NHKFigureCaption,1,NHKSubFigureCaption,1"')]:
 p=front(title,'FrontMatterHeading',True);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p=front();field(p,instr,'Đang cập nhật mục lục…')
# New section main-body starts on a fresh page and Arabic 1, front matter Roman i.
for i,sec in enumerate(d.sections):
 pg=sec._sectPr.find(qn('w:pgNumType'))
 if pg is None:pg=OxmlElement('w:pgNumType');sec._sectPr.append(pg)
 pg.set(qn('w:fmt'),'lowerRoman' if i==1 else 'decimal');pg.set(qn('w:start'),'1')
# Consistent body type and natural terminology; keep quotations/code readable.
for p in d.paragraphs:
 if p._p.xpath('.//w:sectPr') or p._p.xpath('.//w:drawing'):continue
 if p.style.name.startswith('Heading'):unnumber(p)
 if p.text.startswith('KẾT CHƯƠNG'):
  p.style=d.styles['Normal'];p.paragraph_format.keep_with_next=True
  for r in p.runs:r.bold=True
 if p.style.name=='Normal' and p in []:pass
for name in ['TOC 1','TOC 2','TOC 3']:
 s=style(name,12)
 s.paragraph_format.space_after=Pt(3);s.paragraph_format.line_spacing=1.05;s.paragraph_format.keep_with_next=False
# Remove proofing markup and standardize document language.
for x in list(d._element.xpath('.//w:proofErr')):x.getparent().remove(x)
lang=OxmlElement('w:lang');lang.set(qn('w:val'),'vi-VN');d.styles['Normal']._element.get_or_add_rPr().append(lang)
d.core_properties.title='Báo cáo website quản lý trung tâm ngoại ngữ NHK English times';d.core_properties.author='Nguyễn Khánh Huy';d.core_properties.subject='Đồ án môn Lập trình ứng dụng';d.core_properties.comments=''
# Track bibliography actually consulted by the author; retain supplied access dates, do not fabricate new ones.
for i in [859,860,861,862]:
 ps[i].paragraph_format.keep_with_next=True
p=ps[890].insert_paragraph_before('Các phần cần hoàn thiện trong ứng dụng gồm lưu điểm danh theo buổi, tải học liệu cho học viên, gửi thư tự động và dữ liệu biểu đồ theo kỳ. Phân hệ tài liệu đã lọc danh sách theo giáo viên nhưng Upload/Delete còn cần kiểm tra quyền sở hữu tại máy chủ và giới hạn tệp.')
p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
# Readable bibliography avoids stretched spaces in URLs.
for p in ps[906:]:
 p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.space_after=Pt(6)
 if p.text.startswith('['):
  p.paragraph_format.left_indent=Cm(0.7);p.paragraph_format.first_line_indent=Cm(-0.7)
 for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(12)
# Final source and accounting for this editorial pass.
out=R/'final-polish-draft.docx';d.save(out)
(R/'final-polish-audit.json').write_text(json.dumps({'source':'Bao_cao_LLUD_Hoan_thien_Chuong_3.docx','targeted_edits':edits,'screenshots_updated':replacedimages,'table_count':len(d.tables),'inline_images':len(d.inline_shapes),'automatic_table_captions':29,'automatic_figure_entries':52-1,'restored_folder_section':True},ensure_ascii=False,indent=2),encoding='utf8')
print(out,'paragraphs',len(d.paragraphs),'tables',len(d.tables),'images',len(d.inline_shapes),'edits',len(edits))
