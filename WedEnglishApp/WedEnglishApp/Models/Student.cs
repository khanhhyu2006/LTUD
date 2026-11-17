// =================================================================================================
// MODEL: Student.cs - THỰC THỂ HỒ SƠ HỌC VIÊN
// Bảng trong CSDL: Students
// Mục đích: Quản lý thông tin cá nhân của học viên, liên kết 1-1 với tài khoản UserAccount
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Students")] // Ánh xạ tới bảng Students trong SQL Server
    public class Student
    {
        [Key] // Khóa chính của học viên (StudentId tự tăng)
        public int StudentId { get; set; }

        [Required]
        public int AccountId { get; set; } // Khóa ngoại liên kết 1-1 với bảng UserAccounts

        [StringLength(20)]
        public string? PhoneNumber { get; set; } // Số điện thoại liên hệ của học viên

        [StringLength(255)]
        public string? Address { get; set; } // Địa chỉ thường trú / tạm trú

        [StringLength(255)]
        public string? PhotoUrl { get; set; } // Ảnh hồ sơ học viên dùng cho đăng ký và thi xếp lớp

        public DateTime? DateOfBirth { get; set; } // Ngày tháng năm sinh

        // =========================================================================================
        // NAVIGATION PROPERTIES: CÁC MỐI QUAN HỆ TRONG HỆ THỐNG
        // =========================================================================================
        [ForeignKey("AccountId")]
        public virtual UserAccount UserAccount { get; set; } = null!; // Thực thể tài khoản đăng nhập (1 - 1)

        public virtual ICollection<Registration> Registrations { get; set; } = new List<Registration>(); // Danh sách các lớp học viên đã đăng ký (1 - N)
        public virtual ICollection<PlacementTest> PlacementTests { get; set; } = new List<PlacementTest>(); // Lịch sử các bài thi xếp lớp đầu vào (1 - N)
    }
}
