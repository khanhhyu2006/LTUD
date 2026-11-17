from pathlib import Path
root=Path('WedEnglishApp')
def read(p):return (root/p).read_text(encoding='utf-8-sig')
def write(p,s):
 f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s,encoding='utf8')
def replace(p,a,b):
 s=read(p);assert a in s,(p,a[:80]);write(p,s.replace(a,b))
replace('Models/Registration.cs','[Required]\n        public int ClassId { get; set; }','public int? ClassId { get; set; }')
replace('Models/Registration.cs','public DateTime RegistrationDate', '''[Required]
        public int ProgramId { get; set; }

        [ForeignKey(nameof(ProgramId))]
        public virtual CourseProgram Program { get; set; } = null!;

        public DateTime? EarliestStartDate { get; set; }

        [StringLength(30)]
        public string? PreferredSession { get; set; }

        [StringLength(30)]
        public string? PreferredDays { get; set; }

        public DateTime RegistrationDate''')
replace('Data/ApplicationDbContext.cs','// Cấu hình 7: Quan hệ 1 - 1 giữa Registration và Payment', '''modelBuilder.Entity<Registration>()
                .HasOne(r => r.Program).WithMany()
                .HasForeignKey(r => r.ProgramId).OnDelete(DeleteBehavior.Restrict);

            // Cấu hình 7: Quan hệ 1 - 1 giữa Registration và Payment''')
