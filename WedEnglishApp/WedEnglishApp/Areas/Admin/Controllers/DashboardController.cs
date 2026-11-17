// =================================================================================================
// CONTROLLER: DashboardController (Area: Admin) - BẢNG ĐIỀU KHIỂN & BÁO CÁO THỐNG KÊ QUẢN TRỊ VIÊN
// Quyền truy cập: [Area("Admin")], [Authorize(Roles = "Admin")] - Nghiêm ngặt chỉ dành cho Quản trị viên
// Nghiệp vụ: Tổng hợp số lượng dữ liệu, tính tổng doanh thu (Paid) cung cấp cho biểu đồ Chart.js
// =================================================================================================

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]                   // Thuộc phân vùng Areas/Admin
    [Authorize(Roles = "Admin")]      // Kiểm tra Cookie Claims phải có vai trò là "Admin"
    public class DashboardController : Controller
    {
        private readonly ApplicationDbContext _context; // Đối tượng CSDL

        public DashboardController(ApplicationDbContext context)
        {
            _context = context;
        }

        // =============================================================================================
        // HÀM GET: /Admin/Dashboard/Index - HIỂN THỊ TỔNG QUAN VÀ BIỂU ĐỒ DOANH THU CHART.JS
        // =============================================================================================
        public async Task<IActionResult> Index(int? year)
        {
            var selectedYear = year ?? DateTime.Today.Year;
            if (!ModelState.IsValid || !WedEnglishApp.Services.ReportingService.ValidYear(selectedYear)) return BadRequest("Năm không hợp lệ.");
            var report = await new WedEnglishApp.Services.ReportingService(_context).AdminAsync(selectedYear);
            ViewBag.Report = report;
            // Counts exclude soft-deleted records.
            ViewBag.TotalPrograms = await _context.Programs.CountAsync(p => !p.IsDeleted);              // Tổng số khóa học
            ViewBag.TotalClasses = await _context.Classes.CountAsync(c => !c.IsDeleted);                // Tổng số lớp học
            ViewBag.TotalStudents = await _context.Students.CountAsync(s => !s.UserAccount.IsDeleted);              // Tổng số học viên
            ViewBag.TotalTeachers = await _context.Teachers.CountAsync(t => !t.UserAccount.IsDeleted);              // Tổng số giáo viên
            ViewBag.TotalRegistrations = await _context.Registrations.CountAsync(r => !r.IsDeleted);    // Tổng số đơn ghi danh

            // KHỐI 2: Tính tổng doanh thu thực tế từ tất cả các hóa đơn đã thanh toán thành công (Status == "Paid")
            decimal totalRevenue = report.Revenue;
            ViewBag.TotalRevenue = totalRevenue; // Dùng để hiển thị số tiền và truyền vào Chart.js

            // KHỐI 3: Lấy Top 5 lớp học thu hút đông học viên ghi danh nhất (dùng để vẽ biểu đồ so sánh)
            var topClasses = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed"))
                .Where(c => !c.IsDeleted)
                .OrderByDescending(c => c.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed")) // Sắp xếp giảm dần theo số lượng học viên
                .Take(5)                                       // Lấy 5 lớp đứng đầu
                .ToListAsync();

            ViewBag.TopClasses = topClasses;

            // KHỐI 4: Lấy 5 đơn ghi danh đăng ký mới nhất để giáo vụ dễ dàng theo dõi và duyệt
            var recentRegistrations = await _context.Registrations
                .Include(r => r.Student)
                    .ThenInclude(s => s.UserAccount)
                .Include(r => r.Program)
                .Include(r => r.Class)
                .Include(r => r.Payment)
                .Where(r => !r.IsDeleted)
                .OrderByDescending(r => r.RegistrationDate)
                .Take(5)
                .ToListAsync();

            ViewBag.RecentRegistrations = recentRegistrations;

            return View(); // Trả về giao diện Dashboard Index.cshtml của Admin
        }
    }
}
