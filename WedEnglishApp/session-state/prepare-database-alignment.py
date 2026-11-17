from pathlib import Path
base=Path('WedEnglishApp')
script='''SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID('dbo.DatabaseAlignmentHistory','U') IS NULL
    CREATE TABLE dbo.DatabaseAlignmentHistory (
        AlignmentKey nvarchar(100) NOT NULL PRIMARY KEY,
        AppliedAt datetime2 NOT NULL,
        PreviousRegistrations nvarchar(max) NOT NULL,
        PreviousPayments nvarchar(max) NOT NULL,
        PreviousClasses nvarchar(max) NOT NULL,
        Summary nvarchar(max) NOT NULL);
DECLARE @Key nvarchar(100)=N'20261104_course_enrollment_v2';
IF NOT EXISTS(SELECT 1 FROM dbo.DatabaseAlignmentHistory WITH(UPDLOCK,HOLDLOCK) WHERE AlignmentKey=@Key)
BEGIN
    DECLARE @Registrations nvarchar(max)=(SELECT * FROM dbo.Registrations FOR JSON PATH,INCLUDE_NULL_VALUES);
    DECLARE @Payments nvarchar(max)=(SELECT * FROM dbo.Payments FOR JSON PATH,INCLUDE_NULL_VALUES);
    DECLARE @Classes nvarchar(max)=(SELECT * FROM dbo.Classes FOR JSON PATH,INCLUDE_NULL_VALUES);
    DECLARE @CancelledDuplicates int=0,@Unassigned int=0,@ClassStatuses int=0,@LegacyMethods int=0;
    -- Only unpaid pending duplicates are cancelled. Paid orders and receipts are retained.
    UPDATE r SET Status='Cancelled', ClassId=NULL,
        Notes=LEFT(CONCAT(CASE WHEN NULLIF(r.Notes,N'') IS NULL THEN N'' ELSE r.Notes+N' | ' END,
            N'Chuẩn hóa dữ liệu: đơn chờ trùng khóa đã có ghi danh được xác nhận; chưa thu học phí.'),500)
    FROM dbo.Registrations r JOIN dbo.Payments p ON p.RegistrationId=r.RegistrationId
    WHERE r.Status='Pending' AND r.IsDeleted=0 AND p.Status='Pending'
      AND EXISTS(SELECT 1 FROM dbo.Registrations other WHERE other.StudentId=r.StudentId AND other.ProgramId=r.ProgramId
          AND other.RegistrationId<>r.RegistrationId AND other.IsDeleted=0 AND other.Status='Confirmed');
    SET @CancelledDuplicates=@@ROWCOUNT;
    UPDATE r SET ClassId=NULL FROM dbo.Registrations r LEFT JOIN dbo.Payments p ON p.RegistrationId=r.RegistrationId
    WHERE r.Status IN('Pending','Cancelled') AND r.ClassId IS NOT NULL AND ISNULL(p.Status,'Pending')<>'Paid';
    SET @Unassigned=@@ROWCOUNT;
    UPDATE dbo.Classes SET Status=CASE WHEN CONVERT(date,EndDate)<CONVERT(date,GETDATE()) THEN 'Completed'
        WHEN CONVERT(date,StartDate)<=CONVERT(date,GETDATE()) THEN 'InProgress' ELSE 'Planning' END
    WHERE IsDeleted=0 AND Status IN('Planning','InProgress')
      AND Status<>CASE WHEN CONVERT(date,EndDate)<CONVERT(date,GETDATE()) THEN 'Completed'
        WHEN CONVERT(date,StartDate)<=CONVERT(date,GETDATE()) THEN 'InProgress' ELSE 'Planning' END;
    SET @ClassStatuses=@@ROWCOUNT;
    UPDATE p SET PaymentMethod='Cash',TransactionCode=NULL
    FROM dbo.Payments p JOIN dbo.Registrations r ON p.RegistrationId=r.RegistrationId
    WHERE p.Status='Pending' AND p.PaymentMethod IN('VNPay','MoMo') AND r.Status<>'Cancelled';
    SET @LegacyMethods=@@ROWCOUNT;
    INSERT dbo.DatabaseAlignmentHistory VALUES(@Key,SYSDATETIME(),@Registrations,@Payments,@Classes,
        (SELECT @CancelledDuplicates AS CancelledUnpaidDuplicates,@Unassigned AS ClearedPendingClasses,
                @ClassStatuses AS AlignedClassStatuses,@LegacyMethods AS ConvertedUnpaidDemoMethods FOR JSON PATH,WITHOUT_ARRAY_WRAPPER));
END;
'''
checks={
'Programs_Tuition':'dbo.Programs|TuitionFee >= 0 AND DurationWeeks BETWEEN 1 AND 100',
'Classes_DatesCapacity':'dbo.Classes|EndDate >= StartDate AND MaxStudents BETWEEN 1 AND 100',
'Classes_Status':'dbo.Classes|Status IN (\'Planning\',\'InProgress\',\'Completed\',\'Cancelled\')',
'Registrations_Status':'dbo.Registrations|Status IN (\'Pending\',\'Confirmed\',\'Cancelled\') AND (Status <> \'Confirmed\' OR ClassId IS NOT NULL)',
'Registrations_Preferences':'dbo.Registrations|(PreferredDays IS NULL OR PreferredDays IN (\'2,4,6\',\'3,5,7\')) AND (PreferredSession IS NULL OR PreferredSession IN (\'Morning\',\'Afternoon\',\'Evening\',\'Any\'))',
'Payments_AmountStatus':'dbo.Payments|Amount >= 0 AND Status IN (\'Pending\',\'Paid\',\'Failed\')',
'ClassSchedules_DayTime':'dbo.ClassSchedules|DayOfWeek BETWEEN 2 AND 8 AND StartTime < EndTime',
'UserAccounts_Role':'dbo.UserAccounts|Role IN (\'Admin\',\'Teacher\',\'Student\')',
'CourseFeedbacks_Rating':'dbo.CourseFeedbacks|Rating BETWEEN 1 AND 5',
'PlacementTests_Score':'dbo.PlacementTests|Score IS NULL OR Score BETWEEN 0 AND 10'
}
for key,definition in checks.items():
 table,predicate=definition.split('|');name='CK_'+key
 command=f'ALTER TABLE {table} WITH CHECK ADD CONSTRAINT {name} CHECK ({predicate})'
 script+=f"IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'{name}') EXEC(N'{command.replace(chr(39),chr(39)*2)}');\n"
