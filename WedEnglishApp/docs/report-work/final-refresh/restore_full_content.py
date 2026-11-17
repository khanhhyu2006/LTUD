from pathlib import Path
from copy import deepcopy
from io import BytesIO
import re,json
from PIL import Image
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

R=Path(__file__).resolve().parent;ROOT=R.parents[2];A=R/'assets'
d=Document(ROOT/'Bao_cao_HITC_English_Giu_nguyen_noi_dung_goc.docx')
original=Document('D:/LTUD/doanketthucmonWeb.docx')
latest=Document(ROOT/'Bao_cao_LLUD_Hoan_thien.docx')
base=list(d.paragraphs);mapped={};cursor=next(i for i,p in enumerate(base) if p.style.name=='Heading 1' and p.text=='MỞ ĐẦU')
chapter3='CHƯƠNG 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG'
def clean(t):
    t=t.replace(chapter3,'') if not t.startswith(chapter3) else t
    if t.startswith('(Vị trí chèn hình:'):t=t.replace('(Vị trí chèn hình:','',1).strip().removesuffix(')')
    elif t.startswith('(Hình '):t=t[1:].removesuffix(')')
    return re.sub(r'\s+',' ',t).strip()
for i,p in enumerate(original.paragraphs):
    t=clean(p.text)
    if not t:continue
    for j in range(cursor,len(base)):
        if clean(base[j].text)==t:mapped[i]=base[j];cursor=j+1;break
assert len(mapped)==494,(len(mapped),[i for i,p in enumerate(original.paragraphs) if p.text.strip() and i not in mapped])
changes={}
def change(i,text):
    p=mapped[i];changes[i]={'before':p.text,'after':text};p.text=text
def replace(i,a,b):
    if a in mapped[i].text:change(i,mapped[i].text.replace(a,b))

