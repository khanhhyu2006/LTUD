from pathlib import Path
import shutil
ROOT=Path('WedEnglishApp');BACK=Path('session-state/criteria-source-before')
def write(rel,s):
 p=ROOT/rel
 if p.exists():
  b=BACK/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():shutil.copy2(p,b)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf8')
def edit(rel,a,b):
 p=ROOT/rel;s=p.read_text(encoding='utf-8-sig');assert a in s,(rel,a[:60]);write(rel,s.replace(a,b))
write('Models/TeacherActivity.cs','''
using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.Models;
public class TeacherActivity
{
    [Key] public int ActivityId { get; set; }
    public int TeacherId { get; set; }
    [MaxLength(30)] public string Kind { get; set; } = "";
    [MaxLength(300)] public string Description { get; set; } = "";
    public DateTime OccurredAt { get; set; } = DateTime.Now;
    public Teacher Teacher { get; set; } = null!;
}
''')
edit('Models/ClassDocument.cs','public DateTime UploadedAt { get; set; } = DateTime.Now;','public DateTime UploadedAt { get; set; } = DateTime.Now;\n        public bool IsPublished { get; set; } = true;\n        public DateTime? UpdatedAt { get; set; }')
edit('Models/Payment.cs','public DateTime PaymentDate { get; set; } = DateTime.Now;','public DateTime? ConfirmedAt { get; set; }\n        public DateTime PaymentDate { get; set; } = DateTime.Now;')
edit('Data/ApplicationDbContext.cs','public DbSet<ClassDocument> ClassDocuments => Set<ClassDocument>();','public DbSet<TeacherActivity> TeacherActivities => Set<TeacherActivity>();\n        public DbSet<ClassDocument> ClassDocuments => Set<ClassDocument>();')
edit('Data/ApplicationDbContext.cs','base.OnModelCreating(modelBuilder);','''base.OnModelCreating(modelBuilder);
            modelBuilder.Entity<TeacherActivity>().HasOne(a => a.Teacher).WithMany()
                .HasForeignKey(a => a.TeacherId).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<TeacherActivity>().HasIndex(a => new { a.TeacherId, a.OccurredAt });
            modelBuilder.Entity<ClassDocument>().Property(d => d.IsPublished).HasDefaultValue(true);''')
