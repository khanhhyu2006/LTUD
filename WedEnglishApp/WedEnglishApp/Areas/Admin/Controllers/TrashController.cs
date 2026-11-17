// =================================================================================================
// CONTROLLER: TrashController (Area: Admin) - QUẢN LÝ THÙNG RÁC TRUNG TÂM (XÓA MỀM / KHÔI PHỤC)
// Quyền truy cập: [Area("Admin")], [Authorize(Roles = "Admin")] - Dành riêng cho Quản trị viên
// Nghiệp vụ: Xem tất cả dữ liệu đã xóa mềm, khôi phục hoặc xóa vĩnh viễn
// =================================================================================================

using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.ViewModels.Admin;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]                  // Thuộc phân vùng Quản trị viên (Areas/Admin)
    [Authorize(Roles = "Admin")]     // Kiểm tra quyền hạn phải là Admin
    public class TrashController : Controller
    {
        private readonly ApplicationDbContext _context;

        public TrashController(ApplicationDbContext context)
        {
            _context = context;
        }

        // =============================================================================================
        // HÀM 1: GET /Admin/Trash - XEM TẤT CẢ DỮ LIỆU TRONG THÙNG RÁC
        // =============================================================================================
        public async Task<IActionResult> Index(string tab = "all")
        {
            var model = new TrashViewModel
            {
                ActiveTab = tab, // Tab đang được chọn hiển thị (all, banners, programs, classes,...)

                // Lấy danh sách Banner đã xóa mềm
                DeletedBanners = await _context.Banners
                    .Where(b => b.IsDeleted)
                    .OrderByDescending(b => b.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Chương trình học đã xóa mềm
                DeletedPrograms = await _context.Programs
                    .Where(p => p.IsDeleted)
                    .OrderByDescending(p => p.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Lớp học đã xóa mềm
                DeletedClasses = await _context.Classes
                    .Where(c => c.IsDeleted)
                    .Include(c => c.Program)
                    .OrderByDescending(c => c.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Yêu cầu tư vấn đã xóa mềm
                DeletedConsultations = await _context.Consultations
                    .Where(c => c.IsDeleted)
                    .OrderByDescending(c => c.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Đăng ký đã xóa mềm
                DeletedRegistrations = await _context.Registrations
                    .Where(r => r.IsDeleted)
                    .Include(r => r.Student).ThenInclude(s => s.UserAccount)
                    .Include(r => r.Program)
                .Include(r => r.Class).ThenInclude(c => c.Program)
                    .OrderByDescending(r => r.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Bài thi xếp lớp đã xóa mềm
                DeletedPlacementTests = await _context.PlacementTests
                    .Where(pt => pt.IsDeleted)
                    .Include(pt => pt.Student).ThenInclude(s => s.UserAccount)
                    .OrderByDescending(pt => pt.DeletedAt)
                    .ToListAsync(),

                // Lấy danh sách Tài khoản người dùng đã xóa mềm
                DeletedUserAccounts = await _context.UserAccounts
                    .Where(u => u.IsDeleted)
                    .OrderByDescending(u => u.DeletedAt)
                    .ToListAsync()
            };

            return View(model);
        }

        // =============================================================================================
        // HÀM 2: POST /Admin/Trash/Restore - KHÔI PHỤC DỮ LIỆU TỪ THÙNG RÁC
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Restore(string entityType, int id)
        {
            string itemName = ""; // Tên hiển thị của mục đã khôi phục

            switch (entityType)
            {
                case "Banner":
                    var banner = await _context.Banners.FindAsync(id);
                    if (banner == null) return NotFound();
                    banner.IsDeleted = false;
                    banner.DeletedAt = null;
                    itemName = $"Banner '{banner.Title}'";
                    break;

                case "Program":
                    var program = await _context.Programs.FindAsync(id);
                    if (program == null) return NotFound();
                    program.IsDeleted = false;
                    program.DeletedAt = null;
                    itemName = $"Chương trình '{program.ProgramName}'";
                    break;

                case "Class":
                    var cls = await _context.Classes.FindAsync(id);
                    if (cls == null) return NotFound();
                    cls.IsDeleted = false;
                    cls.DeletedAt = null;
                    itemName = $"Lớp học '{cls.ClassName}'";
                    break;

                case "Consultation":
                    var consult = await _context.Consultations.FindAsync(id);
                    if (consult == null) return NotFound();
                    consult.IsDeleted = false;
                    consult.DeletedAt = null;
                    itemName = $"Yêu cầu tư vấn của '{consult.ContactName}'";
                    break;

                case "Registration":
                    var reg = await _context.Registrations.FindAsync(id);
                    if (reg == null) return NotFound();
                    reg.IsDeleted = false;
                    reg.DeletedAt = null;
                    itemName = $"Đăng ký #REG-{id}";
                    break;

                case "PlacementTest":
                    var test = await _context.PlacementTests.FindAsync(id);
                    if (test == null) return NotFound();
                    test.IsDeleted = false;
                    test.DeletedAt = null;
                    itemName = $"Bài thi xếp lớp #{id}";
                    break;

                case "UserAccount":
                    var user = await _context.UserAccounts.FindAsync(id);
                    if (user == null) return NotFound();
                    user.IsDeleted = false;
                    user.DeletedAt = null;
                    itemName = $"Tài khoản '{user.FullName}' ({user.Role})";
                    break;

                default:
                    return BadRequest("Loại dữ liệu không hợp lệ.");
            }

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã khôi phục {itemName} thành công! Dữ liệu đã được đưa trở lại danh sách quản lý.";
            return RedirectToAction(nameof(Index));
        }

        // =============================================================================================
        // HÀM 3: POST /Admin/Trash/PermanentDelete - XÓA VĨNH VIỄN DỮ LIỆU KHỎI CƠ SỞ DỮ LIỆU
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> PermanentDelete(string entityType, int id)
        {
            string itemName = ""; // Tên hiển thị của mục đã xóa vĩnh viễn

            switch (entityType)
            {
                case "Banner":
                    var banner = await _context.Banners.FindAsync(id);
                    if (banner == null) return NotFound();
                    itemName = $"Banner '{banner.Title}'";
                    _context.Banners.Remove(banner);
                    break;

                case "Program":
                    var program = await _context.Programs.Include(p => p.Classes).FirstOrDefaultAsync(p => p.ProgramId == id);
                    if (program == null) return NotFound();
                    if (program.Classes.Any(c => !c.IsDeleted) || await _context.Registrations.AnyAsync(r => r.ProgramId == id))
                    {
                        TempData["ErrorMessage"] = "Không thể xóa vĩnh viễn khóa học vì vẫn còn lớp học hoặc đơn đăng ký liên kết!";
                        return RedirectToAction(nameof(Index));
                    }
                    itemName = $"Chương trình '{program.ProgramName}'";
                    _context.Programs.Remove(program);
                    break;

                case "Class":
                    var cls = await _context.Classes.Include(c => c.Registrations).FirstOrDefaultAsync(c => c.ClassId == id);
                    if (cls == null) return NotFound();
                    if (cls.Registrations.Any(r => !r.IsDeleted))
                    {
                        TempData["ErrorMessage"] = "Không thể xóa vĩnh viễn lớp học vì vẫn còn đăng ký liên kết chưa xóa!";
                        return RedirectToAction(nameof(Index));
                    }
                    itemName = $"Lớp học '{cls.ClassName}'";
                    _context.Classes.Remove(cls);
                    break;

                case "Consultation":
                    var consult = await _context.Consultations.FindAsync(id);
                    if (consult == null) return NotFound();
                    itemName = $"Yêu cầu tư vấn của '{consult.ContactName}'";
                    _context.Consultations.Remove(consult);
                    break;

                case "Registration":
                    var reg = await _context.Registrations.Include(r => r.Payment).FirstOrDefaultAsync(r => r.RegistrationId == id);
                    if (reg == null) return NotFound();
                    if (reg.Payment != null) _context.Payments.Remove(reg.Payment);
                    itemName = $"Đăng ký #REG-{id}";
                    _context.Registrations.Remove(reg);
                    break;

                case "PlacementTest":
                    var test = await _context.PlacementTests.FindAsync(id);
                    if (test == null) return NotFound();
                    itemName = $"Bài thi xếp lớp #{id}";
                    _context.PlacementTests.Remove(test);
                    break;

                case "UserAccount":
                    var user = await _context.UserAccounts
                        .Include(u => u.Student)
                        .Include(u => u.Teacher)
                        .FirstOrDefaultAsync(u => u.AccountId == id);
                    if (user == null) return NotFound();
                    // Xóa bản ghi Student/Teacher liên kết trước
                    if (user.Student != null) _context.Students.Remove(user.Student);
                    if (user.Teacher != null) _context.Teachers.Remove(user.Teacher);
                    itemName = $"Tài khoản '{user.FullName}' ({user.Role})";
                    _context.UserAccounts.Remove(user);
                    break;

                default:
                    return BadRequest("Loại dữ liệu không hợp lệ.");
            }

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã xóa vĩnh viễn {itemName} khỏi hệ thống! Dữ liệu này không thể khôi phục lại.";
            return RedirectToAction(nameof(Index));
        }

        // =============================================================================================
        // HÀM 4: POST /Admin/Trash/EmptyTrash - XÓA SẠCH TOÀN BỘ THÙNG RÁC
        // =============================================================================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> EmptyTrash()
        {
            int totalDeleted = 0;

            // Xóa tất cả Consultation đã xóa mềm
            var deletedConsults = await _context.Consultations.Where(c => c.IsDeleted).ToListAsync();
            _context.Consultations.RemoveRange(deletedConsults);
            totalDeleted += deletedConsults.Count;

            // Xóa tất cả Banner đã xóa mềm
            var deletedBanners = await _context.Banners.Where(b => b.IsDeleted).ToListAsync();
            _context.Banners.RemoveRange(deletedBanners);
            totalDeleted += deletedBanners.Count;

            // Xóa tất cả PlacementTest đã xóa mềm
            var deletedTests = await _context.PlacementTests.Where(pt => pt.IsDeleted).ToListAsync();
            _context.PlacementTests.RemoveRange(deletedTests);
            totalDeleted += deletedTests.Count;

            // Xóa Payment liên kết rồi xóa Registration đã xóa mềm
            var deletedRegs = await _context.Registrations.Where(r => r.IsDeleted).Include(r => r.Payment).ToListAsync();
            foreach (var reg in deletedRegs)
            {
                if (reg.Payment != null) _context.Payments.Remove(reg.Payment);
            }
            _context.Registrations.RemoveRange(deletedRegs);
            totalDeleted += deletedRegs.Count;

            // Xóa Class đã xóa mềm (chỉ các lớp không còn đăng ký chưa xóa)
            var deletedClasses = await _context.Classes.Where(c => c.IsDeleted).Include(c => c.Registrations).ToListAsync();
            var safeClasses = deletedClasses.Where(c => !c.Registrations.Any(r => !r.IsDeleted)).ToList();
            _context.Classes.RemoveRange(safeClasses);
            totalDeleted += safeClasses.Count;

            // Xóa Program đã xóa mềm (chỉ các chương trình không còn lớp chưa xóa)
            var deletedPrograms = await _context.Programs.Where(p => p.IsDeleted).Include(p => p.Classes).ToListAsync();
            var retainedProgramIds = await _context.Registrations.Where(r => !r.IsDeleted).Select(r => r.ProgramId).Distinct().ToListAsync();
            var safePrograms = deletedPrograms.Where(p => !p.Classes.Any(c => !c.IsDeleted) && !retainedProgramIds.Contains(p.ProgramId)).ToList();
            _context.Programs.RemoveRange(safePrograms);
            totalDeleted += safePrograms.Count;

            // Xóa UserAccount đã xóa mềm (kèm Student/Teacher liên kết)
            var deletedUsers = await _context.UserAccounts
                .Where(u => u.IsDeleted)
                .Include(u => u.Student)
                .Include(u => u.Teacher)
                .ToListAsync();
            foreach (var user in deletedUsers)
            {
                if (user.Student != null) _context.Students.Remove(user.Student);
                if (user.Teacher != null) _context.Teachers.Remove(user.Teacher);
            }
            _context.UserAccounts.RemoveRange(deletedUsers);
            totalDeleted += deletedUsers.Count;

            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã dọn sạch thùng rác! Tổng cộng {totalDeleted} mục đã bị xóa vĩnh viễn.";
            return RedirectToAction(nameof(Index));
        }
    }
}