# Keep the author's complete narrative. Only inaccurate claims and changed workflows are corrected.
edits={
13:'Để đạt được mục tiêu tổng quát, đề tài tập trung giải quyết các mục tiêu cụ thể đối với 4 nhóm người sử dụng: Khách, Học viên, Giáo viên và Quản trị viên. Ba vai trò tài khoản được lưu là Student, Teacher và Admin; Khách là người chưa đăng nhập.',
16:'Gửi yêu cầu tư vấn trực tuyến (Consultation): Cho phép người dùng để lại thông tin liên hệ và nguyện vọng khóa học trên website, sau đó trao đổi trực tiếp với Admin trong cuộc hội thoại riêng. Học viên theo dõi lịch sử theo tài khoản; khách giữ cookie hoặc liên kết riêng để xem lại nội dung.',
19:'Kiểm tra trình độ đầu vào (Placement Test): Học viên đăng ký ngày và giờ mong muốn. Admin tạo phòng thi, xếp các học viên đăng ký vào lớp thi và phân công giáo viên chấm cả ca. Giáo viên nhập điểm và cấp độ đề xuất; học viên xem kết quả trong tài khoản. Bộ đề Listening/Reading tự chấm là hướng phát triển tiếp theo.',
20:'Đăng ký khóa học trực tuyến (Registration): Học viên chọn chương trình, ngày có thể bắt đầu, buổi học và nhóm thứ 2–4–6 hoặc 3–5–7 phù hợp với thời gian cá nhân. Học viên không chọn lớp hoặc giáo viên; Admin căn cứ đơn và nguyện vọng để xếp lớp sau.',
25:'Quản lý học viên và chuyên cần: Tra cứu danh sách học viên trong từng lớp, thông tin liên lạc và theo dõi lớp được phân công. Giao diện hiện có checkbox điểm danh; việc lưu chuyên cần theo ngày, buổi và các trạng thái đi trễ hoặc vắng cần được bổ sung.',
31:'Quản lý ghi danh và tư vấn tuyển sinh: Tiếp nhận đơn đăng ký khóa học, đối chiếu nguyện vọng để xếp học viên vào lớp phù hợp và xác nhận học phí theo nghiệp vụ riêng. Admin tiếp nhận yêu cầu tư vấn, gửi trả lời trực tiếp, theo dõi tin chưa đọc và kết thúc hoặc mở lại cuộc hội thoại.',
32:'Quản trị người dùng và phân quyền bảo mật: Cấp tài khoản, cập nhật hồ sơ và phân quyền theo chức năng của hệ thống. Phân hệ học viên có khóa hoặc kích hoạt tài khoản; chức năng khóa/mở riêng cho giáo viên cần tiếp tục hoàn thiện.',
47:'Về bài thi xếp lớp (Placement Test): Hệ thống tập trung vào đăng ký kiểm tra, xếp phòng, phân công người chấm và lưu điểm cùng cấp độ đề xuất. Chưa tích hợp bộ câu hỏi Nghe/Đọc tự chấm, thu âm hoặc chấm điểm AI cho kỹ năng Nói và Viết.',
58:'Sơ đồ thực thể kết hợp (ERD): Thiết kế 16 bảng nghiệp vụ gồm UserAccount, Student, Teacher, CourseProgram, CourseClass, Registration, Payment, PlacementTest, ExamSession, ClassSchedule, ClassDocument, CourseFeedback, TeacherSalary, Consultation, ConsultationMessage và Banner. ClassStatus là thuộc tính trạng thái của lớp, không phải một bảng độc lập.',
74:'Kiểm soát sĩ số (Capacity Control): Mỗi lớp học được thiết lập MaxStudents theo quy mô lớp. Khi Admin xếp học viên, hệ thống đếm các đăng ký Confirmed chưa xóa của lớp, kiểm tra chỗ trống và từ chối vượt sĩ số ngay tại máy chủ. Học viên đăng ký chương trình trước, vì vậy giao diện công khai không dùng nút giữ chỗ một lớp cụ thể.',
116:'Xây dựng phân hệ kiểm tra xếp lớp: Học viên gửi yêu cầu ngày giờ; Admin tổ chức phòng thi, xếp nhiều thí sinh và phân công giáo viên chấm. Kết quả gồm điểm và cấp độ đề xuất; thi trực tuyến tự chấm hai kỹ năng Nghe/Đọc được định hướng phát triển sau.',
124:'Quản lý các chương trình IELTS Master, TOEIC Cấp tốc, Tiếng Anh Giao tiếp, Business English và Cambridge B1/B2; bổ sung tiếng Anh tiểu học, THCS, THPT, Phonics, Cambridge Young Learners, củng cố kiến thức và IELTS Foundation. Danh mục được quản lý động trong cơ sở dữ liệu.',
126:'Quản trị 16 bảng nghiệp vụ có khóa chính, khóa ngoại và các ràng buộc dữ liệu, liên kết từ tài khoản, chương trình và ghi danh tới lớp, học phí, kiểm tra và tư vấn.',
129:'Đề tài hướng tới số hóa quy trình quản lý đào tạo, giảm thao tác nhập liệu và tổng hợp thủ tục thủ công, minh bạch tình trạng học phí và nâng cao trải nghiệm học viên. Mức tiết kiệm thời gian và hiệu quả vận hành cần được đo bằng khảo sát thực tế, chưa có số liệu để khẳng định tỷ lệ phần trăm cụ thể.',
145:'Phía Client: Trình duyệt web sử dụng HTML, CSS và JavaScript cho giao diện MVC. Các thành phần tương tác dùng Fetch để lấy tin tư vấn và cập nhật nội dung mà không tải lại toàn bộ trang. Ứng dụng di động là hướng mở rộng, chưa có sản phẩm độc lập trong phiên bản hiện tại.',
155:'RESTful API là cơ sở lý thuyết cho việc cung cấp endpoint JSON tới ứng dụng di động và các tác vụ Ajax/Fetch. Trong phiên bản hiện tại, một số action MVC trả JSON để phục vụ tương tác, đặc biệt ở phân hệ tư vấn; chưa có một backend API riêng hoàn chỉnh cho React Native.',
156:'Khi mở rộng thành dịch vụ API độc lập, các chức năng xác thực, lịch học và ghi danh cần có hợp đồng dữ liệu, kiểm tra quyền và mã trạng thái HTTP rõ ràng. Các tên AuthApiController, ScheduleApiController và ReservationApiController là ví dụ định hướng, không phải các Controller đã hiện thực trong dự án hiện tại.',
190:'Tầng nghiệp vụ (Business Logic Tier): CourseClassAssignment kiểm tra xếp lớp; ClassSchedulePlanner quản lý lịch tuần; ExamSessionPlanner kiểm tra phòng thi; ConsultationAccess và ConsultationMessaging xử lý quyền và tin nhắn. Một số nghiệp vụ truy vấn, thanh toán và thống kê vẫn nằm trong Controller, chưa tách hoàn toàn thành tầng dịch vụ.',
206:'Áp dụng thuật toán băm mật khẩu một chiều có Salt ngẫu nhiên BCrypt, cơ chế bảo vệ biểu mẫu chống CSRF và hướng dẫn chuyển khoản bằng mã VietQR. MailKit đã được khai báo trong phụ thuộc nhưng dịch vụ gửi thư tự động chưa hoàn thiện; việc xác nhận thu tiền do Admin đối soát.',
212:'Học viên sử dụng được các chức năng công khai của khách như tra cứu chương trình và thông tin liên hệ, đồng thời có thêm hồ sơ, đăng ký khóa học, lịch học và học phí cá nhân. Sơ đồ hiện tại thể hiện các mục tiêu theo từng tác nhân; quyền công khai không phụ thuộc việc có phiên đăng nhập.',
213:'Đăng nhập là điều kiện trước của các nghiệp vụ được bảo vệ như đăng ký khóa học, theo dõi học phí và nhập điểm. Quan hệ include chỉ dùng khi có hành vi bắt buộc dùng lại; không dùng để thay cho mọi điều kiện phân quyền hoặc để mô tả thứ tự mở các màn hình.',
214:'Đăng ký khóa học, xem hướng dẫn đóng học phí và in biên lai có liên hệ về dữ liệu. Xếp lớp và xác nhận thu là hai nghiệp vụ độc lập; biên lai chỉ phản ánh khoản thu hợp lệ. Không mặc định dùng quan hệ extend chỉ vì các chức năng xuất hiện sau bước ghi danh.',
247:'Để ứng dụng vận hành thuận tiện trên máy phát triển và triển khai thử nghiệm, có thể tham khảo cấu hình phần cứng sau. Đây là đề xuất phục vụ chạy IDE, cơ sở dữ liệu và máy chủ cục bộ; thời gian phản hồi cần được đo thực tế, chưa có kết quả kiểm thử tải để bảo đảm một ngưỡng cố định.',
280:'Tiếp nhận tư vấn trực tuyến (Lead Capture): Trang chủ có liên kết tới Tư vấn và Liên hệ. Biểu mẫu tại trang liên hệ nhận Họ tên, Số điện thoại, Email và nội dung cần hỗ trợ; khách không bắt buộc tạo tài khoản trước khi mở cuộc hội thoại riêng với Admin.',
281:'Khóa học nổi bật và lịch lớp tham khảo: Trang chủ trình bày chương trình cùng thời lượng, học phí và liên kết đăng ký. Danh sách lớp cung cấp lịch để tham khảo; việc gửi đơn thuộc khóa học và lưu nguyện vọng, không buộc người học chọn trước một lớp hoặc giáo viên.',
282:'Thanh chỉ số tổng quan (Stats): Hiển thị số chương trình đào tạo, lớp đang mở, giáo viên và học viên theo dữ liệu trình diễn của hệ thống. Các chỉ số này không được hiểu mặc định là số học viên đã tốt nghiệp hoặc kết quả khảo sát uy tín thực tế.',
291:'Yêu cầu hợp lệ được lưu tại Consultations với trạng thái Pending và tạo tin nhắn đầu tiên tại ConsultationMessages. Học viên được gắn chủ sở hữu từ phiên; khách được cấp cookie truy cập và liên kết riêng. Hệ thống mở trang hội thoại để tiếp tục trao đổi với Admin thay vì chỉ hiển thị thông báo gửi thành công.',
298:'Ghi danh khóa học: Tại trang chương trình, học viên mở biểu mẫu Checkout theo ProgramId. Thông tin tài khoản được lấy từ hồ sơ; học viên bổ sung ngày có thể bắt đầu, buổi, nhóm thứ và cách đóng học phí trước khi xác nhận, không chọn trực tiếp một lớp ở trang chủ.',
315:'Danh sách lớp tham khảo của chương trình: Cung cấp ngày khai giảng, lịch tuần và thông tin lớp để người học tìm hiểu. Nút đăng ký thuộc khóa học; học viên gửi nguyện vọng, sau đó Admin lựa chọn lớp phù hợp theo thời gian, sức chứa và kế hoạch đào tạo.',
324:'Mẫu đăng ký kiểm tra giải thích quy trình tiếp nhận yêu cầu, Admin xếp phòng và phân công giáo viên. Bên cạnh biểu mẫu là lịch sử kiểm tra, trạng thái, lịch chính thức và kết quả đã có; chưa có màn hình làm bài bốn kỹ năng trực tuyến.',
325:'Học viên chọn ngày mong muốn từ ngày mai trở đi và một khung giờ thuận tiện: 08:30, 10:00, 14:00, 16:00 hoặc 18:30. Đây là yêu cầu ban đầu; lịch phòng thi chính thức do Admin xác nhận sau khi bố trí ca thi.',
329:'Admin tạo ExamSession với phòng, ngày, giờ và sức chứa; chọn nhiều yêu cầu để xếp cùng lớp thi, rồi phân công giáo viên chấm cả ca. Sau khi xếp, lịch và người chấm được hiển thị cho học viên. IEmailService chưa có quy trình gửi thư xác nhận tự động hoàn chỉnh.',
335:'Giao diện chia hai cột: bên trái nhập ngày có thể bắt đầu, buổi, nhóm 2–4–6 hoặc 3–5–7 và ghi chú; bên phải hiển thị tên khóa học, thời lượng, tổng học phí và lựa chọn đóng tại trung tâm hoặc VietQR. Ảnh hồ sơ là tùy chọn; không có trường chọn lớp hoặc giáo viên.',
336:'Hướng dẫn VietQR sau xác nhận: Khi học viên chọn chuyển khoản và gửi đơn hợp lệ, trang học phí hiển thị mã QR, số tiền và nội dung chuyển khoản theo mã đơn. Người học quét bằng ứng dụng ngân hàng; Admin vẫn phải kiểm tra chứng từ trước khi ghi nhận Paid, không coi việc hiển thị QR là đã thanh toán.',
339:'Kiểm soát dữ liệu khi đăng ký: Máy chủ kiểm tra chương trình đang hoạt động, ngày có thể bắt đầu, buổi và nhóm thứ hợp lệ; ngăn đăng ký trùng khóa học đang hoạt động. Kiểm tra sĩ số và lịch trùng được thực hiện khi Admin xếp học viên vào lớp, không giữ chỗ lớp từ bước đăng ký khóa học.',
340:'Khởi tạo Registration Pending có ProgramId và ClassId để trống, đồng thời tạo Payment Pending trong cùng transaction. Mức phí được lấy từ chương trình ở máy chủ; không sử dụng số tiền hoặc trạng thái tùy ý từ biểu mẫu của người dùng.',
341:'Trang hướng dẫn học phí sinh nội dung chuyển khoản theo mã đăng ký và hiển thị VietQR khi chọn phương thức này. Admin đối soát thu tiền riêng; khi xếp lớp, ngày khai giảng phải bằng hoặc sau ngày học viên có thể bắt đầu, đồng thời kiểm tra đúng khóa, sức chứa và lịch xung đột.',
356:'Hiển thị chi tiết: Tên khóa học, tên lớp, phòng học, giảng viên phụ trách và thời khóa biểu các ca trong tuần. Đơn chưa được xếp có khu vực theo dõi nguyện vọng riêng; đường dẫn tải học liệu trong khu vực học viên là hạng mục cần hoàn thiện.',
368:'Kết quả kiểm tra đầu vào gồm điểm, ngày thi và cấp độ do giáo viên đề xuất được tra cứu tại lịch sử kiểm tra. Hồ sơ cá nhân có liên kết đến kết quả; hiện chưa có bảng điểm riêng cho bốn kỹ năng.',
395:'Lập kế hoạch mở lớp, phân bổ phòng, sĩ số và ngày khai giảng/bế giảng; chọn lịch 2–4–6 hoặc 3–5–7 cùng giờ bắt đầu, kết thúc để lưu ba ca học trong ClassSchedules. Giáo viên có thể được phân công sau. Lịch được áp dụng vào thời khóa biểu học viên và giáo viên trong khoảng thời gian của lớp.',
399:'Quản lý thanh toán (PaymentAdmin): Đối soát chuyển khoản VietQR hoặc xác nhận thu tiền mặt tại trung tâm; cập nhật Payment Paid sau khi kiểm tra. Trạng thái thu tiền tách khỏi Pending hoặc Confirmed của đơn xếp lớp; các đơn và biên lai đã thanh toán trước đây được giữ nguyên để đối chiếu lịch sử.',
400:'Quản lý đăng ký (RegistrationAdmin): Theo dõi đơn theo chương trình, ngày bắt đầu và nguyện vọng; xếp hoặc chuyển sang lớp phù hợp, cập nhật Pending, Confirmed hoặc Cancelled. Chỉ gán ClassId khi Admin xếp lớp; khi trả về chờ hoặc hủy, liên kết lớp được xử lý theo trạng thái đơn.',
401:'Quản lý tư vấn (ConsultationManager): Mở hộp thư, xem thông tin người liên hệ và lịch sử tin nhắn, gửi trả lời trực tiếp cho khách hoặc học viên. Hệ thống có tin chưa đọc, đánh dấu đã xem và thao tác kết thúc/mở lại; giao diện lấy tin mới định kỳ, chưa dùng SignalR hoặc WebSocket.',
424:'Chức năng: Giảng viên theo dõi danh sách lớp được phân công, mở danh sách học viên và thông tin liên hệ. Giao diện có checkbox Có mặt để minh họa thao tác; chưa có bảng lưu chuyên cần theo từng ngày/buổi hoặc các trạng thái đi trễ, vắng có phép và vắng không phép.',
427:'Chức năng: Giảng viên mở lớp thi được phân công, xem danh sách thí sinh và nhập điểm từ 0 đến 10 cùng cấp độ đề xuất (RecommendedLevel) cho từng bài. Bài chấm xong chuyển Completed; khi tất cả bài hoàn tất, ca thi được đánh dấu hoàn thành. Giáo viên khác không được chấm ca không thuộc phân công.',
446:'Kiểm soát truy cập: Authorize và RoleCookieRouter giới hạn từng khu vực theo vai trò. Người chưa có cookie đúng vai trò có thể được chuyển đến trang đăng nhập tương ứng; không phải mọi tình huống truy cập trái quyền đều hiển thị một trang HTTP 403. Các action cá nhân còn cần kiểm tra quyền trên từng bản ghi.',
477:'Đánh giá và kiểm thử: Các bảng ca kiểm thử mô tả tình huống, kết quả cần đạt và phạm vi đã kiểm tra. Luồng đăng ký, xếp lớp, lịch tuần, phòng thi và tư vấn đã được kiểm tra trên dữ liệu riêng; bộ tư vấn ghi nhận 31 kiểm tra đạt. Chưa có số đo độ trễ, kiểm thử tải hoặc căn cứ để khẳng định toàn bộ hệ thống đạt 100% và phản hồi dưới 350 ms.',
490:'Phân hệ học viên và tuyển sinh: Tiếp nhận tư vấn hai chiều, đăng ký kiểm tra đầu vào, gửi nguyện vọng khóa học, theo dõi lớp được Admin xếp, xem hướng dẫn VietQR hoặc đóng tại trung tâm và in biên lai khoản thu đã xác nhận. Xác nhận thu học phí và xếp lớp được xử lý riêng.',
495:'Các luồng mới đã được kiểm tra bằng thao tác và dữ liệu thử riêng; 31 kiểm tra tư vấn bao gồm trao đổi hai chiều, quyền sở hữu, CSRF, nội dung quá dài và kết thúc/mở lại hội thoại. Các ca trong bảng cần phân biệt giữa đã quan sát, đã kiểm tra nghiệp vụ và chưa chạy lại. Hiệu năng hoặc độ tin cậy khi vận hành thực tế cần được đánh giá tiếp.',
}
for i,t in edits.items():change(i,t)
small=[
(43,'tự động thực hiện Migration','hỗ trợ Migration và các script SQL nâng cấp có kiểm soát'),
(44,'thiết kế cấu trúc dữ liệu chuẩn hóa dạng chuẩn 3 (3NF)','thiết kế cấu trúc dữ liệu quan hệ'),
(46,'Sau khi học viên thanh toán, hệ thống cho phép xuất in biên lai học phí điện tử','Sau khi Admin đối soát và xác nhận đã thu, hệ thống cho phép xuất in biên lai học phí điện tử'),
(61,'khắc phục toàn bộ các lỗi tiềm ẩn, đảm bảo hệ thống đạt độ tin cậy và sẵn sàng đưa vào vận hành','khắc phục các lỗi phát hiện trong phạm vi kiểm tra, làm cơ sở tiếp tục đánh giá trước khi vận hành'),
(71,'làm bài kiểm tra năng lực đầu vào và đăng ký lớp học','đăng ký kiểm tra đầu vào và gửi nguyện vọng khóa học'),
(72,'hỗ trợ truy xuất đồng thời cho hàng ngàn người dùng','hỗ trợ truy xuất dữ liệu có kiểm soát; quy mô đồng thời cần kiểm thử tải'),
(79,'thi xếp lớp trực tuyến, đăng ký ca học','đăng ký kiểm tra xếp lớp, gửi nguyện vọng học'),
(117,'giúp thanh toán chuẩn xác 100%','hỗ trợ đối chiếu khoản thu; Admin xác nhận sau khi kiểm tra'),
(125,'kiểm tra xung đột thời khóa biểu 29 ca học trong tuần','kiểm tra xung đột thời khóa biểu theo các ca được cấu hình trong tuần'),
(134,'giữ chỗ lớp học, chống vượt sĩ số overbooking, cập nhật lịch học và điểm danh','xếp lớp theo nguyện vọng, chống vượt sĩ số và cập nhật lịch học; lưu chuyên cần cần được bổ sung'),
(136,'VUS, ILA, PASAL,...','VUS, ILA'),
(138,'tự động hóa toàn diện quy trình','hỗ trợ quy trình'),
(138,'thanh toán học phí quản lý lịch dạy và điểm danh chuyên cần','đối soát học phí và quản lý lịch dạy; chuyên cần là hạng mục tiếp tục hoàn thiện'),
(142,'Mô hình Kết hợp ASP.NET Core MVC & Web API','ASP.NET Core MVC và định hướng Web API'),
(149,'trên cả nền tảng Web và Mobile','trên nền tảng Web, tạo cơ sở mở rộng Mobile'),
(154,'Mô hình RESTful Web API (API Controllers):','Định hướng mở rộng RESTful Web API:'),
(163,'Bootstrap 5 & Tailwind CSS / NativeWind','Bootstrap 5 và CSS tùy chỉnh'),
(167,'Sử dụng Axios / Fetch API để gọi các tuyến RESTful API từ Server xử lý chuyển đổi dữ liệu thời gian thực (Real-time data update)','Sử dụng Fetch API để gọi các action trả JSON, cập nhật tin nhắn tư vấn theo truy vấn định kỳ'),
(169,'Cấu trúc bảng được chuẩn hóa đạt chuẩn 3 (3NF)','Cấu trúc bảng được tổ chức theo các thực thể và quan hệ'),
(170,'chính xác tuyệt đối','theo đơn đăng ký để Admin đối chiếu'),
(182,'100% các câu truy vấn thông qua EF Core đều','Các truy vấn LINQ qua EF Core thường'),
(226,'Phiên bản dài hạn mới nhất của Microsoft','Phiên bản được lựa chọn trong dự án'),
(297,'Hồ sơ của tôi, Lớp học của tôi','Tư vấn của tôi, Hồ sơ của tôi, Lớp học của tôi, Lịch học và thời khóa biểu'),
(404,'hỗ trợ khóa hoặc kích hoạt tài khoản giảng viên tức thì (ToggleStatus)','hỗ trợ xóa mềm và khôi phục; chưa có action khóa/mở giáo viên riêng'),
(411,'Hộp thoại xác nhận 2 lớp ngăn chặn sơ suất','yêu cầu xác nhận để hạn chế thao tác nhầm'),
(413,'tại bất kỳ trang quản lý nào','tại các trang có hỗ trợ xóa mềm'),
(473,'dịch vụ gửi thư điện tử tự động MailKit','phụ thuộc MailKit cho định hướng gửi thư điện tử'),
(474,'trên mọi kích thước thiết bị','trên các kích thước thiết bị được kiểm tra'),
(474,'giải quyết triệt để','xử lý'),
(476,'trên toàn bộ 7 bảng dữ liệu','cho các nhóm dữ liệu có hỗ trợ'),
(487,'dịch vụ gửi email tự động MailKit và cổng thanh toán quét mã VietQR tự động','hướng dẫn chuyển khoản bằng VietQR; dịch vụ gửi thư MailKit chưa hoàn thiện'),
(491,'điểm danh chuyên cần trực tiếp theo từng buổi học,','xem danh sách học viên và giao diện điểm danh minh họa,'),
(493,'trên toàn bộ 7 bảng dữ liệu','ở các nhóm dữ liệu có hỗ trợ'),
]
for i,a,b in small:replace(i,a,b)

