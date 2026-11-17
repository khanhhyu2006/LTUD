using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class StudentManagerController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _environment;

        public StudentManagerController(ApplicationDbContext context, IWebHostEnvironment environment)
        {
            _context = context;
            _environment = environment;
        }

        // GET: Admin/StudentManager
        public async Task<IActionResult> Index()
        {
            var students = await _context.Students
                .Include(s => s.UserAccount)
                .Include(s => s.Registrations)
                .Where(s => !s.UserAccount.IsDeleted) // Chỉ hiển thị tài khoản chưa xóa vào thùng rác
                .OrderByDescending(s => s.StudentId)
                .ToListAsync();

            return View(students);
        }

        // POST: Admin/StudentManager/ToggleStatus/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleStatus(int id)
        {
            var student = await _context.Students.Include(s => s.UserAccount).FirstOrDefaultAsync(s => s.StudentId == id);
            if (student == null) return NotFound();

            student.UserAccount.IsActive = !student.UserAccount.IsActive;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã {(student.UserAccount.IsActive ? "kích hoạt" : "vô hiệu hóa")} tài khoản học viên {student.UserAccount.FullName}.";
            return RedirectToAction(nameof(Index));
        }

        // GET: Admin/StudentManager/Edit/5
        public async Task<IActionResult> Edit(int id)
        {
            var student = await _context.Students
                .Include(s => s.UserAccount)
                .FirstOrDefaultAsync(s => s.StudentId == id);

            if (student == null) return NotFound();

            return View(student);
        }

        // POST: Admin/StudentManager/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, string fullName, string phoneNumber, string address, DateTime? dateOfBirth, IFormFile? photo)
        {
            var student = await _context.Students
                .Include(s => s.UserAccount)
                .FirstOrDefaultAsync(s => s.StudentId == id);

            if (student == null) return NotFound();

            string? photoUrl = null;
            if (photo != null)
            {
                var extension = await ImageUploadValidator.GetValidatedExtensionAsync(photo);
                if (extension == null)
                {
                    ModelState.AddModelError("photo", "Ảnh phải là tệp JPG, PNG hoặc WEBP hợp lệ và dung lượng không quá 5 MB.");
                    return View(student);
                }

                photoUrl = await ImageUploadStorage.SaveAsync(_environment, photo, "students");
            }

            student.UserAccount.FullName = fullName?.Trim() ?? student.UserAccount.FullName;
            student.PhoneNumber = phoneNumber?.Trim();
            student.Address = address?.Trim();
            student.DateOfBirth = dateOfBirth;
            if (photoUrl != null)
            {
                student.PhotoUrl = photoUrl;
                student.UserAccount.AvatarUrl = photoUrl;
            }

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Cập nhật thông tin học viên '{student.UserAccount.FullName}' thành công!";
            return RedirectToAction(nameof(Index));
        }
    }
}
