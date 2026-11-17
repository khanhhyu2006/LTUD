using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;
public static class ExamSessionSchema
{
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(ExamSessionSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.ExamSessions.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
