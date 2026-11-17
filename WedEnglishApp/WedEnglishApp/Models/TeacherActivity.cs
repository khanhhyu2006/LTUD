using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.Models;
public class TeacherActivity
{
    [Key] public int ActivityId { get; set; }
    public int TeacherId { get; set; }
    [MaxLength(30)] public string Kind { get; set; } = "";
    [MaxLength(300)] public string Description { get; set; } = "";
    public DateTime OccurredAt { get; set; } = DateTime.Now;
    public Teacher Teacher { get; set; } = null!;
}