# Old seed registrations also require an independent course key.
s=read('Data/DbInitializer.cs');s=s.replace('context.Database.EnsureCreated();','context.Database.EnsureCreated();\n            CourseEnrollmentSchema.Upgrade(context);')
s=s.replace('context.Registrations.AddRange(registrations);','foreach (var registration in registrations)\n                registration.ProgramId = classes.First(c => c.ClassId == registration.ClassId).ProgramId;\n            context.Registrations.AddRange(registrations);')
write('Data/DbInitializer.cs',s)
write('Data/CourseEnrollmentSchema.cs','''using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;

public static class CourseEnrollmentSchema
{
    // Additive upgrade for databases created through the existing EnsureCreated initializer.
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(CourseEnrollmentSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.CourseEnrollment.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
''')
write('Data/Sql/CourseEnrollment.sql','''SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH('dbo.Registrations','ProgramId') IS NULL
    ALTER TABLE dbo.Registrations ADD ProgramId int NULL;
EXEC(N'UPDATE r SET ProgramId=c.ProgramId FROM dbo.Registrations r JOIN dbo.Classes c ON r.ClassId=c.ClassId WHERE r.ProgramId IS NULL');
EXEC(N'ALTER TABLE dbo.Registrations ALTER COLUMN ProgramId int NOT NULL');
ALTER TABLE dbo.Registrations ALTER COLUMN ClassId int NULL;
IF COL_LENGTH('dbo.Registrations','EarliestStartDate') IS NULL
    ALTER TABLE dbo.Registrations ADD EarliestStartDate datetime2 NULL;
IF COL_LENGTH('dbo.Registrations','PreferredSession') IS NULL
    ALTER TABLE dbo.Registrations ADD PreferredSession nvarchar(30) NULL;
IF COL_LENGTH('dbo.Registrations','PreferredDays') IS NULL
    ALTER TABLE dbo.Registrations ADD PreferredDays nvarchar(30) NULL;
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_Registrations_Programs_ProgramId')
    EXEC(N'ALTER TABLE dbo.Registrations ADD CONSTRAINT FK_Registrations_Programs_ProgramId FOREIGN KEY(ProgramId) REFERENCES dbo.Programs(ProgramId)');
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.Registrations') AND name='IX_Registrations_ProgramId')
    EXEC(N'CREATE INDEX IX_Registrations_ProgramId ON dbo.Registrations(ProgramId)');
COMMIT;
''')
replace('WedEnglishApp.csproj','<Folder Include="Data\\" />','<Folder Include="Data\\" />\n    <EmbeddedResource Include="Data/Sql/CourseEnrollment.sql" />')
write('ViewModels/Enrollment/CourseEnrollmentViewModel.cs','''using System.ComponentModel.DataAnnotations;
using WedEnglishApp.Models;
namespace WedEnglishApp.ViewModels.Enrollment;

public class CourseEnrollmentViewModel
{
    public int ProgramId { get; set; }
    [Required(ErrorMessage = "Chọn ngày sớm nhất bạn có thể bắt đầu học.")]
    [DataType(DataType.Date)]
    public DateTime? EarliestStartDate { get; set; }
    [Required(ErrorMessage = "Chọn buổi học mong muốn.")]
    public string PreferredSession { get; set; } = "Evening";
    public int[] PreferredDays { get; set; } = [];
    public int? DesiredTeacherId { get; set; }
    [StringLength(500, ErrorMessage = "Ghi chú tối đa 500 ký tự.")]
    public string? Notes { get; set; }
    public string PaymentMethod { get; set; } = "Cash";
    public IFormFile? StudentPhoto { get; set; }
    public CourseProgram? Course { get; set; }
    public Student? Student { get; set; }
    public List<Teacher> Teachers { get; set; } = [];
}
''')
write('Controllers/EnrollmentController.cs','''using System.Data;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Enrollment;

namespace WedEnglishApp.Controllers;

[Authorize(Roles = "Student")]
public class EnrollmentController(ApplicationDbContext context, IWebHostEnvironment environment) : Controller
{
    private async Task<bool> LoadAsync(CourseEnrollmentViewModel model)
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var accountId);
        model.Student = await context.Students.Include(s => s.UserAccount)
            .FirstOrDefaultAsync(s => s.AccountId == accountId && !s.UserAccount.IsDeleted && s.UserAccount.IsActive);
        model.Course = await context.Programs.FirstOrDefaultAsync(p => p.ProgramId == model.ProgramId && p.IsActive && !p.IsDeleted);
        model.Teachers = await context.Teachers.Include(t => t.UserAccount)
            .Where(t => t.UserAccount.IsActive && !t.UserAccount.IsDeleted).ToListAsync();
        return model.Student != null && model.Course != null;
    }

    public async Task<IActionResult> Checkout(int programId)
    {
        var model = new CourseEnrollmentViewModel { ProgramId = programId, EarliestStartDate = DateTime.Today.AddDays(1) };
        if (!await LoadAsync(model)) return NotFound();
        if (await context.Registrations.AnyAsync(r => r.StudentId == model.Student!.StudentId && r.ProgramId == programId && !r.IsDeleted && r.Status != "Cancelled"))
        {
            TempData["ErrorMessage"] = "Bạn đã đăng ký khóa học này. Hãy theo dõi trạng thái xếp lớp trong tài khoản.";
            return RedirectToAction("MyClasses", "Student");
        }
        return View(model);
    }

    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Confirm(CourseEnrollmentViewModel model)
    {
        if (!await LoadAsync(model)) return NotFound();
        if (!model.EarliestStartDate.HasValue || model.EarliestStartDate.Value.Date < DateTime.Today)
            ModelState.AddModelError(nameof(model.EarliestStartDate), "Ngày bắt đầu không được ở quá khứ.");
        if (!new[] { "Morning", "Afternoon", "Evening", "Any" }.Contains(model.PreferredSession))
            ModelState.AddModelError(nameof(model.PreferredSession), "Buổi học không hợp lệ.");
        if (model.PreferredDays.Length == 0 || model.PreferredDays.Any(d => d < 2 || d > 8))
            ModelState.AddModelError(nameof(model.PreferredDays), "Chọn ít nhất một thứ có thể học trong tuần.");
        if (!new[] { "Cash", "VietQR" }.Contains(model.PaymentMethod))
            ModelState.AddModelError(nameof(model.PaymentMethod), "Phương thức thanh toán không hợp lệ.");
        if (model.DesiredTeacherId.HasValue && !model.Teachers.Any(t => t.TeacherId == model.DesiredTeacherId))
            ModelState.AddModelError(nameof(model.DesiredTeacherId), "Giáo viên đã ngừng hoạt động hoặc không tồn tại.");
        if (model.StudentPhoto != null && await ImageUploadValidator.GetValidatedExtensionAsync(model.StudentPhoto) == null)
            ModelState.AddModelError(nameof(model.StudentPhoto), "Ảnh JPG, PNG hoặc WEBP tối đa 5 MB.");
        if (!ModelState.IsValid) return View("Checkout", model);

        await using var transaction = await context.Database.BeginTransactionAsync(IsolationLevel.Serializable);
        if (await context.Registrations.AnyAsync(r => r.StudentId == model.Student!.StudentId && r.ProgramId == model.ProgramId && !r.IsDeleted && r.Status != "Cancelled"))
        {
            ModelState.AddModelError("", "Bạn đã đăng ký khóa học này rồi.");
            return View("Checkout", model);
        }
        if (model.StudentPhoto != null)
        {
            model.Student!.PhotoUrl = await ImageUploadStorage.SaveAsync(environment, model.StudentPhoto, "students");
            model.Student.UserAccount.AvatarUrl = model.Student.PhotoUrl;
        }
        var registration = new Registration
        {
            StudentId = model.Student!.StudentId, ProgramId = model.ProgramId, ClassId = null,
            EarliestStartDate = model.EarliestStartDate!.Value.Date,
            PreferredSession = model.PreferredSession,
            PreferredDays = string.Join(",", model.PreferredDays.Distinct().Order()),
            DesiredTeacherId = model.DesiredTeacherId, Notes = model.Notes?.Trim(), Status = "Pending"
        };
        registration.Payment = new Payment
        {
            Amount = model.Course!.TuitionFee, PaymentDate = DateTime.Now,
            PaymentMethod = model.PaymentMethod, Status = "Pending"
        };
        context.Registrations.Add(registration);
        await context.SaveChangesAsync();
        if (model.PaymentMethod == "VietQR")
        {
            registration.Payment.TransactionCode = $"HPREG{registration.RegistrationId}";
            await context.SaveChangesAsync();
        }
        await transaction.CommitAsync();
        TempData["SuccessMessage"] = "Đã nhận đăng ký khóa học và nguyện vọng lịch học. Admin sẽ xếp bạn vào lớp phù hợp.";
        return RedirectToAction("MyClasses", "Student");
    }
}
''')
write('Views/Enrollment/Checkout.cshtml','''@model WedEnglishApp.ViewModels.Enrollment.CourseEnrollmentViewModel
@{ ViewData["Title"] = "Đăng ký khóa học"; }
<div class="container py-5"><div class="row justify-content-center"><div class="col-lg-9">
<h2 class="fw-bold">Đăng ký khóa học</h2>
<h4 class="text-primary">@Model.Course!.ProgramName</h4>
<p>@Model.Course.DurationWeeks tuần · Học phí: <strong>@Model.Course.TuitionFee.ToString("N0") VNĐ</strong></p>
<p>Chọn thời gian bạn có thể học. Trung tâm tiếp nhận nguyện vọng và xếp lớp phù hợp; lịch chính thức được hiển thị sau khi Admin xác nhận.</p>
<form asp-action="Confirm" asp-route-authRole="Student" method="post" enctype="multipart/form-data" class="card p-4">
<div asp-validation-summary="All" class="text-danger" role="alert"></div>
<input asp-for="ProgramId" type="hidden" />
<p>Học viên: <strong>@Model.Student!.UserAccount.FullName</strong> · @Model.Student.UserAccount.Email</p>
<div class="row g-3">
<div class="col-md-6"><label asp-for="EarliestStartDate" class="form-label">Có thể bắt đầu học từ ngày *</label><input asp-for="EarliestStartDate" type="date" min="@DateTime.Today.ToString("yyyy-MM-dd")" class="form-control" required /></div>
<div class="col-md-6"><label asp-for="PreferredSession" class="form-label">Buổi học mong muốn *</label><select asp-for="PreferredSession" class="form-select"><option value="Morning">Buổi sáng (06:00–12:00)</option><option value="Afternoon">Buổi chiều (12:00–18:00)</option><option value="Evening">Buổi tối (18:00–22:00)</option><option value="Any">Linh hoạt các buổi</option></select></div>
<fieldset class="col-12"><legend class="fs-6">Các thứ có thể học * (chọn nhiều)</legend><div class="d-flex flex-wrap gap-3">
@for (var day = 2; day <= 8; day++) { <div class="form-check"><input type="checkbox" name="PreferredDays" value="@day" id="day-@day" class="form-check-input" checked="@(Model.PreferredDays.Contains(day))" /><label for="day-@day" class="form-check-label">@(day == 8 ? "Chủ nhật" : $"Thứ {day}")</label></div> }
</div><div class="form-text">Chỉ chọn những ngày bạn thực sự có thể tham gia. Admin sẽ chọn lịch trong các ngày này.</div></fieldset>
<div class="col-md-6"><label asp-for="DesiredTeacherId" class="form-label">Giáo viên mong muốn (tùy chọn)</label><select asp-for="DesiredTeacherId" class="form-select"><option value="">Để trung tâm phân công</option>@foreach(var teacher in Model.Teachers) { <option value="@teacher.TeacherId">@teacher.UserAccount.FullName</option> }</select></div>
<div class="col-md-6"><label asp-for="StudentPhoto" class="form-label">Cập nhật ảnh hồ sơ (tùy chọn)</label><input asp-for="StudentPhoto" type="file" accept=".jpg,.jpeg,.png,.webp" class="form-control" /></div>
<div class="col-12"><label asp-for="Notes" class="form-label">Nguyện vọng khác</label><textarea asp-for="Notes" maxlength="500" rows="3" class="form-control" placeholder="Ví dụ: chỉ học sau 19 giờ, cần nghỉ một số ngày, muốn học cùng bạn..."></textarea></div>
<div class="col-12"><label asp-for="PaymentMethod" class="form-label">Phương thức đóng học phí</label><select asp-for="PaymentMethod" class="form-select"><option value="Cash">Đóng tại trung tâm</option><option value="VietQR">Chuyển khoản VietQR</option></select><div class="form-text">Hướng dẫn chuyển khoản xuất hiện trong đơn đăng ký sau khi gửi. Thanh toán được trung tâm xác nhận riêng với việc xếp lớp.</div></div>
</div><div class="d-flex gap-3 mt-4"><button class="btn btn-primary" type="submit">Gửi đăng ký khóa học</button><a asp-controller="Program" asp-action="Detail" asp-route-id="@Model.ProgramId" class="btn btn-outline-secondary">Quay lại</a></div>
</form></div></div></div>
''')
# Public pages must never load or advertise unassigned class rosters.
s=read('Controllers/HomeController.cs');a=s.index('                UpcomingClasses =');b=s.index('                FeaturedTeachers =',a);s=s[:a]+s[b:];write('Controllers/HomeController.cs',s)
s=read('Views/Home/Index.cshtml');a=s.index('<!-- 5. UPCOMING');a=s.rfind('<!-- ===',0,a);b=s.index('<!-- 6. TEACHERS',a);b=s.rfind('<!-- ===',a,b);s=s[:a]+s[b:];s=s.replace('Lịch khai giảng &amp; Ưu đãi khóa học mới','Đăng ký khóa học theo lịch phù hợp');write('Views/Home/Index.cshtml',s)
s=read('Controllers/ProgramController.cs');a=s.index('            var program =',s.index('Task<IActionResult> Detail'));b=s.index('            if (program == null)',a);s=s[:a]+'''            var program = await _context.Programs
                .FirstOrDefaultAsync(p => p.ProgramId == id && p.IsActive && !p.IsDeleted);

'''+s[b:];s=s.replace('_context.Programs.Where(p => p.IsActive)','_context.Programs.Where(p => p.IsActive && !p.IsDeleted)');write('Controllers/ProgramController.cs',s)
s=read('Views/Program/Detail.cshtml');a=s.index('            <!-- Các lớp học liên quan -->');b=s.index('\n        </div>',a);s=s[:a]+'''            <div class="card card-custom p-4 border-0 bg-white">
                <h4 class="fw-bold text-primary">Đăng ký và chọn lịch học mong muốn</h4>
                <p>Bạn chọn ngày có thể bắt đầu, buổi học và các thứ trong tuần. Trung tâm sẽ xếp lớp phù hợp và thông báo trong tài khoản học viên.</p>
                <a asp-controller="Enrollment" asp-action="Checkout" asp-route-programId="@Model.ProgramId" asp-route-authRole="Student" class="btn btn-primary">Đăng ký khóa học</a>
            </div>'''+s[b:];write('Views/Program/Detail.cshtml',s)
print('Course enrollment model, database upgrade and public checkout updated')
