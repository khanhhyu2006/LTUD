exec(open('session-state/implement-criteria.py',encoding='utf-8-sig').read().split("write('Models/TeacherActivity.cs'")[0])
write('ViewModels/Reports/ReportModels.cs','''
namespace WedEnglishApp.ViewModels.Reports;
public record MonthSummary(int Month, decimal Amount, int Receipts);
public record ProgramSummary(string Name, int Count);
public record ReceiptSummary(int Id, DateTime Date, string Program, decimal Amount, bool LegacyDate);
public class AdminReportViewModel
{
    public int Year { get; set; }
    public List<MonthSummary> Months { get; set; } = [];
    public List<ProgramSummary> Programs { get; set; } = [];
    public List<ReceiptSummary> Receipts { get; set; } = [];
    public decimal Revenue => Months.Sum(m => m.Amount);
}
public record ClassSummary(string Name, string Program, string Room, string Status, int Students, int Documents, int Published);
public record TestSummary(int Id, string Student, DateTime Date, decimal? Score, string? Level, string Status);
public class TeacherReportViewModel
{
    public string TeacherName { get; set; } = "";
    public DateTime From { get; set; }
    public DateTime To { get; set; }
    public List<ClassSummary> Classes { get; set; } = [];
    public List<TestSummary> Tests { get; set; } = [];
    public int ActivityCount { get; set; }
    public int Graded => Tests.Count(t => t.Status == "Completed" && t.Score.HasValue);
    public decimal? AverageScore => Tests.Where(t => t.Status == "Completed" && t.Score.HasValue).Select(t => t.Score).DefaultIfEmpty().Average();
}
''')
write('Services/CsvExport.cs','''
using System.Text;
namespace WedEnglishApp.Services;
public static class CsvExport
{
    public static byte[] Bytes(IEnumerable<IEnumerable<string>> rows)
    {
        static string Cell(string value)
        {
            value ??= "";
            if (value.TrimStart().Length > 0 && "=+-@".Contains(value.TrimStart()[0]) || value.StartsWith('\\t') || value.StartsWith('\\r')) value = "'" + value;
            return "\\\"" + value.Replace("\\\"", "\\\"\\\"") + "\\\"";
        }
        var text = string.Join("\\r\\n", rows.Select(row => string.Join(",", row.Select(Cell))));
        return Encoding.UTF8.GetPreamble().Concat(Encoding.UTF8.GetBytes(text)).ToArray();
    }
}
''')
write('Services/ReportingService.cs','''
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.ViewModels.Reports;
namespace WedEnglishApp.Services;
public class ReportingService(ApplicationDbContext db)
{
    public static bool ValidYear(int year) => year >= 2000 && year <= 2100;
    public static bool ValidRange(DateTime from, DateTime to) => from.Year >= 2000 && to.Year <= 2100 && from <= to && (to - from).TotalDays <= 3660;
    public async Task<AdminReportViewModel> AdminAsync(int year)
    {
        var start = new DateTime(year, 1, 1);var end = start.AddYears(1);
        var receipts = await db.Payments.AsNoTracking().Where(p => p.Status == "Paid" && (p.ConfirmedAt ?? p.PaymentDate) >= start && (p.ConfirmedAt ?? p.PaymentDate) < end)
            .Select(p => new ReceiptSummary(p.PaymentId, p.ConfirmedAt ?? p.PaymentDate, p.Registration.Program.ProgramName, p.Amount, p.ConfirmedAt == null)).ToListAsync();
        var programs = await db.Registrations.AsNoTracking().Where(r => !r.IsDeleted && r.Status != "Cancelled" && r.RegistrationDate >= start && r.RegistrationDate < end)
            .GroupBy(r => new { r.ProgramId, r.Program.ProgramName }).Select(g => new ProgramSummary(g.Key.ProgramName, g.Count())).ToListAsync();
        return new AdminReportViewModel { Year = year, Receipts = receipts.OrderByDescending(p => p.Date).ThenBy(p => p.Id).ToList(), Programs = programs.OrderByDescending(p => p.Count).ToList(),
            Months = Enumerable.Range(1, 12).Select(month => new MonthSummary(month, receipts.Where(p => p.Date.Month == month).Sum(p => p.Amount), receipts.Count(p => p.Date.Month == month))).ToList() };
    }
    public async Task<TeacherReportViewModel> TeacherAsync(int teacherId, DateTime from, DateTime to)
    {
        var end = to.Date.AddDays(1);from = from.Date;
        var classes = await db.Classes.AsNoTracking().Where(c => c.TeacherId == teacherId && !c.IsDeleted && c.StartDate < end && c.EndDate >= from)
            .OrderBy(c => c.ClassName).Select(c => new ClassSummary(c.ClassName, c.Program.ProgramName, c.Room, c.Status,
                c.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed"), c.Documents.Count(), c.Documents.Count(d => d.IsPublished))).ToListAsync();
        var tests = await db.PlacementTests.AsNoTracking().Where(t => !t.IsDeleted && t.TestDate >= from && t.TestDate < end
            && ((t.ExamSessionId != null && t.ExamSession!.TeacherId == teacherId && t.ExamSession.Status != "Cancelled") || (t.ExamSessionId == null && t.EvaluatedByTeacherId == teacherId)))
            .OrderByDescending(t => t.TestDate).Select(t => new TestSummary(t.TestId, t.Student.UserAccount.FullName, t.TestDate, t.Score, t.RecommendedLevel, t.Status)).ToListAsync();
        return new TeacherReportViewModel { TeacherName = await db.Teachers.Where(t => t.TeacherId == teacherId).Select(t => t.UserAccount.FullName).FirstAsync(), From = from, To = to.Date, Classes = classes, Tests = tests,
            ActivityCount = await db.TeacherActivities.CountAsync(a => a.TeacherId == teacherId && a.OccurredAt >= from && a.OccurredAt < end) };
    }
}
''')
write('Areas/Teacher/Controllers/ReportController.cs','''
using System.Globalization;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;
namespace WedEnglishApp.Areas.Teacher.Controllers;
[Area("Teacher"), Authorize(Roles = "Teacher")]
public class ReportController(ApplicationDbContext db) : Controller
{
    public async Task<IActionResult> Index(DateTime? from, DateTime? to, string? format)
    {
        var first = (from ?? new DateTime(DateTime.Today.Year, 1, 1)).Date;
        var last = (to ?? new DateTime(DateTime.Today.Year, 12, 31)).Date;
        if (!ModelState.IsValid || !ReportingService.ValidRange(first, last)) return BadRequest("Khoảng ngày không hợp lệ; chọn từ năm 2000 đến 2100, tối đa 10 năm.");
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var accountId);
        var id = await db.Teachers.Where(t => t.AccountId == accountId && !t.UserAccount.IsDeleted).Select(t => t.TeacherId).FirstOrDefaultAsync();
        if (id == 0) return NotFound();
        var model = await new ReportingService(db).TeacherAsync(id, first, last);
        Response.Headers.CacheControl = "private, no-store";
        if (format == "csv")
        {
            var rows = new List<string[]> { new[] { "Báo cáo giáo viên", model.TeacherName }, new[] { "Từ ngày", first.ToString("yyyy-MM-dd"), "Đến ngày", last.ToString("yyyy-MM-dd") },
                new[] { "Lớp", "Khóa học", "Phòng", "Trạng thái", "Sĩ số hiện tại", "Tài liệu", "Đã công bố" } };
            rows.AddRange(model.Classes.Select(c => new[] { c.Name, c.Program, c.Room, c.Status, c.Students.ToString(), c.Documents.ToString(), c.Published.ToString() }));
            rows.Add(new[] { "Bài kiểm tra", "Học viên", "Ngày thi", "Điểm", "Cấp độ", "Trạng thái" });
            rows.AddRange(model.Tests.Select(t => new[] { t.Id.ToString(), t.Student, t.Date.ToString("yyyy-MM-dd"), t.Score?.ToString(CultureInfo.InvariantCulture) ?? "", t.Level ?? "", t.Status }));
            return File(CsvExport.Bytes(rows), "text/csv; charset=utf-8", $"Bao-cao-giao-vien-{first:yyyyMMdd}-{last:yyyyMMdd}.csv");
        }
        return View(model);
    }
}
''')
write('Areas/Admin/Controllers/ReportController.cs','''
using System.Globalization;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;
namespace WedEnglishApp.Areas.Admin.Controllers;
[Area("Admin"), Authorize(Roles = "Admin")]
public class ReportController(ApplicationDbContext db) : Controller
{
    public async Task<IActionResult> Index(int? year, string? format)
    {
        var selected = year ?? DateTime.Today.Year;
        if (!ModelState.IsValid || !ReportingService.ValidYear(selected)) return BadRequest("Năm báo cáo phải từ 2000 đến 2100.");
        var model = await new ReportingService(db).AdminAsync(selected);
        Response.Headers.CacheControl = "private, no-store";
        if (format == "csv")
        {
            var rows = new List<string[]> { new[] { "Năm", selected.ToString() }, new[] { "Tháng", "Khoản đã thu (VND)", "Số biên lai" } };
            rows.AddRange(model.Months.Select(m => new[] { m.Month.ToString(), m.Amount.ToString(CultureInfo.InvariantCulture), m.Receipts.ToString() }));
            rows.Add(new[] { "Mã biên lai", "Ngày ghi nhận", "Chương trình", "Số tiền", "Cơ sở thời gian" });
            rows.AddRange(model.Receipts.Select(r => new[] { r.Id.ToString(), r.Date.ToString("yyyy-MM-dd HH:mm:ss"), r.Program, r.Amount.ToString(CultureInfo.InvariantCulture), r.LegacyDate ? "PaymentDate lịch sử" : "ConfirmedAt" }));
            return File(CsvExport.Bytes(rows), "text/csv; charset=utf-8", $"Bao-cao-thu-hoc-phi-{selected}.csv");
        }
        ViewBag.DataCounts = new Dictionary<string, int> {
            ["UserAccounts"] = await db.UserAccounts.CountAsync(), ["Students"] = await db.Students.CountAsync(), ["Teachers"] = await db.Teachers.CountAsync(),
            ["Programs"] = await db.Programs.CountAsync(), ["Classes"] = await db.Classes.CountAsync(), ["Registrations"] = await db.Registrations.CountAsync(),
            ["Payments"] = await db.Payments.CountAsync(), ["ClassSchedules"] = await db.ClassSchedules.CountAsync(), ["ClassDocuments"] = await db.ClassDocuments.CountAsync(),
            ["ExamSessions"] = await db.ExamSessions.CountAsync(), ["PlacementTests"] = await db.PlacementTests.CountAsync(), ["CourseFeedbacks"] = await db.CourseFeedbacks.CountAsync(),
            ["Consultations"] = await db.Consultations.CountAsync(), ["ConsultationMessages"] = await db.ConsultationMessages.CountAsync(), ["TeacherSalaries"] = await db.TeacherSalaries.CountAsync(),
            ["Banners"] = await db.Banners.CountAsync(), ["TeacherActivities"] = await db.TeacherActivities.CountAsync() };
        ViewBag.RegistrationStates = await db.Registrations.GroupBy(r => r.Status).Select(g => new { Status = g.Key, Count = g.Count() }).ToDictionaryAsync(r => r.Status, r => r.Count);
        ViewBag.PaymentStates = await db.Payments.GroupBy(r => r.Status).Select(g => new { Status = g.Key, Count = g.Count() }).ToDictionaryAsync(r => r.Status, r => r.Count);
        return View(model);
    }
}
''')
# Replace fixed chart data with the same queries used by the financial report.
edit('Areas/Admin/Controllers/DashboardController.cs','public async Task<IActionResult> Index()','public async Task<IActionResult> Index(int? year)')
edit('Areas/Admin/Controllers/DashboardController.cs','// KHỐI 1: Đếm tổng số lượng thực thể phục vụ 5 thẻ Card thống kê trên đầu trang','''var selectedYear = year ?? DateTime.Today.Year;
            if (!ModelState.IsValid || !WedEnglishApp.Services.ReportingService.ValidYear(selectedYear)) return BadRequest("Năm không hợp lệ.");
            var report = await new WedEnglishApp.Services.ReportingService(_context).AdminAsync(selectedYear);
            ViewBag.Report = report;
            // Counts exclude soft-deleted records.''')
