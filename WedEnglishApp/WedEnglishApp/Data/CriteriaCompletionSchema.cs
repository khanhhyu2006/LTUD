using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;
public static class CriteriaCompletionSchema
{
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(CriteriaCompletionSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.CriteriaCompletion.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
