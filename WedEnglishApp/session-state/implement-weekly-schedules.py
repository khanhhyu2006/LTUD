from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
s=r('Data/ApplicationDbContext.cs');s=s.replace('.HasForeignKey(r => r.ClassId)','.HasForeignKey(r => new { r.ClassId, r.ProgramId })\n                .HasPrincipalKey(c => new { c.ClassId, c.ProgramId })');at=s.index('            // Cấu hình 7:');s=s[:at]+'''            modelBuilder.Entity<CourseClass>().HasAlternateKey(c => new { c.ClassId, c.ProgramId });
            modelBuilder.Entity<Registration>().HasIndex(r => new { r.StudentId, r.ProgramId });
            modelBuilder.Entity<Registration>().ToTable("Registrations", t =>
            {
                t.HasTrigger("TR_Registrations_CourseFlow");
                t.UseSqlOutputClause(false);
            });
            modelBuilder.Entity<Payment>().ToTable("Payments", t =>
            {
                t.HasTrigger("TR_Payments_CourseFlow");
                t.UseSqlOutputClause(false);
            });
            modelBuilder.Entity<ClassSchedule>()
                .HasIndex(s => new { s.ClassId, s.DayOfWeek, s.StartTime, s.EndTime })
                .IsUnique().HasDatabaseName("UX_ClassSchedules_Class_Day_Time");

'''+s[at:];w('Data/ApplicationDbContext.cs',s)
w('ViewModels/Admin/ClassScheduleInput.cs','''using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.ViewModels.Admin;

public class ClassScheduleInput
{
    [Required] public string SchedulePattern { get; set; } = string.Empty;
    [Required] public TimeSpan? StartTime { get; set; }
    [Required] public TimeSpan? EndTime { get; set; }
}
''')
w('Services/ClassSchedulePlanner.cs','''using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.ViewModels.Admin;
namespace WedEnglishApp.Services;

public static class ClassSchedulePlanner
{
    public static async Task<string?> ValidateAsync(ApplicationDbContext context, CourseClass cls, ClassScheduleInput input)
    {
        var daysText = EnrollmentSchedule.GetDays(input.SchedulePattern);
        if (daysText == null) return "Chọn lịch Thứ 2–4–6 hoặc Thứ 3–5–7.";
        if (!input.StartTime.HasValue || !input.EndTime.HasValue || input.StartTime < TimeSpan.Zero || input.EndTime >= TimeSpan.FromDays(1) || input.StartTime >= input.EndTime)
            return "Giờ kết thúc phải sau giờ bắt đầu và nằm trong cùng ngày.";
        var days = daysText.Split(',').Select(int.Parse).ToArray();
        var others = await context.Classes.Include(c => c.Schedules)
            .Where(c => c.ClassId != cls.ClassId && !c.IsDeleted && c.Status != "Cancelled" && c.Status != "Completed"
                && c.StartDate <= cls.EndDate && c.EndDate >= cls.StartDate).ToListAsync();
        var occupied = others.Where(c => c.Schedules.Any(s => days.Contains(s.DayOfWeek) && s.StartTime < input.EndTime.Value && input.StartTime.Value < s.EndTime)).ToList();
        if (occupied.Any(c => !string.IsNullOrWhiteSpace(cls.Room) && string.Equals(c.Room.Trim(), cls.Room.Trim(), StringComparison.OrdinalIgnoreCase)))
            return "Phòng học đã có lớp khác trong thời gian này.";
        if (cls.TeacherId.HasValue && occupied.Any(c => c.TeacherId == cls.TeacherId))
            return "Giáo viên đã có lịch dạy trùng với lịch mới.";
        var students = await context.Registrations.Where(r => r.ClassId == cls.ClassId && !r.IsDeleted && r.Status == "Confirmed").Select(r => r.StudentId).ToListAsync();
        var occupiedIds = occupied.Select(c => c.ClassId).ToArray();
        if (students.Any() && await context.Registrations.AnyAsync(r => r.ClassId.HasValue && occupiedIds.Contains(r.ClassId.Value) && students.Contains(r.StudentId) && !r.IsDeleted && r.Status == "Confirmed"))
            return "Lịch mới trùng với lớp khác của học viên đang học trong lớp này.";
        return null;
    }

    public static List<ClassSchedule> Create(ClassScheduleInput input) => EnrollmentSchedule.GetDays(input.SchedulePattern)!
        .Split(',').Select(day => new ClassSchedule { DayOfWeek = int.Parse(day), StartTime = input.StartTime!.Value, EndTime = input.EndTime!.Value }).ToList();
}
''')
s=r('Areas/Admin/Controllers/ClassManagerController.cs');s='using WedEnglishApp.Services;\nusing WedEnglishApp.ViewModels.Admin;\nusing System.Data;\n'+s;s=s.replace('.Include(c => c.Program)\n                .Include(c => c.Teacher).ThenInclude(t => t!.UserAccount)\n                .Include(c => c.Registrations)', '.Include(c => c.Program)\n                .Include(c => c.Schedules)\n                .Include(c => c.Teacher).ThenInclude(t => t!.UserAccount)\n                .Include(c => c.Registrations)')
# Dedicated schedule form on the assignment screen.
a=s.index('        // POST: Admin/ClassManager/AddStudentToClass')
s=s[:a]+'''        [HttpPost]
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

'''+s[a:]
s=s.replace('public async Task<IActionResult> Create(CourseClass cls)', 'public async Task<IActionResult> Create(CourseClass cls, ClassScheduleInput input)')
s=s.replace('            if (ModelState.IsValid)\n            {\n                _context.Classes.Add(cls);', '''            if (string.IsNullOrEmpty(input.SchedulePattern))
            {
                ModelState.Remove(nameof(input.SchedulePattern));
                ModelState.Remove(nameof(input.StartTime));
                ModelState.Remove(nameof(input.EndTime));
            }
            else
            {
                var scheduleError = await ClassSchedulePlanner.ValidateAsync(_context, cls, input);
                if (scheduleError != null) ModelState.AddModelError("", scheduleError);
                else cls.Schedules = ClassSchedulePlanner.Create(input);
            }
            if (ModelState.IsValid)
            {
                _context.Classes.Add(cls);''')
