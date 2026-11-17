// =================================================================================================
// MODEL: Teacher.cs - THỰC THỂ HỒ SƠ GIẢNG VIÊN
// Bảng trong CSDL: Teachers
// Mục đích: Quản lý thông tin bằng cấp, chuyên môn, tiểu sử của giảng viên trong trung tâm
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Teachers")] // Ánh xạ tới bảng Teachers trong SQL Server
    public class Teacher
    {
        [Key] // Khóa chính (TeacherId tự tăng)
        public int TeacherId { get; set; }

        [Required]
        public int AccountId { get; set; } // Khóa ngoại liên kết 1-1 với UserAccounts

        [Required]
        [StringLength(100)]
        public string Specialization { get; set; } = string.Empty; // Chuyên môn giảng dạy: IELTS, TOEIC, Giao tiếp, Tiếng Anh Thiếu nhi

        [StringLength(1000)]
        public string? Bio { get; set; } // Giới thiệu bản thân, số năm kinh nghiệm giảng dạy

        [StringLength(100)]
        public string? Degree { get; set; } // Học vị / Bằng cấp: ThS. Ngôn ngữ Anh, Cử nhân Sư phạm, IELTS 8.5...

        [StringLength(255)]
        public string? PhotoUrl { get; set; } // Ảnh hồ sơ do giảng viên tải lên

        // =========================================================================================
        // NAVIGATION PROPERTIES: CÁC MỐI QUAN HỆ TRONG HỆ THỐNG
        // =========================================================================================
        [ForeignKey("AccountId")]
        public virtual UserAccount UserAccount { get; set; } = null!; // Thực thể tài khoản đăng nhập (1 - 1)

        public virtual ICollection<CourseClass> Classes { get; set; } = new List<CourseClass>(); // Danh sách các lớp được phân công dạy (1 - N)
        public virtual ICollection<PlacementTest> EvaluatedTests { get; set; } = new List<PlacementTest>(); // Các bài thi xếp lớp giáo viên đã chấm (1 - N)
    }
}
