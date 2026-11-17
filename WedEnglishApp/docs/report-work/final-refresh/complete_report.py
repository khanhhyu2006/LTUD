from pathlib import Path
from copy import deepcopy
import re,json,io
from PIL import Image
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

R=Path(__file__).resolve().parent; A=R/'assets'; ROOT=R.parents[2]
d=Document(ROOT/'Bao_cao_HITC_English_50_trang_noi_dung.docx'); ps=list(d.paragraphs)
# Remove the scan edge beneath the retained school logo without changing its size.
logo=Image.open(io.BytesIO(d.part.related_parts['rId8'].blob)).convert('RGB')
logo.paste('white',(0,logo.height-3,logo.width,logo.height));logo_buffer=io.BytesIO();logo.save(logo_buffer,format='PNG');d.part.related_parts['rId8']._blob=logo_buffer.getvalue()
def setp(i,t):ps[i].text=t
updates={
98:'Học viên: Cập nhật hồ sơ, đăng ký khóa học theo ngày bắt đầu và lịch mong muốn; theo dõi lớp được xếp, thời khóa biểu, học phí, biên lai, kết quả kiểm tra và các cuộc tư vấn.',
100:'Admin: Quản lý đào tạo, tài khoản, ghi danh, xếp lớp, lịch học, học phí, phòng thi, phân công giáo viên, lương, tư vấn, banner và thùng rác.',
105:'Giới hạn: Kiểm tra đầu vào gồm đăng ký, xếp phòng và nhập điểm; chưa tổ chức đề thi trực tuyến tự chấm. Học phí hiện nhận tại trung tâm hoặc qua VietQR và được Admin xác nhận thủ công.',
113:'Quy trình bắt đầu khi khách tra cứu khóa học và trao đổi tư vấn. Học viên đăng ký chương trình, khai báo ngày có thể bắt đầu, buổi và nhóm thứ mong muốn. Admin tiếp nhận đơn, lựa chọn lớp phù hợp và phân công giáo viên. Việc xác nhận thu học phí được thực hiện riêng với việc xếp lớp.',
133:'Dữ liệu tuyển sinh: Lưu yêu cầu và lịch sử tin nhắn giữa khách hoặc học viên với Admin; theo dõi trạng thái và số tin chưa đọc.',
134:'Dữ liệu đào tạo: Tổ chức chương trình cho các nhóm tuổi, lớp học, lịch 2–4–6 hoặc 3–5–7 và giáo viên; điều phối học viên từ đơn đăng ký khóa học.',
153:'Lược đồ dữ liệu: ApplicationDbContext khai báo thực thể và quan hệ. Dự án có thư mục Migrations; các đợt bổ sung ghi danh, phòng thi và tư vấn sử dụng script SQL nâng cấp để giữ dữ liệu cũ, thay vì xóa rồi tạo lại cơ sở dữ liệu.',
154:'Tổ chức nghiệp vụ: Controller điều phối yêu cầu; các dịch vụ CourseClassAssignment, ClassSchedulePlanner và ExamSessionPlanner tập trung kiểm tra xếp lớp, lịch học và phòng thi. ConsultationAccess và ConsultationMessaging kiểm soát quyền truy cập, lưu tin nhắn.',
163:'Giao dịch: Tạo đơn và học phí được thực hiện trong cùng transaction. Các thao tác xếp lớp và xếp nhiều thí sinh vào phòng cũng dùng giao dịch để tránh lưu một phần khi xảy ra lỗi. Khóa ngoại, chỉ mục và điều kiện trạng thái bổ sung kiểm soát ở tầng dữ liệu.',
170:'Hiển thị QR: Sau khi xác nhận đăng ký, trang học phí hiển thị thông tin đóng tiền. Với VietQR, nội dung chuyển khoản gắn mã đơn để Admin đối chiếu; QR chỉ hỗ trợ chuyển khoản, không xác nhận tiền đã về. [10]',
172:'Phạm vi hiện tại: Đơn mới chỉ chọn đóng tại trung tâm hoặc VietQR. Các bản ghi VNPay/MoMo cũ được giữ để đối chiếu lịch sử; chưa có IPN tự động. EmailService chưa có luồng gửi thư hoàn chỉnh.',
186:'Khách xem trang chủ, tìm kiếm và lọc chương trình, tra cứu học phí và lớp tham khảo. Khách có thể gửi yêu cầu tư vấn, tiếp tục trao đổi với Admin trong cuộc hội thoại riêng và đăng ký tài khoản Student. Liên kết riêng và cookie truy cập giúp khách xem lại tư vấn trên trình duyệt mà không phải có tài khoản.',
190:'Học viên đăng ký khóa học, không chọn lớp hoặc giáo viên. Biểu mẫu lưu ngày có thể bắt đầu, buổi học, nhóm 2–4–6 hoặc 3–5–7 và ghi chú. Sau đó học viên theo dõi đơn chờ xếp, lớp được Admin xác nhận, học phí, biên lai, lịch học và lịch thi. Học viên còn đăng ký kiểm tra đầu vào, xem điểm, gửi đánh giá và trao đổi tư vấn theo tài khoản.',
194:'Giáo viên theo dõi lớp phụ trách, danh sách học viên, lịch dạy và tài liệu. Đối với kiểm tra đầu vào, giáo viên mở lớp thi được phân công, xem danh sách thí sinh và nhập điểm cùng cấp độ đề xuất. Giáo viên có thể xem phản hồi của các lớp liên quan và bảng lương cá nhân. Giao diện điểm danh hiện chưa lưu chuyên cần theo buổi.',
198:'Admin quản lý chương trình, lớp học, lịch trong tuần, giáo viên và học viên. Admin tiếp nhận đơn đăng ký theo nguyện vọng, xếp lớp, đối soát học phí; tạo phòng thi, xếp nhiều thí sinh và phân công giáo viên chấm cả lớp thi. Các nhóm chức năng khác gồm trả lời tư vấn, quản lý lương, thống kê, banner và thùng rác.',
207:'3.3.2 Đăng ký khóa học và gửi nguyện vọng',
209:'Điều kiện trước: Có phiên Student hợp lệ và chương trình đang tuyển sinh. Ngày có thể bắt đầu không trước ngày hiện tại; chọn buổi, nhóm lịch 246 hoặc 357 và cách đóng học phí hợp lệ.',
210:'Luồng xử lý: Học viên điền ngày bắt đầu, buổi, nhóm thứ và ghi chú; ảnh hồ sơ là tùy chọn. Máy chủ lấy học phí từ chương trình, kiểm tra đơn trùng và tạo Registration cùng Payment trong một giao dịch. Đơn mới Pending, ProgramId được lưu và ClassId để trống; học viên được chuyển tới hướng dẫn đóng học phí.',
211:'Kết quả và ngoại lệ: Đơn được hiển thị ở khu vực chờ xếp lớp. Dữ liệu sai hoặc đăng ký trùng khóa học đang hoạt động bị từ chối. Thanh toán và xếp lớp không tự động xác nhận lẫn nhau; Admin thực hiện từng nghiệp vụ sau khi kiểm tra.',
215:'Luồng xử lý: Admin kiểm tra số tiền, mã đơn và chứng từ rồi xác nhận Payment Paid. Hệ thống giữ trạng thái xếp lớp độc lập: đơn chưa được bố trí lớp vẫn Pending. Học viên xem học phí và biên lai theo quyền sở hữu tài khoản.',
219:'Điều kiện trước: Học viên có tài khoản và chưa có yêu cầu kiểm tra đang chờ xử lý. Ngày mong muốn từ ngày mai trở đi; Admin cần tạo ca thi với phòng, thời gian, sức chứa trước khi xếp thí sinh.',
220:'Luồng xử lý: Học viên gửi ngày và giờ mong muốn. Admin tạo ExamSession, chọn nhiều yêu cầu để xếp vào phòng và phân công một giáo viên chấm cả ca. Hệ thống kiểm tra sức chứa, ngày yêu cầu, lịch phòng, giáo viên và lịch học viên. Giáo viên mở ca được giao, nhập điểm từ 0 đến 10 và cấp độ đề xuất cho từng bài.',
221:'Kết quả: Lịch thi chính thức xuất hiện sau khi xếp phòng. Từng PlacementTest chuyển Completed khi chấm; ca thi hoàn tất khi tất cả bài được chấm. Không đổi người chấm khi ca đã có điểm và không đưa bài đã chấm về danh sách chờ.',
233:'Mô hình hiện tại có 16 bảng nghiệp vụ: tài khoản, học viên, giáo viên, chương trình, lớp, ghi danh, học phí, lịch học, tài liệu, phòng thi, bài kiểm tra, phản hồi, lương, tư vấn, tin nhắn và banner. Hai hình sau tách nhóm đào tạo khỏi nhóm hỗ trợ để giữ chữ dễ đọc; các quan hệ chi tiết được đối chiếu trong từ điển dữ liệu.',
239:'Programs liên kết một–nhiều với Classes và Registrations. Đơn đăng ký bắt buộc có ProgramId nhưng ClassId có thể trống trong thời gian chờ xếp. EarliestStartDate, PreferredSession và PreferredDays lưu nguyện vọng. Lớp có lịch tại ClassSchedules; Payment có RegistrationId duy nhất. DesiredTeacherId được giữ cho dữ liệu cũ, không còn là lựa chọn ở biểu mẫu mới.',
241:'ExamSessions lưu lớp thi, phòng, ngày giờ, sức chứa và giáo viên được phân công; PlacementTests gắn yêu cầu và kết quả của từng học viên với ca thi. Consultations lưu chủ cuộc tư vấn và trạng thái; ConsultationMessages lưu người gửi, nội dung và thời điểm. Các bảng phản hồi, lương, tài liệu và banner phục vụ vận hành, không thay thế dữ liệu ghi danh hoặc học phí.',
248:'Khóa ngoại bảo đảm đơn thuộc đúng học viên và chương trình. ClassId có thể trống nhưng khi được gán phải thuộc ProgramId của đơn. Payment liên kết duy nhất với Registration. Các ràng buộc trạng thái, mức phí, sĩ số và giờ học ngăn dữ liệu ngoài phạm vi cho phép. Xóa mềm và xóa vật lý được xử lý riêng theo quan hệ.',
249:'Luồng ghi danh gồm tra cứu chương trình, gửi nguyện vọng, tạo đơn và học phí, Admin xếp lớp và đối soát thu tiền. Luồng thi gồm đăng ký, tạo ca, xếp thí sinh, phân công và nhập điểm. Luồng tư vấn gồm mở cuộc hội thoại, trao đổi, đánh dấu đã đọc, kết thúc hoặc mở lại. Lương giáo viên là nghiệp vụ riêng với thu học phí.',
251:'Tạo đơn và học phí: Lưu trong một transaction, bảo đảm cùng thành công hoặc cùng hoàn tác. Đơn mới bắt đầu Pending và chưa có ClassId; không tin học phí hoặc trạng thái do biểu mẫu tự gửi lên.',
252:'Xác nhận thu: Admin đối soát trước khi chuyển Paid. Các đơn và biên lai đã thanh toán từ trước được giữ nguyên để đối chiếu, kể cả một số ghi danh trùng trong lịch sử; quy tắc chống trùng áp dụng cho thao tác mới.',
253:'Xếp lớp: Kiểm tra đúng khóa học, trạng thái lớp, sĩ số còn trống và ngày khai giảng từ EarliestStartDate trở đi. Buổi và nhóm thứ là nguyện vọng để Admin cân nhắc; lớp chưa có lịch chi tiết vẫn có thể được xếp. Khi lịch đã có, kiểm tra xung đột với lớp đã xác nhận của học viên.',
260:'Phạm vi đánh giá: Quy tắc ghi danh, xếp lớp, lịch học, phòng thi và tư vấn đã được bổ sung ở các dịch vụ tương ứng. Những hạng mục chưa hoàn thiện như điểm danh theo buổi, gửi email và đối soát ngân hàng tự động được phân biệt với chức năng đã triển khai.',
262:'Phiên bản hiện tại đã tách đăng ký khóa học khỏi xếp lớp, bổ sung lịch học theo hai nhóm thứ, phòng thi và trao đổi tư vấn hai chiều. PlacementTest vẫn là yêu cầu kiểm tra và kết quả do giáo viên nhập, chưa có bộ đề trực tuyến tự chấm. Checkbox điểm danh chưa tạo bản ghi chuyên cần theo ngày hoặc buổi.',
263:'VietQR hiển thị hướng dẫn chuyển khoản; Admin xác nhận khoản thu. EmailService và các dịch vụ cổng thanh toán chưa có tích hợp tự động hoàn chỉnh. Quyền tải tài liệu riêng trong khu vực học viên và khóa/mở tài khoản giáo viên còn cần hoàn thiện. Các hạn chế này được đưa vào hướng phát triển thay vì mô tả như tính năng đã có.',
269:'Cơ sở dữ liệu: SQL Server LocalDB với EnglishCenterDb. ApplicationDbContext ánh xạ dữ liệu; DbInitializer cung cấp dữ liệu ban đầu. Script nâng cấp lược đồ được áp dụng có kiểm soát, kèm sao lưu và ghi nhận đợt nâng cấp để tránh ghi lại dữ liệu nhiều lần.',
274:'Các thành phần dưới đây được đối chiếu với tệp dự án và giao diện đang chạy. Phụ thuộc được khai báo chưa đồng nghĩa đã có nghiệp vụ tích hợp hoàn chỉnh, đặc biệt với gửi email và cổng thanh toán.',
281:'Giao diện được chia theo nhóm sử dụng, có thanh điều hướng và biểu mẫu nhất quán. Các hình hiện thực trong chương này được chụp từ phiên bản ứng dụng cục bộ ngày 04/11/2026, sử dụng dữ liệu trình diễn. Hình được đặt cùng phần mô tả đầu vào, xử lý và kết quả của chức năng.',
288:'Tư vấn: Trang liên hệ tạo cuộc hội thoại với Admin. Khách truy cập bằng liên kết hoặc cookie riêng; học viên xem lịch sử theo tài khoản. Tin nhắn được cập nhật định kỳ tại trình duyệt, không tự gửi email cho người liên hệ.',
302:'Điều hướng: Các lớp chỉ cung cấp lịch tham khảo. Nút đăng ký thuộc chương trình và mở biểu mẫu nguyện vọng; học viên không phải chọn một lớp cụ thể trước khi gửi đơn.',
306:'Học viên: Chọn ngày và một ca giờ mong muốn, sau đó theo dõi yêu cầu đang chờ xếp phòng hoặc lịch thi chính thức được Admin xác nhận.',
307:'Xử lý: BookTest kiểm tra ngày từ ngày mai trở đi và ngăn nhiều yêu cầu Pending của cùng học viên. Admin bố trí phòng, lớp thi và người chấm trong phân hệ quản trị.',
308:'Giới hạn: Giáo viên được phân công nhập điểm và cấp độ đề xuất. Hệ thống chưa cung cấp bộ đề trực tuyến tự chấm hoặc gửi email xác nhận tự động.',
312:'Checkout: Chọn ngày có thể bắt đầu, buổi học, nhóm 2–4–6 hoặc 3–5–7, ghi chú và cách đóng học phí. Không có trường chọn lớp hay chọn giáo viên; ảnh hồ sơ là tùy chọn.',
313:'Ghi dữ liệu: Confirm kiểm tra chương trình, dữ liệu và đăng ký trùng; tạo Registration Pending cùng Payment Pending trong transaction. Sau đó chuyển sang trang hướng dẫn tiền mặt hoặc VietQR theo lựa chọn.',
314:'Theo dõi: Admin xếp lớp đúng khóa học, ngày bắt đầu và sĩ số; lịch chính thức hiển thị sau khi đơn Confirmed. Việc xác nhận Paid là thao tác riêng, có căn cứ thu tiền; ảnh QR không phải bằng chứng thanh toán.',
323:'Lớp học: Phân biệt đơn chờ xếp với lớp đã được Admin xác nhận. Thẻ chờ hiển thị chương trình, ngày có thể bắt đầu, buổi, nhóm thứ và tình trạng học phí.',
324:'Lịch tuần: Lấy các ClassSchedules của lớp đã được xếp và lịch kiểm tra đã có phòng. Khi Admin lưu lịch 246 hoặc 357, các ca được dùng thống nhất trong thời khóa biểu; đơn chờ xếp chưa có lịch lớp chính thức.',
354:'Lớp: Nhập chương trình, phòng, sĩ số, ngày bắt đầu và kết thúc; giáo viên có thể phân công sau. Chọn lịch 2–4–6 hoặc 3–5–7 cùng giờ bắt đầu, kết thúc để tạo ba ca trong ClassSchedules.',
355:'Ràng buộc: Kiểm tra khoảng ngày, giờ kết thúc sau giờ bắt đầu, lịch trùng phòng hoặc giáo viên và học viên liên quan. Tạo hoặc cập nhật lịch được lưu cùng giao dịch; chương trình của lớp đã tạo không được đổi tùy tiện.',
361:'Ghi danh: Xem đơn theo chương trình và nguyện vọng, sau đó xếp hoặc chuyển sang lớp phù hợp. Khi trả về chờ xếp hoặc hủy, liên kết ClassId được bỏ theo nghiệp vụ; trạng thái học phí vẫn được theo dõi riêng.',
363:'Tư vấn: Admin mở cuộc hội thoại, đọc lịch sử và gửi trả lời; có số tin chưa đọc, thao tác kết thúc hoặc mở lại. Người dùng nhận nội dung trong trang tư vấn; hệ thống chưa gửi thư điện tử tự động.',
395:'Phân công: Giáo viên xem danh sách lớp thi được giao, mở từng ca để xem thí sinh. Truy vấn kiểm tra TeacherId của ca; giáo viên khác không được chấm thay bằng cách đổi ID.',
396:'Kết quả: Nhập điểm 0–10 và cấp độ đề xuất cho từng thí sinh. Khi chấm xong toàn bộ, trạng thái ca chuyển Completed. Hệ thống chưa lưu bảng điểm riêng cho bốn kỹ năng hoặc tự chấm đề thi trực tuyến.',
430:'Quan sát giao diện: Đăng nhập bằng các tài khoản mẫu và mở các trang ở cả ba vai trò. Ảnh chụp và mã phản hồi được lưu để đối chiếu với các chức năng mô tả trong báo cáo.',
432:'Kiểm tra nghiệp vụ: Các luồng mới được chạy với cơ sở dữ liệu kiểm thử riêng. Bộ kiểm tra tư vấn ghi nhận 31 kiểm tra đạt, gồm trao đổi hai chiều, phân quyền, giới hạn nội dung và đóng/mở hội thoại. Chưa có kết quả kiểm thử tải hoặc đo độ trễ để kết luận về hiệu năng vận hành.',
440:'Chương 4 trình bày giao diện thực tế theo vai trò và các tình huống kiểm tra. Các luồng mới đã được đối chiếu bằng mã nguồn, thao tác và dữ liệu kiểm thử riêng. Kết quả này xác nhận phạm vi đã kiểm tra, không thay thế kiểm thử tải hoặc đánh giá an toàn cho môi trường vận hành thương mại.',
444:'Dữ liệu: Thiết kế 16 bảng nghiệp vụ trên SQL Server; bổ sung liên kết chương trình trong ghi danh, lớp thi và tin nhắn tư vấn, đồng thời giữ các đơn và biên lai đã thanh toán để đối chiếu.',
445:'Chức năng: Đăng ký khóa học theo nguyện vọng, Admin xếp lớp, tạo lịch tuần, xếp phòng thi và phân công chấm; theo dõi học phí, tài liệu, phản hồi, lương và trao đổi tư vấn hai chiều.',
449:'Thanh toán: Hiện nhận tiền mặt hoặc VietQR với xác nhận nội bộ; chưa tự đối soát ngân hàng hoặc nhận IPN từ cổng thanh toán.',
450:'Vận hành: Cần bổ sung nhật ký thao tác đầy đủ, giám sát và thử phục hồi sao lưu; tiếp tục kiểm tra quyền từng bản ghi ở các phân hệ tài liệu và quản trị.',
453:'Ưu tiên trước: Hoàn thiện chuyên cần theo buổi, luồng học liệu cho học viên và bộ kiểm thử hồi quy cho ghi danh, lịch học, phòng thi, học phí và tư vấn.',
}
for i,t in updates.items():setp(i,t)
# Update captions without retaining stale cached sequence fields.
captions={235:'Lược đồ nhóm tài khoản đào tạo và học phí',285:'Trang chủ HITC English',291:'Menu tài khoản học viên',299:'Danh mục chương trình và bộ lọc',304:'Chi tiết chương trình và lớp tham khảo',310:'Đăng ký kiểm tra xếp lớp',316:'Đăng ký khóa học theo nguyện vọng và cách đóng học phí',321:'Biên lai học phí nội bộ',327:'Đơn chờ xếp và các lớp của học viên',329:'Thời khóa biểu học và kiểm tra',334:'Lịch sử học phí',339:'Hồ sơ học viên',346:'Bảng điều khiển quản trị',351:'Quản lý banner',357:'Quản lý chương trình đào tạo',359:'Danh sách lớp và phân công giáo viên',365:'Tiếp nhận đơn và xếp lớp',367:'Đối soát và xác nhận học phí',372:'Quản lý giáo viên',374:'Quản lý học viên',380:'Thùng rác dữ liệu',386:'Bảng điều khiển giáo viên',391:'Các lớp được phân công giảng dạy',393:'Danh sách học viên của lớp',398:'Các lớp thi được phân công chấm',403:'Quản lý tài liệu lớp học',405:'Phản hồi của học viên',407:'Bảng lương cá nhân giáo viên',409:'Quản lý lương tại Admin',416:'Đăng nhập theo vai trò',421:'Đăng ký tài khoản học viên',426:'Đổi mật khẩu'}
for i,t in captions.items():setp(i,'Hình. '+t)