# Copy the current, expanded chapter three. The author's original section 3.1 remains.
def find(doc,text):return next(p for p in doc.paragraphs if p.style.name.startswith('Heading') and p.text==text)
def copied(elements):
    out=[]
    for source in elements:
        e=deepcopy(source)
        for tag in ['w:bookmarkStart','w:bookmarkEnd']:
            for n in list(e.iter(qn(tag))):n.getparent().remove(n)
        for blip in e.iter(qn('a:blip')):
            old=blip.get(qn('r:embed'))
            if old:
                rid,_=d.part.get_or_add_image(BytesIO(latest.part.related_parts[old].blob));blip.set(qn('r:embed'),rid)
        for n in e.iter(qn('w:instrText')):
            if n.text and 'SEQ Hinh' in n.text:n.text=' SEQ Hinh \\* ARABIC '
        out.append(e)
    return out
start=find(d,'3.2 Phân rã use case theo từng tác nhân')._p;end=find(d,'CHƯƠNG 4. HIỆN THỰC HÓA VÀ KIỂM THỬ HỆ THỐNG')._p
node=start
while node is not end:
    nxt=node.getnext();node.getparent().remove(node);node=nxt
source_start=find(latest,'3.2 Phân rã use case theo từng tác nhân')._p
source_end=find(latest,'CHƯƠNG 4. HIỆN THỰC HÓA VÀ KIỂM THỬ HỆ THỐNG')._p
nodes=[];node=source_start
while node is not source_end:nodes.append(node);node=node.getnext()
for node in copied(nodes):end.addprevious(node)