s=s.replace('TempData["SuccessMessage"] = "Thêm mới lớp học thành công!";\n                return RedirectToAction(nameof(Index));','TempData["SuccessMessage"] = "Đã tạo lớp. Bạn có thể thiết lập lịch học và xếp học viên tại đây.";\n                return RedirectToAction(nameof(Details), new { id = cls.ClassId });')
# Preserve entity state on edits, and refuse mismatched program/invalid dates/capacity.
s=s.replace('''            if (ModelState.IsValid)
            {
                _context.Update(cls);''','''            var existing = await _context.Classes.Include(c => c.Registrations).FirstOrDefaultAsync(c => c.ClassId == id && !c.IsDeleted);
            if (existing == null) return NotFound();
            if (cls.EndDate < cls.StartDate) ModelState.AddModelError("", "Ngày kết thúc phải sau ngày khai giảng.");
            if (existing.Registrations.Any() && existing.ProgramId != cls.ProgramId) ModelState.AddModelError("", "Lớp đã có ghi danh; không đổi sang khóa học khác.");
            if (cls.MaxStudents < existing.Registrations.Count(r => !r.IsDeleted && r.Status == "Confirmed")) ModelState.AddModelError("", "Sĩ số tối đa thấp hơn số học viên đang được xếp.");
            if (ModelState.IsValid)
            {
                existing.ClassName = cls.ClassName; existing.ProgramId = cls.ProgramId;
                existing.TeacherId = cls.TeacherId; existing.Room = cls.Room;
                existing.StartDate = cls.StartDate; existing.EndDate = cls.EndDate;
                existing.MaxStudents = cls.MaxStudents; existing.Status = cls.Status;''')