# Replace screenshots and drawings while keeping original textual structure.
names=['home','home-student','programs','detail','test','checkout','receipt','myclasses','schedule','payments','profile','admin-dashboard','admin-banners','admin-programs','admin-classes','admin-registrations','admin-payments','admin-teachers','admin-students','admin-trash','teacher-dashboard','teacher-classes','teacher-students','teacher-tests','teacher-documents','teacher-feedback','teacher-salary','admin-salaries','login','register','change-password']
repls={f'rId{i}':A/f'ui-{name}.png' for i,name in zip(range(21,52),names)}
repls.update({f'rId{i}':A/f'{name}.png' for i,name in zip(range(15,21),['uc-overview','uc-guest','uc-student','uc-teacher','uc-admin','data-model'])})
for rid,path in repls.items():
    assert path.exists(),path
    im=Image.open(path).convert('RGB');buf=io.BytesIO();im.save(buf,format='PNG');d.part.related_parts[rid]._blob=buf.getvalue()
    for shape in d.inline_shapes:
        if shape._inline.xpath('.//a:blip/@r:embed')==[rid]:
            w=15.7;h=w*im.height/im.width
            if h>17.8:w*=17.8/h;h=17.8
            shape.width=Cm(w);shape.height=Cm(h)

def para(text,style='Normal'):
    return d.add_paragraph(text,style)
