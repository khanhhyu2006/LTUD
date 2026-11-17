using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.ViewModels.Consultations;
public class StartConsultationViewModel
{
    [Required(ErrorMessage="Nhập họ và tên."), StringLength(100)] public string ContactName { get; set; } = "";
    [Required(ErrorMessage="Nhập email liên hệ."), EmailAddress, StringLength(100)] public string ContactEmail { get; set; } = "";
    [Required(ErrorMessage="Nhập số điện thoại."), StringLength(20), RegularExpression(@"^[0-9+() -]{7,20}$", ErrorMessage="Số điện thoại không hợp lệ.")]
    public string PhoneNumber { get; set; } = "";
    [Required(ErrorMessage="Nhập câu hỏi cần tư vấn."), StringLength(1000)] public string Question { get; set; } = "";
    public bool IsStudent { get; set; }
}
