using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.Models;
public class ConsultationMessage
{
    public int MessageId { get; set; }
    public int ConsultationId { get; set; }
    [StringLength(20)] public string SenderRole { get; set; } = "Customer";
    public int? SenderAccountId { get; set; }
    public UserAccount? SenderAccount { get; set; }
    [Required, StringLength(2000)] public string Body { get; set; } = string.Empty;
    public DateTime SentAt { get; set; } = DateTime.Now;
    public Consultation Consultation { get; set; } = null!;
}