def before(i,text,style='Normal'):
    p=para(text,style);ps[i]._p.addprevious(p._p);return p
def after(i,items):
    anchor=ps[i]._p
    for p in items:anchor.addnext(p._p);anchor=p._p
def figure(name,caption,width=15.7):
    p=para('');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    im=Image.open(A/(name+'.png'));height=width*im.height/im.width
    if height>17.8:width*=17.8/height
    p.add_run().add_picture(str(A/(name+'.png')),width=Cm(width));p.paragraph_format.keep_with_next=True
    return [p,para('Hình. '+caption,'HITCFigureCaption')]

# Three-level headings use the same hierarchy as the supplied layout example.
for i,t in [(113,'1.1.1 Chuyển đổi quy trình quản lý'),(115,'1.1.2 Tập trung và liên kết dữ liệu'),(116,'1.1.3 Phân quyền và điều kiện nghiệp vụ'),(146,'2.1.1 Mô hình khách và máy chủ'),(148,'2.1.2 Tổ chức theo MVC và Areas'),(151,'2.2.1 Ngôn ngữ C#'),(152,'2.2.2 Ánh xạ và truy vấn dữ liệu'),(156,'2.3.1 Razor và Bootstrap'),(158,'2.3.2 JavaScript và biểu đồ'),(160,'2.4.1 Lưu trữ và quan hệ'),(163,'2.4.2 Tính nhất quán của giao dịch'),(165,'2.5.1 Cookie và định tuyến vai trò'),(167,'2.5.2 Mật khẩu và bảo vệ biểu mẫu')]:before(i,t,'Heading 3')
before(173,'2.7 Cập nhật tư vấn và bảo toàn dữ liệu','Heading 2')
before(173,'2.7.1 Truy vấn tin nhắn định kỳ','Heading 3')
before(173,'Giao diện tư vấn gửi yêu cầu lấy tin mới khoảng mỗi hai giây, sử dụng mã tin cuối đã nhận để lấy phần phát sinh. Cách này tận dụng các action HTTP và cơ chế cookie sẵn có của ứng dụng MVC. Hộp thư Admin kiểm tra thay đổi khoảng mỗi năm giây. Đây là cơ chế polling, chưa phải kết nối liên tục bằng WebSocket.')
before(173,'Tin nhắn được lưu tại ConsultationMessages, còn cuộc tư vấn giữ trạng thái và mốc đã đọc của từng phía. Nội dung được mã hóa khi hiển thị và chèn bằng textContent ở trình duyệt. Quyền đọc, gửi và đánh dấu đã đọc phải được kiểm tra lại tại máy chủ; việc biết mã cuộc tư vấn không tự cấp quyền truy cập.')
before(173,'2.7.2 Nâng cấp lược đồ có giữ lịch sử','Heading 3')
before(173,'Khi đổi nghiệp vụ từ chọn lớp sang đăng ký khóa học, dữ liệu cần bổ sung ProgramId và cho phép ClassId để trống. Các liên kết cũ được điền lại từ lớp đã có; đơn và biên lai đã thanh toán được giữ để đối chiếu. Lớp thi và tin nhắn được bổ sung bằng bảng riêng, tránh ghép nhiều bản ghi khác bản chất trong cùng một trường.')
before(173,'Mỗi lần nâng cấp cần sao lưu, kiểm tra dữ liệu trước và sau khi áp dụng, đồng thời ghi nhận script đã chạy. Việc tồn tại bản sao lưu chưa chứng minh khả năng phục hồi; thử khôi phục trên môi trường riêng vẫn là bước cần thiết trước khi đưa hệ thống vào sử dụng thực tế.')