write('Data/Sql/CriteriaCompletion.sql','''
SET XACT_ABORT ON;
BEGIN TRANSACTION;
EXEC sp_getapplock @Resource=N'NHK.CriteriaCompletion.v1', @LockMode='Exclusive', @LockOwner='Transaction';
IF COL_LENGTH('dbo.ClassDocuments','IsPublished') IS NULL
 ALTER TABLE dbo.ClassDocuments ADD IsPublished bit NOT NULL CONSTRAINT DF_ClassDocuments_IsPublished DEFAULT(1);
IF COL_LENGTH('dbo.ClassDocuments','UpdatedAt') IS NULL
 ALTER TABLE dbo.ClassDocuments ADD UpdatedAt datetime2 NULL;
IF COL_LENGTH('dbo.Payments','ConfirmedAt') IS NULL
 ALTER TABLE dbo.Payments ADD ConfirmedAt datetime2 NULL;
IF OBJECT_ID('dbo.TeacherActivities','U') IS NULL
BEGIN
 CREATE TABLE dbo.TeacherActivities(
  ActivityId int IDENTITY(1,1) NOT NULL CONSTRAINT PK_TeacherActivities PRIMARY KEY,
  TeacherId int NOT NULL,
  Kind nvarchar(30) NOT NULL,
  Description nvarchar(300) NOT NULL,
  OccurredAt datetime2 NOT NULL,
  CONSTRAINT FK_TeacherActivities_Teachers FOREIGN KEY(TeacherId) REFERENCES dbo.Teachers(TeacherId) ON DELETE CASCADE);
 CREATE INDEX IX_TeacherActivities_TeacherId_OccurredAt ON dbo.TeacherActivities(TeacherId,OccurredAt);
END;
COMMIT;
''')
write('Data/CriteriaCompletionSchema.cs','''
using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;
public static class CriteriaCompletionSchema
{
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(CriteriaCompletionSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.CriteriaCompletion.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
''')
edit('WedEnglishApp.csproj','<EmbeddedResource Include="Data/Sql/ConsultationChat.sql" />','<EmbeddedResource Include="Data/Sql/ConsultationChat.sql" />\n    <EmbeddedResource Include="Data/Sql/CriteriaCompletion.sql" />')
edit('Data/DbInitializer.cs','ConsultationChatSchema.Upgrade(context);','ConsultationChatSchema.Upgrade(context);\n            CriteriaCompletionSchema.Upgrade(context);')
write('Services/CookieAccountValidation.cs','''
using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
namespace WedEnglishApp.Services;
public static class CookieAccountValidation
{
    public static async Task ValidateAsync(CookieValidatePrincipalContext context)
    {
        int.TryParse(context.Principal?.FindFirstValue(ClaimTypes.NameIdentifier), out var id);
        var role = context.Principal?.FindFirstValue(ClaimTypes.Role);
        var db = context.HttpContext.RequestServices.GetRequiredService<ApplicationDbContext>();
        if (!await db.UserAccounts.AnyAsync(a => a.AccountId == id && a.IsActive && !a.IsDeleted && a.Role == role))
        {
            context.RejectPrincipal();
            await context.HttpContext.SignOutAsync(context.Scheme.Name);
        }
    }
}
''')
edit('Program.cs','options.SlidingExpiration = true;','options.SlidingExpiration = true;\n        options.Events.OnValidatePrincipal = WedEnglishApp.Services.CookieAccountValidation.ValidateAsync;')
# Legacy document files are accessible only through authorized download actions.
edit('Program.cs','app.UseStaticFiles();','''app.Use(async (context, next) =>
{
    if (context.Request.Path.StartsWithSegments("/uploads/documents", StringComparison.OrdinalIgnoreCase)
        || context.Request.Path.StartsWithSegments("/App_Data", StringComparison.OrdinalIgnoreCase))
    { context.Response.StatusCode = 404; return; }
    await next();
});
app.UseStaticFiles();''')
write('Services/DocumentStorage.cs','''
using System.IO.Compression;
namespace WedEnglishApp.Services;
public class DocumentStorage(IWebHostEnvironment env)
{
    public const long MaxBytes = 10 * 1024 * 1024;
    private static readonly HashSet<string> Extensions = new(StringComparer.OrdinalIgnoreCase) { ".pdf", ".docx", ".pptx", ".xlsx", ".txt" };
    public async Task<string?> ValidateAsync(IFormFile? file)
    {
        if (file == null || file.Length == 0 || file.Length > MaxBytes) return "Tệp phải có nội dung và không quá 10 MB.";
        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (!Extensions.Contains(ext)) return "Chỉ nhận PDF, DOCX, PPTX, XLSX hoặc TXT.";
        try
        {
            await using var input = file.OpenReadStream();
            var header = new byte[5]; var read = await input.ReadAsync(header);
            if (ext == ".pdf" && (read < 5 || !header.AsSpan().SequenceEqual("%PDF-"u8))) return "Nội dung tệp PDF không hợp lệ.";
            if (ext == ".txt")
            {
                input.Position = 0;
                using var reader = new StreamReader(input, new System.Text.UTF8Encoding(false, true), true);
                var text = await reader.ReadToEndAsync();
                if (text.Contains('\\0')) return "Tệp TXT phải là văn bản hợp lệ.";
            }
            if (ext is ".docx" or ".pptx" or ".xlsx")
            {
                input.Position = 0;
                using var zip = new ZipArchive(input, ZipArchiveMode.Read);
                var entry = ext == ".docx" ? "word/document.xml" : ext == ".pptx" ? "ppt/presentation.xml" : "xl/workbook.xml";
                if (zip.GetEntry("[Content_Types].xml") == null || zip.GetEntry(entry) == null
                    || zip.Entries.Count > 2048 || zip.Entries.Sum(e => e.Length) > 100L * 1024 * 1024)
                    return "Cấu trúc tệp Office không hợp lệ hoặc quá lớn.";
            }
        }
        catch (Exception ex) when (ex is InvalidDataException or IOException or System.Text.DecoderFallbackException)
        { return "Không thể đọc nội dung tệp. Vui lòng chọn tệp hợp lệ."; }
        return null;
    }
    public async Task<string> SaveAsync(IFormFile file)
    {
        var directory = Path.Combine(env.ContentRootPath, "App_Data", "ClassDocuments");
        Directory.CreateDirectory(directory);
        var name = Guid.NewGuid().ToString("N") + Path.GetExtension(file.FileName).ToLowerInvariant();
        await using var target = new FileStream(Path.Combine(directory, name), FileMode.CreateNew);
        await file.CopyToAsync(target);
        return "private-documents/" + name;
    }
    public string? Resolve(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        var prefix = value.StartsWith("private-documents/", StringComparison.Ordinal) ? "private-documents/" : "/uploads/documents/";
        if (!value.StartsWith(prefix, StringComparison.Ordinal)) return null;
        var name = value[prefix.Length..];
        if (string.IsNullOrWhiteSpace(name) || name != Path.GetFileName(name) || name.Contains('\\\\') || name.Contains('/') || name.Contains(':')) return null;
        var directory = prefix == "private-documents/" ? Path.Combine(env.ContentRootPath, "App_Data", "ClassDocuments") : Path.Combine(env.WebRootPath, "uploads", "documents");
        var full = Path.GetFullPath(Path.Combine(directory, name));
        return full.StartsWith(Path.GetFullPath(directory) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && File.Exists(full) ? full : null;
    }
    public void TryDelete(string value)
    {
        // Only private, generated filenames may be removed; legacy files are retained for recovery.
        if (!value.StartsWith("private-documents/", StringComparison.Ordinal)) return;
        var file = Resolve(value);
        if (file != null) { try { File.Delete(file); } catch (IOException) { } catch (UnauthorizedAccessException) { } }
    }
}
''')
write('Areas/Teacher/Controllers/DocumentController.cs','''
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
''')
write('Controllers/StudentMaterialsController.cs','''
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
namespace WedEnglishApp.Controllers;
[Authorize(Roles = "Student"), Route("Student/Materials")]
public class StudentMaterialsController(ApplicationDbContext db, IWebHostEnvironment env) : Controller
{
    private IQueryable<ClassDocument> Accessible()
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var id);
        return db.ClassDocuments.Where(d => d.IsPublished && !d.Class.IsDeleted && db.Registrations.Any(r =>
            r.ClassId == d.ClassId && r.Status == "Confirmed" && !r.IsDeleted && r.Student.AccountId == id && !r.Student.UserAccount.IsDeleted));
    }
    [HttpGet("")]
    public async Task<IActionResult> Index(int? classId)
    {
        var query = Accessible(); if (classId.HasValue) query = query.Where(d => d.ClassId == classId);
        return View(await query.Include(d => d.Class).OrderByDescending(d => d.UploadedAt).ToListAsync());
    }
    [HttpGet("Download/{id:int}")]
    public async Task<IActionResult> Download(int id)
    {
        var item = await Accessible().FirstOrDefaultAsync(d => d.DocumentId == id); if (item == null) return NotFound();
        var file = new DocumentStorage(env).Resolve(item.FilePath); if (file == null) return NotFound();
        Response.Headers["X-Content-Type-Options"] = "nosniff";Response.Headers.CacheControl = "private, no-store";
        return PhysicalFile(file,"application/octet-stream","Tai-lieu-" + item.DocumentId + Path.GetExtension(file));
    }
}
''')
edit('Areas/Admin/Controllers/TeacherManagerController.cs','// GET: Admin/TeacherManager/Create','''[HttpPost, ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleStatus(int id)
        {
            var teacher = await _context.Teachers.Include(t => t.UserAccount).FirstOrDefaultAsync(t => t.TeacherId == id && !t.UserAccount.IsDeleted);
            if (teacher == null) return NotFound();
            teacher.UserAccount.IsActive = !teacher.UserAccount.IsActive;
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = teacher.UserAccount.IsActive ? "Đã kích hoạt tài khoản giáo viên." : "Đã vô hiệu hóa tài khoản giáo viên; phiên đăng nhập sẽ bị thu hồi ở yêu cầu tiếp theo.";
            return RedirectToAction(nameof(Index));
        }
        // GET: Admin/TeacherManager/Create''')