script+='''IF NOT EXISTS(SELECT 1 FROM sys.key_constraints WHERE name='AK_Classes_ClassId_ProgramId')
    ALTER TABLE dbo.Classes ADD CONSTRAINT AK_Classes_ClassId_ProgramId UNIQUE(ClassId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_Registrations_Classes_ClassId_ProgramId')
    ALTER TABLE dbo.Registrations WITH CHECK ADD CONSTRAINT FK_Registrations_Classes_ClassId_ProgramId
        FOREIGN KEY(ClassId,ProgramId) REFERENCES dbo.Classes(ClassId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.Registrations') AND name='IX_Registrations_StudentId_ProgramId')
    CREATE INDEX IX_Registrations_StudentId_ProgramId ON dbo.Registrations(StudentId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.ClassSchedules') AND name='UX_ClassSchedules_Class_Day_Time')
    CREATE UNIQUE INDEX UX_ClassSchedules_Class_Day_Time ON dbo.ClassSchedules(ClassId,DayOfWeek,StartTime,EndTime);
'''
triggers={
'TR_Registrations_CourseFlow':'''CREATE OR ALTER TRIGGER dbo.TR_Registrations_CourseFlow ON dbo.Registrations AFTER INSERT,UPDATE AS
BEGIN
 SET NOCOUNT ON;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.RegistrationId=d.RegistrationId
   WHERE d.RegistrationId IS NULL AND (i.DesiredTeacherId IS NOT NULL OR i.EarliestStartDate IS NULL
       OR i.PreferredDays IS NULL OR i.PreferredSession IS NULL OR i.Status<>'Pending' OR i.ClassId IS NOT NULL))
   THROW 51001,N'Đơn mới phải đăng ký khóa học, có nguyện vọng lịch và chưa xếp lớp.',1;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.RegistrationId=d.RegistrationId
   WHERE i.IsDeleted=0 AND i.Status<>'Cancelled'
     AND (d.RegistrationId IS NULL OR d.IsDeleted=1 OR d.Status='Cancelled' OR d.StudentId<>i.StudentId OR d.ProgramId<>i.ProgramId)
     AND (SELECT COUNT(*) FROM dbo.Registrations r WHERE r.StudentId=i.StudentId AND r.ProgramId=i.ProgramId AND r.IsDeleted=0 AND r.Status<>'Cancelled')>1)
   THROW 51002,N'Học viên đã có đơn đăng ký khóa học này; không tạo thêm đơn trùng.',1;
END''',
'TR_Payments_CourseFlow':'''CREATE OR ALTER TRIGGER dbo.TR_Payments_CourseFlow ON dbo.Payments AFTER INSERT,UPDATE AS
BEGIN
 SET NOCOUNT ON;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.PaymentId=d.PaymentId
   WHERE (d.PaymentId IS NULL OR d.PaymentMethod<>i.PaymentMethod) AND i.PaymentMethod NOT IN('Cash','VietQR'))
   THROW 51003,N'Đơn học phí mới chỉ dùng tiền mặt hoặc VietQR.',1;
 IF EXISTS(SELECT 1 FROM inserted i JOIN deleted d ON i.PaymentId=d.PaymentId
   WHERE d.Status='Paid' AND (i.Status<>'Paid' OR i.Amount<>d.Amount OR i.RegistrationId<>d.RegistrationId OR i.PaymentMethod<>d.PaymentMethod))
   THROW 51004,N'Không thay đổi khoản thu đã được xác nhận; giữ nguyên lịch sử học phí.',1;
END'''
}
for sql in triggers.values():script+="EXEC(N'"+sql.replace("'","''")+"');\n"
script+='COMMIT;\n'
p=base/'Data/Sql/DatabaseAlignment.sql';p.write_text(script,encoding='utf8')
p=base/'Data/CourseEnrollmentSchema.cs';s=p.read_text(encoding='utf8');s=s.replace('    // Additive upgrade', '''    public static void AlignData(ApplicationDbContext context)
    {
        using var stream = typeof(CourseEnrollmentSchema).Assembly.GetManifestResourceStream("WedEnglishApp.Data.Sql.DatabaseAlignment.sql")!;
        using var reader = new StreamReader(stream);
        context.Database.ExecuteSqlRaw(reader.ReadToEnd());
    }

    // Additive upgrade''');p.write_text(s,encoding='utf8')
