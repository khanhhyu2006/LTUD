using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
namespace WedEnglishApp.Areas.Teacher.Controllers;
[Area("Teacher"), Authorize(Roles = "Teacher")]
public class DocumentController(ApplicationDbContext db, IWebHostEnvironment env) : Controller
{
    private readonly DocumentStorage storage = new(env);
    private async Task<int> TeacherIdAsync()
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var id);
        return await db.Teachers.Where(t => t.AccountId == id && t.UserAccount.IsActive && !t.UserAccount.IsDeleted).Select(t => t.TeacherId).FirstOrDefaultAsync();
    }
    private void Log(int teacherId, string kind, string title) => db.TeacherActivities.Add(new TeacherActivity { TeacherId = teacherId, Kind = kind, Description = title });
    private Task<ClassDocument?> OwnAsync(int id, int teacherId) => db.ClassDocuments.Include(d => d.Class)
        .FirstOrDefaultAsync(d => d.DocumentId == id && d.Class.TeacherId == teacherId && !d.Class.IsDeleted);
    public async Task<IActionResult> Index()
    {
        var teacherId = await TeacherIdAsync();
        ViewBag.Classes = new SelectList(await db.Classes.Where(c => c.TeacherId == teacherId && !c.IsDeleted).OrderBy(c => c.ClassName).ToListAsync(), "ClassId", "ClassName");
        return View(await db.ClassDocuments.Include(d => d.Class).Where(d => d.Class.TeacherId == teacherId && !d.Class.IsDeleted).OrderByDescending(d => d.UploadedAt).ToListAsync());
    }
    [HttpPost, ValidateAntiForgeryToken, RequestSizeLimit(11 * 1024 * 1024)]
    public async Task<IActionResult> Upload(int classId, string? title, IFormFile? documentFile, bool isPublished = false)
    {
        var teacherId = await TeacherIdAsync();
        if (!await db.Classes.AnyAsync(c => c.ClassId == classId && c.TeacherId == teacherId && !c.IsDeleted)) return NotFound();
        var error = !ModelState.IsValid || string.IsNullOrWhiteSpace(title) || title.Trim().Length > 200 ? "Tiêu đề bắt buộc, tối đa 200 ký tự." : await storage.ValidateAsync(documentFile);
        if (error != null) { TempData["ErrorMessage"] = error; return RedirectToAction(nameof(Index)); }
        var saved = await storage.SaveAsync(documentFile!);
        db.ClassDocuments.Add(new ClassDocument { ClassId = classId, Title = title!.Trim(), FilePath = saved, IsPublished = isPublished });
        Log(teacherId, "DocumentCreate", "Tải tài liệu: " + title.Trim());
        try { await db.SaveChangesAsync(); } catch { storage.TryDelete(saved); throw; }
        TempData["SuccessMessage"] = "Đã tải tài liệu " + (isPublished ? "và công bố cho lớp." : "ở trạng thái bản nháp.");
        return RedirectToAction(nameof(Index));
    }
    public async Task<IActionResult> Edit(int id)
    {
        var item = await OwnAsync(id, await TeacherIdAsync());
        return item == null ? NotFound() : View(item);
    }
    [HttpPost, ValidateAntiForgeryToken, RequestSizeLimit(11 * 1024 * 1024)]
    public async Task<IActionResult> Edit(int id, string? title, bool isPublished, IFormFile? documentFile)
    {
        var teacherId = await TeacherIdAsync(); var item = await OwnAsync(id, teacherId);
        if (item == null) return NotFound();
        string? error = !ModelState.IsValid || string.IsNullOrWhiteSpace(title) || title.Trim().Length > 200 ? "Tiêu đề bắt buộc, tối đa 200 ký tự." : null;
        if (error == null && documentFile != null) error = await storage.ValidateAsync(documentFile);
        if (error != null) { TempData["ErrorMessage"] = error; return RedirectToAction(nameof(Edit), new { id }); }
        var old = item.FilePath;string? saved = null;
        if (documentFile != null) item.FilePath = saved = await storage.SaveAsync(documentFile);
        item.Title = title!.Trim(); item.IsPublished = isPublished; item.UpdatedAt = DateTime.Now;
        Log(teacherId, "DocumentEdit", "Sửa tài liệu: " + item.Title);
        try { await db.SaveChangesAsync(); } catch { if (saved != null) storage.TryDelete(saved); throw; }
        if (saved != null && !await db.ClassDocuments.AnyAsync(d => d.FilePath == old)) storage.TryDelete(old);
        TempData["SuccessMessage"] = "Đã cập nhật tài liệu."; return RedirectToAction(nameof(Index));
    }
    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> SetPublished(int id, bool published)
    {
        if (!ModelState.IsValid) return BadRequest("Trạng thái công bố không hợp lệ.");
        var teacherId = await TeacherIdAsync();var item = await OwnAsync(id, teacherId);
        if (item == null) return NotFound();
        item.IsPublished = published;item.UpdatedAt = DateTime.Now;
        Log(teacherId, "DocumentStatus", (published ? "Công bố tài liệu: " : "Ẩn tài liệu: ") + item.Title);
        await db.SaveChangesAsync();TempData["SuccessMessage"] = published ? "Đã công bố tài liệu cho học viên trong lớp." : "Đã ẩn tài liệu khỏi học viên.";
        return RedirectToAction(nameof(Index));
    }
    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        var teacherId = await TeacherIdAsync();var item = await OwnAsync(id, teacherId);
        if (item == null) return NotFound();
        var old = item.FilePath;db.ClassDocuments.Remove(item);Log(teacherId, "DocumentDelete", "Xóa tài liệu: " + item.Title);
        await db.SaveChangesAsync();if (!await db.ClassDocuments.AnyAsync(d => d.FilePath == old)) storage.TryDelete(old);
        TempData["SuccessMessage"] = "Đã xóa tài liệu.";return RedirectToAction(nameof(Index));
    }
    public async Task<IActionResult> Download(int id)
    {
        var item = await OwnAsync(id, await TeacherIdAsync());if (item == null) return NotFound();
        var file = storage.Resolve(item.FilePath);if (file == null) return NotFound();
        Response.Headers["X-Content-Type-Options"] = "nosniff"; Response.Headers.CacheControl = "private, no-store";
        return PhysicalFile(file, "application/octet-stream", "Tai-lieu-" + item.DocumentId + Path.GetExtension(file));
    }
}