after(235,figure('data-support','Lược đồ nhóm kiểm tra tư vấn và hỗ trợ',width=14))
after(211,[para('3.3.3 Xếp lớp theo đơn đăng ký','Heading 3'),para('Tác nhân chính là Admin. Hệ thống đối chiếu chương trình, ngày khai giảng, sĩ số và lịch của học viên trước khi gán ClassId. Ngày khai giảng bằng hoặc sau ngày học viên có thể bắt đầu là phù hợp. Buổi và thứ được hiển thị để Admin trao đổi, cân nhắc; chúng không tự động loại lớp chưa có thời khóa biểu. Sau khi lưu, đơn chuyển Confirmed và lớp xuất hiện trong tài khoản học viên.')])
after(231,[para('3.3.8 Tư vấn trực tiếp với khách và học viên','Heading 3'),para('Người dùng gửi thông tin liên hệ và câu hỏi để mở cuộc tư vấn. Học viên được nhận diện theo tài khoản; khách được cấp quyền bằng cookie và liên kết riêng, không dựa vào email tự khai. Admin mở hộp thư và gửi trả lời. Mỗi tin nhắn được lưu riêng; giao diện lấy phần phát sinh định kỳ mà không tải lại toàn bộ trang.'),para('Nội dung được giới hạn 2000 ký tự và hiển thị dưới dạng văn bản. Khi Admin kết thúc, máy chủ từ chối tin gửi tiếp cho đến khi mở lại. Yêu cầu xem, gửi và đánh dấu đã đọc phải được kiểm tra quyền; liên kết không hợp lệ không được tiết lộ lịch sử.')])
# Re-sequence the remaining use case headings.
for i,n in [(212,4),(217,5),(222,6),(227,7)]:ps[i].text=re.sub(r'^3\.3\.\d+',f'3.3.{n}',ps[i].text)
after(249,figure('enrollment-flow','Luồng đăng ký xếp lớp và xác nhận học phí độc lập'))

