using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class TeacherManagerController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly IWebHostEnvironment _environment;

        public TeacherManagerController(ApplicationDbContext context, IWebHostEnvironment environment)
        {
            _context = context;
            _environment = environment;
        }

        // GET: Admin/TeacherManager
        public async Task<IActionResult> Index()
        {
            var teachers = await _context.Teachers
                .Include(t => t.UserAccount)
                .Include(t => t.Classes)
                .Where(t => !t.UserAccount.IsDeleted) // Chỉ hiển thị tài khoản chưa xóa vào thùng rác
                .ToListAsync();

            return View(teachers);
        }

        [HttpPost, ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleStatus(int id)
        {
            var teacher = await _context.Teachers.Include(t => t.UserAccount).FirstOrDefaultAsync(t => t.TeacherId == id && !t.UserAccount.IsDeleted);
            if (teacher == null) return NotFound();
            teacher.UserAccount.IsActive = !teacher.UserAccount.IsActive;
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = teacher.UserAccount.IsActive ? "Đã kích hoạt tài khoản giáo viên." : "Đã vô hiệu hóa tài khoản giáo viên; phiên đăng nhập sẽ bị thu hồi ở yêu cầu tiếp theo.";
            return RedirectToAction(nameof(Index));
        }
        // GET: Admin/TeacherManager/Create
        public IActionResult Create()
        {
            return View();
        }

        // POST: Admin/TeacherManager/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(string fullName, string email, string password, string specialization, string degree, string bio, IFormFile? photo)
        {
            if (string.IsNullOrWhiteSpace(fullName) || string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(password))
            {
                ModelState.AddModelError(string.Empty, "Vui lòng nhập đầy đủ họ tên, email và mật khẩu.");
                return View();
            }

            if (await _context.UserAccounts.AnyAsync(u => u.Email.ToLower() == email.Trim().ToLower()))
            {
                ModelState.AddModelError("email", "Email này đã tồn tại trong hệ thống.");
                return View();
            }

            string? photoUrl = null;
            if (photo != null)
            {
                var extension = await ImageUploadValidator.GetValidatedExtensionAsync(photo);
                if (extension == null)
                {
                    ModelState.AddModelError("photo", "Ảnh phải là tệp JPG, PNG hoặc WEBP hợp lệ và dung lượng không quá 5 MB.");
                    return View();
                }

                photoUrl = await ImageUploadStorage.SaveAsync(_environment, photo, "teachers");
            }

            var user = new UserAccount
            {
                FullName = fullName.Trim(),
                Email = email.Trim().ToLower(),
                PasswordHash = BCrypt.Net.BCrypt.HashPassword(password),
                Role = "Teacher",
                AvatarUrl = photoUrl ?? "/images/avatars/teacher1.png",
                IsActive = true,
                CreatedAt = DateTime.Now
            };

            _context.UserAccounts.Add(user);
            await _context.SaveChangesAsync();

            var teacher = new WedEnglishApp.Models.Teacher
            {
                AccountId = user.AccountId,
                Specialization = specialization?.Trim() ?? "Tiếng Anh",
                Degree = degree?.Trim() ?? "Cử nhân",
                Bio = bio?.Trim(),
                PhotoUrl = photoUrl
            };

            _context.Teachers.Add(teacher);
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Thêm giảng viên '{fullName}' thành công!";
            return RedirectToAction(nameof(Index));
        }

        // POST: Admin/TeacherManager/Delete/5 - chuyển tài khoản giáo viên nghỉ việc vào thùng rác
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var teacher = await _context.Teachers
                .Include(t => t.UserAccount)
                .FirstOrDefaultAsync(t => t.TeacherId == id && !t.UserAccount.IsDeleted);

            if (teacher == null) return NotFound();

            teacher.UserAccount.IsDeleted = true;
            teacher.UserAccount.DeletedAt = DateTime.Now;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã chuyển tài khoản giảng viên {teacher.UserAccount.FullName} vào thùng rác. Có thể khôi phục trong mục Thùng rác.";
            return RedirectToAction(nameof(Index));
        }

        // GET: Admin/TeacherManager/Edit/5
        public async Task<IActionResult> Edit(int id)
        {
            var teacher = await _context.Teachers
                .Include(t => t.UserAccount)
                .FirstOrDefaultAsync(t => t.TeacherId == id);

            if (teacher == null) return NotFound();

            return View(teacher);
        }

        // POST: Admin/TeacherManager/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, string fullName, string degree, string specialization, string bio, IFormFile? photo)
        {
            var teacher = await _context.Teachers
                .Include(t => t.UserAccount)
                .FirstOrDefaultAsync(t => t.TeacherId == id);

            if (teacher == null) return NotFound();

            string? photoUrl = null;
            if (photo != null)
            {
                var extension = await ImageUploadValidator.GetValidatedExtensionAsync(photo);
                if (extension == null)
                {
                    ModelState.AddModelError("photo", "Ảnh phải là tệp JPG, PNG hoặc WEBP hợp lệ và dung lượng không quá 5 MB.");
                    return View(teacher);
                }

                photoUrl = await ImageUploadStorage.SaveAsync(_environment, photo, "teachers");
            }

            teacher.UserAccount.FullName = fullName?.Trim() ?? teacher.UserAccount.FullName;
            teacher.Degree = degree?.Trim();
            teacher.Specialization = specialization?.Trim() ?? teacher.Specialization;
            teacher.Bio = bio?.Trim();
            if (photoUrl != null)
            {
                teacher.PhotoUrl = photoUrl;
                teacher.UserAccount.AvatarUrl = photoUrl;
            }

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Cập nhật thông tin giảng viên '{teacher.UserAccount.FullName}' thành công!";
            return RedirectToAction(nameof(Index));
        }
    }
}
