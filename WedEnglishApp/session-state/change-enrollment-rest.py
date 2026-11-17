from pathlib import Path
exec(Path('session-state/change-enrollment.py').read_text(encoding='utf-8-sig').split("replace('Models/Registration.cs'")[0])
# Preserve read-only class information, all enrollment links use ProgramId.
replace('Controllers/HomeController.cs','                FeaturedTeachers =', '''                UpcomingClasses = await _context.Classes.Include(c => c.Program).Include(c => c.Schedules)
                    .Where(c => !c.IsDeleted && c.Program.IsActive && !c.Program.IsDeleted && (c.Status == "Planning" || c.Status == "InProgress"))
                    .OrderBy(c => c.StartDate).Take(4).ToListAsync(),

                FeaturedTeachers =''')
replace('Controllers/ProgramController.cs','var program = await _context.Programs\n                .FirstOrDefaultAsync', '''var program = await _context.Programs
                .Include(p => p.Classes.Where(c => !c.IsDeleted && (c.Status == "Planning" || c.Status == "InProgress")))
                    .ThenInclude(c => c.Schedules)
                .FirstOrDefaultAsync''')
write('Views/Shared/_AvailableClasses.cshtml','''@model IEnumerable<WedEnglishApp.Models.CourseClass>
<div class="row g-3">
@foreach (var cls in Model) {
<div class="col-lg-6"><div class="card p-3 h-100"><h5>@cls.ClassName</h5>
<p class="mb-1">Khai giảng: @cls.StartDate.ToString("dd/MM/yyyy") · Phòng: @cls.Room</p>
<p class="small text-muted">@string.Join(", ", cls.Schedules.OrderBy(s => s.DayOfWeek).Select(s => $"{(s.DayOfWeek == 8 ? "CN" : $"Thứ {s.DayOfWeek}")} {s.StartTime:hh\\:mm}–{s.EndTime:hh\\:mm}"))</p>
<a asp-controller="Enrollment" asp-action="Checkout" asp-route-programId="@cls.ProgramId" asp-route-authRole="Student" class="btn btn-outline-primary mt-auto">Đăng ký khóa học và gửi nguyện vọng</a>
</div></div>
}
</div>
''')
replace('Views/Program/Detail.cshtml','            <div class="card card-custom p-4 border-0 bg-white">\n                <h4 class="fw-bold text-primary">Đăng ký', '''            <div class="mb-4"><h4>Các lớp hiện có để tham khảo</h4>
                <p class="text-muted">Không cần chọn lớp khi đăng ký. Admin sẽ xếp lớp theo nguyện vọng của bạn.</p>
                @if (Model.Classes.Any()) { @await Html.PartialAsync("_AvailableClasses", Model.Classes) }
                else { <p>Trung tâm đang tiếp nhận đăng ký khóa học và sắp xếp lớp mới.</p> }
            </div>
            <div class="card card-custom p-4 border-0 bg-white">
                <h4 class="fw-bold text-primary">Đăng ký''')
