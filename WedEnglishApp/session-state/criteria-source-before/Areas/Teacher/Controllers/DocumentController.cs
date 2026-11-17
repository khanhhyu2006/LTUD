using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Areas.Teacher.Controllers
{
    [Area("Teacher")]
    [Authorize(Roles = "Teacher")]
    public class DocumentController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _env;

        public DocumentController(ApplicationDbContext context, IWebHostEnvironment env)
        {
            _context = context;
            _env = env;
        }

        private async Task<int> GetTeacherIdAsync()
        {
            var userIdStr = User.FindFirstValue(ClaimTypes.NameIdentifier);
            if (!int.TryParse(userIdStr, out int accountId)) return 0;
            var teacher = await _context.Teachers.FirstOrDefaultAsync(t => t.AccountId == accountId);
            return teacher?.TeacherId ?? 0;
        }

        // GET: Teacher/Document
        public async Task<IActionResult> Index()
        {
            int teacherId = await GetTeacherIdAsync();
            if (teacherId == 0) return RedirectToAction("Login", "Account", new { area = "" });

            var documents = await _context.ClassDocuments
                .Include(d => d.Class)
                .Where(d => d.Class.TeacherId == teacherId)
                .OrderByDescending(d => d.UploadedAt)
                .ToListAsync();

            ViewBag.Classes = new SelectList(await _context.Classes.Where(c => c.TeacherId == teacherId).ToListAsync(), "ClassId", "ClassName");
            return View(documents);
        }

        // POST: Teacher/Document/Upload
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Upload(int classId, string title, IFormFile? documentFile)
        {
            if (classId == 0 || string.IsNullOrWhiteSpace(title) || documentFile == null)
            {
                TempData["ErrorMessage"] = "Vui lòng chọn lớp, nhập tiêu đề và chọn file tài liệu!";
                return RedirectToAction(nameof(Index));
            }

            string uploadsFolder = Path.Combine(_env.WebRootPath, "uploads", "documents");
            if (!Directory.Exists(uploadsFolder))
            {
                Directory.CreateDirectory(uploadsFolder);
            }

            string uniqueFileName = $"{Guid.NewGuid()}_{Path.GetFileName(documentFile.FileName)}";
            string filePath = Path.Combine(uploadsFolder, uniqueFileName);

            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await documentFile.CopyToAsync(stream);
            }

            var doc = new ClassDocument
            {
                ClassId = classId,
                Title = title.Trim(),
                FilePath = $"/uploads/documents/{uniqueFileName}",
                UploadedAt = DateTime.Now
            };

            _context.ClassDocuments.Add(doc);
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Tải lên tài liệu '{title}' thành công!";
            return RedirectToAction(nameof(Index));
        }

        // POST: Teacher/Document/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var doc = await _context.ClassDocuments.FindAsync(id);
            if (doc != null)
            {
                _context.ClassDocuments.Remove(doc);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Đã xóa tài liệu thành công!";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