edit('Areas/Teacher/Controllers/TeacherTestController.cs','await context.SaveChangesAsync();','''context.TeacherActivities.Add(new WedEnglishApp.Models.TeacherActivity { TeacherId = teacherId, Kind = "Grade", Description = "Lưu kết quả kiểm tra #" + id + ": " + score.ToString("0.##") + "/10" });
        await context.SaveChangesAsync();''')
edit('Areas/Teacher/Controllers/TeacherDashboardController.cs','.Include(t => t.Classes)','.Include(t => t.Classes.Where(c => !c.IsDeleted))')
edit('Areas/Teacher/Controllers/TeacherDashboardController.cs','.ThenInclude(c => c.Registrations)','.ThenInclude(c => c.Registrations.Where(r => !r.IsDeleted && r.Status == "Confirmed"))')
edit('Areas/Teacher/Controllers/TeacherDashboardController.cs','return View(teacher);','''ViewBag.RecentActivities = await _context.TeacherActivities.AsNoTracking().Where(a => a.TeacherId == teacher.TeacherId).OrderByDescending(a => a.OccurredAt).ThenByDescending(a => a.ActivityId).Take(10).ToListAsync();
            return View(teacher);''')
edit('Areas/Teacher/Controllers/TeacherDashboardController.cs','ViewBag.TotalStudents = teacher.Classes.Sum(c => c.Registrations.Count);','ViewBag.TotalStudents = teacher.Classes.SelectMany(c => c.Registrations).Select(r => r.StudentId).Distinct().Count();')
edit('Areas/Teacher/Controllers/TeacherDashboardController.cs','await _context.SaveChangesAsync();','''_context.TeacherActivities.Add(new WedEnglishApp.Models.TeacherActivity { TeacherId = teacher.TeacherId, Kind = "Profile", Description = "Cập nhật ảnh hồ sơ" });
            await _context.SaveChangesAsync();''')
edit('Areas/Admin/Controllers/PaymentAdminController.cs','payment.Status = "Paid";','''if (payment.Status != "Paid") payment.ConfirmedAt = DateTime.Now;
            payment.Status = "Paid";''')
# Existing paid rows remain untouched, including duplicate historical receipts.
edit('Views/Student/PrintReceipt.cshtml','Model.PaymentDate.ToString(', '(Model.ConfirmedAt ?? Model.PaymentDate).ToString(')
print('Implemented schema, document workflow, session revocation and activity history.')
