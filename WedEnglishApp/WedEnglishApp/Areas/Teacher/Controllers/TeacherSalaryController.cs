using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    // =================================================================================================
    // CONTROLLER: TeacherSalaryController (Area: Teacher) - XEM LỊCH SỬ THU NHẬP & BẢNG LƯƠNG CỦA TÔI
    // =================================================================================================
    [Area("Teacher")]
    [Authorize(Roles = "Teacher")]
    public class TeacherSalaryController : Controller
    {
        private readonly ApplicationDbContext _context;

        public TeacherSalaryController(ApplicationDbContext context)
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

        // GET: Teacher/TeacherSalary
        public async Task<IActionResult> Index()
        {
            int teacherId = await GetTeacherIdAsync();
            if (teacherId == 0) return RedirectToAction("Login", "Account", new { area = "" });

            var salaries = await _context.TeacherSalaries
                .Include(s => s.Teacher).ThenInclude(t => t.UserAccount)
                .Where(s => s.TeacherId == teacherId)
                .OrderByDescending(s => s.Year)
                .ThenByDescending(s => s.Month)
                .ToListAsync();

            // Khắc phục lỗi hiển thị font chữ tiếng Việt do mã hóa cũ
            bool hasCorruptedNote = false;
            foreach (var s in salaries)
            {
                if (!string.IsNullOrEmpty(s.Note) && (s.Note.Contains("Tá") || s.Note.Contains("LÆ") || s.Note.Contains("Â") || s.Note.Contains("Ã") || s.Note.Contains("°")))
                {
                    if (s.Month == 11) s.Note = "Tạm tính lương tháng 11/2026";
                    else if (s.Month == 10) s.Note = "Lương tháng 10/2026 - Giảng dạy tốt";
                    else s.Note = $"Lương giảng dạy tháng {s.Month}/{s.Year}";
                    hasCorruptedNote = true;
                }
            }
            if (hasCorruptedNote)
            {
                await _context.SaveChangesAsync();
            }

            return View(salaries);
        }
    }
}
