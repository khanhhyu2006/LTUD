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
                c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed").Select(r => r.StudentId).Distinct().Count(), c.Documents.Count(), c.Documents.Count(d => d.IsPublished))).ToListAsync();
        var tests = await db.PlacementTests.AsNoTracking().Where(t => !t.IsDeleted && t.TestDate >= from && t.TestDate < end
            && ((t.ExamSessionId != null && t.ExamSession!.TeacherId == teacherId && t.ExamSession.Status != "Cancelled") || (t.ExamSessionId == null && t.EvaluatedByTeacherId == teacherId)))
            .OrderByDescending(t => t.TestDate).Select(t => new TestSummary(t.TestId, t.Student.UserAccount.FullName, t.TestDate, t.Score, t.RecommendedLevel, t.Status)).ToListAsync();
        return new TeacherReportViewModel { TeacherName = await db.Teachers.Where(t => t.TeacherId == teacherId).Select(t => t.UserAccount.FullName).FirstAsync(), From = from, To = to.Date, Classes = classes, Tests = tests,
            ActivityCount = await db.TeacherActivities.CountAsync(a => a.TeacherId == teacherId && a.OccurredAt >= from && a.OccurredAt < end) };
    }
}
