# Luồng đăng ký và xếp lớp hiện tại

## Ghi danh khóa học

- Học viên đăng ký khóa học; không chọn lớp hoặc giáo viên. Hai nhóm lịch là 246 và 357, kèm buổi học, ngày có thể bắt đầu và ghi chú.
- Server lưu ProgramId, ngày/nguyện vọng, ClassId rỗng và Status Pending. Thanh toán Cash hoặc VietQR được tạo trong cùng transaction; số tiền lấy từ khóa học.
- Sau đăng ký, Enrollment/Payment chỉ cho chủ đơn xem hướng dẫn, QR theo mã HPREG hoặc cách nộp tại quầy. Xác nhận học phí độc lập với xếp lớp.
- Admin xếp vào lớp cùng khóa, còn chỗ, khai giảng từ ngày học viên có thể bắt đầu. Buổi/thứ là nguyện vọng tham khảo, không chặn xếp lớp. Nếu đã có lịch chi tiết, vẫn kiểm tra trùng lịch với lớp khác của học viên.

## Lịch học của lớp

- Tạo và sửa lớp đều có nhóm lịch 246 hoặc 357 và giờ bắt đầu/kết thúc. Lưu lớp đồng thời ghi 3 bản ghi ClassSchedules trong transaction.
- Trang chi tiết phân lớp có form lưu lịch chung. Lịch được dùng trực tiếp bởi thời khóa biểu học viên và giáo viên, trong khoảng ngày bắt đầu/kết thúc lớp.
- Kiểm tra giờ kết thúc sau giờ bắt đầu, trùng phòng, trùng giáo viên và lịch khác của học viên đã được xếp. Lịch cũ ngoài hai nhóm được giữ lại nếu Admin chưa chủ động đổi.

## Thi xếp lớp theo phòng/ca

- Học viên gửi ngày/giờ mong muốn; đăng ký mới chưa có phòng hoặc giáo viên. Không tạo nhiều yêu cầu thi chưa hoàn tất cho cùng học viên.
- Admin tạo ExamSession với tên, ngày, giờ, phòng, sĩ số; chọn nhiều đăng ký chờ để xếp cùng ca, rồi phân công giáo viên chấm toàn bộ ca.
- Xếp hàng loạt kiểm tra toàn bộ yêu cầu trước khi lưu: sĩ số, ngày mong muốn, trùng học viên và trùng lịch. Vượt sĩ số thì không thêm một phần danh sách.
- Giáo viên chỉ xem/chấm ca được giao. Điểm 0–10 và đề xuất trình độ lưu theo từng PlacementTest. Khi tất cả bài đã được chấm, ca chuyển Completed.
- Lịch chính thức và kết quả xuất hiện trong tài khoản học viên. Không đổi giáo viên khi ca đã có bài chấm, không gỡ học viên đã có kết quả.

## Cấu trúc và dữ liệu

- Script nhúng CourseEnrollment.sql, DatabaseAlignment.sql và ExamSessions.sql nâng cấp cộng thêm, chạy lại được qua DbInitializer.
- DatabaseAlignmentHistory và ExamSessionUpgradeHistory lưu dữ liệu trước chuẩn hóa. Đơn/biên lai đã thu tiền và điểm thi cũ được bảo toàn.
- Ràng buộc kiểm tra miền dữ liệu, cặp lớp/khóa qua FK ghép, lịch trùng hệt qua unique index và quy tắc ghi danh/thu tiền qua trigger. EF dùng UseSqlOutputClause(false) cho bảng có trigger.
- Không còn đoạn khởi động tự ghi đè ghi chú lương. Dữ liệu mẫu mới dùng hai phương thức Cash/VietQR, không tạo đơn trùng cùng khóa cho một học viên.

## Kiểm tra đã thực hiện

- Build Debug thành công, 0 lỗi và 0 cảnh báo biên dịch.
- Kiểm thử trên bản sao riêng: 22 kiểm tra database/lịch lớp và 36 kiểm tra luồng lịch lớp/phòng thi/chấm điểm đạt (bao gồm kiểm tra HTTP).
- DBCC CHECKDB và CHECKCONSTRAINTS của database chính không báo lỗi; đối chiếu nhật ký có 0 khoản đã thu và 0 kết quả thi cũ bị thay đổi.
- Kiểm tra chỉ đọc trên IIS https://localhost:44317: trang chủ, tạo/sửa/chi tiết lớp, danh sách/tạo phòng thi, ghi danh và học phí đều HTTP 200. Phiên IIS hiện tại đã được khởi động lại với bản Debug mới.