# Align chapter four into real second and third level sections.
for i in [282,340,381,410]:
    if i==282:ps[i]._p.getparent().remove(ps[i]._p)
    else:ps[i].style='Heading 2'
setp(280,'4.2 Giao diện khách và học viên');setp(340,'4.3 Giao diện quản trị viên');setp(381,'4.4 Giao diện giáo viên');setp(410,'4.5 Xác thực tài khoản');setp(427,'4.6 Kiểm tra hệ thống')
groups={2:[283,289,295,300,305,311,317,322,330,335],3:[341,347,352,360,368,375],4:[382,387,394,399],5:[411,417,422]}
for section,ids in groups.items():
    for j,i in enumerate(ids,1):ps[i].text=f'4.{section}.{j} '+re.sub(r'^[A-J]\.\s*','',ps[i].text)
setp(311,'4.2.6 Đăng ký khóa học và học phí')
setp(428,'4.6.1 Mục tiêu và phương pháp kiểm tra');setp(433,'4.6.2 Kịch bản kiểm tra theo phân hệ')
after(339,[para('4.2.11 Liên hệ và tư vấn','Heading 3'),para('Người học hoặc khách nhập câu hỏi tại trang liên hệ. Sau khi gửi hợp lệ, hệ thống mở cuộc trao đổi riêng với Admin. Học viên có mục Tư vấn của tôi; khách giữ liên kết riêng để truy cập lại. Nội dung phản hồi xuất hiện trong cuộc hội thoại, không phải một thông báo đã liên hệ thay cho câu trả lời.')]+figure('ui-contact','Liên hệ và mở cuộc tư vấn'))
after(359,[para('Lịch học được thiết lập ngay trên biểu mẫu tạo hoặc sửa lớp. Nhóm 246 tương ứng thứ Hai, Tư, Sáu; nhóm 357 tương ứng thứ Ba, Năm, Bảy. Ba ca có chung khung giờ và được áp dụng cho lịch tuần trong khoảng ngày của lớp. Việc gán giáo viên có thể thực hiện sau.')]+figure('ui-class-create','Tạo lớp và chọn lịch học trong tuần'))
after(380,[para('4.3.7 Tổ chức phòng thi và phân công chấm','Heading 3'),para('Admin tạo lớp thi với tên, phòng, ngày, giờ và sức chứa. Tại trang chi tiết, Admin chọn nhiều học viên chờ xếp rồi xác nhận, sau đó phân công giáo viên chấm cả ca. Hệ thống không tự tạo phòng hoặc người chấm từ yêu cầu của học viên.')]+figure('ui-exam-create','Tạo lớp thi và phòng thi')+[para('Danh sách ca thi cho biết sĩ số, giáo viên và tiến độ chấm. Các lịch trùng hoặc lựa chọn vượt sức chứa phải được xử lý trước khi lưu; yêu cầu chưa xếp vẫn nằm trong danh sách chờ.')]+figure('ui-admin-tests','Quản lý ca thi và danh sách chờ xếp phòng')+[para('4.3.8 Trao đổi tư vấn với người học','Heading 3'),para('Hộp thư tư vấn hiển thị người liên hệ, câu hỏi gần nhất và số tin chưa đọc. Admin mở từng cuộc hội thoại để xem lịch sử và gửi nội dung trả lời, có thể kết thúc hoặc mở lại khi cần. Việc tải tin mới dùng truy vấn định kỳ; đây chưa phải kết nối WebSocket hoặc SignalR.')]+figure('ui-admin-consultations','Hộp thư tư vấn của Admin')+figure('ui-consultation-thread','Chi tiết cuộc tư vấn và ô trả lời'))
before(406,'4.4.5 Theo dõi lương giảng dạy','Heading 3')
before(406,'Giáo viên xem các kỳ lương và trạng thái chi trả của mình; Admin tạo kỳ lương, kiểm tra thành phần và xác nhận thanh toán. Dữ liệu lương được quản lý độc lập với khoản học phí của học viên.')
# The same explanation of use case notation already appears in section 3.1.1.
ps[264]._p.getparent().remove(ps[264]._p)
ps[263]._p.getparent().remove(ps[263]._p)

