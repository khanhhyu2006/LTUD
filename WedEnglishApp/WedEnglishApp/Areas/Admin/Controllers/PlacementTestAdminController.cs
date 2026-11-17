using System.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
namespace WedEnglishApp.Areas.Admin.Controllers;

[Area("Admin"), Authorize(Roles = "Admin")]
public class PlacementTestAdminController(ApplicationDbContext context) : Controller
{
    private async Task TeachersAsync() => ViewBag.Teachers = await context.Teachers.Include(t => t.UserAccount)
        .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted).ToListAsync();

    public async Task<IActionResult> Index()
    {
        ViewBag.Waiting = await context.PlacementTests.Include(t => t.Student).ThenInclude(s => s.UserAccount)
            .Where(t => !t.IsDeleted && t.Status == "Pending" && t.ExamSessionId == null).OrderBy(t => t.TestDate).ToListAsync();
        return View(await context.ExamSessions.Include(s => s.Teacher).ThenInclude(t => t!.UserAccount)
            .Include(s => s.Tests.Where(t => !t.IsDeleted)).OrderByDescending(s => s.ExamDate).ToListAsync());
    }

    public async Task<IActionResult> Create()
    {
        await TeachersAsync();
        return View(new ExamSession { Name = $"KT-{DateTime.Today.AddDays(1):yyyyMMdd}-01" });
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(ExamSession model)
    {
        model.Status = "Planning";
        model.Name = model.Name?.Trim() ?? ""; model.Room = model.Room?.Trim() ?? "";
        if (ModelState.IsValid)
        {
            var error = await ExamSessionPlanner.ValidateAsync(context, model);
            if (error == null)
            {
                context.ExamSessions.Add(model); await context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Đã tạo lớp thi. Chọn học viên đăng ký để xếp vào phòng thi.";
                return RedirectToAction(nameof(Details), new { id = model.ExamSessionId });
            }
            ModelState.AddModelError("", error);
        }
        await TeachersAsync(); return View(model);
    }

    public async Task<IActionResult> Details(int id)
    {
        var session = await context.ExamSessions.Include(s => s.Teacher).ThenInclude(t => t!.UserAccount)
            .Include(s => s.Tests.Where(t => !t.IsDeleted)).ThenInclude(t => t.Student).ThenInclude(s => s.UserAccount)
            .FirstOrDefaultAsync(s => s.ExamSessionId == id);
        if (session == null) return NotFound();
        ViewBag.Waiting = await context.PlacementTests.Include(t => t.Student).ThenInclude(s => s.UserAccount)
            .Where(t => !t.IsDeleted && t.Status == "Pending" && t.ExamSessionId == null && (t.RequestedDate ?? t.TestDate).Date <= session.ExamDate.Date)
            .OrderBy(t => t.RequestedDate ?? t.TestDate).ToListAsync();
        await TeachersAsync(); return View(session);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> AssignStudents(int sessionId, int[] testIds)
    {
        await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
        var session = await context.ExamSessions.Include(s => s.Tests.Where(t => !t.IsDeleted)).FirstOrDefaultAsync(s => s.ExamSessionId == sessionId);
        if (session == null) return NotFound();
        string? error = null;
        var ids = testIds.Distinct().ToArray();
        var tests = await context.PlacementTests.Where(t => ids.Contains(t.TestId) && !t.IsDeleted && t.Status == "Pending" && t.ExamSessionId == null).ToListAsync();
        if (session.Status == "Cancelled" || session.Status == "Completed") error = "Lớp thi đã đóng.";
        else if (ids.Length == 0 || tests.Count != ids.Length) error = "Chọn các đăng ký đang chờ xếp phòng thi.";
        else if (session.Tests.Count + tests.Count > session.Capacity) error = "Số học viên vượt quá sĩ số phòng thi; chưa có học viên nào được thêm.";
        else if (tests.Any(t => (t.RequestedDate ?? t.TestDate).Date > session.ExamDate.Date)) error = "Ngày thi sớm hơn ngày học viên có thể tham dự.";
        else if (tests.Select(t => t.StudentId).Distinct().Count() != tests.Count || tests.Any(t => session.Tests.Any(x => x.StudentId == t.StudentId))) error = "Một học viên chỉ được xuất hiện một lần trong lớp thi.";
        if (error == null)
        {
            var students = tests.Select(t => t.StudentId).ToArray();
            var day = session.ExamDate.DayOfWeek == DayOfWeek.Sunday ? 8 : (int)session.ExamDate.DayOfWeek + 1;
            var clash = await context.Registrations.AnyAsync(r => students.Contains(r.StudentId) && !r.IsDeleted && r.Status == "Confirmed" && r.ClassId != null
                && r.Class.StartDate.Date <= session.ExamDate.Date && r.Class.EndDate.Date >= session.ExamDate.Date
                && r.Class.Schedules.Any(s => s.DayOfWeek == day && s.StartTime < session.EndTime && session.StartTime < s.EndTime));
            var examClash = await context.PlacementTests.AnyAsync(t => students.Contains(t.StudentId) && !t.IsDeleted && t.ExamSessionId != null && t.ExamSession!.Status != "Cancelled"
                && t.ExamSession.ExamDate.Date == session.ExamDate.Date && t.ExamSession.StartTime < session.EndTime && session.StartTime < t.ExamSession.EndTime);
            if (clash || examClash) error = "Học viên được chọn có lịch học hoặc lịch thi khác trùng giờ.";
        }
        if (error != null)
        {
            TempData["ErrorMessage"] = error;
            return RedirectToAction(nameof(Details), new { id = sessionId });
        }
        foreach (var test in tests) ExamSessionPlanner.CopySchedule(test, session);
        await context.SaveChangesAsync(); await transaction.CommitAsync();
        TempData["SuccessMessage"] = $"Đã xếp {tests.Count} học viên vào lớp thi {session.Name}.";
        return RedirectToAction(nameof(Details), new { id = sessionId });
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> AssignTeacher(int sessionId, int? teacherId)
    {
        await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
        var session = await context.ExamSessions.Include(s => s.Tests.Where(t => !t.IsDeleted)).FirstOrDefaultAsync(s => s.ExamSessionId == sessionId);
        if (session == null) return NotFound();
        if (session.Tests.Any(t => t.Status == "Completed") && session.TeacherId != teacherId)
        {
            TempData["ErrorMessage"] = "Lớp thi đã có bài được chấm; giữ nguyên giáo viên để bảo toàn kết quả.";
            return RedirectToAction(nameof(Details), new { id = sessionId });
        }
        session.TeacherId = teacherId;
        var error = await ExamSessionPlanner.ValidateAsync(context, session);
        if (error != null)
        {
            TempData["ErrorMessage"] = error;
            return RedirectToAction(nameof(Details), new { id = sessionId });
        }
        foreach (var test in session.Tests) test.EvaluatedByTeacherId = teacherId;
        await context.SaveChangesAsync(); await transaction.CommitAsync();
        TempData["SuccessMessage"] = "Đã phân công giáo viên chấm toàn bộ lớp thi.";
        return RedirectToAction(nameof(Details), new { id = sessionId });
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> RemoveStudent(int id)
    {
        var test = await context.PlacementTests.FindAsync(id);
        if (test == null || !test.ExamSessionId.HasValue) return NotFound();
        var sessionId = test.ExamSessionId.Value;
        if (test.Status == "Completed") TempData["ErrorMessage"] = "Không gỡ học viên đã có kết quả thi.";
        else
        {
            test.ExamSessionId = null; test.EvaluatedByTeacherId = null; test.Room = null;
            test.TestDate = test.RequestedDate ?? test.TestDate; test.TestTime = test.RequestedTime ?? test.TestTime;
            await context.SaveChangesAsync(); TempData["SuccessMessage"] = "Đã đưa học viên về danh sách chờ xếp phòng thi.";
        }
        return RedirectToAction(nameof(Details), new { id = sessionId });
    }
}