replace('Views/Home/Index.cshtml','<!-- 6. TEACHERS', '''<!-- 6. TEACHERS''') # insert before teachers section
s=read('Views/Home/Index.cshtml');at=s.index('<!-- 6. TEACHERS');at=s.rfind('<!-- ===',0,at);s=s[:at]+'''<section class="py-5 bg-light"><div class="container"><h3>Các lớp hiện có</h3>
<p>Tham khảo lịch học của trung tâm. Khi đăng ký khóa học, bạn chỉ cần gửi lịch mong muốn; Admin sẽ xếp lớp sau.</p>
@await Html.PartialAsync("_AvailableClasses", Model.UpcomingClasses)
</div></section>

'''+s[at:];write('Views/Home/Index.cshtml',s)
replace('Data/DbInitializer.cs','context.Registrations.Add(reg);','reg.ProgramId = cls.ProgramId;\n                    context.Registrations.Add(reg);')
write('Services/CourseClassAssignment.cs','''using System.Data;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public static class CourseClassAssignment
{
    public static string? CheckPreferences(Registration registration, CourseClass cls)
    {
        if (registration.ProgramId != cls.ProgramId) return "Lớp phải thuộc đúng khóa học đã đăng ký.";
        if (cls.IsDeleted || (cls.Status != "Planning" && cls.Status != "InProgress")) return "Lớp đã đóng hoặc ngừng hoạt động.";
        if (registration.EarliestStartDate.HasValue && cls.StartDate.Date < registration.EarliestStartDate.Value.Date)
            return "Lớp khai giảng trước ngày học viên có thể bắt đầu.";
        if (!string.IsNullOrWhiteSpace(registration.PreferredDays) || !string.IsNullOrWhiteSpace(registration.PreferredSession))
        {
            if (!cls.Schedules.Any()) return "Lớp chưa có lịch học để đối chiếu nguyện vọng.";
            var days = (registration.PreferredDays ?? "").Split(',', StringSplitOptions.RemoveEmptyEntries).Select(int.Parse).ToHashSet();
            if (days.Count > 0 && cls.Schedules.Any(s => !days.Contains(s.DayOfWeek))) return "Thứ học của lớp không nằm trong lịch học viên đã chọn.";
            var (start, end) = registration.PreferredSession switch
            {
                "Morning" => (6, 12), "Afternoon" => (12, 18), "Evening" => (18, 22), _ => (0, 24)
            };
            if (cls.Schedules.Any(s => s.StartTime < TimeSpan.FromHours(start) || s.EndTime > TimeSpan.FromHours(end)))
                return "Giờ học của lớp không phù hợp buổi học mong muốn.";
        }
        return null;
    }

    public static async Task<string?> AssignAsync(ApplicationDbContext context, int registrationId, int classId)
    {
        await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
        var registration = await context.Registrations.FirstOrDefaultAsync(r => r.RegistrationId == registrationId && !r.IsDeleted);
        var cls = await context.Classes.Include(c => c.Schedules).Include(c => c.Program).FirstOrDefaultAsync(c => c.ClassId == classId);
        if (registration == null || cls == null) return "Không tìm thấy đơn đăng ký hoặc lớp học.";
        if (registration.Status == "Cancelled") return "Không thể xếp lớp cho đơn đã hủy.";
        if (cls.Program.IsDeleted || !cls.Program.IsActive) return "Khóa học đã ngừng hoạt động.";
        var mismatch = CheckPreferences(registration, cls);
        if (mismatch != null) return mismatch;
        var count = await context.Registrations.CountAsync(r => r.ClassId == classId && r.RegistrationId != registrationId && !r.IsDeleted && r.Status == "Confirmed");
        if (count >= cls.MaxStudents) return "Lớp đã đủ sĩ số.";
        var others = await context.Registrations.Include(r => r.Class).ThenInclude(c => c.Schedules)
            .Where(r => r.StudentId == registration.StudentId && r.RegistrationId != registrationId && r.ClassId != null && !r.IsDeleted && r.Status == "Confirmed").ToListAsync();
        if (others.Any(r => r.Class.StartDate <= cls.EndDate && cls.StartDate <= r.Class.EndDate &&
            r.Class.Schedules.Any(a => cls.Schedules.Any(b => a.DayOfWeek == b.DayOfWeek && a.StartTime < b.EndTime && b.StartTime < a.EndTime))))
            return "Lịch lớp trùng với lớp học viên đã được xếp.";
        registration.ClassId = classId;
        registration.Status = "Confirmed";
        await context.SaveChangesAsync();
        await transaction.CommitAsync();
        return null;
    }
}
''')
s=read('Areas/Admin/Controllers/RegistrationAdminController.cs');s=s.replace('.Where(r => !r.IsDeleted)','.Where(r => !r.IsDeleted)\n                .Include(r => r.Program)');s=s.replace('r.Class.ProgramId == programId.Value','r.ProgramId == programId.Value');s=s.replace('.Include(c => c.Program)','.Include(c => c.Program)\n                .Include(c => c.Schedules)\n                .Include(c => c.Registrations)');a=s.index('            var reg =',s.index('Task<IActionResult> AssignClass'));b=s.index('            return RedirectToAction(nameof(Index));',a);s=s[:a]+'''            var error = await WedEnglishApp.Services.CourseClassAssignment.AssignAsync(_context, registrationId, newClassId);
            TempData[error == null ? "SuccessMessage" : "ErrorMessage"] = error ?? "Đã xếp học viên vào lớp phù hợp.";
'''+s[b:];s=s.replace('            reg.Status = status;','''            if (status != "Pending" && status != "Cancelled")
            {
                TempData["ErrorMessage"] = "Dùng chức năng Xếp lớp để xác nhận đơn đăng ký.";
                return RedirectToAction(nameof(Index));
            }
            reg.ClassId = null;
            reg.Status = status;''');write('Areas/Admin/Controllers/RegistrationAdminController.cs',s)
