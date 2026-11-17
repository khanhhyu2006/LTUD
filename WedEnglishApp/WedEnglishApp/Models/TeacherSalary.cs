// =================================================================================================
// MODEL: TeacherSalary.cs - THỰC THỂ QUẢN LÝ BẢNG LƯƠNG GIẢNG VIÊN
// Bảng trong CSDL: TeacherSalaries
// Mục đích: Quản lý lương tháng, lương theo buổi/giờ dạy, phụ cấp, thưởng và trạng thái thanh toán lương
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("TeacherSalaries")]
    public class TeacherSalary
    {
        [Key]
        public int SalaryId { get; set; }

        [Required]
        public int TeacherId { get; set; } // Giảng viên nhận lương

        [Required]
        public int Month { get; set; } // Tháng tính lương (1 - 12)

        [Required]
        public int Year { get; set; } // Năm tính lương (VD: 2026)

        [Column(TypeName = "decimal(18,2)")]
        [Range(0, 1000000000)]
        public decimal BaseSalary { get; set; } = 8000000; // Lương cơ bản tháng

        public int TotalTeachingHours { get; set; } = 40; // Tổng số giờ/buổi dạy trong tháng

        [Column(TypeName = "decimal(18,2)")]
        public decimal HourlyRate { get; set; } = 250000; // Đơn giá mỗi giờ dạy (VD: 250.000 đ/giờ)

        [Column(TypeName = "decimal(18,2)")]
        public decimal Bonus { get; set; } = 0; // Tiền thưởng / Khen thưởng

        [Column(TypeName = "decimal(18,2)")]
        public decimal Deduction { get; set; } = 0; // Khấu trừ (nghỉ không phép, đi trễ...)

        [Column(TypeName = "decimal(18,2)")]
        public decimal TotalSalary { get; set; } // Tổng thực nhận = BaseSalary + (TotalTeachingHours * HourlyRate) + Bonus - Deduction

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Pending"; // Trạng thái: "Pending" (Chờ duyệt), "Paid" (Đã chi trả)

        public DateTime? PaymentDate { get; set; } // Ngày thanh toán lương

        [StringLength(500)]
        public string? Note { get; set; } // Ghi chú chi tiết

        public DateTime CreatedAt { get; set; } = DateTime.Now;

        // =========================================================================================
        // NAVIGATION PROPERTY
        // =========================================================================================
        [ForeignKey("TeacherId")]
        public virtual Teacher Teacher { get; set; } = null!;
    }
}
