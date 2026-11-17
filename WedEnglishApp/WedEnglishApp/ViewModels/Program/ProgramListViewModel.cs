using WedEnglishApp.Models;

namespace WedEnglishApp.ViewModels.Program
{
    public class ProgramListViewModel
    {
        public List<CourseProgram> Programs { get; set; } = new();
        public string? SearchTerm { get; set; }
        public string? SelectedLevel { get; set; }
        public decimal? MinFee { get; set; }
        public decimal? MaxFee { get; set; }
        public int CurrentPage { get; set; } = 1;
        public int TotalPages { get; set; } = 1;
        public int PageSize { get; set; } = 6;
        public int TotalItems { get; set; }
    }
}