# Correct data dictionaries and all tables retained from the original report.
def rowset(table,row,values):
    for c,t in zip(table.rows[row].cells,values):c.text=t
rowset(d.tables[0],1,['Khách vãng lai','Tra cứu chương trình; trao đổi tư vấn riêng và đăng ký tài khoản.'])
rowset(d.tables[0],2,['Học viên','Gửi nguyện vọng, theo dõi đơn và lớp được xếp, lịch học, học phí, kiểm tra và tư vấn.'])
d.tables[0].rows[3].cells[0].text='Giảng viên'
d.tables[0].rows[4].cells[0].text='Quản trị viên'
rowset(d.tables[1],6,['Registration','PK RegistrationId; FK StudentId, ProgramId, ClassId?','Ngày bắt đầu, buổi, nhóm thứ; ClassId trống khi chờ xếp.'])
rowset(d.tables[1],8,['PlacementTest','PK TestId; FK StudentId, ExamSessionId?','Yêu cầu, lịch chính thức, điểm và cấp độ đề xuất.'])
rowset(d.tables[1],13,['Consultation','PK ConsultationId; FK OwnerAccountId?','Chủ cuộc tư vấn, khóa truy cập khách, trạng thái và mốc đã đọc.'])
for vals in [['ExamSession','PK ExamSessionId; FK TeacherId?','Phòng, ngày giờ, sức chứa; giáo viên chấm cả ca.'],['ConsultationMessage','PK MessageId; FK ConsultationId, SenderAccountId?','Vai trò gửi, nội dung và thời điểm; thuộc một cuộc tư vấn.']]:
    cells=d.tables[1].add_row().cells
    for c,t in zip(cells,vals):c.text=t