# Restore updated pictures into the original prose, retaining the original figure positions.
names=['home','home-student','programs','detail','test','checkout','receipt','myclasses','schedule','payments','profile','admin-dashboard','admin-banners','admin-programs','admin-classes','admin-registrations','admin-payments','admin-teachers','admin-students','admin-trash','teacher-dashboard','teacher-classes','teacher-students','teacher-tests','teacher-documents','teacher-feedback','teacher-salary','admin-salaries','login','register','change-password']
for rid,name in [(f'rId{i}',f'ui-{n}') for i,n in zip(range(21,52),names)]+[('rId15','uc-overview')]:
    d.part.related_parts[rid]._blob=(A/(name+'.png')).read_bytes()
d.part.related_parts['rId8']._blob=latest.part.related_parts['rId8'].blob

# Add the new interface examples next to the matching original descriptions.
def newp(text,style='Normal'):return d.add_paragraph(text,style)
def pic(name,caption):
    p=newp('');p.add_run().add_picture(str(A/(name+'.png')),width=Cm(14.7));p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    return [p,newp(caption,'HITCFigureCaption')]
def after(anchor,paragraphs):
    e=anchor._p
    for p in paragraphs:e.addnext(p._p);e=p._p
after(mapped[215],[newp('Các nhóm chức năng được phân rã theo bốn tác nhân: Khách, Học viên, Giáo viên và Admin. Các sơ đồ ở mục 3.2 làm rõ mục tiêu của từng nhóm; đặc tả ở mục 3.3 trình bày điều kiện, luồng xử lý và kết quả của các nghiệp vụ chính.')])
after(mapped[371], [newp('4.2.7 Liên hệ và tư vấn trực tiếp','Heading 3'),newp('Người học mở trang liên hệ để gửi câu hỏi và tiếp tục trao đổi trong cuộc tư vấn riêng. Học viên xem lịch sử theo tài khoản; khách sử dụng cookie hoặc liên kết truy cập riêng. Tin nhắn mới được tải định kỳ, nội dung chỉ được đọc hoặc gửi khi có quyền phù hợp.')]+pic('ui-contact','Liên hệ và mở cuộc tư vấn'))
after(mapped[397],pic('ui-class-create','Tạo lớp với lịch học 246 hoặc 357'))
after(mapped[417],[newp('4.3.7 Tạo phòng thi và phân công chấm','Heading 3'),newp('Admin tạo ca thi với tên, phòng, ngày, giờ và sức chứa. Tại trang chi tiết, Admin chọn nhiều học viên chờ xếp và phân công giáo viên chấm cả lớp thi. Hệ thống kiểm tra trùng phòng, lịch giáo viên, lịch học viên và số chỗ còn lại trước khi lưu.')]+pic('ui-exam-create','Tạo lớp thi và phòng thi')+pic('ui-admin-tests','Danh sách phòng thi và yêu cầu chờ xếp')+[newp('4.3.8 Quản lý trao đổi tư vấn','Heading 3'),newp('Hộp thư tổng hợp cuộc tư vấn, tin gần nhất và số tin chưa đọc. Admin gửi câu trả lời trong trang chi tiết, có thể kết thúc hoặc mở lại. Tin của khách tạo trạng thái Pending, trả lời của Admin tạo Replied; cuộc đã Closed bị chặn gửi thêm tới khi được mở lại.')]+pic('ui-admin-consultations','Hộp thư tư vấn trực tiếp')+pic('ui-consultation-thread','Lịch sử trao đổi và ô trả lời tư vấn'))

