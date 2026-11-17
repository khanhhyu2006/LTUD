using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Admin;
using System.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;

namespace WedEnglishApp.Areas.Admin.Controllers
{
    [Area("Admin")]
    [Authorize(Roles = "Admin")]
    public class ClassManagerController : Controller
    {
        private readonly ApplicationDbContext _context;

        public ClassManagerController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: Admin/ClassManager
        public async Task<IActionResult> Index()
        {
            var classes = await _context.Classes
                .Where(c => !c.IsDeleted)
                .Include(c => c.Program)
                .Include(c => c.Teacher)
                    .ThenInclude(t => t!.UserAccount)
                .Include(c => c.Registrations)
                .OrderByDescending(c => c.StartDate)
                .ToListAsync();

            ViewBag.Teachers = await _context.Teachers
                .Include(t => t.UserAccount)
                .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted)
                .OrderBy(t => t.UserAccount.FullName)
                .ToListAsync();

            return View(classes);
        }

        // POST: Admin/ClassManager/AssignTeacher
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> AssignTeacher(int classId, int? teacherId)
        {
            var cls = await _context.Classes.FindAsync(classId);
            if (cls == null) return NotFound();

            cls.TeacherId = (teacherId.HasValue && teacherId.Value > 0) ? teacherId : null;
            await _context.SaveChangesAsync();

            if (cls.TeacherId.HasValue)
            {
                var teacher = await _context.Teachers.Include(t => t.UserAccount).FirstOrDefaultAsync(t => t.TeacherId == cls.TeacherId);
                TempData["SuccessMessage"] = $"Đã chọn Giáo viên Chủ nhiệm '{teacher?.UserAccount.FullName}' cho lớp '{cls.ClassName}' thành công!";
            }
            else
            {
                TempData["SuccessMessage"] = $"Đã hủy chỉ định GVCN cho lớp '{cls.ClassName}'. Lớp hiện ở trạng thái chờ phân bổ.";
            }

            return RedirectToAction(nameof(Index));
        }

        // GET: Admin/ClassManager/Details/5
        public async Task<IActionResult> Details(int id)
        {
            var cls = await _context.Classes
                .Include(c => c.Program)
                .Include(c => c.Schedules)
                .Include(c => c.Teacher).ThenInclude(t => t!.UserAccount)
                .Include(c => c.Registrations)
                    .ThenInclude(r => r.Student).ThenInclude(s => s.UserAccount)
                .Include(c => c.Registrations)
                    .ThenInclude(r => r.DesiredTeacher).ThenInclude(t => t!.UserAccount)
                .Include(c => c.Registrations)
                    .ThenInclude(r => r.Payment)
                .FirstOrDefaultAsync(c => c.ClassId == id && !c.IsDeleted);

            if (cls == null) return NotFound();

            // Lấy danh sách các học viên đã đăng ký cùng Chương trình học (ProgramId) này
            // nhưng chưa được xếp vào lớp này (đang chờ hoặc ở lớp khác)
            var otherRegistrations = await _context.Registrations
                .Include(r => r.Student).ThenInclude(s => s.UserAccount)
                .Include(r => r.Class)
                .Include(r => r.DesiredTeacher).ThenInclude(t => t!.UserAccount)
                .Include(r => r.Payment)
                .Where(r => !r.IsDeleted && r.ProgramId == cls.ProgramId && (r.ClassId == null || r.ClassId != cls.ClassId) && r.Status != "Cancelled")
                .OrderByDescending(r => r.RegistrationDate)
                .ToListAsync();

            ViewBag.OtherRegistrations = otherRegistrations;
            ViewBag.Teachers = await _context.Teachers
                .Include(t => t.UserAccount)
                .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted)
                .OrderBy(t => t.UserAccount.FullName)
                .ToListAsync();

