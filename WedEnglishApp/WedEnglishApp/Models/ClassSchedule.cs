// =================================================================================================
// MODEL: ClassSchedule.cs - THỰC THỂ LỊCH HỌC / THỜI KHÓA BIỂU CÁC CA TRONG TUẦN
// Bảng trong CSDL: ClassSchedules (Bảng bổ sung đề xuất)
// Mục đích: Phân bổ ca học chi tiết (Thứ mấy trong tuần, giờ bắt đầu, giờ kết thúc) cho từng lớp
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("ClassSchedules")] // Ánh xạ tới bảng ClassSchedules trong SQL Server
    public class ClassSchedule
    {
        [Key] // Khóa chính (ScheduleId tự tăng)
        public int ScheduleId { get; set; }

        [Required]
        public int ClassId { get; set; } // Khóa ngoại liên kết tới lớp học (CourseClass)

        [Range(2, 8, ErrorMessage = "Thứ trong tuần từ 2 (Thứ Hai) đến 8 (Chủ Nhật)")]
        public int DayOfWeek { get; set; } // Thứ trong tuần (2: Thứ Hai, 3: Thứ Ba, ..., 8: Chủ Nhật)

        public TimeSpan StartTime { get; set; } // Giờ bắt đầu ca học (VD: 18:00:00)

        public TimeSpan EndTime { get; set; } // Giờ kết thúc ca học (VD: 19:30:00)

        // =========================================================================================
        // NAVIGATION PROPERTY
        // =========================================================================================
        [ForeignKey("ClassId")]
        public virtual CourseClass Class { get; set; } = null!; // Lớp học sở hữu lịch học này (N - 1)
    }
}