# Rebuild consistent heading levels without deleting any of the author's paragraphs.
heading_updates={65:('1.1.1 Chuyển dịch mô hình quản lý sang nền tảng số',3),73:('1.1.2 Đồng bộ dữ liệu và kiểm soát sĩ số',3),76:('1.1.3 Phân quyền sử dụng hệ thống',3),82:('1.2 Khảo sát và đánh giá các hệ thống thực tế',2),83:('1.2.1 Website VUS',3),94:('1.2.2 Website ILA Vietnam',3),107:('1.3 Vấn đề tồn tại và giải pháp đề xuất',2),108:('1.3.1 Những vấn đề còn tồn tại',3),113:('1.3.2 Giải pháp công nghệ và nghiệp vụ',3),120:('1.4 Mục tiêu đối tượng và phạm vi',2),121:('1.4.1 Đối tượng người dùng mục tiêu',3),123:('1.4.2 Phạm vi đề tài',3),128:('1.4.3 Ý nghĩa thực tiễn',3),215:('3.1.2 Phân rã các nhóm chức năng',3),274:('4.2.1 Trang chủ khi chưa đăng nhập',3),292:('4.2.2 Trang chủ và tài khoản học viên',3),302:('4.2.3 Danh mục và chi tiết khóa học',3),321:('4.2.4 Đăng ký kiểm tra đầu vào',3),332:('4.2.5 Đăng ký khóa học và học phí',3),352:('4.2.6 Không gian học tập của học viên',3),372:('4.3 Phân hệ quản trị viên',2),374:('4.3.1 Bảng điều khiển quản trị',3),382:('4.3.2 Quản lý banner',3),390:('4.3.3 Chương trình lớp và lịch học',3),398:('4.3.4 Ghi danh học phí và tư vấn',3),403:('4.3.5 Hồ sơ giáo viên và học viên',3),407:('4.3.6 Thùng rác và dữ liệu đã xóa',3),418:('4.4 Phân hệ giáo viên',2),420:('4.4.1 Bảng điều khiển giáo viên',3),423:('4.4.2 Theo dõi lớp và học viên',3),426:('4.4.3 Chấm kiểm tra xếp lớp',3),429:('4.4.4 Tài liệu và phản hồi',3),432:('4.5 Xác thực và quản lý tài khoản',2),434:('4.5.1 Đăng nhập',3),441:('4.5.2 Đăng ký tài khoản',3),444:('4.5.3 Đổi mật khẩu và kiểm soát truy cập',3),448:('4.6 Kiểm thử hệ thống',2),450:('4.6.1 Mục tiêu và phương pháp',3),462:('4.6.2 Kịch bản kiểm thử',3)}
heading_updates.pop(83);heading_updates.pop(94);heading_updates.pop(107)
heading_updates[84]=('1.2.1 Website VUS',3)
heading_updates[96]=('1.2.2 Website ILA Vietnam',3)
heading_updates[108]=('1.3 Vấn đề tồn tại và giải pháp đề xuất',2)
heading_updates[109]=('1.3.1 Những vấn đề còn tồn tại',3)
for i,(t,level) in heading_updates.items():
    if i in mapped:change(i,t);mapped[i].style='Heading '+str(level)