p=base/'WedEnglishApp.csproj';s=p.read_text(encoding='utf8').replace('<EmbeddedResource Include="Data/Sql/CourseEnrollment.sql" />','<EmbeddedResource Include="Data/Sql/CourseEnrollment.sql" />\n    <EmbeddedResource Include="Data/Sql/DatabaseAlignment.sql" />');p.write_text(s,encoding='utf8')
p=base/'Data/DbInitializer.cs';s=p.read_text(encoding='utf8');a=s.index('            // Fix Unicode encoding issue');b=s.index('            // Nếu đã có dữ liệu',a);s=s[:a]+s[b:];s=s.replace('            if (context.UserAccounts.Any())\n            {\n                return;','            if (context.UserAccounts.Any())\n            {\n                CourseEnrollmentSchema.AlignData(context);\n                return;')
s=s.replace('int classIdx = (s + c) % classes.Count;\n                    var assignedClass = classes[classIdx];\n                    var assignedProgram = programs.First(p => p.ProgramId == assignedClass.ProgramId);','var assignedProgram = programs[(s + c) % programs.Count];\n                    var assignedClass = classes.Where(cl => cl.ProgramId == assignedProgram.ProgramId).ElementAt(c % 2);')
s=s.replace('ClassId = assignedClass.ClassId,\n                        RegistrationDate','ClassId = regStatus == "Confirmed" ? assignedClass.ClassId : null,\n                        ProgramId = assignedProgram.ProgramId,\n                        EarliestStartDate = regStatus == "Confirmed" ? assignedClass.StartDate.Date : DateTime.Today.AddDays(7),\n                        PreferredDays = c % 2 == 0 ? "2,4,6" : "3,5,7",\n                        PreferredSession = "Evening",\n                        RegistrationDate')
s=s.replace('string payMethod = (regIndex % 2 == 0) ? "VNPay" : "Cash";', 'string payMethod = (regIndex % 2 == 0) ? "VietQR" : "Cash";')
a=s.index('        private static void FixTeacherSalaryNotes');s=s[:a]+'''    }
}
''';idx=s.rfind('        }');s=s[:idx]+'            CourseEnrollmentSchema.AlignData(context);\n'+s[idx:];p.write_text(s,encoding='utf8')
print('Prepared audited alignment and safe startup synchronization')
