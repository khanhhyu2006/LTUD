using System.Data;
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
        // Buổi và thứ là nguyện vọng để Admin tham khảo, không phải điều kiện chặn xếp lớp.
        // Lớp có thể được xếp trước khi trung tâm hoàn tất lịch học chi tiết.
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