w('Areas/Admin/Controllers/ClassManagerController.cs',s)
form='''<div class="admin-card p-4 mb-4" id="weekly-schedule">
    <h5 class="fw-bold">Lịch học trong tuần của lớp</h5>
    <p class="small text-muted">Lịch này dùng chung cho cả lớp và hiển thị trên thời khóa biểu sau khi học viên được xếp vào lớp.</p>
    @if (Model.Schedules.Any()) {
        <p class="small">Lịch hiện tại: <strong>@string.Join(", ", Model.Schedules.OrderBy(s => s.DayOfWeek).Select(s => $"T{s.DayOfWeek}: {s.StartTime.ToString(@"hh\\:mm")}–{s.EndTime.ToString(@"hh\\:mm")}"))</strong></p>
    }
    <form asp-action="SaveSchedule" method="post" class="row g-3 align-items-end">
        @Html.AntiForgeryToken()
        <input type="hidden" name="classId" value="@Model.ClassId" />
        <div class="col-md-4"><label class="form-label" for="weekly-pattern">Các thứ học</label><select name="SchedulePattern" id="weekly-pattern" class="form-select" required><option value="">Chọn lịch trong tuần</option><option value="246">Thứ 2 – Thứ 4 – Thứ 6</option><option value="357">Thứ 3 – Thứ 5 – Thứ 7</option></select></div>
        <div class="col-md-3"><label class="form-label" for="weekly-start">Giờ bắt đầu</label><input type="time" name="StartTime" id="weekly-start" class="form-control" required /></div>
        <div class="col-md-3"><label class="form-label" for="weekly-end">Giờ kết thúc</label><input type="time" name="EndTime" id="weekly-end" class="form-control" required /></div>
        <div class="col-md-2"><button class="btn btn-primary w-100" type="submit">Lưu lịch học</button></div>
    </form>
</div>
'''
s=r('Areas/Admin/Views/ClassManager/Details.cshtml');idx=s.index('<!-- Card tổng quan');s=s[:idx]+form+'\n'+s[idx:];w('Areas/Admin/Views/ClassManager/Details.cshtml',s)
# Optional schedule during initial class creation; same canonical field names.
s=r('Areas/Admin/Views/ClassManager/Create.cshtml');idx=s.index('                <div class="mb-4">\n                    <label asp-for="Status"');s=s[:idx]+'''                <fieldset class="mb-4"><legend class="fs-6 fw-bold">Lịch học trong tuần</legend><div class="row g-3">
                    <div class="col-md-6"><label for="create-pattern" class="form-label">Nhóm thứ học</label><select id="create-pattern" name="SchedulePattern" class="form-select"><option value="">Thiết lập sau khi tạo lớp</option><option value="246">Thứ 2 – Thứ 4 – Thứ 6</option><option value="357">Thứ 3 – Thứ 5 – Thứ 7</option></select></div>
                    <div class="col-md-3"><label for="create-start" class="form-label">Giờ bắt đầu</label><input id="create-start" name="StartTime" type="time" class="form-control" /></div>
                    <div class="col-md-3"><label for="create-end" class="form-label">Giờ kết thúc</label><input id="create-end" name="EndTime" type="time" class="form-control" /></div>
                </div></fieldset>
'''+s[idx:];w('Areas/Admin/Views/ClassManager/Create.cshtml',s)
# Prevent reactivating cancelled duplicates through the admin status shortcut.
s=r('Areas/Admin/Controllers/RegistrationAdminController.cs');a=s.index('            reg.ClassId = null;');s=s[:a]+'''            if (status == "Pending" && (reg.Status == "Cancelled" || reg.IsDeleted) && await _context.Registrations.AnyAsync(r => r.RegistrationId != id && r.StudentId == reg.StudentId && r.ProgramId == reg.ProgramId && !r.IsDeleted && r.Status != "Cancelled"))
            {
                TempData["ErrorMessage"] = "Học viên đã có một đơn đang hoạt động cho khóa học này.";
                return RedirectToAction(nameof(Index));
            }
'''+s[a:];w('Areas/Admin/Controllers/RegistrationAdminController.cs',s)
print('EF mapping, weekly schedule planner and assignment forms updated')
