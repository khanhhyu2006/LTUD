from pathlib import Path
p=Path('docs/course-enrollment.md');s=p.read_text(encoding='utf-8-sig');s=s.replace('các thứ có thể học (2–8, trong đó 8 là Chủ nhật), giáo viên mong muốn và ghi chú','nhóm lịch Thứ 2–4–6 hoặc Thứ 3–5–7 và ghi chú');s+='''
## Form đăng ký và thanh toán đã chỉnh

- Bỏ chọn giáo viên khỏi form và ViewModel; đơn mới không nhận DesiredTeacherId do client gửi.
- Chỉ nhận SchedulePattern 246 hoặc 357; server tự đổi thành PreferredDays tương ứng, không nhận danh sách thứ tùy ý.
- Form chia phần lịch học và học phí. Ảnh hồ sơ không bắt buộc, nằm trong thông tin bổ sung.
- Sau Confirm, chuyển đến Enrollment/Payment?registrationId=... để xem số tiền và QR theo đơn hoặc hướng dẫn nộp tiền tại quầy. GET kiểm tra chủ sở hữu, trạng thái xóa và hủy; khoản thu vẫn Pending đến khi Admin xác nhận.
- Đã chạy bản cập nhật với database sao chép riêng, 15 kiểm tra qua trình duyệt đạt: hai nhóm lịch, chặn nhóm không hợp lệ, QR, tiền mặt, quyền sở hữu và bố cục 1366/1024/390 px. SQL xác nhận DesiredTeacherId và ClassId rỗng, học phí và trạng thái lưu đúng. Database chính không nhận các đơn thử này.
''';p.write_text(s,encoding='utf8')
