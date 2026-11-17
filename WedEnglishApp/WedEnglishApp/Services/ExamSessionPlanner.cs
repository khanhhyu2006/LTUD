using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public static class ExamSessionPlanner
{
    public static async Task<string?> ValidateAsync(ApplicationDbContext context, ExamSession session)
    {
        if (session.ExamDate.Date < DateTime.Today || session.StartTime < TimeSpan.Zero || session.StartTime >= session.EndTime || session.EndTime >= TimeSpan.FromDays(1))
            return "Chọn ngày thi từ hôm nay và giờ kết thúc sau giờ bắt đầu.";
        if (session.TeacherId.HasValue && !await context.Teachers.AnyAsync(t => t.TeacherId == session.TeacherId && t.UserAccount.IsActive && !t.UserAccount.IsDeleted))
            return "Giáo viên không tồn tại hoặc đã ngừng hoạt động.";
        if (await context.ExamSessions.AnyAsync(s => s.ExamSessionId != session.ExamSessionId && s.Name == session.Name)) return "Mã lớp thi đã tồn tại.";
        var others = await context.ExamSessions.Where(s => s.ExamSessionId != session.ExamSessionId && s.Status != "Cancelled" && s.ExamDate.Date == session.ExamDate.Date && s.StartTime < session.EndTime && session.StartTime < s.EndTime).ToListAsync();
        if (others.Any(s => string.Equals(s.Room.Trim(), session.Room.Trim(), StringComparison.OrdinalIgnoreCase))) return "Phòng đã có ca thi trong khoảng giờ này.";
        if (session.TeacherId.HasValue && others.Any(s => s.TeacherId == session.TeacherId)) return "Giáo viên đã được phân công ca thi trùng giờ.";
        var day = session.ExamDate.DayOfWeek == DayOfWeek.Sunday ? 8 : (int)session.ExamDate.DayOfWeek + 1;
        var classes = await context.Classes.Include(c => c.Schedules).Where(c => !c.IsDeleted && c.Status != "Cancelled" && c.Status != "Completed" && c.StartDate.Date <= session.ExamDate.Date && c.EndDate.Date >= session.ExamDate.Date).ToListAsync();
        var overlap = classes.Where(c => c.Schedules.Any(s => s.DayOfWeek == day && s.StartTime < session.EndTime && session.StartTime < s.EndTime));
        if (overlap.Any(c => string.Equals(c.Room.Trim(), session.Room.Trim(), StringComparison.OrdinalIgnoreCase))) return "Phòng đang có lớp học trong giờ thi.";
        if (session.TeacherId.HasValue && overlap.Any(c => c.TeacherId == session.TeacherId)) return "Giáo viên đang có lịch giảng dạy trong giờ thi.";
        return null;
    }

    public static void CopySchedule(PlacementTest test, ExamSession session)
    {
        test.ExamSessionId = session.ExamSessionId;
        test.TestDate = session.ExamDate.Date;
        test.TestTime = session.StartTime.ToString(@"hh\:mm");
        test.Room = session.Room;
        test.EvaluatedByTeacherId = session.TeacherId;
    }
}
