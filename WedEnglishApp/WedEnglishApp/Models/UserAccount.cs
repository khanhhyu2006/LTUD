// =================================================================================================
// MODEL: UserAccount.cs - THỰC THỂ TÀI KHOẢN NGƯỜI DÙNG HỆ THỐNG
// Bảng trong CSDL: UserAccounts
// Mục đích: Quản lý thông tin đăng nhập, mật khẩu băm, vai trò (Role: Admin, Teacher, Student)
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("UserAccounts")] // Ánh xạ tới bảng UserAccounts trong SQL Server
    public class UserAccount
    {
        [Key] // Khóa chính (Primary Key - Identity tự tăng trong SQL Server)
        public int AccountId { get; set; }

        [Required(ErrorMessage = "Họ và tên không được để trống")] // Bắt buộc nhập
        [StringLength(100)] // Chiều dài tối đa 100 ký tự (nvarchar(100))
        public string FullName { get; set; } = string.Empty; // Họ và tên đầy đủ

        [Required(ErrorMessage = "Email không được để trống")]
        [EmailAddress(ErrorMessage = "Email không đúng định dạng")] // Kiểm tra định dạng email hợp lệ
        [StringLength(100)]
        public string Email { get; set; } = string.Empty; // Địa chỉ email duy nhất (dùng đăng nhập)

        [Required]
        public string PasswordHash { get; set; } = string.Empty; // Mật khẩu đã được mã hóa 1 chiều bằng BCrypt

        [Required]
        [StringLength(20)]
        public string Role { get; set; } = "Student"; // Vai trò người dùng: "Admin", "Teacher", "Student"

        [StringLength(255)]
        public string? AvatarUrl { get; set; } // Đường dẫn lưu trữ ảnh đại diện đại diện (Upload vào wwwroot/uploads)

        public bool IsActive { get; set; } = true; // Trạng thái kích hoạt: true = Hoạt động, false = Bị khóa

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm xóa vào thùng rác

        public DateTime CreatedAt { get; set; } = DateTime.Now; // Thời điểm tạo tài khoản

        // =========================================================================================
        // NAVIGATION PROPERTIES: THUỘC TÍNH ĐIỀU HƯỚNG LIÊN KẾT THỰC THỂ TRONG ENTITY FRAMEWORK
        // =========================================================================================
        public virtual Student? Student { get; set; } // Liên kết 1 - 1 với bảng Students (nếu là học viên)
        public virtual Teacher? Teacher { get; set; } // Liên kết 1 - 1 với bảng Teachers (nếu là giáo viên)
    }
}
