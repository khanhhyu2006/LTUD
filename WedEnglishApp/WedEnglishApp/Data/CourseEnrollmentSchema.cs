using Microsoft.EntityFrameworkCore;
namespace WedEnglishApp.Data;

public static class CourseEnrollmentSchema
{
    public static void AlignData(ApplicationDbContext context)
    {
        using var stream = typeof(CourseEnrollmentSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.DatabaseAlignment.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }

    // Additive upgrade for databases created through the existing EnsureCreated initializer.
    public static void Upgrade(ApplicationDbContext context)
    {
        using var stream = typeof(CourseEnrollmentSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.CourseEnrollment.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }
}