s=read('Areas/Admin/Controllers/ClassManagerController.cs');s=s.replace('r.Class.ProgramId == cls.ProgramId','r.ProgramId == cls.ProgramId');s=s.replace('r.ClassId != cls.ClassId','(r.ClassId == null || r.ClassId != cls.ClassId)');a=s.index('            var reg =',s.index('Task<IActionResult> AddStudentToClass'));b=s.index('            return RedirectToAction(nameof(Details), new { id = classId });',a);# first redirect is nested capacity condition; replace to next action boundary instead
b=s.index('        // POST: Admin/ClassManager/RemoveStudentFromClass',a)
s=s[:a]+'''            var error = await WedEnglishApp.Services.CourseClassAssignment.AssignAsync(_context, registrationId, classId);
            TempData[error == null ? "SuccessMessage" : "ErrorMessage"] = error ?? "Đã xếp học viên vào lớp phù hợp.";
            return RedirectToAction(nameof(Details), new { id = classId });
        }

'''+s[b:];s=s.replace('if (reg == null) return NotFound();\n\n            reg.Status = "Pending";','if (reg == null || reg.ClassId != classId) return NotFound();\n\n            reg.ClassId = null;\n            reg.Status = "Pending";');write('Areas/Admin/Controllers/ClassManagerController.cs',s)
s=read('Areas/Admin/Controllers/PaymentAdminController.cs');s=s.replace('payment.Registration.Status = "Confirmed";','// Payment confirmation never assigns a class.');s=s.replace('if (payment == null) return NotFound();','if (payment == null || payment.Registration.IsDeleted || payment.Registration.Status == "Cancelled") return NotFound();');write('Areas/Admin/Controllers/PaymentAdminController.cs',s)
# Load the independent program wherever registrations or their receipts are displayed.
for file in ['Controllers/StudentController.cs','Areas/Admin/Controllers/PaymentAdminController.cs','Areas/Admin/Controllers/TrashController.cs']:
 s=read(file).replace('.Include(p => p.Registration)', '.Include(p => p.Registration).ThenInclude(r => r.Program)').replace('.Include(r => r.Class)', '.Include(r => r.Program)\n                .Include(r => r.Class)')
 if file=='Controllers/StudentController.cs':
  s=s.replace('.Where(r => r.StudentId == studentId)', '.Where(r => r.StudentId == studentId && !r.IsDeleted)')
  s=s.replace('.Where(r => r.StudentId == studentId && r.Status != "Cancelled")', '.Where(r => r.StudentId == studentId && !r.IsDeleted && r.ClassId != null && r.Status == "Confirmed")')
 write(file,s)
# All remaining record views must support unassigned registrations.
for file in ['Views/Student/PrintReceipt.cshtml','Views/Student/MyPayments.cshtml','Areas/Admin/Views/PaymentAdmin/Index.cshtml','Areas/Admin/Views/Dashboard/Index.cshtml','Areas/Admin/Views/ClassManager/Details.cshtml','Areas/Admin/Views/Trash/Index.cshtml']:
 s=read(file)
 s=s.replace('Model.Registration.Class.Program.', 'Model.Registration.Program.').replace('p.Registration.Class.Program.', 'p.Registration.Program.')
 s=s.replace('@Model.Registration.Class.ClassName','@(Model.Registration.Class?.ClassName ?? "Chờ xếp lớp")').replace('@p.Registration.Class.ClassName','@(p.Registration.Class?.ClassName ?? "Chờ xếp lớp")')
 s=s.replace('@r.Class.ClassName','@(r.Class?.ClassName ?? "Chờ xếp lớp")').replace('@reg.Class.ClassName','@(reg.Class?.ClassName ?? "Chờ xếp lớp")')
 s=s.replace('@r.Class?.Program?.ProgramName','@r.Program?.ProgramName')
 write(file,s)
write('Views/Shared/_EnrollmentPreferences.cshtml','''@model WedEnglishApp.Models.Registration
<div class="small">
<div>Có thể bắt đầu: <strong>@(Model.EarliestStartDate?.ToString("dd/MM/yyyy") ?? "Chưa cung cấp")</strong></div>
<div>Buổi: <strong>@(Model.PreferredSession switch { "Morning" => "Sáng (06:00–12:00)", "Afternoon" => "Chiều (12:00–18:00)", "Evening" => "Tối (18:00–22:00)", "Any" => "Linh hoạt", _ => "Chưa cung cấp" })</strong></div>
<div>Thứ có thể học: <strong>@(string.IsNullOrWhiteSpace(Model.PreferredDays) ? "Chưa cung cấp" : string.Join(", ", Model.PreferredDays.Split(',').Select(d => d == "8" ? "Chủ nhật" : $"Thứ {d}")))</strong></div>
@if (Model.DesiredTeacher != null) { <div>Giáo viên mong muốn: @Model.DesiredTeacher.UserAccount.FullName</div> }
@if (!string.IsNullOrWhiteSpace(Model.Notes)) { <div>Ghi chú: @Model.Notes</div> }
</div>
''')
print('Assignment rules, class visibility and dependent queries updated')
