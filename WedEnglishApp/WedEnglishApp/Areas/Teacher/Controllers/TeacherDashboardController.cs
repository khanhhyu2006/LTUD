// =================================================================================================
// CONTROLLER: TeacherDashboardController (Area: Teacher) - BẢNG ĐIỀU KHIỂN CỦA GIẢNG VIÊN
// Quyền truy cập: [Area("Teacher")], [Authorize(Roles = "Teacher")] - Chỉ dành cho Giáo viên
// Nghiệp vụ: Thống kê số lớp phụ trách, tổng số học viên đang theo học, số bài test xếp lớp cần chấm
// =================================================================================================

using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    [Area("Teacher")]                // Thuộc phân vùng Areas/Teacher
    [Authorize(Roles = "Teacher")]   // Kiểm tra người dùng phải có Role là "Teacher"
    public class TeacherDashboardController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _environment;

        public TeacherDashboardController(ApplicationDbContext context, IWebHostEnvironment environment)
        {
            _context = context;
            _environment = environment;
        }

        // =============================================================================================
        // HÀM GET: /Teacher/TeacherDashboard/Index - XEM TỔNG QUAN CÔNG TÁC GIẢNG DẠY
        // =============================================================================================
        public async Task<IActionResult> Index()
        {
            // Bước 1: Lấy mã AccountId của giáo viên đang đăng nhập từ Cookie Claims
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return RedirectToAction("Login", "Account", new { area = "" });

            // Bước 2: Truy vấn hồ sơ Teacher kèm:
            // - Tài khoản UserAccount
            // - Danh sách các lớp được phân công (Classes)
            // - Chương trình học của từng lớp (Program)
            // - Danh sách học viên ghi danh của từng lớp (Registrations)
            // - Thời khóa biểu ca học trong tuần (Schedules)
            var teacher = await _context.Teachers
                .Include(t => t.UserAccount)
                .Include(t => t.Classes.Where(c => !c.IsDeleted))
                    .ThenInclude(c => c.Program)
                .Include(t => t.Classes.Where(c => !c.IsDeleted))
                    .ThenInclude(c => c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed"))
                .Include(t => t.Classes.Where(c => !c.IsDeleted))
                    .ThenInclude(c => c.Schedules)
                .FirstOrDefaultAsync(t => t.AccountId == accountId);

            if (teacher == null) return NotFound();

            // Bước 3: Thống kê 3 chỉ số phục vụ thẻ Card trên Dashboard giáo viên
            ViewBag.TotalClasses = teacher.Classes.Count;                            // Tổng số lớp phụ trách
            ViewBag.TotalStudents = teacher.Classes.SelectMany(c => c.Registrations).Select(r => r.StudentId).Distinct().Count(); // Tổng số học viên đang dạy
            ViewBag.PendingTests = await _context.PlacementTests.CountAsync(pt => pt.Status == "Pending" && !pt.IsDeleted && pt.EvaluatedByTeacherId == teacher.TeacherId); // Số bài thi xếp lớp chờ chấm

            ViewBag.RecentActivities = await _context.TeacherActivities.AsNoTracking().Where(a => a.TeacherId == teacher.TeacherId).OrderByDescending(a => a.OccurredAt).ThenByDescending(a => a.ActivityId).Take(10).ToListAsync();
            return View(teacher); // Trả về giao diện Dashboard của Giảng viên
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> UploadPhoto(IFormFile? photo)
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId))
                return RedirectToAction("Login", "Account", new { area = "" });

            var teacher = await _context.Teachers
                .Include(t => t.UserAccount)
                .FirstOrDefaultAsync(t => t.AccountId == accountId);
            if (teacher == null) return NotFound();

            if (photo == null || photo.Length == 0)
            {
                TempData["ErrorMessage"] = "Vui lòng chọn ảnh để tải lên.";
                return RedirectToAction(nameof(Index));
            }

            var extension = await ImageUploadValidator.GetValidatedExtensionAsync(photo);
            if (extension == null)
            {
                TempData["ErrorMessage"] = "Ảnh phải là tệp JPG, PNG hoặc WEBP hợp lệ và dung lượng không quá 5 MB.";
                return RedirectToAction(nameof(Index));
            }

            teacher.PhotoUrl = await ImageUploadStorage.SaveAsync(_environment, photo, "teachers");
            teacher.UserAccount.AvatarUrl = teacher.PhotoUrl;
            _context.TeacherActivities.Add(new WedEnglishApp.Models.TeacherActivity { TeacherId = teacher.TeacherId, Kind = "Profile", Description = "Cập nhật ảnh hồ sơ" });
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = "Cập nhật ảnh hồ sơ thành công.";
            return RedirectToAction(nameof(Index));
        }
    }
}
