using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class ProgramManagerController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ProgramManagerController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Admin/ProgramManager
        public async Task<IActionResult> Index()
        {
            var programs = await _context.Programs
                .Where(p => !p.IsDeleted)
                .Include(p => p.Classes.Where(c => !c.IsDeleted))
                .OrderByDescending(p => p.ProgramId)
                .ToListAsync();
            return View(programs);
        }

        // GET: Admin/ProgramManager/Create
        public IActionResult Create()
        {
            return View(new CourseProgram());
        }

        // POST: Admin/ProgramManager/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(CourseProgram program)
        {
            if (ModelState.IsValid)
            {
                program.CreatedAt = DateTime.Now;
                _context.Programs.Add(program);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Thêm mới chương trình học thành công!";
                return RedirectToAction(nameof(Index));
            }
            return View(program);
        }

        // GET: Admin/ProgramManager/Edit/5
        public async Task<IActionResult> Edit(int id)
        {
            var program = await _context.Programs.FindAsync(id);
            if (program == null) return NotFound();
            return View(program);
        }

        // POST: Admin/ProgramManager/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, CourseProgram program)
        {
            if (id != program.ProgramId) return NotFound();

            if (ModelState.IsValid)
            {
                _context.Update(program);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Cập nhật chương trình học thành công!";
                return RedirectToAction(nameof(Index));
            }
            return View(program);
        }

        // POST: Admin/ProgramManager/ToggleStatus/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> ToggleStatus(int id)
        {
            var program = await _context.Programs.FindAsync(id);
            if (program == null) return NotFound();

            program.IsActive = !program.IsActive;
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã cập nhật trạng thái chương trình '{program.ProgramName}' thành {(program.IsActive ? "Kích hoạt" : "Tạm dừng")}.";
            return RedirectToAction(nameof(Index));
        }

        // POST: Admin/ProgramManager/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var program = await _context.Programs.Include(p => p.Classes.Where(c => !c.IsDeleted)).FirstOrDefaultAsync(p => p.ProgramId == id);
            if (program == null) return NotFound();

            if (program.Classes.Any())
            {
                TempData["ErrorMessage"] = "Không thể xóa chương trình đang có lớp học đang hoạt động! Bạn có thể chuyển trạng thái sang Tạm dừng hoặc xóa lớp học trước.";
                return RedirectToAction(nameof(Index));
            }

            program.IsDeleted = true;
            program.DeletedAt = DateTime.Now;
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã chuyển chương trình '{program.ProgramName}' vào thùng rác! Bạn có thể xem hoặc khôi phục trong mục Thùng rác.";
            return RedirectToAction(nameof(Index));
        }
    }
}
