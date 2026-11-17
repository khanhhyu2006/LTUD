// =================================================================================================
// MODEL: PlacementTest.cs - THỰC THỂ KIỂM TRA & THI XẾP LỚP TRÌNH ĐỘ ĐẦU VÀO
// Bảng trong CSDL: PlacementTests
// Mục đích: Quản lý lịch thi xếp lớp của học viên, điểm số và gợi ý khóa học đề xuất
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("PlacementTests")] // Ánh xạ tới bảng PlacementTests trong SQL Server
    public class PlacementTest
    {
        [Key] // Khóa chính (TestId tự tăng)
        public int TestId { get; set; }

        [Required]
        public int StudentId { get; set; } // Khóa ngoại liên kết tới học viên dự thi

        public int? EvaluatedByTeacherId { get; set; } // Khóa ngoại liên kết tới Giảng viên chấm thi (null nếu chưa chấm)

        public int? ExamSessionId { get; set; }
        [ForeignKey(nameof(ExamSessionId))]
        public virtual ExamSession? ExamSession { get; set; }
        public DateTime? RequestedDate { get; set; }
        [StringLength(20)] public string? RequestedTime { get; set; }

        public DateTime TestDate { get; set; } // Ngày diễn ra bài thi xếp lớp

        [StringLength(20)]
        public string TestTime { get; set; } = "09:00 AM"; // Ca thi / Giờ thi (VD: 09:00 AM, 02:00 PM)

        [StringLength(100)]
        public string? Room { get; set; } // Phòng thi xếp lớp do Admin phân bổ

        [Column(TypeName = "decimal(4,2)")]
        [Range(0, 10)]
        public decimal? Score { get; set; } // Điểm số đánh giá (Thang điểm 10 hoặc IELTS tương ứng)

        [StringLength(100)]
        public string? RecommendedLevel { get; set; } // Khóa học được hệ thống hoặc GV đề xuất (VD: "IELTS 5.5+", "Giao tiếp nâng cao")

        [Required]
        [StringLength(30)]
        public string Status { get; set; } = "Pending"; // Trạng thái: "Pending" (Chờ thi/Chờ chấm), "Completed" (Đã có kết quả)

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm xóa vào thùng rác

        // =========================================================================================
        // NAVIGATION PROPERTIES: CÁC MỐI QUAN HỆ TRONG HỆ THỐNG
        // =========================================================================================
        [ForeignKey("StudentId")]
        public virtual Student Student { get; set; } = null!; // Hồ sơ học viên làm bài thi (N - 1)

        [ForeignKey("EvaluatedByTeacherId")]
        public virtual Teacher? EvaluatedByTeacher { get; set; } // Giảng viên chấm bài kiểm tra (N - 1)
    }
}
