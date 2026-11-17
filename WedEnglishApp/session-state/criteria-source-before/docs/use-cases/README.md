# Sơ đồ use case – NHK English times

Phân tích từ mã nguồn hiện có ngày 03/11/2026. Có ba vai trò tài khoản: Student, Teacher, Admin. Khách là tác nhân chưa đăng nhập, không phải một loại tài khoản. Mỗi tài khoản cùng vai trò dùng chung sơ đồ.

Mở **index.html** để xem toàn bộ sơ đồ, phóng to và in. Tệp SVG là ảnh vector chèn vào báo cáo; tệp PlantUML (.puml) dùng để chỉnh sửa. Chạy lại: `node docs/use-cases/generate.cjs`.

## Quy ước

Người que là tác nhân, hình elip là use case, khung chữ nhật là ranh giới hệ thống. Đường liền là quan hệ tương tác, không thể hiện thứ tự thực hiện. Sơ đồ tổng quát gộp các mục tiêu nghiệp vụ; sơ đồ từng vai trò phân rã chức năng. Không dùng include/extend khi chưa có quan hệ bắt buộc hoặc mở rộng rõ ràng. Đăng nhập là điều kiện trước cho các chức năng bảo vệ, không phải bước được gọi lại trong mỗi use case. Chức năng công khai vẫn có thể được truy cập khi dùng tài khoản; không lặp lại toàn bộ ở mọi sơ đồ.

## Giới hạn được xác nhận từ mã nguồn

- **Điểm danh:** checkbox trong Teacher/Views/TeachingClass/Students.cshtml chưa có thao tác lưu; AttendanceController chỉ trả View. Không đưa điểm danh đã lưu vào sơ đồ.
- **Thanh toán:** VietQR hiển thị ảnh QR; Admin xác nhận thu tiền. Enrollment.Confirm tự gán Paid cho lựa chọn VNPay/MoMo; các lớp VnPayService/IVnPayService còn trống, chưa có luồng gọi cổng hoặc callback thật. Sơ đồ không thêm tác nhân cổng thanh toán tự động.
- **Tài liệu học viên:** chưa tìm thấy giao diện/action tra cứu, tải tài liệu trong Student; hiện quản lý/tải tài liệu nằm ở Teacher.
- **Tư vấn:** Admin đổi trạng thái Pending/Replied; chưa có thao tác gửi nội dung trả lời/email trong ConsultationManagerController.
- **Tài khoản giáo viên:** có tạo, sửa và xóa mềm; chưa có action khóa/mở riêng như học viên.
- **Lương, banner, thùng rác:** có triển khai trong mã nguồn, đã bổ sung vào bộ sơ đồ.
- Đây là tài liệu phân tích tĩnh chức năng, chưa phải kết quả kiểm thử vận hành hay kiểm toán phân quyền.

## Use case tổng quát

![Use case tổng quát](01-tong-quat.svg)

## Use case khách chưa đăng nhập

![Use case khách chưa đăng nhập](02-khach.svg)

| Use case | Controller / Action hoặc View đối chiếu |
|---|---|
| Xem trang chủ, khóa học nổi bật | Home.Index |
| Tìm kiếm, lọc và xem danh sách khóa học | Program.Index |
| Xem chi tiết khóa học và lớp mở | Program.Detail |
| Xem thông tin liên hệ | Home.Contact |
| Gửi yêu cầu tư vấn | Consultation.Submit |
| Đăng ký tài khoản học viên | Account.Register |
| Đăng nhập | Account.Login |

## Use case tài khoản học viên

![Use case tài khoản học viên](03-hoc-vien.svg)

| Use case | Controller / Action hoặc View đối chiếu |
|---|---|
| Đăng nhập | Account.Login |
| Đổi mật khẩu | Account.ChangePassword |
| Đăng xuất | Account.Logout |
| Xem và cập nhật hồ sơ, ảnh đại diện | Student.Profile |
| Tra cứu khóa học và lớp mở | Program.Index / Detail |
| Đăng ký lớp và chọn cách thanh toán | Enrollment.Checkout / Confirm |
| Gửi nguyện vọng giáo viên, ghi chú, ảnh | Enrollment.Confirm |
| Xem lớp đã đăng ký và trạng thái | Student.MyClasses |
| Xem lịch học và lịch thi theo tuần | Student.Schedule |
| Xem lịch sử học phí | Student.MyPayments |
| Xem và in biên lai học phí | Student.PrintReceipt |
| Đặt lịch kiểm tra xếp lớp | PlacementTest.BookTest (POST) |
| Xem lịch, điểm và cấp độ đề xuất | PlacementTest.BookTest (GET) |
| Gửi đánh giá, nhận xét khóa học | Student.SubmitFeedback |

