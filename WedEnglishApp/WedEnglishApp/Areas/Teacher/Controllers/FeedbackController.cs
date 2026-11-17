using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    [Area("Teacher")]
    [Authorize(Roles = "Teacher")]
    public class FeedbackController : Controller
    {
        private readonly ApplicationDbContext _context;

        public FeedbackController(ApplicationDbContext context)
        {
            _context = context;
        }

        public async Task<IActionResult> Index()
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return RedirectToAction("Login", "Account", new { area = "" });

            var teacher = await _context.Teachers.FirstOrDefaultAsync(t => t.AccountId == accountId);
            if (teacher == null) return NotFound();

            // Lấy tất cả phản hồi của các lớp do giáo viên này phụ trách
            var feedbacks = await _context.CourseFeedbacks
                .Include(f => f.Student)
                    .ThenInclude(s => s.UserAccount)
                .Include(f => f.Class)
                    .ThenInclude(c => c.Program)
                .Where(f => f.Class.TeacherId == teacher.TeacherId)
                .OrderByDescending(f => f.CreatedAt)
                .ToListAsync();

            return View(feedbacks);
        }
    }
}
