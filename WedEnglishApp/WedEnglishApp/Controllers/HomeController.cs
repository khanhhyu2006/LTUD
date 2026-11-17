// =================================================================================================
// CONTROLLER: HomeController.cs - QUẢN LÝ TRANG CHỦ VÀ TRANG CÔNG KHAI CỦA WEBSITE
// Quyền truy cập: Mọi người dùng (Khách vãng lai, Học viên, Giáo viên đều truy cập được)
// Nghiệp vụ: Hiển thị banner, số liệu thống kê trung tâm, khóa học nổi bật, lớp sắp mở, giáo viên tiêu biểu
// =================================================================================================
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.ViewModels.Home;

namespace WedEnglishApp.Controllers
{
    public class HomeController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly WedEnglishApp.Services.ConsultationAccess _consultationAccess;

        public HomeController(ApplicationDbContext context, WedEnglishApp.Services.ConsultationAccess consultationAccess)
        {
            _context = context;
            _consultationAccess = consultationAccess;
        }

        // =============================================================================================
        // HÀM 1: GET / - TRANG CHỦ WEBSITE TRUNG TÂM NGOẠI NGỮ
        // =============================================================================================
        public async Task<IActionResult> Index()
        {
            var today = DateTime.Today;
            var model = new HomeViewModel
            {
                Banners = await _context.Banners
                    .Where(b => b.IsActive && !b.IsDeleted)
                    .OrderBy(b => b.DisplayOrder)
                    .ToListAsync(),

                FeaturedPrograms = await _context.Programs
                    .Where(p => p.IsActive && !p.IsDeleted)
                    .OrderByDescending(p => p.ProgramId)
                    .Take(3)
                    .ToListAsync(),

                UpcomingClasses = await _context.Classes.Include(c => c.Program).Include(c => c.Schedules)
                    .Where(c => !c.IsDeleted && c.Program.IsActive && !c.Program.IsDeleted && (c.Status == "Planning" || c.Status == "InProgress") && c.EndDate >= today && c.EndDate >= c.StartDate)
                    .OrderBy(c => c.StartDate < today).ThenBy(c => c.StartDate).Take(4).ToListAsync(),

                FeaturedTeachers = await _context.Teachers
                    .Include(t => t.UserAccount)
                    .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted)
                    .Take(3)
                    .ToListAsync(),

                TopTestStudents = await _context.PlacementTests
                    .Include(pt => pt.Student)
                        .ThenInclude(s => s.UserAccount)
                    .Where(pt => pt.Score.HasValue && !pt.IsDeleted && pt.Status == "Completed")
                    .OrderByDescending(pt => pt.Score)
                    .Take(4)
                    .Select(pt => new TopStudentViewModel
                    {
                        StudentName = pt.Student.UserAccount.FullName,
                        AvatarUrl = pt.Student.UserAccount.AvatarUrl,
                        Score = (double)pt.Score!.Value,
                        TestName = "Thi xếp lớp đầu vào",
                        TargetCourse = !string.IsNullOrWhiteSpace(pt.RecommendedLevel) ? pt.RecommendedLevel : "Lộ trình bứt phá"
                    })
                    .ToListAsync(),

                TotalPrograms = await _context.Programs.CountAsync(p => p.IsActive),
                TotalClasses = await _context.Classes.CountAsync(),
                TotalStudents = await _context.Students.CountAsync(),
                TotalTeachers = await _context.Teachers.CountAsync()
            };

            return View(model);
        }

        // =============================================================================================
        // HÀM 2: GET /Home/Contact - TRANG LIÊN HỆ & BẢN ĐỒ TRUNG TÂM
        // =============================================================================================
        public async Task<IActionResult> Contact()
        {
            var student = await _consultationAccess.StudentAsync(HttpContext);
            return View(new WedEnglishApp.ViewModels.Consultations.StartConsultationViewModel
            {
                IsStudent=student!=null, ContactName=student?.FullName??"", ContactEmail=student?.Email??"", PhoneNumber=student?.Student?.PhoneNumber??""
            });
        }
    }
}