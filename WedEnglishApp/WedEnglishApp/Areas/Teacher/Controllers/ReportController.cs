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
