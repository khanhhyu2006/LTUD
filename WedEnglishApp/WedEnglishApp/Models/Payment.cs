// =================================================================================================
// MODEL: Payment.cs - THỰC THỂ HÓA ĐƠN & BIÊN LAI THANH TOÁN HỌC PHÍ
// Bảng trong CSDL: Payments
// Mục đích: Quản lý số tiền đã thu, hình thức thanh toán (VietQR, Tiền mặt), mã giao dịch và trạng thái
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Payments")] // Ánh xạ tới bảng Payments trong SQL Server
    public class Payment
    {
        [Key] // Khóa chính (PaymentId tự tăng)
        public int PaymentId { get; set; }

        [Required]
        public int RegistrationId { get; set; } // Khóa ngoại liên kết 1-1 với đơn đăng ký (Registration)

        [Column(TypeName = "decimal(18,2)")]
        public decimal Amount { get; set; } // Số tiền học phí phải nộp (VNĐ)

        public DateTime? ConfirmedAt { get; set; }
        public DateTime PaymentDate { get; set; } = DateTime.Now; // Thời điểm tạo hóa đơn / thực hiện thanh toán

        [Required]
        [StringLength(50)]
        public string PaymentMethod { get; set; } = "Cash"; // Phương thức: "VietQR", "Cash" (Tiền mặt), "VNPay", "BankTransfer"

        [StringLength(100)]
        public string? TransactionCode { get; set; } // Mã giao dịch ngân hàng / Mã quét VietQR (VD: VIETQR20261017...)

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Pending"; // Trạng thái hóa đơn: "Pending" (Chờ thu), "Paid" (Đã thu tiền), "Failed" (Thất bại)

        // =========================================================================================
        // NAVIGATION PROPERTY: QUAN HỆ 1 - 1 VỚI ĐƠN ĐĂNG KÝ
        // =========================================================================================
        [ForeignKey("RegistrationId")]
        public virtual Registration Registration { get; set; } = null!; // Đơn đăng ký sở hữu hóa đơn này (1 - 1)
    }
}
