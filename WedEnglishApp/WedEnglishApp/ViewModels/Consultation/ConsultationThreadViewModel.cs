namespace WedEnglishApp.ViewModels.Consultations;
public class ConsultationThreadViewModel
{
    public WedEnglishApp.Models.Consultation Conversation { get; set; } = null!;
    public bool IsAdmin { get; set; }
    public string FeedUrl { get; set; } = "";
    public string SendUrl { get; set; } = "";
    public string ReadUrl { get; set; } = "";
    public string? RecoveryUrl { get; set; }
}
