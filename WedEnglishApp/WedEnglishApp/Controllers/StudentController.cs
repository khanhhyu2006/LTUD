// =================================================================================================
// CONTROLLER: StudentController - QUẢN LÝ KHU VỰC CÁ NHÂN CỦA HỌC VIÊN (STUDENT PORTAL)
// Quyền truy cập: [Authorize(Roles = "Student")] - Chỉ dành cho học viên đã đăng nhập
// Bao gồm: Xem hồ sơ, Upload avatar, Xem thời khóa biểu/Lớp học của tôi, Lịch sử hóa đơn, In biên lai, Đánh giá sao
// =================================================================================================

using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Student;

namespace WedEnglishApp.Controllers
{
    [Authorize(Roles = "Student")] // Chỉ cho phép vai trò Student truy cập
    public class StudentController : Controller
    {
        private readonly ApplicationDbContext _context; // Đối tượng CSDL
        private readonly IWebHostEnvironment _env;       // Dùng để lấy đường dẫn thư mục wwwroot lưu file avatar

        public StudentController(ApplicationDbContext context, IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        // =============================================================================================
        // HÀM HỖ TRỢ NỘI BỘ: LẤY ACCOUNT ID VÀ STUDENT ID CỦA HỌC VIÊN ĐANG ĐĂNG NHẬP
        // =============================================================================================
        private async Task<(int accountId, int studentId)> GetStudentIdsAsync()
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return (0, 0);

            var student = await _context.Students.FirstOrDefaultAsync(s => s.AccountId == accountId);
            return (accountId, student?.StudentId ?? 0);
        }

        // =============================================================================================
        // HÀM 1: GET /Student/Profile - XEM THÔNG TIN HỒ SƠ HỌC VIÊN
        // =============================================================================================
        public async Task<IActionResult> Profile()
        {
            var (accountId, studentId) = await GetStudentIdsAsync();
            if (accountId == 0) return RedirectToAction("Login", "Account");

            var student = await _context.Students
                .Include(s => s.UserAccount)
                .FirstOrDefaultAsync(s => s.StudentId == studentId);

            if (student == null) return NotFound();

            // Đóng gói dữ liệu vào ViewModel để hiển thị ra View
            var viewModel = new StudentProfileViewModel
            {
                StudentId = student.StudentId,
                AccountId = student.AccountId,
                FullName = student.UserAccount.FullName,
                Email = student.UserAccount.Email,
                PhoneNumber = student.PhoneNumber,
                Address = student.Address,
                DateOfBirth = student.DateOfBirth,
                AvatarUrl = student.PhotoUrl ?? student.UserAccount.AvatarUrl
            };

            return View(viewModel);
        }

        // =============================================================================================
        // HÀM 2: POST /Student/Profile - CẬP NHẬT THÔNG TIN HỒ SƠ & TẢI LÊN ẢNH ĐẠI DIỆN (AVATAR)
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken] // Chống CSRF
        public async Task<IActionResult> Profile(StudentProfileViewModel model)
        {
            var (accountId, studentId) = await GetStudentIdsAsync();
            if (accountId == 0) return RedirectToAction("Login", "Account");

            var student = await _context.Students
                .Include(s => s.UserAccount)
                .FirstOrDefaultAsync(s => s.StudentId == studentId);

            if (student == null) return NotFound();

            string? photoUrl = null;
            if (model.AvatarFile != null)
            {
                var extension = await ImageUploadValidator.GetValidatedExtensionAsync(model.AvatarFile);
                if (extension == null)
                {
                    ModelState.AddModelError(nameof(model.AvatarFile), "Ảnh phải là tệp JPG, PNG hoặc WEBP hợp lệ và dung lượng không quá 5 MB.");
                }
                else
                {
                    photoUrl = await ImageUploadStorage.SaveAsync(_env, model.AvatarFile, "students");
                }
            }

            if (ModelState.IsValid)
            {
                student.UserAccount.FullName = model.FullName.Trim();
                student.PhoneNumber = model.PhoneNumber?.Trim();
                student.Address = model.Address?.Trim();
                student.DateOfBirth = model.DateOfBirth;
                if (photoUrl != null)
                {
                    student.PhotoUrl = photoUrl;
                    student.UserAccount.AvatarUrl = photoUrl;
                }

                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Cập nhật hồ sơ cá nhân thành công!";
                return RedirectToAction(nameof(Profile));
            }

            model.AvatarUrl = student.PhotoUrl ?? student.UserAccount.AvatarUrl;
            model.Email = student.UserAccount.Email;
            return View(model);
        }

