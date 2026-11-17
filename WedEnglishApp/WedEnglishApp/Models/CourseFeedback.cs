// =================================================================================================
// MODEL: CourseFeedback.cs - THỰC THỂ ĐÁNH GIÁ & PHẢN HỒI CHẤT LƯỢNG KHÓA HỌC
// Bảng trong CSDL: CourseFeedbacks
// Mục đích: Cho phép học viên gửi đánh giá số sao (1-5 sao) và nhận xét về giảng viên / lớp học
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("CourseFeedbacks")] // Ánh xạ tới bảng CourseFeedbacks trong SQL Server
    public class CourseFeedback
    {
        [Key] // Khóa chính (FeedbackId tự tăng)
        public int FeedbackId { get; set; }

        [Required]
        public int StudentId { get; set; } // Khóa ngoại liên kết tới học viên đánh giá

        [Required]
        public int ClassId { get; set; } // Khóa ngoại liên kết tới lớp học được đánh giá

        [Range(1, 5, ErrorMessage = "Đánh giá từ 1 đến 5 sao")]
        public int Rating { get; set; } = 5; // Số sao đánh giá chất lượng (1 đến 5 sao)

        [Required(ErrorMessage = "Vui lòng nhập nhận xét của bạn")]
        [StringLength(1000)]
        public string Comment { get; set; } = string.Empty; // Ý kiến đóng góp, nhận xét chi tiết

        public DateTime CreatedAt { get; set; } = DateTime.Now; // Thời gian gửi đánh giá

        // =========================================================================================
        // NAVIGATION PROPERTIES
        // =========================================================================================
        [ForeignKey("StudentId")]
        public virtual Student Student { get; set; } = null!; // Học viên gửi đánh giá (N - 1)

        [ForeignKey("ClassId")]
        public virtual CourseClass Class { get; set; } = null!; // Lớp học nhận đánh giá (N - 1)
    }
}
