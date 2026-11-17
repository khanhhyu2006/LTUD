// =================================================================================================
// MODEL: CourseClass.cs - THỰC THỂ LỚP HỌC THỰC TẾ TRONG TRUNG TÂM
// Bảng trong CSDL: Classes
// Mục đích: Quản lý lớp học cụ thể (mã lớp, phòng học, sĩ số tối đa, ngày khai giảng, trạng thái)
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.AspNetCore.Mvc.ModelBinding.Validation;

namespace WedEnglishApp.Models
{
    [Table("Classes")] // Ánh xạ tới bảng Classes trong SQL Server
    public class CourseClass
    {
        [Key] // Khóa chính (ClassId tự tăng)
        public int ClassId { get; set; }

        [Required]
        [Range(1, int.MaxValue, ErrorMessage = "Vui lòng chọn chương trình học")]
        public int ProgramId { get; set; } // Khóa ngoại liên kết tới khóa học (Program)

        public int? TeacherId { get; set; } // Khóa ngoại liên kết tới Giảng viên phụ trách đứng lớp (có thể null nếu chưa gán GV)

        [Required(ErrorMessage = "Tên lớp không được để trống")]
        [StringLength(100)]
        public string ClassName { get; set; } = string.Empty; // Tên lớp học hiển thị (VD: "IELTS 6.5 - K01")

        [StringLength(50)]
        public string Room { get; set; } = "Room 101"; // Phòng học tại cơ sở (VD: "Lab 201", "Phòng A302")

        [Range(1, 100)]
        public int MaxStudents { get; set; } = 25; // Sĩ số tối đa của lớp học (dùng để kiểm soát không cho đăng ký vượt quá)

        public DateTime StartDate { get; set; } // Ngày khai giảng lớp học

        public DateTime EndDate { get; set; } // Ngày bế giảng dự kiến

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Planning"; // Trạng thái lớp: "Planning" (Chiêu sinh), "InProgress" (Đang học), "Completed" (Kết thúc), "Cancelled" (Hủy)

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm chuyển vào thùng rác

        // =========================================================================================
        // NAVIGATION PROPERTIES: CÁC MỐI QUAN HỆ TRONG HỆ THỐNG
        // =========================================================================================
        [ValidateNever]
        [ForeignKey("ProgramId")]
        public virtual CourseProgram Program { get; set; } = null!; // Thực thể chương trình học trực thuộc (N - 1)

        [ValidateNever]
        [ForeignKey("TeacherId")]
        public virtual Teacher? Teacher { get; set; } // Giảng viên phụ trách lớp (N - 1)

        public virtual ICollection<Registration> Registrations { get; set; } = new List<Registration>(); // Danh sách học viên đăng ký lớp này (1 - N)
        public virtual ICollection<ClassSchedule> Schedules { get; set; } = new List<ClassSchedule>(); // Thời khóa biểu các ca học trong tuần (1 - N)
        public virtual ICollection<ClassDocument> Documents { get; set; } = new List<ClassDocument>(); // Tài liệu giáo trình của lớp (1 - N)
    }
}