## Use case tài khoản giáo viên

![Use case tài khoản giáo viên](04-giao-vien.svg)

| Use case | Controller / Action hoặc View đối chiếu |
|---|---|
| Đăng nhập | Account.Login |
| Đổi mật khẩu | Account.ChangePassword |
| Đăng xuất | Account.Logout |
| Xem bảng điều khiển giảng dạy | Teacher/TeacherDashboard.Index |
| Cập nhật ảnh hồ sơ | Teacher/TeacherDashboard.UploadPhoto |
| Xem các lớp được phân công | Teacher/TeachingClass.Index |
| Xem danh sách học viên của lớp | Teacher/TeachingClass.Students |
| Xem lịch dạy và lịch thi được giao | Teacher/TeachingClass.Schedule |
| Xem, tải lên và xóa tài liệu lớp | Teacher/Document.Index / Upload / Delete |
| Tải tài liệu về | Teacher/Views/Document/Index.cshtml (liên kết tệp) |
| Xem bài kiểm tra được phân công | Teacher/TeacherTest.Index |
| Chấm điểm và đề xuất cấp độ | Teacher/TeacherTest.Grade |
| Xem phản hồi của học viên | Teacher/Feedback.Index |
| Xem bảng lương và trạng thái chi trả | Teacher/TeacherSalary.Index |

## Use case tài khoản quản trị viên

![Use case tài khoản quản trị viên](05-admin.svg)

| Use case | Controller / Action hoặc View đối chiếu |
|---|---|
| Đăng nhập | Account.Login |
| Đổi mật khẩu | Account.ChangePassword |
| Đăng xuất | Account.Logout |
| Xem thống kê và biểu đồ doanh thu | Admin/Dashboard.Index |
| Quản lý chương trình, bật / tắt tuyển sinh | Admin/ProgramManager.Index / Create / Edit / Delete / ToggleStatus |
| Thêm, sửa, xóa mềm lớp và lịch học | Admin/ClassManager.Index / Create / Edit / Delete |
| Xem chi tiết lớp, phân công giáo viên | Admin/ClassManager.Details / AssignTeacher |
| Thêm / Gỡ học viên khỏi lớp | Admin/ClassManager.AddStudentToClass / RemoveStudentFromClass |
| Tạo, sửa, xóa mềm hồ sơ giáo viên | Admin/TeacherManager.Index / Create / Edit / Delete |
| Sửa hồ sơ, khóa / mở tài khoản học viên | Admin/StudentManager.Index / Edit / ToggleStatus |
| Xếp / Chuyển lớp cho đơn đăng ký | Admin/RegistrationAdmin.AssignClass |
| Duyệt, hủy, xóa mềm đơn đăng ký | Admin/RegistrationAdmin.Index / UpdateStatus / Delete |
| Xem học phí và xác nhận thu tiền | Admin/PaymentAdmin.Index / ConfirmPayment |
| Xem và in biên lai học phí | Admin/PaymentAdmin.PrintReceipt |
| Xếp lịch, phòng, giáo viên thi đầu vào | Admin/PlacementTestAdmin.Index / AssignScheduleAndTeacher |
| Cập nhật điểm, cấp độ / Xóa mềm lịch thi | Admin/PlacementTestAdmin.UpdateResult / Delete |
| Lập, sửa, lọc và xóa bảng lương | Admin/SalaryAdmin.Index / CreateOrUpdate / Delete |
| Xác nhận chi trả lương giáo viên | Admin/SalaryAdmin.ConfirmPayment |
| Xem, đổi trạng thái, xóa mềm tư vấn | Admin/ConsultationManager.Index / ToggleStatus / Delete |
| Quản lý banner và bật / tắt hiển thị | Admin/BannerManager.Index / Create / Edit / Delete / ToggleActive |
| Xem và khôi phục dữ liệu thùng rác | Admin/Trash.Index / Restore |
| Xóa vĩnh viễn / Dọn thùng rác | Admin/Trash.PermanentDelete / EmptyTrash |