mapped[273].style='Normal'
mapped[266].text='4.2 Giao diện khách và học viên'
# Keep title wording as a normal grouping label where deeper levels would be excessive.
for i in [130,192,470]:mapped[i].style='Heading 2'

# Captions remain paired with images; remove only redundant group captions, keeping their text as prose.
for i in [359,397,402,406,425,431]:
    mapped[i].style='Normal'
    change(i,re.sub(r'^Hình\s+4\.\d+\s*:\s*','Nhóm hình minh họa: ',mapped[i].text))
change(209,'Sơ đồ use case tổng quát hệ thống HITC English')
change(343,'Đăng ký khóa học theo nguyện vọng và cách đóng học phí')
change(371,'Hồ sơ cá nhân của học viên')
change(428,'Các lớp thi được phân công chấm')
change(447,'Đổi mật khẩu và kiểm soát truy cập')

# Preserve all seven original tables and their row structure. Amend stale test claims in place.
table_changes=[]
for ti,t in enumerate(d.tables):
    for ri,row in enumerate(t.rows):
        for ci,c in enumerate(row.cells):
            old=c.text;new=old
            new=re.sub(r'ĐẠT\s*\(Pass\)|Đạt\s*\(Pass\)|100% Pass|\bPASS\b','Cần kiểm tra lại',new)
            if old.strip().lower() in ['pass','đạt']:new='Cần kiểm tra lại'
            new=new.replace('11 bảng','16 bảng').replace('14 bảng','16 bảng').replace('kế thừa TPT','liên kết hồ sơ một–một')
            if new!=old:c.text=new;table_changes.append([ti,ri,ci,old,new])

