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
        public async Task<IActionResult> Index()
        {
            // KHỐI 1: Đếm tổng số lượng thực thể phục vụ 5 thẻ Card thống kê trên đầu trang
            ViewBag.TotalPrograms = await _context.Programs.CountAsync();              // Tổng số khóa học
            ViewBag.TotalClasses = await _context.Classes.CountAsync();                // Tổng số lớp học
            ViewBag.TotalStudents = await _context.Students.CountAsync();              // Tổng số học viên
            ViewBag.TotalTeachers = await _context.Teachers.CountAsync();              // Tổng số giáo viên
            ViewBag.TotalRegistrations = await _context.Registrations.CountAsync();    // Tổng số đơn ghi danh

            // KHỐI 2: Tính tổng doanh thu thực tế từ tất cả các hóa đơn đã thanh toán thành công (Status == "Paid")
            decimal totalRevenue = await _context.Payments
                .Where(p => p.Status == "Paid")
                .SumAsync(p => p.Amount);
            ViewBag.TotalRevenue = totalRevenue; // Dùng để hiển thị số tiền và truyền vào Chart.js

            // KHỐI 3: Lấy Top 5 lớp học thu hút đông học viên ghi danh nhất (dùng để vẽ biểu đồ so sánh)
            var topClasses = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Registrations)
                .OrderByDescending(c => c.Registrations.Count) // Sắp xếp giảm dần theo số lượng học viên
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
                .OrderByDescending(r => r.RegistrationDate)
                .Take(5)
                .ToListAsync();

            ViewBag.RecentRegistrations = recentRegistrations;

            return View(); // Trả về giao diện Dashboard Index.cshtml của Admin
        }
    }
}