        // =============================================================================================
        // HÀM 3: GET /Student/MyClasses - XEM DANH SÁCH LỚP HỌC ĐÃ ĐĂNG KÝ & THỜI KHÓA BIỂU
        // =============================================================================================
        public async Task<IActionResult> MyClasses()
        {
            var (_, studentId) = await GetStudentIdsAsync();
            if (studentId == 0) return RedirectToAction("Login", "Account");

            // Truy vấn toàn bộ các đơn đăng ký của học viên này
            // Kèm thông tin lớp, chương trình học, giảng viên phụ trách, thời khóa biểu và hóa đơn thanh toán
            var registrations = await _context.Registrations
                .Include(r => r.Program)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Program)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Teacher)
                        .ThenInclude(t => t!.UserAccount)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Schedules)
                .Include(r => r.DesiredTeacher)
                    .ThenInclude(t => t!.UserAccount)
                .Include(r => r.Payment)
                .Where(r => r.StudentId == studentId && !r.IsDeleted)
                .OrderByDescending(r => r.RegistrationDate)
                .ToListAsync();

            return View(registrations); // Trả về giao diện MyClasses.cshtml
        }

        // =============================================================================================
        // HÀM: GET /Student/Schedule - THỜI KHÓA BIỂU THEO NGÀY THÁNG NĂM CỤ THỂ / THEO TUẦN
        // Tham số: weekOffset (-1: tuần trước, 0: tuần này, 1: tuần kế tiếp,...)
        // =============================================================================================
        public async Task<IActionResult> Schedule(int weekOffset = 0)
        {
            var (_, studentId) = await GetStudentIdsAsync();
            if (studentId == 0) return RedirectToAction("Login", "Account");

            var registrations = await _context.Registrations
                .Include(r => r.Program)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Program)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Teacher)
                        .ThenInclude(t => t!.UserAccount)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Schedules)
                .Where(r => r.StudentId == studentId && !r.IsDeleted && r.ClassId != null && r.Status == "Confirmed")
                .ToListAsync();

            // Truy vấn lịch thi xếp lớp do Admin phân công kèm phòng thi
            var placementTests = await _context.PlacementTests
                .Include(pt => pt.ExamSession)
                .Include(pt => pt.EvaluatedByTeacher)
                    .ThenInclude(t => t!.UserAccount)
                .Where(pt => pt.StudentId == studentId && !pt.IsDeleted && pt.ExamSessionId != null && pt.ExamSession!.Status != "Cancelled")
                .OrderByDescending(pt => pt.TestDate)
                .ToListAsync();

            // Tính toán ngày Thứ Hai và Chủ Nhật cụ thể của tuần đang xem
            DateTime today = DateTime.Today;
            int currentDayOfWeek = (int)today.DayOfWeek;
            int daysSinceMonday = currentDayOfWeek == 0 ? 6 : currentDayOfWeek - 1;
            DateTime mondayOfCurrentWeek = today.AddDays(-daysSinceMonday);
            DateTime startOfWeek = mondayOfCurrentWeek.AddDays(weekOffset * 7);
            DateTime endOfWeek = startOfWeek.AddDays(6);

            ViewBag.PlacementTests = placementTests;
            ViewBag.WeekOffset = weekOffset;
            ViewBag.StartOfWeek = startOfWeek;
            ViewBag.EndOfWeek = endOfWeek;

            return View(registrations);
        }

        // =============================================================================================
        // HÀM 4: GET /Student/MyPayments - XEM LỊCH SỬ CÁC HÓA ĐƠN HỌC PHÍ ĐÃ NỘP
        // =============================================================================================
        public async Task<IActionResult> MyPayments()
        {
            var (_, studentId) = await GetStudentIdsAsync();
            if (studentId == 0) return RedirectToAction("Login", "Account");

            var payments = await _context.Payments
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Class)
                        .ThenInclude(c => c.Program)
                .Where(p => p.Registration.StudentId == studentId)
                .OrderByDescending(p => p.PaymentDate)
                .ToListAsync();

            return View(payments); // Trả về giao diện MyPayments.cshtml
        }

        // =============================================================================================
        // HÀM 5: GET /Student/PrintReceipt/{id} - HIỂN THỊ VÀ IN BIÊN LAI THU TIỀN HỌC PHÍ
        // =============================================================================================
        public async Task<IActionResult> PrintReceipt(int id)
        {
            var (_, studentId) = await GetStudentIdsAsync();
            if (studentId == 0) return RedirectToAction("Login", "Account");

            // Lấy hóa đơn Payment theo id, đảm bảo hóa đơn này đúng là của học viên đang đăng nhập
            var payment = await _context.Payments
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Student)
                        .ThenInclude(s => s.UserAccount)
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Class)
                        .ThenInclude(c => c.Program)
                .Include(p => p.Registration).ThenInclude(r => r.Program)
                .Include(p => p.Registration)
                    .ThenInclude(r => r.Class)
                        .ThenInclude(c => c.Teacher)
                            .ThenInclude(t => t!.UserAccount)
                .FirstOrDefaultAsync(p => p.PaymentId == id && p.Status == "Paid" && p.Registration.StudentId == studentId);

            if (payment == null) return NotFound();

            return View(payment); // View chứa mẫu in hóa đơn chuẩn khổ A4 kèm lệnh in window.print()
        }

        // =============================================================================================
        // HÀM 6: POST /Student/SubmitFeedback - GỬI ĐÁNH GIÁ SỐ SAO VÀ PHẢN HỒI VỀ KHÓA HỌC
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> SubmitFeedback(int classId, int rating, string comment)
        {
            var (_, studentId) = await GetStudentIdsAsync();
            if (studentId == 0) return RedirectToAction("Login", "Account");

            if (classId <= 0 || string.IsNullOrWhiteSpace(comment))
            {
                TempData["ErrorMessage"] = "Vui lòng nhập nội dung đánh giá nhận xét!";
                return RedirectToAction(nameof(MyClasses));
            }

            if (!await _context.Registrations.AnyAsync(r => r.StudentId == studentId && r.ClassId == classId && !r.IsDeleted && r.Status == "Confirmed"))
                return Forbid();

            // Tạo bản ghi CourseFeedback mới
            var feedback = new CourseFeedback
            {
                StudentId = studentId,
                ClassId = classId,
                Rating = Math.Clamp(rating, 1, 5), // Giới hạn số sao đánh giá trong khoảng 1 đến 5
                Comment = comment.Trim(),
                CreatedAt = DateTime.Now
            };

            _context.CourseFeedbacks.Add(feedback);
            await _context.SaveChangesAsync(); // Lưu vào SQL Server

            TempData["SuccessMessage"] = "Cảm ơn bạn đã gửi đánh giá phản hồi về khóa học!";
            return RedirectToAction(nameof(MyClasses));
        }
    }
}
