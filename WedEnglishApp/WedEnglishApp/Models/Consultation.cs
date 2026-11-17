// =================================================================================================
// MODEL: Consultation.cs - THỰC THỂ TIẾP NHẬN YÊU CẦU TƯ VẤN KHÓA HỌC
// Bảng trong CSDL: Consultations (Bảng bổ sung đề xuất)
// Mục đích: Lưu cuộc tư vấn hai chiều giữa học viên/khách và Admin, kèm quyền theo dõi riêng.
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Consultations")] // Ánh xạ tới bảng Consultations trong SQL Server
    public class Consultation
    {
        [Key] // Khóa chính (ConsultationId tự tăng)
        public int ConsultationId { get; set; }

        [Required(ErrorMessage = "Vui lòng nhập họ và tên")]
        [StringLength(100)]
        public string ContactName { get; set; } = string.Empty; // Họ và tên khách hàng cần tư vấn

        [Required(ErrorMessage = "Vui lòng nhập email")]
        [EmailAddress(ErrorMessage = "Email không hợp lệ")]
        [StringLength(100)]
        public string ContactEmail { get; set; } = string.Empty; // Email liên hệ

        [Required(ErrorMessage = "Vui lòng nhập số điện thoại")]
        [StringLength(20)]
        public string PhoneNumber { get; set; } = string.Empty; // Số điện thoại để chuyên viên gọi tư vấn

        [Required(ErrorMessage = "Vui lòng nhập nội dung câu hỏi tư vấn")]
        [StringLength(1000)]
        public string Question { get; set; } = string.Empty; // Câu hỏi hoặc nguyện vọng (VD: Luyện thi IELTS cấp tốc)

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Pending"; // Pending: chờ Admin; Replied: Admin đã trả lời; Closed: đã kết thúc.

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm xóa vào thùng rác

        public int? OwnerAccountId { get; set; }
        [ForeignKey(nameof(OwnerAccountId))] public virtual UserAccount? OwnerAccount { get; set; }
        [StringLength(64)] public string? GuestAccessHash { get; set; }
        public DateTime LastMessageAt { get; set; } = DateTime.Now;
        public int AdminLastReadMessageId { get; set; }
        public int CustomerLastReadMessageId { get; set; }
        public virtual List<ConsultationMessage> Messages { get; set; } = [];

        public DateTime CreatedAt { get; set; } = DateTime.Now; // Thời điểm khách gửi thông tin
    }
}