# Keep the original test cases and examples, distinguish observations from test plans.
def cellset(table,row,col,value):
    old=table.rows[row].cells[col].text;table.rows[row].cells[col].text=value
    table_changes.append(['specific',row,col,old,value])
for t in d.tables:
    heads=[c.text.strip() for c in t.rows[0].cells]
    if 'Kết quả thực tế' in heads:
        actual=heads.index('Kết quả thực tế')
        for row in t.rows[1:]:
            code=row.cells[0].text
            if code not in ['TC-AUTH-02','TC-AUTH-04','TC-AUTH-05','TC-CUST-01','TC-CUST-03','TC-CUST-04','TC-TEACH-02']:
                old=row.cells[actual].text
                row.cells[actual].text='Chưa chạy lại ca này. Nội dung cần đối chiếu: '+old
                table_changes.append([code,'actual',old,row.cells[actual].text])
            for c in row.cells:
                old=c.text;new=old.replace('student1@hitc.edu.vn','hocvien1@gmail.com').replace('Nguyễn Văn An','Học Viên Nguyễn Văn 1')
                if new!=old:c.text=new
            if code=='TC-AUTH-04':
                row.cells[3].text='Chặn nội dung trái quyền; chuyển đến đăng nhập theo cookie vai trò đang thiếu.'
                row.cells[actual].text='Đã quan sát chuyển đến đăng nhập Admin; không mặc định mọi trường hợp trả trang 403.'
            elif code=='TC-CUST-01':
                row.cells[3].text='Tạo cuộc tư vấn Pending và tin nhắn đầu tiên; mở hội thoại riêng để trao đổi với Admin.'
                row.cells[actual].text='Đã kiểm tra tạo cuộc tư vấn và trao đổi hai chiều trên dữ liệu thử riêng.'
            elif code=='TC-CUST-02':
                row.cells[2].text='Chọn ngày từ ngày mai trở đi và khung giờ mong muốn trên biểu mẫu.'
                row.cells[3].text='Tạo PlacementTest Pending chờ Admin xếp phòng; chưa tự gửi email xác nhận.'
                row.cells[actual].text='Chưa chạy lại ca này trong lần rà soát báo cáo; luồng phòng thi đã được kiểm tra riêng.'
            elif code=='TC-CUST-03':
                row.cells[1].text='Đăng ký khóa học và gửi nguyện vọng'
                row.cells[2].text='Chọn chương trình, ngày bắt đầu, buổi, nhóm 246 hoặc 357 và cách đóng học phí.'
                row.cells[3].text='Tạo Registration Pending chưa gán ClassId và Payment Pending trong một giao dịch.'
                row.cells[actual].text='Đã kiểm tra luồng mới trên dữ liệu thử; chuyển tới hướng dẫn đóng học phí theo đơn.'
            elif code=='TC-CUST-04':
                row.cells[2].text='Admin xếp học viên vào lớp đã đạt MaxStudents.'
                row.cells[3].text='Từ chối xếp vượt sĩ số ở máy chủ; giữ đơn ở trạng thái phù hợp.'
                row.cells[actual].text='Đã kiểm tra điều kiện xếp lớp; không dùng thao tác chọn lớp tại trang công khai.'
            elif code=='TC-CUST-05':
                row.cells[2].text='Học viên chuyển khoản VietQR hoặc đóng tại trung tâm; Admin đối soát và xác nhận.'
                row.cells[actual].text='Đã xem biên lai mẫu; chưa thực hiện giao dịch ngân hàng thực tế trong lần rà soát này.'
            elif code=='TC-TEACH-01':
                row.cells[3].text='Yêu cầu phát triển: lưu ngày, buổi và trạng thái chuyên cần theo học viên.'
                row.cells[actual].text='Hiện mới có checkbox giao diện; chưa hiện thực lưu chuyên cần theo buổi.'
            elif code=='TC-TEACH-02':
                row.cells[2].text='Giáo viên được giao ca nhập điểm 7.5 và cấp độ IELTS 6.5+ cho bài của thí sinh.'
                row.cells[3].text='Cập nhật PlacementTest Completed; học viên xem điểm và cấp độ trong lịch sử kiểm tra.'
                row.cells[actual].text='Đã kiểm tra luồng chấm theo ca và quyền giáo viên trên dữ liệu thử riêng.'
            elif code=='TC-TEACH-03':
                row.cells[3].text='Tệp được lưu và gắn đúng lớp; giáo viên quản lý liên kết tải. Luồng học liệu riêng cho học viên cần bổ sung.'
            if len(row.cells)==6 and code in ['TC-AUTH-02','TC-AUTH-04','TC-AUTH-05']:row.cells[5].text='Đã quan sát'
            elif len(row.cells)==6 and code in ['TC-CUST-01','TC-CUST-03','TC-CUST-04']:row.cells[5].text='Đã kiểm tra luồng mới'
    if heads[:2]==['Thành phần','Công nghệ / Thư viện']:
        t.rows[0].cells[3].text='Vai trò trong dự án'
        t.rows[5].cells[0].text='Thư điện tử'
        t.rows[5].cells[3].text='Định hướng gửi thư xác nhận lịch thi và thông báo học phí; dịch vụ hiện chưa hoàn thiện.'
        t.rows[9].cells[3].text='Hỗ trợ mô tả và kiểm tra endpoint trong môi trường phát triển.'

