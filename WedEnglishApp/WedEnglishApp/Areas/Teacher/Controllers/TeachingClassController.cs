using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    [Area("Teacher")]
    [Authorize(Roles = "Teacher")]
    public class TeachingClassController : Controller
    {
        private readonly ApplicationDbContext _context;

        public TeachingClassController(ApplicationDbContext context)
        {
            _context = context;
        }

        private async Task<int> GetTeacherIdAsync()
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return 0;
            var teacher = await _context.Teachers.FirstOrDefaultAsync(t => t.AccountId == accountId);
            return teacher?.TeacherId ?? 0;
        }

        // GET: Teacher/TeachingClass
        public async Task<IActionResult> Index()
        {
            int teacherId = await GetTeacherIdAsync();
            if (teacherId == 0) return RedirectToAction("Login", "Account", new { area = "" });

            var classes = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Registrations)
                .Include(c => c.Schedules)
                .Where(c => c.TeacherId == teacherId)
                .OrderByDescending(c => c.StartDate)
                .ToListAsync();

            return View(classes);
        }

        // GET: Teacher/TeachingClass/Schedule
        public async Task<IActionResult> Schedule(int weekOffset = 0)
        {
            int teacherId = await GetTeacherIdAsync();
            if (teacherId == 0) return RedirectToAction("Login", "Account", new { area = "" });

            var classes = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Registrations)
                .Include(c => c.Schedules)
                .Where(c => c.TeacherId == teacherId && !c.IsDeleted)
                .OrderBy(c => c.ClassName)
                .ToListAsync();

            // Truy vấn danh sách lịch khảo thí / coi thi mà Admin đã phân công cho giáo viên này
            ViewBag.AssignedTests = await _context.PlacementTests
                .Include(pt => pt.Student).ThenInclude(s => s.UserAccount)
                .Where(pt => pt.EvaluatedByTeacherId == teacherId && !pt.IsDeleted)
                .OrderByDescending(pt => pt.TestDate)
                .ToListAsync();

            // Tính toán ngày Thứ Hai và Chủ Nhật cụ thể của tuần đang xem
            DateTime today = DateTime.Today;
            int currentDayOfWeek = (int)today.DayOfWeek;
            int daysSinceMonday = currentDayOfWeek == 0 ? 6 : currentDayOfWeek - 1;
            DateTime mondayOfCurrentWeek = today.AddDays(-daysSinceMonday);
            DateTime startOfWeek = mondayOfCurrentWeek.AddDays(weekOffset * 7);
            DateTime endOfWeek = startOfWeek.AddDays(6);

            ViewBag.WeekOffset = weekOffset;
            ViewBag.StartOfWeek = startOfWeek;
            ViewBag.EndOfWeek = endOfWeek;

            return View(classes);
        }

        // GET: Teacher/TeachingClass/Students/5
        public async Task<IActionResult> Students(int id)
        {
            int teacherId = await GetTeacherIdAsync();
            if (teacherId == 0) return RedirectToAction("Login", "Account", new { area = "" });

            var cls = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Registrations)
                    .ThenInclude(r => r.Student)
                        .ThenInclude(s => s.UserAccount)
                .Include(c => c.Registrations)
                    .ThenInclude(r => r.Payment)
                .FirstOrDefaultAsync(c => c.ClassId == id && c.TeacherId == teacherId);

            if (cls == null) return NotFound();

            return View(cls);
        }
    }
}
