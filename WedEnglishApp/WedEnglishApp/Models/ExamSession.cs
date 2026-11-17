using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc.ModelBinding.Validation;
namespace WedEnglishApp.Models;

public class ExamSession
{
    public int ExamSessionId { get; set; }
    [Required, StringLength(100)] public string Name { get; set; } = string.Empty;
    [Required, StringLength(100)] public string Room { get; set; } = string.Empty;
    [DataType(DataType.Date)] public DateTime ExamDate { get; set; } = DateTime.Today.AddDays(1);
    [DataType(DataType.Time)] public TimeSpan StartTime { get; set; } = TimeSpan.FromHours(9);
    [DataType(DataType.Time)] public TimeSpan EndTime { get; set; } = TimeSpan.FromHours(10);
    [Range(1,100)] public int Capacity { get; set; } = 20;
    public int? TeacherId { get; set; }
    [StringLength(30)] public string Status { get; set; } = "Planning";
    [ValidateNever] public Teacher? Teacher { get; set; }
    [ValidateNever] public List<PlacementTest> Tests { get; set; } = [];
}
