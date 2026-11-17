using Microsoft.EntityFrameworkCore;
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
