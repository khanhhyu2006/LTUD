from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
w('Areas/Admin/Controllers/PlacementTestAdminController.cs','''using System.Data;
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
''')
w('Areas/Teacher/Controllers/TeacherTestController.cs','''using System.Security.Claims;
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
''')
s=r('Controllers/PlacementTestController.cs');s=s.replace('.Include(s => s.PlacementTests)','.Include(s => s.PlacementTests.Where(t => !t.IsDeleted)).ThenInclude(t => t.ExamSession)\n                .Include(s => s.PlacementTests.Where(t => !t.IsDeleted))');s=s.replace('if (testDate < DateTime.Today)','if (!ModelState.IsValid || testDate.Date < DateTime.Today.AddDays(1))');a=s.index('            // Tạo bản ghi PlacementTest mới');s=s[:a]+'''            if (!new[] { "08:30 AM", "10:00 AM", "02:00 PM", "04:00 PM", "06:30 PM" }.Contains(testTime))
            {
                TempData["ErrorMessage"] = "Khung giờ mong muốn không hợp lệ.";
                return RedirectToAction(nameof(BookTest));
            }
            if (await _context.PlacementTests.AnyAsync(t => t.StudentId == student.StudentId && !t.IsDeleted && t.Status == "Pending"))
            {
                TempData["ErrorMessage"] = "Bạn đã có đăng ký thi chưa hoàn tất. Hãy theo dõi lịch thi trong tài khoản.";
                return RedirectToAction(nameof(BookTest));
            }
'''+s[a:];s=s.replace('StudentId = student.StudentId,\n                TestDate', 'StudentId = student.StudentId,\n                RequestedDate = testDate.Date, RequestedTime = testTime, Room = null,\n                TestDate');s=s.replace('Đăng ký lịch kiểm tra xếp lớp thành công! Giáo viên sẽ liên hệ và xếp ca thi.','Đã tiếp nhận đăng ký. Admin sẽ xếp bạn vào phòng thi và phân công giáo viên chấm ca thi.');w('Controllers/PlacementTestController.cs',s)
s=r('Controllers/StudentController.cs');s=s.replace('var placementTests = await _context.PlacementTests\n','var placementTests = await _context.PlacementTests\n                .Include(pt => pt.ExamSession)\n');s=s.replace('.Where(pt => pt.StudentId == studentId && !pt.IsDeleted)', '.Where(pt => pt.StudentId == studentId && !pt.IsDeleted && pt.ExamSessionId != null && pt.ExamSession!.Status != "Cancelled")');w('Controllers/StudentController.cs',s)
s=r('Areas/Teacher/Controllers/TeacherDashboardController.cs').replace('CountAsync(pt => pt.Status == "Pending")','CountAsync(pt => pt.Status == "Pending" && !pt.IsDeleted && pt.EvaluatedByTeacherId == teacher.TeacherId)');# inspect local variable name below before build
w('Areas/Teacher/Controllers/TeacherDashboardController.cs',s)
print('Grouped exam administration, student requests and teacher grading implemented')
