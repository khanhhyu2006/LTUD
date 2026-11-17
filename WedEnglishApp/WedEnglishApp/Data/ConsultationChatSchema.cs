using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;
public static class ConsultationChatSchema
{
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(ConsultationChatSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.ConsultationChat.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
