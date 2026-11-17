using WedEnglishApp.Models;

namespace WedEnglishApp.ViewModels.Home
{
    public class HomeViewModel
    {
        public List<TopStudentViewModel> TopTestStudents { get; set; } = new List<TopStudentViewModel>();
        public List<Banner> Banners { get; set; } = new(); // Danh sách banner động từ cơ sở dữ liệu
        public List<CourseProgram> FeaturedPrograms { get; set; } = new();
        public List<CourseClass> UpcomingClasses { get; set; } = new();
        public List<Teacher> FeaturedTeachers { get; set; } = new();
        public int TotalPrograms { get; set; }
        public int TotalStudents { get; set; }
        public int TotalClasses { get; set; }
        public int TotalTeachers { get; set; }
    }
}
