// =================================================================================================
// MODEL: Registration.cs - THỰC THỂ ĐĂNG KÝ HỌC / GHI DANH LỚP HỌC
// Bảng trong CSDL: Registrations
// Mục đích: Ghi danh khóa học và lưu nguyện vọng; ClassId được gán sau khi Admin xếp lớp.
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Registrations")] // Ánh xạ tới bảng Registrations trong SQL Server
    public class Registration
    {
        [Key] // Khóa chính (RegistrationId tự tăng)
        public int RegistrationId { get; set; }

        [Required]
        public int StudentId { get; set; } // Khóa ngoại liên kết tới học viên đăng ký

        public int? ClassId { get; set; } // Khóa ngoại liên kết tới lớp học được chọn

        [Required]
        public int ProgramId { get; set; }

        [ForeignKey(nameof(ProgramId))]
        public virtual CourseProgram Program { get; set; } = null!;

        public DateTime? EarliestStartDate { get; set; }

        [StringLength(30)]
        public string? PreferredSession { get; set; }

        [StringLength(30)]
        public string? PreferredDays { get; set; }

        public DateTime RegistrationDate { get; set; } = DateTime.Now; // Thời điểm học viên bấm đăng ký trên website

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Pending"; // Pending: chờ xếp lớp; Confirmed: Admin đã xếp lớp; Cancelled: đã hủy. Độc lập trạng thái học phí.

        public int? DesiredTeacherId { get; set; } // Giảng viên học viên mong muốn được học cùng

        [StringLength(500)]
        public string? Notes { get; set; } // Ghi chú / Nguyện vọng xếp lớp của học viên

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm xóa vào thùng rác

        // =========================================================================================
        // NAVIGATION PROPERTIES: CÁC MỐI QUAN HỆ TRONG HỆ THỐNG
        // =========================================================================================
        [ForeignKey("StudentId")]
        public virtual Student Student { get; set; } = null!; // Hồ sơ học viên thực hiện đăng ký (N - 1)

        [ForeignKey("ClassId")]
        public virtual CourseClass Class { get; set; } = null!; // Lớp học được đăng ký (N - 1)

        [ForeignKey("DesiredTeacherId")]
        public virtual Teacher? DesiredTeacher { get; set; } // Giảng viên mong muốn (N - 1)

        public virtual Payment? Payment { get; set; } // Hóa đơn học phí liên kết 1 - 1
    }
}