for a,b in [('Programs.CountAsync()','Programs.CountAsync(p => !p.IsDeleted)'),('Classes.CountAsync()','Classes.CountAsync(c => !c.IsDeleted)'),('Students.CountAsync()','Students.CountAsync(s => !s.UserAccount.IsDeleted)'),('Teachers.CountAsync()','Teachers.CountAsync(t => !t.UserAccount.IsDeleted)'),('Registrations.CountAsync()','Registrations.CountAsync(r => !r.IsDeleted)')]:edit('Areas/Admin/Controllers/DashboardController.cs',a,b)
p=ROOT/'Areas/Admin/Controllers/DashboardController.cs';s=p.read_text(encoding='utf8');a=s.index('decimal totalRevenue =');b=s.index('ViewBag.TotalRevenue =',a);s=s[:a]+'decimal totalRevenue = report.Revenue;\n            '+s[b:];write('Areas/Admin/Controllers/DashboardController.cs',s)
edit('Areas/Admin/Controllers/DashboardController.cs','.Include(c => c.Registrations)','.Include(c => c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed")))')
# correct extra closing parenthesis in the query replacement
edit('Areas/Admin/Controllers/DashboardController.cs','"Confirmed")))','"Confirmed"))')
edit('Areas/Admin/Controllers/DashboardController.cs','.OrderByDescending(c => c.Registrations.Count)','.Where(c => !c.IsDeleted)\n                .OrderByDescending(c => c.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed"))')
edit('Areas/Admin/Controllers/DashboardController.cs','.OrderByDescending(r => r.RegistrationDate)','.Where(r => !r.IsDeleted)\n                .OrderByDescending(r => r.RegistrationDate)')
print('Implemented scoped teacher reports and live financial reports.')
