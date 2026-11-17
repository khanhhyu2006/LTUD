namespace WedEnglishApp.ViewModels.Reports;
public record MonthSummary(int Month, decimal Amount, int Receipts);
public record ProgramSummary(string Name, int Count);
public record ReceiptSummary(int Id, DateTime Date, string Program, decimal Amount, bool LegacyDate);
public class AdminReportViewModel
{
    public int Year { get; set; }
    public List<MonthSummary> Months { get; set; } = [];
    public List<ProgramSummary> Programs { get; set; } = [];
    public List<ReceiptSummary> Receipts { get; set; } = [];
    public decimal Revenue => Months.Sum(m => m.Amount);
}
public record ClassSummary(string Name, string Program, string Room, string Status, int Students, int Documents, int Published);
public record TestSummary(int Id, string Student, DateTime Date, decimal? Score, string? Level, string Status);
public class TeacherReportViewModel
{
    public string TeacherName { get; set; } = "";
    public DateTime From { get; set; }
    public DateTime To { get; set; }
    public List<ClassSummary> Classes { get; set; } = [];
    public List<TestSummary> Tests { get; set; } = [];
    public int ActivityCount { get; set; }
    public int Graded => Tests.Count(t => t.Status == "Completed" && t.Score.HasValue);
    public decimal? AverageScore => Tests.Where(t => t.Status == "Completed" && t.Score.HasValue).Select(t => t.Score).DefaultIfEmpty().Average();
}
