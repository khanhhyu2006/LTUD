using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.ViewModels.Admin;

public class ClassScheduleInput
{
    public bool AllowKeepExisting { get; set; }
    [Required] public string SchedulePattern { get; set; } = string.Empty;
    [Required] public TimeSpan? StartTime { get; set; }
    [Required] public TimeSpan? EndTime { get; set; }
}