rowset(d.tables[2],4,['Student/Program/Class – Registration','1 – N; Class tùy chọn','Đơn thuộc học viên và chương trình; chỉ gán lớp sau khi Admin xếp.'])
rowset(d.tables[2],7,['ExamSession – PlacementTest','1 – N','Yêu cầu có thể chưa có ca; giáo viên chấm được phân công theo ca.'])
for vals in [['Consultation – Message','1 – N','Mỗi tin thuộc một cuộc tư vấn; không được đọc chỉ bằng cách đoán ID.'],['UserAccount – Consultation','1 – N; tùy chọn','Học viên có OwnerAccountId; khách dùng mã truy cập riêng.']]:
    cells=d.tables[2].add_row().cells
    for c,t in zip(cells,vals):c.text=t
rowset(d.tables[3],1,['Đơn đăng ký','Pending, Confirmed, Cancelled','Pending chưa xếp; Confirmed có lớp phù hợp; độc lập với học phí.'])
rowset(d.tables[3],2,['Học phí','Pending, Paid','Admin xác nhận sau đối soát; không tự xếp lớp.'])
rowset(d.tables[3],3,['Kiểm tra đầu vào','Pending, Completed','Chờ phòng hoặc chờ chấm; Completed khi nhập kết quả.'])
rowset(d.tables[3],6,['Tư vấn','Pending, Replied, Closed','Tin khách tạo Pending; Admin trả lời Replied; Closed chặn gửi tiếp.'])
rowset(d.tables[6],2,['Data Access','EF Core và SQL Server provider','8.0.x','LINQ, ánh xạ quan hệ và giao dịch.'])
rowset(d.tables[6],5,['Thư điện tử','MailKit và MimeKit','Phụ thuộc dự án','Dịch vụ gửi thư chưa hoàn thiện.'])
rowset(d.tables[8],1,['CUST-01','Tư vấn hai chiều','Tin tới đúng cuộc hội thoại, quyền truy cập riêng.','Đã kiểm tra bộ tư vấn'])
rowset(d.tables[8],3,['CUST-03','Đăng ký khóa học','Pending, ClassId trống; lưu nguyện vọng và Payment.','Đã kiểm tra luồng mới'])
rowset(d.tables[8],4,['CUST-04','Xếp lớp và lịch tuần','Chặn lớp đầy, ngày sớm và lịch xung đột.','Đã kiểm tra luồng mới'])
rowset(d.tables[9],2,['TEACH-02','Chấm lớp thi được giao','Chỉ đúng giáo viên chấm; điểm 0–10.','Đã kiểm tra luồng phòng thi'])

# Normalize headings, paragraph styles and captions for consistent print layout.
for name in ['Normal','Body Text','List Paragraph']:
    try:st=d.styles[name]
    except KeyError:continue
    st.font.name='Times New Roman';st.font.size=Pt(13);st.font.color.rgb=RGBColor(0,0,0)
for name,size in [('Heading 1',15),('Heading 2',14),('Heading 3',13)]:
    st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.bold=True;st.font.color.rgb=RGBColor(0,0,0)
    st.paragraph_format.keep_with_next=True
