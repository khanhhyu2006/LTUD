using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
namespace WedEnglishApp.Areas.Teacher.Controllers;

[Area("Teacher"), Authorize(Roles = "Teacher")]
public class TeacherTestController(ApplicationDbContext context) : Controller
{
    private async Task<int> TeacherIdAsync()
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var id);
        return await context.Teachers.Where(t => t.AccountId == id).Select(t => t.TeacherId).FirstOrDefaultAsync();
    }
    public async Task<IActionResult> Index()
    {
        var teacherId = await TeacherIdAsync();
        return View(await context.ExamSessions.Include(s => s.Tests.Where(t => !t.IsDeleted))
            .Where(s => s.TeacherId == teacherId && s.Status != "Cancelled").OrderByDescending(s => s.ExamDate).ToListAsync());
    }
    public async Task<IActionResult> Session(int id)
    {
        var teacherId = await TeacherIdAsync();
        var session = await context.ExamSessions.Include(s => s.Tests.Where(t => !t.IsDeleted)).ThenInclude(t => t.Student).ThenInclude(s => s.UserAccount)
            .FirstOrDefaultAsync(s => s.ExamSessionId == id && s.TeacherId == teacherId && s.Status != "Cancelled");
        return session == null ? NotFound() : View(session);
    }
    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Grade(int id, decimal score, string recommendedLevel)
    {
        var teacherId = await TeacherIdAsync();
        var test = await context.PlacementTests.Include(t => t.ExamSession)
            .FirstOrDefaultAsync(t => t.TestId == id && !t.IsDeleted && t.ExamSessionId != null && t.ExamSession!.TeacherId == teacherId && t.ExamSession.Status != "Cancelled");
        if (test == null) return NotFound();
        if (!ModelState.IsValid || score < 0 || score > 10 || string.IsNullOrWhiteSpace(recommendedLevel) || recommendedLevel.Trim().Length > 100)
        {
            TempData["ErrorMessage"] = "Điểm phải từ 0 đến 10 và trình độ đề xuất không quá 100 ký tự.";
            return RedirectToAction(nameof(Session), new { id = test.ExamSessionId });
        }
        test.Score = score; test.RecommendedLevel = recommendedLevel.Trim(); test.Status = "Completed";
        test.ExamSession!.Status = await context.PlacementTests.AnyAsync(t => t.ExamSessionId == test.ExamSessionId && t.TestId != id && !t.IsDeleted && t.Status != "Completed") ? "InProgress" : "Completed";
        await context.SaveChangesAsync();
        TempData["SuccessMessage"] = "Đã lưu kết quả thi của học viên.";
        return RedirectToAction(nameof(Session), new { id = test.ExamSessionId });
    }
}
