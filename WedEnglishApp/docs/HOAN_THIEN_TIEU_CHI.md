# Hoàn thiện tiêu chí NHK English times

Đã bổ sung vào ứng dụng ASP.NET Core MVC hiện có, giữ nguyên ba vai trò tài khoản. Vai trò giáo viên được đối chiếu với nhóm nhân viên của phiếu chấm.

## Chức năng đã bổ sung

- Giáo viên: nhật ký hoạt động gần đây; quản lý tài liệu có thêm, sửa, xóa, công bố/ẩn và tải xuống.
- Học viên: `/Student/Materials` chỉ liệt kê/tải tài liệu đã công bố cho lớp có ghi danh Confirmed.
- Kiểm tra tài liệu tại máy chủ: quyền sở hữu lớp, tiêu đề 1–200 ký tự, tối đa 10 MB; PDF/DOCX/PPTX/XLSX/TXT, kiểm tra nội dung định dạng. Tệp mới lưu tại `App_Data/ClassDocuments`; đường tĩnh `/uploads/documents` bị chặn. Tải về qua action có kiểm tra quyền.
- `/Teacher/Report`: lọc ngày, lớp phụ trách, sĩ số hiện tại, kết quả thi và hoạt động; xuất CSV UTF-8, in/lưu PDF qua trình duyệt.
- `/Admin/Dashboard`: chọn năm, 12 tháng doanh thu và cơ cấu ghi danh từ SQL Server.
- `/Admin/Report`: tổng hợp tháng, chi tiết chứng từ, số bản ghi 17 bảng và trạng thái; xuất CSV, in/lưu PDF.
- Admin khóa/mở giáo viên tại `/Admin/TeacherManager`. Mỗi yêu cầu kiểm tra lại tài khoản; phiên cũ bị từ chối sau khi khóa/xóa mềm.
- CSV xử lý ô bắt đầu bằng ký tự công thức. Tất cả thao tác thay đổi mới yêu cầu anti-forgery.
- Hai tài liệu mẫu được ghi nhãn rõ trong lớp CB_01_T246, một bản nháp, một bản công bố.

## Database và bảo toàn dữ liệu

`Data/Sql/CriteriaCompletion.sql` là nâng cấp bổ sung, chạy lặp an toàn qua `DbInitializer`:

- `ClassDocuments.IsPublished`, `ClassDocuments.UpdatedAt`.
- `Payments.ConfirmedAt` (NULL cho chứng từ lịch sử; không đoán lại ngày thu).
- Bảng `TeacherActivities`, FK đến Teachers, chỉ mục theo giáo viên/thời điểm.

Tổng 17 bảng ứng dụng, 157 cột. Khoản thu mới ghi ConfirmedAt bằng UPDATE có điều kiện; yêu cầu xác nhận lặp không thay mốc đầu tiên. Báo cáo dùng ConfirmedAt, hoặc PaymentDate cho khoản cũ. Trạng thái thu và xếp lớp độc lập.

Bản sao lưu COPY_ONLY: `session-state/db-backups/before-criteria-20261105.bak`. Hash trên toàn bộ trường cũ của Payments và Registrations không đổi sau nâng cấp; chứng từ Paid và các ghi danh trùng lịch sử giữ nguyên. Minh chứng: `session-state/criteria-production-upgrade.json`.

## Kiểm thử và trình diễn

- Build thành công, 0 warning/0 error.
- 64 kiểm tra tự động trên `EnglishCenterCriteriaTest`; kết quả `session-state/criteria-checks/results.json`.
- Kiểm tra CRUD, sai quyền của giáo viên/học viên/khách, tệp giả hoặc quá dung lượng, CSRF, CSV, tổng doanh thu khớp SQL, khóa phiên và kích hoạt lại.
- Các trang mới kiểm tra 390/1024/1440 px; bảng nhiều cột cuộn trong vùng bảng.
- Smoke test trên database chính với Admin/Teacher/Student; kiểm tra bản in PDF và ảnh giao diện.
- Script `session-state/test-criteria-workflows.cjs` chỉ dùng host 5275/database test; fixture dùng tài khoản có tiền tố criteria và được tạo trong bản sao riêng.

Chạy ứng dụng: `dotnet run --project WedEnglishApp/WedEnglishApp.csproj --launch-profile https`. Profile hiện tại dùng HTTPS 7117, HTTP 5267. Khi chạy lại qua Visual Studio/IIS Express, build và khởi động lại profile đang dùng để tải DLL mới.

## Đối chiếu năm nhóm tính năng bổ sung

Có thể trình diễn VietQR, học liệu riêng/tải tệp, tư vấn hai chiều, biểu đồ dữ liệu thật, xuất báo cáo; bảo mật theo vai trò/bản ghi là minh chứng bổ sung. Việc chấp thuận nhóm tính năng và cách chia điểm do giảng viên quyết định. Phiếu hiện có phần điểm tổng và điểm chi tiết chưa khớp, không tự quy đổi thành 100/100.

Không tuyên bố đã có email tự động, callback ngân hàng, API tạo PDF riêng hoặc chuyên cần lưu theo buổi. PDF báo cáo được lưu từ hộp thoại in của trình duyệt. Chưa có kiểm thử tải/bảo mật chuyên sâu.
