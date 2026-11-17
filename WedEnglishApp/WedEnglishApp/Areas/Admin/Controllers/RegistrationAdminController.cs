using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class RegistrationAdminController : Controller
    {
        private readonly ApplicationDbContext _context;

        public RegistrationAdminController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Admin/RegistrationAdmin
        public async Task<IActionResult> Index(int? programId = null)
        {
            var query = _context.Registrations
                .Where(r => !r.IsDeleted)
                .Include(r => r.Program)
                .Include(r => r.Student)
                    .ThenInclude(s => s.UserAccount)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Program)
                .Include(r => r.Class)
                    .ThenInclude(c => c.Teacher)
                        .ThenInclude(t => t!.UserAccount)
                .Include(r => r.DesiredTeacher)
                    .ThenInclude(t => t!.UserAccount)
                .Include(r => r.Payment)
                .AsQueryable();

            if (programId.HasValue && programId.Value > 0)
            {
                query = query.Where(r => r.ProgramId == programId.Value);
            }

            var registrations = await query
                .OrderByDescending(r => r.RegistrationDate)
                .ToListAsync();

            ViewBag.Programs = await _context.Programs
                .Where(p => !p.IsDeleted)
                .OrderBy(p => p.ProgramName)
                .ToListAsync();

            ViewBag.SelectedProgramId = programId;

            // Lấy danh sách các lớp đang mở để Admin có thể xếp/chuyển lớp
            ViewBag.AvailableClasses = await _context.Classes
                .Where(c => !c.IsDeleted)
                .Include(c => c.Program)
                .Include(c => c.Schedules)
                .Include(c => c.Registrations)
                .Include(c => c.Teacher).ThenInclude(t => t!.UserAccount)
                .OrderBy(c => c.ClassName)
                .ToListAsync();

            return View(registrations);
        }

        // POST: Admin/RegistrationAdmin/AssignClass
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> AssignClass(int registrationId, int newClassId)
        {
            var error = await WedEnglishApp.Services.CourseClassAssignment.AssignAsync(_context, registrationId, newClassId);
            TempData[error == null ? "SuccessMessage" : "ErrorMessage"] = error ?? "Đã xếp học viên vào lớp phù hợp.";
            return RedirectToAction(nameof(Index));
        }

        // POST: Admin/RegistrationAdmin/UpdateStatus
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> UpdateStatus(int id, string status)
        {
            var reg = await _context.Registrations.FindAsync(id);
            if (reg == null) return NotFound();

            if (status != "Pending" && status != "Cancelled")
            {
                TempData["ErrorMessage"] = "Dùng chức năng Xếp lớp để xác nhận đơn đăng ký.";
                return RedirectToAction(nameof(Index));
            }
            if (status == "Pending" && (reg.Status == "Cancelled" || reg.IsDeleted) && await _context.Registrations.AnyAsync(r => r.RegistrationId != id && r.StudentId == reg.StudentId && r.ProgramId == reg.ProgramId && !r.IsDeleted && r.Status != "Cancelled"))
            {
                TempData["ErrorMessage"] = "Học viên đã có một đơn đang hoạt động cho khóa học này.";
                return RedirectToAction(nameof(Index));
            }
            reg.ClassId = null;
            reg.Status = status;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã cập nhật trạng thái đăng ký #REG-{id} thành '{status}'.";
            return RedirectToAction(nameof(Index));
        }

        // POST: Admin/RegistrationAdmin/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var reg = await _context.Registrations.FindAsync(id);
            if (reg == null) return NotFound();

            reg.IsDeleted = true;
            reg.DeletedAt = DateTime.Now;
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã chuyển đăng ký #REG-{id} vào thùng rác! Bạn có thể xem hoặc khôi phục trong mục Thùng rác.";
            return RedirectToAction(nameof(Index));
        }
    }
}
