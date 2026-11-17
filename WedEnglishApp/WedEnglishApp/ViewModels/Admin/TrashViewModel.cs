// =================================================================================================
// VIEWMODEL: TrashViewModel.cs - DỮ LIỆU HIỂN THỊ TRÊN TRANG THÙNG RÁC (ADMIN)
// Mục đích: Gom tất cả bản ghi đã xóa mềm từ nhiều bảng để hiển thị trên 1 trang duy nhất
// =================================================================================================

using WedEnglishApp.Models;

namespace WedEnglishApp.ViewModels.Admin
{
    public class TrashViewModel
    {
        public string ActiveTab { get; set; } = "all"; // Tab đang được chọn hiển thị

        // Danh sách các bản ghi đã xóa mềm từ từng bảng
        public List<Banner> DeletedBanners { get; set; } = new();
        public List<CourseProgram> DeletedPrograms { get; set; } = new();
        public List<CourseClass> DeletedClasses { get; set; } = new();
        public List<Consultation> DeletedConsultations { get; set; } = new();
        public List<Registration> DeletedRegistrations { get; set; } = new();
        public List<PlacementTest> DeletedPlacementTests { get; set; } = new();
        public List<UserAccount> DeletedUserAccounts { get; set; } = new();

        // Tổng số mục trong thùng rác
        public int TotalItems =>
            DeletedBanners.Count + DeletedPrograms.Count + DeletedClasses.Count +
            DeletedConsultations.Count + DeletedRegistrations.Count +
            DeletedPlacementTests.Count + DeletedUserAccounts.Count;
    }
}
