// =================================================================================================
// MODEL: CourseProgram.cs - THỰC THỂ CHƯƠNG TRÌNH ĐÀO TẠO / KHÓA HỌC
// Bảng trong CSDL: Programs
// Mục đích: Quản lý thông tin khóa học (IELTS, TOEIC, Giao tiếp), học phí, chuẩn đầu ra, thời lượng
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Programs")] // Ánh xạ tới bảng Programs trong SQL Server
    public class CourseProgram
    {
        [Key] // Khóa chính (ProgramId tự tăng)
        public int ProgramId { get; set; }

        [Required(ErrorMessage = "Tên chương trình không được để trống")]
        [StringLength(150)]
        public string ProgramName { get; set; } = string.Empty; // Tên khóa học (VD: "IELTS Master 6.5+")

        [Required]
        [StringLength(50)]
        public string Level { get; set; } = "Beginner"; // Trình độ yêu cầu: Beginner, Intermediate, Advanced

        [Range(1, 100)]
        public int DurationWeeks { get; set; } // Thời lượng khóa học (tính theo số tuần, VD: 12 tuần)

        [Column(TypeName = "decimal(18,2)")]
        [Range(0, 100000000, ErrorMessage = "Học phí không hợp lệ")]
        public decimal TuitionFee { get; set; } // Học phí chuẩn của khóa học (VD: 6.800.000 VNĐ)

        [Required]
        public string Description { get; set; } = string.Empty; // Mô tả chi tiết lộ trình học tập

        public string? LearningOutcomes { get; set; } // Chuẩn đầu ra sau khi hoàn thành khóa học

        [StringLength(255)]
        public string? ImageUrl { get; set; } // Ảnh đại diện khóa học hiển thị trên trang chủ

        public bool IsActive { get; set; } = true; // Trạng thái tuyển sinh: true = Đang mở, false = Tạm đóng

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm xóa vào thùng rác

        public DateTime CreatedAt { get; set; } = DateTime.Now; // Ngày tạo khóa học

        // =========================================================================================
        // NAVIGATION PROPERTIES: MỐI QUAN HỆ 1 - N VỚI LỚP HỌC
        // =========================================================================================
        public virtual ICollection<CourseClass> Classes { get; set; } = new List<CourseClass>(); // 1 khóa học mở được nhiều lớp học (Classes)
    }
}
