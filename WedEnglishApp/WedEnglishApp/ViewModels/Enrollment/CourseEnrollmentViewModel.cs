using System.ComponentModel.DataAnnotations;
using WedEnglishApp.Models;
namespace WedEnglishApp.ViewModels.Enrollment;

public class CourseEnrollmentViewModel
{
    public int ProgramId { get; set; }
    [Required(ErrorMessage = "Chọn ngày sớm nhất bạn có thể bắt đầu học.")]
    [DataType(DataType.Date)]
    public DateTime? EarliestStartDate { get; set; }
    [Required(ErrorMessage = "Chọn buổi học mong muốn.")]
    public string PreferredSession { get; set; } = "Evening";
    [Required(ErrorMessage = "Chọn lịch học Thứ 2–4–6 hoặc Thứ 3–5–7.")]
    public string SchedulePattern { get; set; } = string.Empty;
    [StringLength(500, ErrorMessage = "Ghi chú tối đa 500 ký tự.")]
    public string? Notes { get; set; }
    public string PaymentMethod { get; set; } = "Cash";
    public IFormFile? StudentPhoto { get; set; }
    public CourseProgram? Course { get; set; }
    public WedEnglishApp.Models.Student? Student { get; set; }
}
