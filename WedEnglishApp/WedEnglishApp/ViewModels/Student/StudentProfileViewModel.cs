using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Http;

namespace WedEnglishApp.ViewModels.Student
{
    public class StudentProfileViewModel
    {
        public int StudentId { get; set; }
        public int AccountId { get; set; }

        [Required(ErrorMessage = "Họ và tên không được để trống")]
        [StringLength(100)]
        public string FullName { get; set; } = string.Empty;

        public string Email { get; set; } = string.Empty;

        [Required(ErrorMessage = "Vui lòng nhập Số điện thoại")]
        [RegularExpression(@"^(0[3|5|7|8|9])+([0-9]{8})$", ErrorMessage = "Số điện thoại không hợp lệ")]
        public string? PhoneNumber { get; set; }

        [StringLength(255)]
        public string? Address { get; set; }

        [DataType(DataType.Date)]
        public DateTime? DateOfBirth { get; set; }

        public string? AvatarUrl { get; set; }

        public IFormFile? AvatarFile { get; set; }
    }
}
