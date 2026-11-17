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
