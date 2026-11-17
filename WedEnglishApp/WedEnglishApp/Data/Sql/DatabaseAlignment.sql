SET XACT_ABORT ON;
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
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Programs_Tuition') EXEC(N'ALTER TABLE dbo.Programs WITH CHECK ADD CONSTRAINT CK_Programs_Tuition CHECK (TuitionFee >= 0 AND DurationWeeks BETWEEN 1 AND 100)');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Classes_DatesCapacity') EXEC(N'ALTER TABLE dbo.Classes WITH CHECK ADD CONSTRAINT CK_Classes_DatesCapacity CHECK (EndDate >= StartDate AND MaxStudents BETWEEN 1 AND 100)');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Classes_Status') EXEC(N'ALTER TABLE dbo.Classes WITH CHECK ADD CONSTRAINT CK_Classes_Status CHECK (Status IN (''Planning'',''InProgress'',''Completed'',''Cancelled''))');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Registrations_Status') EXEC(N'ALTER TABLE dbo.Registrations WITH CHECK ADD CONSTRAINT CK_Registrations_Status CHECK (Status IN (''Pending'',''Confirmed'',''Cancelled'') AND (Status <> ''Confirmed'' OR ClassId IS NOT NULL))');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Registrations_Preferences') EXEC(N'ALTER TABLE dbo.Registrations WITH CHECK ADD CONSTRAINT CK_Registrations_Preferences CHECK ((PreferredDays IS NULL OR PreferredDays IN (''2,4,6'',''3,5,7'')) AND (PreferredSession IS NULL OR PreferredSession IN (''Morning'',''Afternoon'',''Evening'',''Any'')))');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_Payments_AmountStatus') EXEC(N'ALTER TABLE dbo.Payments WITH CHECK ADD CONSTRAINT CK_Payments_AmountStatus CHECK (Amount >= 0 AND Status IN (''Pending'',''Paid'',''Failed''))');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_ClassSchedules_DayTime') EXEC(N'ALTER TABLE dbo.ClassSchedules WITH CHECK ADD CONSTRAINT CK_ClassSchedules_DayTime CHECK (DayOfWeek BETWEEN 2 AND 8 AND StartTime < EndTime)');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_UserAccounts_Role') EXEC(N'ALTER TABLE dbo.UserAccounts WITH CHECK ADD CONSTRAINT CK_UserAccounts_Role CHECK (Role IN (''Admin'',''Teacher'',''Student''))');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_CourseFeedbacks_Rating') EXEC(N'ALTER TABLE dbo.CourseFeedbacks WITH CHECK ADD CONSTRAINT CK_CourseFeedbacks_Rating CHECK (Rating BETWEEN 1 AND 5)');
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name=N'CK_PlacementTests_Score') EXEC(N'ALTER TABLE dbo.PlacementTests WITH CHECK ADD CONSTRAINT CK_PlacementTests_Score CHECK (Score IS NULL OR Score BETWEEN 0 AND 10)');
IF NOT EXISTS(SELECT 1 FROM sys.key_constraints WHERE name='AK_Classes_ClassId_ProgramId')
    ALTER TABLE dbo.Classes ADD CONSTRAINT AK_Classes_ClassId_ProgramId UNIQUE(ClassId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_Registrations_Classes_ClassId_ProgramId')
    ALTER TABLE dbo.Registrations WITH CHECK ADD CONSTRAINT FK_Registrations_Classes_ClassId_ProgramId
        FOREIGN KEY(ClassId,ProgramId) REFERENCES dbo.Classes(ClassId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.Registrations') AND name='IX_Registrations_StudentId_ProgramId')
    CREATE INDEX IX_Registrations_StudentId_ProgramId ON dbo.Registrations(StudentId,ProgramId);
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.ClassSchedules') AND name='UX_ClassSchedules_Class_Day_Time')
    CREATE UNIQUE INDEX UX_ClassSchedules_Class_Day_Time ON dbo.ClassSchedules(ClassId,DayOfWeek,StartTime,EndTime);
EXEC(N'CREATE OR ALTER TRIGGER dbo.TR_Registrations_CourseFlow ON dbo.Registrations AFTER INSERT,UPDATE AS
BEGIN
 SET NOCOUNT ON;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.RegistrationId=d.RegistrationId
   WHERE d.RegistrationId IS NULL AND (i.DesiredTeacherId IS NOT NULL OR i.EarliestStartDate IS NULL
       OR i.PreferredDays IS NULL OR i.PreferredSession IS NULL OR i.Status<>''Pending'' OR i.ClassId IS NOT NULL))
   THROW 51001,N''Đơn mới phải đăng ký khóa học, có nguyện vọng lịch và chưa xếp lớp.'',1;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.RegistrationId=d.RegistrationId
   WHERE i.IsDeleted=0 AND i.Status<>''Cancelled''
     AND (d.RegistrationId IS NULL OR d.IsDeleted=1 OR d.Status=''Cancelled'' OR d.StudentId<>i.StudentId OR d.ProgramId<>i.ProgramId)
     AND (SELECT COUNT(*) FROM dbo.Registrations r WHERE r.StudentId=i.StudentId AND r.ProgramId=i.ProgramId AND r.IsDeleted=0 AND r.Status<>''Cancelled'')>1)
   THROW 51002,N''Học viên đã có đơn đăng ký khóa học này; không tạo thêm đơn trùng.'',1;
END');
EXEC(N'CREATE OR ALTER TRIGGER dbo.TR_Payments_CourseFlow ON dbo.Payments AFTER INSERT,UPDATE AS
BEGIN
 SET NOCOUNT ON;
 IF EXISTS(SELECT 1 FROM inserted i LEFT JOIN deleted d ON i.PaymentId=d.PaymentId
   WHERE (d.PaymentId IS NULL OR d.PaymentMethod<>i.PaymentMethod) AND i.PaymentMethod NOT IN(''Cash'',''VietQR''))
   THROW 51003,N''Đơn học phí mới chỉ dùng tiền mặt hoặc VietQR.'',1;
 IF EXISTS(SELECT 1 FROM inserted i JOIN deleted d ON i.PaymentId=d.PaymentId
   WHERE d.Status=''Paid'' AND (i.Status<>''Paid'' OR i.Amount<>d.Amount OR i.RegistrationId<>d.RegistrationId OR i.PaymentMethod<>d.PaymentMethod))
   THROW 51004,N''Không thay đổi khoản thu đã được xác nhận; giữ nguyên lịch sử học phí.'',1;
END');
COMMIT;
