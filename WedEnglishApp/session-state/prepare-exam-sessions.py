from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
w('Models/ExamSession.cs','''using System.ComponentModel.DataAnnotations;
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
''')
s=r('Models/PlacementTest.cs');s=s.replace('        public DateTime TestDate', '''        public int? ExamSessionId { get; set; }
        [ForeignKey(nameof(ExamSessionId))]
        public virtual ExamSession? ExamSession { get; set; }
        public DateTime? RequestedDate { get; set; }
        [StringLength(20)] public string? RequestedTime { get; set; }

        public DateTime TestDate''');s=s.replace('public string? Room { get; set; } = "Phòng Khảo Thí 101";', 'public string? Room { get; set; }');w('Models/PlacementTest.cs',s)
s=r('Data/ApplicationDbContext.cs');s=s.replace('        public DbSet<PlacementTest> PlacementTests', '        public DbSet<ExamSession> ExamSessions => Set<ExamSession>();\n        public DbSet<PlacementTest> PlacementTests');at=s.index('            // Cấu hình 9:');s=s[:at]+'''            modelBuilder.Entity<ExamSession>().HasIndex(s => s.Name).IsUnique();
            modelBuilder.Entity<ExamSession>().HasOne(s => s.Teacher).WithMany()
                .HasForeignKey(s => s.TeacherId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<PlacementTest>().HasOne(t => t.ExamSession).WithMany(s => s.Tests)
                .HasForeignKey(t => t.ExamSessionId).OnDelete(DeleteBehavior.Restrict);

'''+s[at:];w('Data/ApplicationDbContext.cs',s)
w('Data/Sql/ExamSessions.sql',"""SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID('dbo.ExamSessions','U') IS NULL
 CREATE TABLE dbo.ExamSessions(
 ExamSessionId int IDENTITY NOT NULL CONSTRAINT PK_ExamSessions PRIMARY KEY,
 Name nvarchar(100) NOT NULL, Room nvarchar(100) NOT NULL, ExamDate datetime2 NOT NULL,
 StartTime time NOT NULL, EndTime time NOT NULL, Capacity int NOT NULL, TeacherId int NULL,
 Status nvarchar(30) NOT NULL,
 CONSTRAINT FK_ExamSessions_Teachers_TeacherId FOREIGN KEY(TeacherId) REFERENCES dbo.Teachers(TeacherId));
IF COL_LENGTH('dbo.PlacementTests','ExamSessionId') IS NULL ALTER TABLE dbo.PlacementTests ADD ExamSessionId int NULL;
IF COL_LENGTH('dbo.PlacementTests','RequestedDate') IS NULL ALTER TABLE dbo.PlacementTests ADD RequestedDate datetime2 NULL;
IF COL_LENGTH('dbo.PlacementTests','RequestedTime') IS NULL ALTER TABLE dbo.PlacementTests ADD RequestedTime nvarchar(20) NULL;
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_PlacementTests_ExamSessions_ExamSessionId')
 EXEC(N'ALTER TABLE dbo.PlacementTests ADD CONSTRAINT FK_PlacementTests_ExamSessions_ExamSessionId FOREIGN KEY(ExamSessionId) REFERENCES dbo.ExamSessions(ExamSessionId)');
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.ExamSessions') AND name='IX_ExamSessions_Name')
 CREATE UNIQUE INDEX IX_ExamSessions_Name ON dbo.ExamSessions(Name);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.PlacementTests') AND name='IX_PlacementTests_ExamSessionId')
 EXEC(N'CREATE INDEX IX_PlacementTests_ExamSessionId ON dbo.PlacementTests(ExamSessionId)');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name='CK_ExamSessions_TimeCapacity')
 ALTER TABLE dbo.ExamSessions ADD CONSTRAINT CK_ExamSessions_TimeCapacity CHECK(StartTime<EndTime AND Capacity BETWEEN 1 AND 100);
-- Preserve legacy appointments and scores, grouping only records that were already assigned or completed.
EXEC(N'
SELECT CONVERT(date,TestDate) AS ExamDate,TRY_CONVERT(time(0),TestTime) AS StartTime,
 COALESCE(NULLIF(Room,N''''),N''Phòng thi cũ'') AS Room,EvaluatedByTeacherId AS TeacherId,MIN(TestId) AS FirstTestId,
 COUNT(*) AS TestCount,SUM(CASE WHEN Status=''Completed'' THEN 1 ELSE 0 END) AS Graded
INTO #LegacyExamGroups FROM dbo.PlacementTests
WHERE ExamSessionId IS NULL AND IsDeleted=0 AND (Status=''Completed'' OR EvaluatedByTeacherId IS NOT NULL)
 AND TRY_CONVERT(time(0),TestTime) IS NOT NULL AND TRY_CONVERT(time(0),TestTime)<''23:00''
GROUP BY CONVERT(date,TestDate),TRY_CONVERT(time(0),TestTime),COALESCE(NULLIF(Room,N''''),N''Phòng thi cũ''),EvaluatedByTeacherId;
INSERT dbo.ExamSessions(Name,Room,ExamDate,StartTime,EndTime,Capacity,TeacherId,Status)
SELECT CONCAT(N''KT-CU-'',g.FirstTestId),g.Room,g.ExamDate,g.StartTime,DATEADD(minute,45,g.StartTime),
 CASE WHEN g.TestCount>20 THEN g.TestCount ELSE 20 END,g.TeacherId,CASE WHEN g.Graded=g.TestCount THEN ''Completed'' ELSE ''InProgress'' END
FROM #LegacyExamGroups g WHERE NOT EXISTS(SELECT 1 FROM dbo.ExamSessions s WHERE s.Name=CONCAT(N''KT-CU-'',g.FirstTestId));
UPDATE t SET ExamSessionId=s.ExamSessionId
FROM dbo.PlacementTests t JOIN #LegacyExamGroups g ON CONVERT(date,t.TestDate)=g.ExamDate
 AND TRY_CONVERT(time(0),t.TestTime)=g.StartTime AND COALESCE(NULLIF(t.Room,N''''),N''Phòng thi cũ'')=g.Room
 AND (t.EvaluatedByTeacherId=g.TeacherId OR t.EvaluatedByTeacherId IS NULL AND g.TeacherId IS NULL)
JOIN dbo.ExamSessions s ON s.Name=CONCAT(N''KT-CU-'',g.FirstTestId)
WHERE t.ExamSessionId IS NULL AND t.IsDeleted=0 AND (t.Status=''Completed'' OR t.EvaluatedByTeacherId IS NOT NULL);
DROP TABLE #LegacyExamGroups;
');
COMMIT;
""")
w('Data/ExamSessionSchema.cs','''using Microsoft.EntityFrameworkCore;
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
''')
s=r('Data/DbInitializer.cs').replace('            CourseEnrollmentSchema.Upgrade(context);','            CourseEnrollmentSchema.Upgrade(context);\n            ExamSessionSchema.Upgrade(context);');# seed legacy tests get grouped after initial seed
s=s.replace('            CourseEnrollmentSchema.AlignData(context);\n        }','            CourseEnrollmentSchema.AlignData(context);\n            ExamSessionSchema.Upgrade(context);\n        }');w('Data/DbInitializer.cs',s)
s=r('WedEnglishApp.csproj').replace('<EmbeddedResource Include="Data/Sql/DatabaseAlignment.sql" />','<EmbeddedResource Include="Data/Sql/DatabaseAlignment.sql" />\n    <EmbeddedResource Include="Data/Sql/ExamSessions.sql" />');w('WedEnglishApp.csproj',s)
w('Services/ExamSessionPlanner.cs',r'''using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public static class ExamSessionPlanner
{
    public static async Task<string?> ValidateAsync(ApplicationDbContext context, ExamSession session)
    {
        if (session.ExamDate.Date < DateTime.Today || session.StartTime < TimeSpan.Zero || session.StartTime >= session.EndTime || session.EndTime >= TimeSpan.FromDays(1))
            return "Chọn ngày thi từ hôm nay và giờ kết thúc sau giờ bắt đầu.";
        if (session.TeacherId.HasValue && !await context.Teachers.AnyAsync(t => t.TeacherId == session.TeacherId && t.UserAccount.IsActive && !t.UserAccount.IsDeleted))
            return "Giáo viên không tồn tại hoặc đã ngừng hoạt động.";
        if (await context.ExamSessions.AnyAsync(s => s.ExamSessionId != session.ExamSessionId && s.Name == session.Name)) return "Mã lớp thi đã tồn tại.";
        var others = await context.ExamSessions.Where(s => s.ExamSessionId != session.ExamSessionId && s.Status != "Cancelled" && s.ExamDate.Date == session.ExamDate.Date && s.StartTime < session.EndTime && session.StartTime < s.EndTime).ToListAsync();
        if (others.Any(s => string.Equals(s.Room.Trim(), session.Room.Trim(), StringComparison.OrdinalIgnoreCase))) return "Phòng đã có ca thi trong khoảng giờ này.";
        if (session.TeacherId.HasValue && others.Any(s => s.TeacherId == session.TeacherId)) return "Giáo viên đã được phân công ca thi trùng giờ.";
        var day = session.ExamDate.DayOfWeek == DayOfWeek.Sunday ? 8 : (int)session.ExamDate.DayOfWeek + 1;
        var classes = await context.Classes.Include(c => c.Schedules).Where(c => !c.IsDeleted && c.Status != "Cancelled" && c.Status != "Completed" && c.StartDate.Date <= session.ExamDate.Date && c.EndDate.Date >= session.ExamDate.Date).ToListAsync();
        var overlap = classes.Where(c => c.Schedules.Any(s => s.DayOfWeek == day && s.StartTime < session.EndTime && session.StartTime < s.EndTime));
        if (overlap.Any(c => string.Equals(c.Room.Trim(), session.Room.Trim(), StringComparison.OrdinalIgnoreCase))) return "Phòng đang có lớp học trong giờ thi.";
        if (session.TeacherId.HasValue && overlap.Any(c => c.TeacherId == session.TeacherId)) return "Giáo viên đang có lịch giảng dạy trong giờ thi.";
        return null;
    }

    public static void CopySchedule(PlacementTest test, ExamSession session)
    {
        test.ExamSessionId = session.ExamSessionId;
        test.TestDate = session.ExamDate.Date;
        test.TestTime = session.StartTime.ToString(@"hh\:mm");
        test.Room = session.Room;
        test.EvaluatedByTeacherId = session.TeacherId;
    }
}
'''.replace('@"hh\\:mm"','@"hh\:mm"'))
print('Exam session schema and shared scheduling rules prepared')