            return View(cls);
        }

        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> SaveSchedule(int classId, ClassScheduleInput input)
        {
            await using var transaction = await _context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
            var cls = await _context.Classes.Include(c => c.Schedules).FirstOrDefaultAsync(c => c.ClassId == classId && !c.IsDeleted);
            if (cls == null) return NotFound();
            var error = ModelState.IsValid ? await ClassSchedulePlanner.ValidateAsync(_context, cls, input) : "Chọn nhóm thứ và nhập giờ học hợp lệ.";
            if (error != null)
            {
                TempData["ErrorMessage"] = error;
                return RedirectToAction(nameof(Details), new { id = classId });
            }
            _context.ClassSchedules.RemoveRange(cls.Schedules);
            await _context.SaveChangesAsync();
            cls.Schedules = ClassSchedulePlanner.Create(input);
            await _context.SaveChangesAsync();
            await transaction.CommitAsync();
            TempData["SuccessMessage"] = "Đã lưu lịch học trong tuần. Thời khóa biểu của học viên và giáo viên được cập nhật theo lịch lớp.";
            return RedirectToAction(nameof(Details), new { id = classId });
        }

        // POST: Admin/ClassManager/AddStudentToClass
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> AddStudentToClass(int registrationId, int classId)
        {
            var error = await WedEnglishApp.Services.CourseClassAssignment.AssignAsync(_context, registrationId, classId);
            TempData[error == null ? "SuccessMessage" : "ErrorMessage"] = error ?? "Đã xếp học viên vào lớp phù hợp.";
            return RedirectToAction(nameof(Details), new { id = classId });
        }

        // POST: Admin/ClassManager/RemoveStudentFromClass
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> RemoveStudentFromClass(int registrationId, int classId)
        {
            var reg = await _context.Registrations
                .Include(r => r.Student).ThenInclude(s => s.UserAccount)
                .FirstOrDefaultAsync(r => r.RegistrationId == registrationId);

            if (reg == null || reg.ClassId != classId) return NotFound();

            reg.ClassId = null;
            reg.Status = "Pending";
            await _context.SaveChangesAsync();

            TempData["SuccessMessage"] = $"Đã chuyển trạng thái học viên '{reg.Student.UserAccount.FullName}' về 'Chờ xếp lớp' (Pending).";
            return RedirectToAction(nameof(Details), new { id = classId });
        }

        // GET: Admin/ClassManager/Create
        public async Task<IActionResult> Create()
        {
            await PopulateClassFormOptionsAsync();
            ViewBag.ScheduleForm = new ClassScheduleInput();
            return View(new CourseClass
            {
                StartDate = DateTime.Today.AddDays(7),
                EndDate = DateTime.Today.AddDays(90),
                Status = "Planning"
            });
        }

        // POST: Admin/ClassManager/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(CourseClass cls, ClassScheduleInput input)
        {
            // Khi tạo mới lớp học, lớp chưa có giáo viên cụ thể nào chịu trách nhiệm
            cls.TeacherId = null;

            if (cls.EndDate < cls.StartDate)
            {
                ModelState.AddModelError(nameof(cls.EndDate), "Ngày bế giảng phải sau hoặc bằng ngày khai giảng.");
            }

            var programExists = await _context.Programs.AnyAsync(p =>
                p.ProgramId == cls.ProgramId && p.IsActive && !p.IsDeleted);
            if (!programExists)
            {
                ModelState.AddModelError(nameof(cls.ProgramId), "Chương trình học đã chọn không tồn tại hoặc đã ngừng hoạt động.");
            }

            ViewBag.ScheduleForm = input;
            var scheduleError = await ClassSchedulePlanner.ValidateAsync(_context, cls, input);
            if (scheduleError != null) ModelState.AddModelError("", scheduleError);
            else cls.Schedules = ClassSchedulePlanner.Create(input);
            if (ModelState.IsValid)
            {
                _context.Classes.Add(cls);
                await _context.SaveChangesAsync();
                TempData["SuccessMessage"] = "Đã tạo lớp. Bạn có thể thiết lập lịch học và xếp học viên tại đây.";
                return RedirectToAction(nameof(Details), new { id = cls.ClassId });
            }

            await PopulateClassFormOptionsAsync(cls.ProgramId, cls.TeacherId);
            return View(cls);
        }

        private async Task PopulateClassFormOptionsAsync(int? selectedProgramId = null, int? selectedTeacherId = null)
        {
            var programs = await _context.Programs
                .Where(p => p.IsActive && !p.IsDeleted)
                .OrderBy(p => p.ProgramName)
                .ToListAsync();
            var teachers = await _context.Teachers
                .Include(t => t.UserAccount)
                .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted)
                .OrderBy(t => t.UserAccount.FullName)
                .ToListAsync();

            ViewBag.Programs = new SelectList(programs, "ProgramId", "ProgramName", selectedProgramId);
            ViewBag.Teachers = new SelectList(teachers, "TeacherId", "UserAccount.FullName", selectedTeacherId);
        }

        // GET: Admin/ClassManager/Edit/5
        public async Task<IActionResult> Edit(int id)
        {
            var cls = await _context.Classes.Include(c => c.Schedules).FirstOrDefaultAsync(c => c.ClassId == id);
            if (cls == null) return NotFound();
            var days = string.Join(",", cls.Schedules.OrderBy(s => s.DayOfWeek).Select(s => s.DayOfWeek));
            ViewBag.ScheduleForm = new ClassScheduleInput
            {
                SchedulePattern = days == "2,4,6" ? "246" : days == "3,5,7" ? "357" : cls.Schedules.Any() ? "Keep" : "",
                AllowKeepExisting = cls.Schedules.Any() && days != "2,4,6" && days != "3,5,7",
                StartTime = cls.Schedules.FirstOrDefault()?.StartTime,
                EndTime = cls.Schedules.FirstOrDefault()?.EndTime
            };
            ViewBag.Programs = new SelectList(await _context.Programs.Where(p => p.IsActive).ToListAsync(), "ProgramId", "ProgramName", cls.ProgramId);
            ViewBag.Teachers = new SelectList(await _context.Teachers.Include(t => t.UserAccount).ToListAsync(), "TeacherId", "UserAccount.FullName", cls.TeacherId);
            return View(cls);
        }

        // POST: Admin/ClassManager/Edit/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Edit(int id, CourseClass cls, ClassScheduleInput input)
        {
            if (id != cls.ClassId) return NotFound();

            await using var transaction = await _context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
            var existing = await _context.Classes.Include(c => c.Registrations).Include(c => c.Schedules).FirstOrDefaultAsync(c => c.ClassId == id && !c.IsDeleted);
            if (existing == null) return NotFound();
            if (cls.EndDate < cls.StartDate) ModelState.AddModelError("", "Ngày kết thúc phải sau ngày khai giảng.");
            if (existing.ProgramId != cls.ProgramId) ModelState.AddModelError("", "Khóa học của lớp được cố định để bảo toàn ghi danh. Hãy tạo lớp mới nếu cần đổi khóa.");
            if (existing.Registrations.Any(r => !r.IsDeleted && r.Status == "Confirmed" && r.EarliestStartDate.HasValue && r.EarliestStartDate.Value.Date > cls.StartDate.Date)) ModelState.AddModelError("", "Ngày khai giảng sớm hơn ngày học viên trong lớp có thể bắt đầu.");
            if (cls.MaxStudents < existing.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed")) ModelState.AddModelError("", "Sĩ số tối đa thấp hơn số học viên đang được xếp.");
            input.AllowKeepExisting = existing.Schedules.Any();
            ViewBag.ScheduleForm = input;
            if (input.SchedulePattern != "Keep" || !existing.Schedules.Any())
            {
                var scheduleError = await ClassSchedulePlanner.ValidateAsync(_context, cls, input);
                if (scheduleError != null) ModelState.AddModelError("", scheduleError);
            }
            if (ModelState.IsValid)
            {
                existing.ClassName = cls.ClassName; existing.ProgramId = cls.ProgramId;
                existing.TeacherId = cls.TeacherId; existing.Room = cls.Room;
                existing.StartDate = cls.StartDate; existing.EndDate = cls.EndDate;
                existing.MaxStudents = cls.MaxStudents; existing.Status = cls.Status;
                if (input.SchedulePattern != "Keep")
                {
                    _context.ClassSchedules.RemoveRange(existing.Schedules);
                    await _context.SaveChangesAsync();
                    existing.Schedules = ClassSchedulePlanner.Create(input);
                }
                await _context.SaveChangesAsync();
                await transaction.CommitAsync();
                TempData["SuccessMessage"] = "Cập nhật lớp học thành công!";
                return RedirectToAction(nameof(Index));
            }

            ViewBag.Programs = new SelectList(await _context.Programs.Where(p => p.IsActive && !p.IsDeleted).ToListAsync(), "ProgramId", "ProgramName", cls.ProgramId);
            ViewBag.Teachers = new SelectList(await _context.Teachers.Include(t => t.UserAccount).Where(t => !t.UserAccount.IsDeleted).ToListAsync(), "TeacherId", "UserAccount.FullName", cls.TeacherId);
            return View(cls);
        }

        // POST: Admin/ClassManager/Delete/5
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var cls = await _context.Classes.Include(c => c.Registrations).FirstOrDefaultAsync(c => c.ClassId == id);
            if (cls == null) return NotFound();

            cls.IsDeleted = true;
            cls.DeletedAt = DateTime.Now;
            await _context.SaveChangesAsync();
            TempData["SuccessMessage"] = $"Đã chuyển lớp học '{cls.ClassName}' vào thùng rác! Bạn có thể xem hoặc khôi phục trong mục Thùng rác.";
            return RedirectToAction(nameof(Index));
        }
    }
}