for name in ['TOC 1','TOC 2','TOC 3']:
    try:st=d.styles[name]
    except KeyError:continue
    st.font.name='Times New Roman';st.font.size=Pt(11);st.paragraph_format.space_after=Pt(1);st.paragraph_format.line_spacing=1.05
main=False;fig=0
for p in d.paragraphs:
    if p.style.name=='Heading 1' and p.text=='MỞ ĐẦU':main=True
    if not main:continue
    f=p.paragraph_format
    for n in list(p._p.get_or_add_pPr().findall(qn('w:numPr'))):p._p.get_or_add_pPr().remove(n)
    if p.style.name.startswith('Heading'):
        f.keep_with_next=True;f.keep_together=True;f.space_before=Pt(10);f.space_after=Pt(6);f.first_line_indent=Cm(0);f.line_spacing=1.15
        if p.style.name=='Heading 1':f.page_break_before=True
        elif p.text.startswith(('3.4.5','3.5.1','3.5.2')):f.page_break_before=False
        for r in p.runs:r.font.color.rgb=RGBColor(0,0,0)
    elif p._p.xpath('.//w:drawing'):
        f.keep_with_next=True;f.space_before=Pt(3);f.space_after=Pt(3);f.line_spacing=1;f.first_line_indent=Cm(0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    elif p.style.name=='HITCFigureCaption':
        fig+=1;title=re.sub(r'^Hình\s*[\d.]*\s*[.:]?\s*','',p.text)
        p.clear();p.add_run('Hình ')
        r=p.add_run();begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin');r._r.append(begin)
        ins=OxmlElement('w:instrText');ins.set(qn('xml:space'),'preserve');ins.text=' SEQ Hinh \\* ARABIC ';p.add_run()._r.append(ins)
        sep=OxmlElement('w:fldChar');sep.set(qn('w:fldCharType'),'separate');p.add_run()._r.append(sep);p.add_run(str(fig))
        end=OxmlElement('w:fldChar');end.set(qn('w:fldCharType'),'end');p.add_run()._r.append(end);p.add_run('. '+title)
        f.space_before=Pt(2);f.space_after=Pt(7);f.line_spacing=1.1;f.keep_with_next=False;f.keep_together=True;f.first_line_indent=Cm(0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(11);r.italic=True;r.font.color.rgb=RGBColor(0,0,0)
    elif p.text.strip():
        f.first_line_indent=Cm(.75);f.left_indent=Cm(0);f.right_indent=Cm(0);f.space_before=Pt(0);f.space_after=Pt(6);f.line_spacing=1.35;f.keep_with_next=False;f.keep_together=False;f.widow_control=True;p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(13);r.font.color.rgb=RGBColor(0,0,0)
    # Clear inherited bullet style without introducing visible list markers.
    np=OxmlElement('w:numPr');ni=OxmlElement('w:numId');ni.set(qn('w:val'),'0');np.append(ni);p._p.get_or_add_pPr().append(np)

for t in d.tables:
    for j,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
        if j==0:trpr.append(OxmlElement('w:tblHeader'))
        for c in row.cells:
            tcpr=c._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for side in ['top','left','bottom','right']:
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            tcpr.append(borders)
            sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'E8EDF3' if j==0 else 'FFFFFF' if j%2 else 'F7F8FA');tcpr.append(sh)
            for p in c.paragraphs:
                p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_after=Pt(2);p.paragraph_format.space_before=Pt(0);p.paragraph_format.first_line_indent=Cm(0)
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(11);r.font.color.rgb=RGBColor(0,0,0);r.bold=j==0

# This single-cell note repeats the preceding database paragraph.
redundant=d.tables[5]._tbl;redundant.getparent().remove(redundant)

# Keep the short introduction on a single page.
intro=False
for p in d.paragraphs:
    if p.style.name=='Heading 1':intro=p.text=='MỞ ĐẦU'
    if intro and p.style.name=='Normal' and p.text.strip():
        p.paragraph_format.line_spacing=1.15;p.paragraph_format.space_after=Pt(4)
references=False
for p in d.paragraphs:
    if p.style.name=='Heading 1' and p.text=='TÀI LIỆU THAM KHẢO':references=True
    if references and p.style.name=='Normal':
        p.alignment=WD_ALIGN_PARAGRAPH.LEFT;p.paragraph_format.line_spacing=1.15;p.paragraph_format.space_after=Pt(6)

# Populate levels one through three in the automatic contents.
for x in d.element.xpath('//w:instrText'):
    if x.text and 'TOC' in x.text and '\\o' in x.text:x.text=' TOC \\o "1-3" \\h \\z \\u '
settings=d.settings.element
u=OxmlElement('w:updateFields');u.set(qn('w:val'),'true');settings.append(u)
d.core_properties.author='Nguyễn Khánh Huy';d.core_properties.title='Xây dựng website quản lý trung tâm ngoại ngữ HITC English';d.core_properties.subject='Báo cáo đồ án Lập trình ứng dụng'
out=R/'completed-draft.docx';d.save(out)
(R/'content-audit.json').write_text(json.dumps({'source':'Báo cáo gốc của Nguyễn Khánh Huy và mã nguồn WedEnglishApp','paragraphs_updated':len(updates),'figures':fig,'tables':len(d.tables),'layout_reference_only':True},ensure_ascii=False,indent=2),encoding='utf8')
print(out,'figures',fig)