# Layout is tightened through spacing and picture size, never by shortening narrative.
for name,size in [('Normal',13),('Heading 1',15),('Heading 2',14),('Heading 3',13),('Title',18),('HITCFigureCaption',11)]:
    st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
    for e in list(st.element.iter(qn('w:pBdr'))):e.getparent().remove(e)
main=False;fig=0
for p in d.paragraphs:
    if p.style.name=='Heading 1' and p.text=='MỞ ĐẦU':main=True
    if not main:continue
    f=p.paragraph_format;pr=p._p.get_or_add_pPr()
    for n in list(pr.findall(qn('w:numPr'))):pr.remove(n)
    np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);pr.append(np)
    f.left_indent=Cm(0);f.right_indent=Cm(0);f.page_break_before=False
    if p.style.name.startswith('Heading'):
        f.keep_with_next=True;f.keep_together=True;f.first_line_indent=Cm(0);f.line_spacing=1.05;f.space_before=Pt(8);f.space_after=Pt(4)
        if p.style.name=='Heading 1':f.page_break_before=True
    elif p._p.xpath('.//w:drawing'):
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.first_line_indent=Cm(0);f.line_spacing=1;f.space_after=Pt(2);f.space_before=Pt(2);f.keep_with_next=True
    elif p.style.name=='HITCFigureCaption':
        fig+=1;title=re.sub(r'^(?:Hình|Hình)\s*[\d.a-zA-Z]*\s*[:.]?\s*','',p.text.strip());p.clear();p.add_run('Hình ')
        def fld(tag,val=None):
            x=OxmlElement(tag)
            if val:x.set(qn('w:fldCharType'),val)
            p.add_run()._r.append(x);return x
        fld('w:fldChar','begin');fld('w:instrText').text=' SEQ Hinh \\* ARABIC ';fld('w:fldChar','separate');p.add_run(str(fig));fld('w:fldChar','end');p.add_run('. '+title)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER;f.first_line_indent=Cm(0);f.line_spacing=1.05;f.space_before=Pt(1);f.space_after=Pt(5);f.keep_with_next=False;f.keep_together=True
        for r in p.runs:r.font.size=Pt(11);r.italic=True
    else:
        f.first_line_indent=Cm(.65);f.line_spacing=1.12;f.space_before=Pt(0);f.space_after=Pt(2);f.keep_with_next=False;f.keep_together=False;f.widow_control=True;p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p.runs:
        r.font.name='Times New Roman';r.font.color.rgb=RGBColor(0,0,0)
        if not p.style.name.startswith('Heading') and p.style.name!='HITCFigureCaption':r.font.size=Pt(13)
for shape in d.inline_shapes:
    rid=shape._inline.xpath('.//a:blip/@r:embed')[0]
    if rid=='rId8':continue
    im=Image.open(BytesIO(d.part.related_parts[rid].blob));w=14.7;h=w*im.height/im.width
    if h>16.2:w*=16.2/h;h=16.2
    shape.width=Cm(w);shape.height=Cm(h)
for t in d.tables:
    for j,row in enumerate(t.rows):
        tr=row._tr.get_or_add_trPr();tr.append(OxmlElement('w:cantSplit'))
        if j==0:tr.append(OxmlElement('w:tblHeader'))
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_before=Pt(1);p.paragraph_format.space_after=Pt(2);p.paragraph_format.first_line_indent=Cm(0)
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10.5);r.font.color.rgb=RGBColor(0,0,0)
for x in d.element.xpath('//w:instrText'):
    if x.text and 'TOC' in x.text and '\\o' in x.text:x.text=' TOC \\o "1-3" \\h \\z \\u '

# Every original nonempty paragraph still has a physical element in this document.
missing=[i for i,p in mapped.items() if p._p.getparent() is None]
assert not missing,missing
assert len(mapped)==494
d.core_properties.title='Báo cáo HITC English khôi phục đầy đủ nội dung gốc';d.core_properties.author='Nguyễn Khánh Huy'
out=R/'full-restored-draft.docx';d.save(out)
audit={'source_paragraphs':494,'original_paragraphs_retained':len(mapped),'deleted_original_paragraphs':missing,'updated_paragraphs':changes,'table_cell_updates':table_changes,'figures':fig,'body_words_without_cached_contents':sum(len(p.text.split()) for p in d.paragraphs if not p.style.name.lower().startswith('toc'))}
(R/'full-restoration-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print('Original paragraphs retained',len(mapped),'Deleted',len(missing),'Updated',len(changes),'Figures',fig,'Words',audit['body_words_without_cached_contents'])
print(out)
