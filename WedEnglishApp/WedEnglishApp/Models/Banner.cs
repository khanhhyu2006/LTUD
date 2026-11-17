// =================================================================================================
// MODEL: Banner.cs - THỰC THỂ QUẢN LÝ BANNER QUẢNG BÁ TRÊN TRANG CHỦ
// Bảng trong CSDL: Banners
// Mục đích: Quản lý tiêu đề, mô tả, hình ảnh, thứ tự hiển thị và đường link (LinkUrl) dẫn tới trang đích
// =================================================================================================

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace WedEnglishApp.Models
{
    [Table("Banners")] // Ánh xạ tới bảng Banners trong SQL Server
    public class Banner
    {
        [Key] // Khóa chính (BannerId tự tăng)
        public int BannerId { get; set; }

        [Required(ErrorMessage = "Tiêu đề banner không được để trống")]
        [StringLength(200, ErrorMessage = "Tiêu đề không vượt quá 200 ký tự")]
        public string Title { get; set; } = string.Empty; // Tiêu đề chính của Banner

        [StringLength(500, ErrorMessage = "Mô tả phụ không vượt quá 500 ký tự")]
        public string? Subtitle { get; set; } // Phụ đề / Đoạn giới thiệu ngắn

        [StringLength(500)]
        public string ImageUrl { get; set; } = string.Empty; // Đường dẫn hình ảnh banner (Upload hoặc URL)

        [Required(ErrorMessage = "Đường dẫn liên kết (LinkUrl) không được để trống")]
        [StringLength(500)]
        public string LinkUrl { get; set; } = "/Program"; // Đường link điều hướng khi click vào banner (VD: /Program/Detail/1, /PlacementTest/BookTest)

        [StringLength(50)]
        public string ButtonText { get; set; } = "Khám phá ngay"; // Nhãn nút bấm kêu gọi hành động (Call To Action)

        public int DisplayOrder { get; set; } = 1; // Thứ tự ưu tiên hiển thị (số nhỏ hiển thị trước)

        public bool IsActive { get; set; } = true; // Trạng thái hiển thị: true = Đang hiện, false = Tạm ẩn

        public bool IsDeleted { get; set; } = false; // Trạng thái xóa mềm: true = Trong thùng rác (ẩn), false = Bình thường

        public DateTime? DeletedAt { get; set; } // Thời điểm chuyển vào thùng rác

        public DateTime CreatedAt { get; set; } = DateTime.Now; // Thời điểm tạo banner
    }
}

