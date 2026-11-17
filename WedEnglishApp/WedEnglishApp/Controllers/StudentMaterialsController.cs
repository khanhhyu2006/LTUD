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
