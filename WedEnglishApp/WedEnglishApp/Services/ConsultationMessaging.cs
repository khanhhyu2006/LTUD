using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public static class ConsultationMessaging
{
    public static string? Validate(Consultation conversation, string? body)
    {
        if (conversation.Status == "Closed") return "Cuộc tư vấn đã kết thúc. Vui lòng tạo yêu cầu mới hoặc chờ Admin mở lại.";
        if (string.IsNullOrWhiteSpace(body) || body.Trim().Length > 2000) return "Tin nhắn cần từ 1 đến 2000 ký tự.";
        return null;
    }
    public static async Task<bool> AddAsync(ApplicationDbContext context, Consultation conversation, string body, bool isAdmin, int? accountId)
    {
        await using var transaction = await context.Database.BeginTransactionAsync();
        var updated = await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && !c.IsDeleted && c.Status != "Closed")
            .ExecuteUpdateAsync(update => update.SetProperty(c => c.Status, isAdmin ? "Replied" : "Pending").SetProperty(c => c.LastMessageAt, DateTime.Now));
        if (updated == 0) return false;
        context.ConsultationMessages.Add(new ConsultationMessage
        {
            ConsultationId = conversation.ConsultationId, Body = body.Trim(),
            SenderRole = isAdmin ? "Admin" : "Customer", SenderAccountId = accountId, SentAt = DateTime.Now
        });
        await context.SaveChangesAsync();
        await transaction.CommitAsync();
        return true;
    }
    public static async Task<object> FeedAsync(ApplicationDbContext context, Consultation conversation, int afterId)
    {
        var messages = await context.ConsultationMessages.Where(m => m.ConsultationId == conversation.ConsultationId && m.MessageId > afterId)
            .OrderBy(m => m.MessageId).Take(100).Select(m => new { id=m.MessageId, body=m.Body, isAdmin=m.SenderRole=="Admin", sentAt=m.SentAt }).ToListAsync();
        return new { status=conversation.Status, messages };
    }
    public static async Task MarkReadAsync(ApplicationDbContext context, Consultation conversation, int lastMessageId, bool isAdmin)
    {
        var bounded = await context.ConsultationMessages.Where(m => m.ConsultationId == conversation.ConsultationId && m.MessageId <= lastMessageId).MaxAsync(m => (int?)m.MessageId) ?? 0;
        if (isAdmin)
            await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && c.AdminLastReadMessageId < bounded).ExecuteUpdateAsync(s => s.SetProperty(c => c.AdminLastReadMessageId, bounded));
        else
            await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && c.CustomerLastReadMessageId < bounded).ExecuteUpdateAsync(s => s.SetProperty(c => c.CustomerLastReadMessageId, bounded));
    }
}
