# Chuẩn hóa dữ liệu ứng dụng ngày 04 tháng 11 năm 2026

Database áp dụng: EnglishCenterDb. Không sửa các database hệ thống SQL Server.

## Sao lưu và nhật ký

Các bản sao lưu trước thay đổi được giữ trong session-state/db-backups, gồm before-database-alignment-20261104.bak, before-alignment-apply-20261104.bak và before-exam-rooms-20261104.bak. Nhật ký trước chuyển đổi nằm trong DatabaseAlignmentHistory và ExamSessionUpgradeHistory.

## Dữ liệu đã chuẩn hóa

- 3 đơn chờ trùng khóa chưa thu tiền chuyển Cancelled, giữ bản ghi và lịch sử.
- 2 đơn chờ còn lại được gỡ ClassId; các đơn chờ mới bắt đầu với ClassId rỗng.
- 7 trạng thái lớp Planning/InProgress được đối chiếu ngày bắt đầu/kết thúc.
- 1 khoản chờ dùng cổng thử nghiệm cũ chuyển sang Cash. Các khoản đã Paid, gồm phương thức VNPay/MoMo lịch sử, giữ nguyên.
- Theo lựa chọn của người dùng, giữ nguyên các cặp ghi danh đã thanh toán dù trùng khóa. Trigger chỉ ngăn tạo/kích hoạt thêm đơn trùng mới.
- 13 bài thi đã hoàn tất được liên kết vào 12 ca thi lịch sử phù hợp, giữ nguyên điểm và đề xuất.
- 7 yêu cầu thi trùng chưa xếp phòng, chưa phân công, chưa chấm được chuyển vào thùng rác; bản gốc được giữ trong nhật ký chuyển đổi. Các yêu cầu thi đã có điểm không bị xóa hoặc sửa.

## Cách sử dụng sau cập nhật

Tạo lớp hoặc Sửa lớp: chọn 246/357 và giờ học, sau đó lưu. Lớp đã tạo nhưng chưa có lịch cần được Admin chọn giờ thực tế; không tự đoán giờ từ tên lớp hoặc nguyện vọng.

Quản lý kiểm tra xếp lớp: tạo lớp thi/phòng thi, mở chi tiết, chọn học viên đăng ký để xếp hàng loạt rồi phân công giáo viên chấm cả ca. Giáo viên mở lớp thi được giao để chấm từng bài.
