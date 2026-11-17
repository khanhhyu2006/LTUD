using System.Data;
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
        var preferredDays = EnrollmentSchedule.GetDays(model.SchedulePattern);
        if (preferredDays == null)
            ModelState.AddModelError(nameof(model.SchedulePattern), "Chọn một trong hai lịch học: Thứ 2–4–6 hoặc Thứ 3–5–7.");
        if (!new[] { "Cash", "VietQR" }.Contains(model.PaymentMethod))
            ModelState.AddModelError(nameof(model.PaymentMethod), "Phương thức thanh toán không hợp lệ.");
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
            PreferredDays = preferredDays,
            Notes = model.Notes?.Trim(), Status = "Pending"
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
        return RedirectToAction(nameof(Payment), new { registrationId = registration.RegistrationId });
    }

    public async Task<IActionResult> Payment(int registrationId)
    {
        int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier), out var accountId);
        var registration = await context.Registrations
            .Include(r => r.Program).Include(r => r.Payment)
            .Include(r => r.Student).ThenInclude(s => s.UserAccount)
            .FirstOrDefaultAsync(r => r.RegistrationId == registrationId && r.Student.AccountId == accountId && !r.IsDeleted);
        if (registration == null || registration.Status == "Cancelled") return NotFound();
        return View(registration);
    }
}
