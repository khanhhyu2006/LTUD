from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
s=r('Models/Consultation.cs').replace('        public DateTime CreatedAt', '''        public int? OwnerAccountId { get; set; }
        [ForeignKey(nameof(OwnerAccountId))] public virtual UserAccount? OwnerAccount { get; set; }
        [StringLength(64)] public string? GuestAccessHash { get; set; }
        public DateTime LastMessageAt { get; set; } = DateTime.Now;
        public int AdminLastReadMessageId { get; set; }
        public int CustomerLastReadMessageId { get; set; }
        public virtual List<ConsultationMessage> Messages { get; set; } = [];

        public DateTime CreatedAt''');w('Models/Consultation.cs',s)
w('Models/ConsultationMessage.cs','''using System.ComponentModel.DataAnnotations;
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
''')
s=r('Data/ApplicationDbContext.cs');s=s.replace('        public DbSet<Consultation> Consultations', '        public DbSet<ConsultationMessage> ConsultationMessages => Set<ConsultationMessage>();\n        public DbSet<Consultation> Consultations');at=s.index('            // Cấu hình 9:');s=s[:at]+'''            modelBuilder.Entity<Consultation>().HasOne(c => c.OwnerAccount).WithMany()
                .HasForeignKey(c => c.OwnerAccountId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<ConsultationMessage>().HasKey(m => m.MessageId);
            modelBuilder.Entity<ConsultationMessage>().HasOne(m => m.Consultation).WithMany(c => c.Messages)
                .HasForeignKey(m => m.ConsultationId).OnDelete(DeleteBehavior.Cascade);
            modelBuilder.Entity<ConsultationMessage>().HasOne(m => m.SenderAccount).WithMany()
                .HasForeignKey(m => m.SenderAccountId).OnDelete(DeleteBehavior.Restrict);
            modelBuilder.Entity<ConsultationMessage>().HasIndex(m => new { m.ConsultationId, m.MessageId });

'''+s[at:];w('Data/ApplicationDbContext.cs',s)
w('Data/Sql/ConsultationChat.sql','''SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH('dbo.Consultations','OwnerAccountId') IS NULL ALTER TABLE dbo.Consultations ADD OwnerAccountId int NULL;
IF COL_LENGTH('dbo.Consultations','GuestAccessHash') IS NULL ALTER TABLE dbo.Consultations ADD GuestAccessHash nvarchar(64) NULL;
IF COL_LENGTH('dbo.Consultations','LastMessageAt') IS NULL
BEGIN
 ALTER TABLE dbo.Consultations ADD LastMessageAt datetime2 NULL;
 EXEC(N'UPDATE dbo.Consultations SET LastMessageAt=CreatedAt WHERE LastMessageAt IS NULL');
 ALTER TABLE dbo.Consultations ALTER COLUMN LastMessageAt datetime2 NOT NULL;
END;
IF COL_LENGTH('dbo.Consultations','AdminLastReadMessageId') IS NULL ALTER TABLE dbo.Consultations ADD AdminLastReadMessageId int NOT NULL CONSTRAINT DF_Consultations_AdminLastRead DEFAULT 0;
IF COL_LENGTH('dbo.Consultations','CustomerLastReadMessageId') IS NULL ALTER TABLE dbo.Consultations ADD CustomerLastReadMessageId int NOT NULL CONSTRAINT DF_Consultations_CustomerLastRead DEFAULT 0;
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_Consultations_UserAccounts_OwnerAccountId')
 EXEC(N'ALTER TABLE dbo.Consultations ADD CONSTRAINT FK_Consultations_UserAccounts_OwnerAccountId FOREIGN KEY(OwnerAccountId) REFERENCES dbo.UserAccounts(AccountId)');
IF OBJECT_ID('dbo.ConsultationMessages','U') IS NULL
 CREATE TABLE dbo.ConsultationMessages(
 MessageId int IDENTITY NOT NULL CONSTRAINT PK_ConsultationMessages PRIMARY KEY,
 ConsultationId int NOT NULL,SenderRole nvarchar(20) NOT NULL,SenderAccountId int NULL,
 Body nvarchar(2000) NOT NULL,SentAt datetime2 NOT NULL,
 CONSTRAINT FK_ConsultationMessages_Consultations_ConsultationId FOREIGN KEY(ConsultationId) REFERENCES dbo.Consultations(ConsultationId) ON DELETE CASCADE,
 CONSTRAINT FK_ConsultationMessages_UserAccounts_SenderAccountId FOREIGN KEY(SenderAccountId) REFERENCES dbo.UserAccounts(AccountId));
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.ConsultationMessages') AND name='IX_ConsultationMessages_ConsultationId_MessageId')
 CREATE INDEX IX_ConsultationMessages_ConsultationId_MessageId ON dbo.ConsultationMessages(ConsultationId,MessageId);
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name='CK_ConsultationMessages_Sender')
 ALTER TABLE dbo.ConsultationMessages ADD CONSTRAINT CK_ConsultationMessages_Sender CHECK(SenderRole IN('Customer','Admin'));
INSERT dbo.ConsultationMessages(ConsultationId,SenderRole,SenderAccountId,Body,SentAt)
SELECT c.ConsultationId,'Customer',NULL,c.Question,c.CreatedAt FROM dbo.Consultations c
WHERE NOT EXISTS(SELECT 1 FROM dbo.ConsultationMessages m WHERE m.ConsultationId=c.ConsultationId);
COMMIT;
''')
w('Data/ConsultationChatSchema.cs','''using Microsoft.EntityFrameworkCore;
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
''')
s=r('Data/DbInitializer.cs');s=s.replace('            ExamSessionSchema.Upgrade(context);','            ExamSessionSchema.Upgrade(context);\n            ConsultationChatSchema.Upgrade(context);');w('Data/DbInitializer.cs',s)
s=r('WedEnglishApp.csproj').replace('<EmbeddedResource Include="Data/Sql/ExamSessions.sql" />','<EmbeddedResource Include="Data/Sql/ExamSessions.sql" />\n    <EmbeddedResource Include="Data/Sql/ConsultationChat.sql" />');w('WedEnglishApp.csproj',s)
w('ViewModels/Consultation/StartConsultationViewModel.cs',r'''using System.ComponentModel.DataAnnotations;
namespace WedEnglishApp.ViewModels.Consultation;
public class StartConsultationViewModel
{
    [Required(ErrorMessage="Nhập họ và tên."), StringLength(100)] public string ContactName { get; set; } = "";
    [Required(ErrorMessage="Nhập email liên hệ."), EmailAddress, StringLength(100)] public string ContactEmail { get; set; } = "";
    [Required(ErrorMessage="Nhập số điện thoại."), StringLength(20), RegularExpression(@"^[0-9+() -]{7,20}$", ErrorMessage="Số điện thoại không hợp lệ.")]
    public string PhoneNumber { get; set; } = "";
    [Required(ErrorMessage="Nhập câu hỏi cần tư vấn."), StringLength(1000)] public string Question { get; set; } = "";
    public bool IsStudent { get; set; }
}
''')
w('ViewModels/Consultation/ConsultationThreadViewModel.cs','''namespace WedEnglishApp.ViewModels.Consultation;
public class ConsultationThreadViewModel
{
    public WedEnglishApp.Models.Consultation Conversation { get; set; } = null!;
    public bool IsAdmin { get; set; }
    public string FeedUrl { get; set; } = "";
    public string SendUrl { get; set; } = "";
    public string ReadUrl { get; set; } = "";
    public string? RecoveryUrl { get; set; }
}
''')
w('Services/ConsultationAccess.cs','''using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public class ConsultationAccess(ApplicationDbContext context)
{
    public async Task<UserAccount?> StudentAsync(HttpContext http)
    {
        var auth = await http.AuthenticateAsync("StudentCookie");
        if (!auth.Succeeded || !int.TryParse(auth.Principal?.FindFirstValue(ClaimTypes.NameIdentifier), out var id)) return null;
        return await context.UserAccounts.Include(u => u.Student).FirstOrDefaultAsync(u => u.AccountId == id && u.Role == "Student" && u.IsActive && !u.IsDeleted);
    }
    public static string CookieName(int id) => $"HITC.Consultation.{id}";
    public static string Token() => WebEncoders.Base64UrlEncode(RandomNumberGenerator.GetBytes(32));
    public static string Hash(string token) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(token)));
    public static bool Matches(string? hash, string? token)
    {
        if (hash?.Length != 64 || string.IsNullOrEmpty(token) || token.Length > 200) return false;
        try { return CryptographicOperations.FixedTimeEquals(Convert.FromHexString(hash), SHA256.HashData(Encoding.UTF8.GetBytes(token))); }
        catch (FormatException) { return false; }
    }
    public static void Remember(HttpContext http, int id, string token) => http.Response.Cookies.Append(CookieName(id), token,
        new CookieOptions { HttpOnly=true, Secure=http.Request.IsHttps, SameSite=SameSiteMode.Lax, Path="/Consultation", Expires=DateTimeOffset.UtcNow.AddDays(30), IsEssential=true });
    public async Task<bool> CanReadAsync(HttpContext http, Consultation conversation)
    {
        if (conversation.IsDeleted) return false;
        if (conversation.OwnerAccountId.HasValue) return (await StudentAsync(http))?.AccountId == conversation.OwnerAccountId.Value;
        return Matches(conversation.GuestAccessHash, http.Request.Cookies[CookieName(conversation.ConsultationId)]);
    }
}
''')
s=r('Program.cs').replace('builder.Services.AddControllersWithViews();','builder.Services.AddControllersWithViews();\nbuilder.Services.AddScoped<WedEnglishApp.Services.ConsultationAccess>();');s=s.replace('|| path.StartsWithSegments("/PlacementTest", StringComparison.OrdinalIgnoreCase))','|| path.StartsWithSegments("/PlacementTest", StringComparison.OrdinalIgnoreCase)\n                    || path.StartsWithSegments("/Consultation", StringComparison.OrdinalIgnoreCase))');w('Program.cs',s)
print('Two-way consultation schema, scoped access and view models prepared')
