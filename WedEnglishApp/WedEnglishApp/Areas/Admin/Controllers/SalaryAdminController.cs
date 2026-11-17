using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    // =================================================================================================
    // CONTROLLER: SalaryAdminController (Area: Admin) - QUẢN LÝ BẢNG LƯƠNG GIẢNG VIÊN
    // =================================================================================================
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class SalaryAdminController : Controller
    {
        private readonly ApplicationDbContext _context;

        public SalaryAdminController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Admin/SalaryAdmin
        public async Task<IActionResult> Index(int? month, int? year, int? teacherId)
        {
            var query = _context.TeacherSalaries
                .Include(s => s.Teacher).ThenInclude(t => t.UserAccount)
                .AsQueryable();

            if (month.HasValue && month.Value > 0)
            {
                query = query.Where(s => s.Month == month.Value);
            }
            if (year.HasValue && year.Value > 0)
            {
                query = query.Where(s => s.Year == year.Value);
            }
            if (teacherId.HasValue && teacherId.Value > 0)
            {
                query = query.Where(s => s.TeacherId == teacherId.Value);
            }

            var salaries = await query
                .OrderByDescending(s => s.Year)
                .ThenByDescending(s => s.Month)
                .ToListAsync();

            // Khắc phục lỗi font chữ tiếng Việt do mã hóa cũ
            bool hasCorruptedNote = false;
            foreach (var s in salaries)
            {
                if (!string.IsNullOrEmpty(s.Note) && (s.Note.Contains("Tá") || s.Note.Contains("LÆ") || s.Note.Contains("Â") || s.Note.Contains("Ã") || s.Note.Contains("°")))
                {
                    if (s.Month == 11) s.Note = "Tạm tính lương tháng 11/2026";
                    else if (s.Month == 10) s.Note = "Lương tháng 10/2026 - Giảng dạy tốt";
                    else s.Note = $"Lương giảng dạy tháng {s.Month}/{s.Year}";
                    hasCorruptedNote = true;
                }
            }
            if (hasCorruptedNote)
            {
                await _context.SaveChangesAsync();
            }

            ViewBag.Teachers = await _context.Teachers
                .Include(t => t.UserAccount)
                .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted)
                .ToListAsync();

            ViewBag.SelectedMonth = month;
            ViewBag.SelectedYear = year;
            ViewBag.SelectedTeacherId = teacherId;

            return View(salaries);
        }

        // POST: Admin/SalaryAdmin/CreateOrUpdate
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> CreateOrUpdate(int? salaryId, int teacherId, int month, int year, decimal baseSalary, int totalTeachingHours, decimal hourlyRate, decimal bonus, decimal deduction, string? note)
        {
            decimal totalSalary = baseSalary + (totalTeachingHours * hourlyRate) + bonus - deduction;
            if (totalSalary < 0) totalSalary = 0;

            if (salaryId.HasValue && salaryId.Value > 0)
            {
                var existing = await _context.TeacherSalaries.FindAsync(salaryId.Value);
                if (existing != null)
                {
                    existing.TeacherId = teacherId;
                    existing.Month = month;
                    existing.Year = year;
                    existing.BaseSalary = baseSalary;
                    existing.TotalTeachingHours = totalTeachingHours;
                    existing.HourlyRate = hourlyRate;
                    existing.Bonus = bonus;
                    existing.Deduction = deduction;
                    existing.TotalSalary = totalSalary;
                    existing.Note = note?.Trim();
                    await _context.SaveChangesAsync();
                    TempData["SuccessMessage"] = "Cập nhật bảng tính lương thành công!";
                }
            }
            else
            {
                var newSalary = new TeacherSalary
                {
                    TeacherId = teacherId,
                    Month = month,
                    Year = year,
                    BaseSalary = baseSalary,
                    TotalTeachingHours = totalTeachingHours,
                    HourlyRate = hourlyRate,
                    Bonus = bonus,
                    Deduction = deduction,
                    TotalSalary = totalSalary,
                    Status = "Pending",
                    Note = note?.Trim(),
                    CreatedAt = DateTime.Now
                };
                _context.TeacherSalaries.Add(newSalary);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Thêm mới bảng lương thành công!";
            }

            return RedirectToAction(nameof(Index), new { month, year, teacherId });
        }

        // POST: Admin/SalaryAdmin/ConfirmPayment
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ConfirmPayment(int id)
        {
            var salary = await _context.TeacherSalaries
                .Include(s => s.Teacher).ThenInclude(t => t.UserAccount)
                .FirstOrDefaultAsync(s => s.SalaryId == id);

            if (salary == null) return NotFound();

            salary.Status = "Paid";
            salary.PaymentDate = DateTime.Now;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã duyệt chi trả lương thành công cho giảng viên '{salary.Teacher.UserAccount.FullName}' (Tháng {salary.Month}/{salary.Year})!";
            return RedirectToAction(nameof(Index));
        }

        // POST: Admin/SalaryAdmin/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var salary = await _context.TeacherSalaries.FindAsync(id);
            if (salary != null)
            {
                _context.TeacherSalaries.Remove(salary);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Đã xóa bản ghi lương thành công!";
            }
            return RedirectToAction(nameof(Index));
        }
    }
}
