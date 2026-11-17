namespace WedEnglishApp.ViewModels.Home
{
    public class TopStudentViewModel
    {
        public string StudentName { get; set; } = string.Empty;
        public string? AvatarUrl { get; set; }
        public double Score { get; set; }
        public string TestName { get; set; } = string.Empty;
        public string? TargetCourse { get; set; }
    }
}