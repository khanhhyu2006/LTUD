param([ValidateSet('Fixture','Inspect','ResetDocuments')][string]$Mode='Inspect')
$ErrorActionPreference='Stop'
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=EnglishCenterCriteriaTest;Integrated Security=true;TrustServerCertificate=true');$c.Open()
try {
$q=$c.CreateCommand();$q.CommandTimeout=90
if($Mode -eq 'ResetDocuments'){$q.CommandText="DELETE d FROM ClassDocuments d JOIN Classes c ON c.ClassId=d.ClassId JOIN Programs p ON p.ProgramId=c.ProgramId WHERE p.ProgramName=N'Criteria workflow test'";$null=$q.ExecuteNonQuery()}
if($Mode -eq 'Fixture'){
$q.CommandText=@'
SET XACT_ABORT ON;BEGIN TRANSACTION;
DECLARE @ta int=(SELECT TeacherId FROM Teachers t JOIN UserAccounts u ON u.AccountId=t.AccountId WHERE u.Email='criteria.teacher.a@example.test');
DECLARE @tb int=(SELECT TeacherId FROM Teachers t JOIN UserAccounts u ON u.AccountId=t.AccountId WHERE u.Email='criteria.teacher.b@example.test');
DECLARE @sa int=(SELECT StudentId FROM Students s JOIN UserAccounts u ON u.AccountId=s.AccountId WHERE u.Email='criteria.student.a@example.test');
DECLARE @sb int=(SELECT StudentId FROM Students s JOIN UserAccounts u ON u.AccountId=s.AccountId WHERE u.Email='criteria.student.b@example.test');
IF @ta IS NULL OR @tb IS NULL OR @sa IS NULL OR @sb IS NULL THROW 51000,'Test accounts missing',1;
IF EXISTS(SELECT 1 FROM Programs WHERE ProgramName=N'Criteria workflow test') THROW 51000,'Fixtures already exist',1;
INSERT Programs(ProgramName,Level,DurationWeeks,TuitionFee,Description,IsActive,CreatedAt,IsDeleted)VALUES(N'Criteria workflow test','Beginner',12,500000,N'Isolated criteria test',1,GETDATE(),0);
DECLARE @p int=SCOPE_IDENTITY();
INSERT Classes(ProgramId,TeacherId,ClassName,Room,MaxStudents,StartDate,EndDate,Status,IsDeleted)VALUES(@p,@ta,N'=2+2',N'Criteria-A',20,CAST(GETDATE() AS date),DATEADD(day,84,GETDATE()),'Planning',0);
DECLARE @ca int=SCOPE_IDENTITY();
INSERT Classes(ProgramId,TeacherId,ClassName,Room,MaxStudents,StartDate,EndDate,Status,IsDeleted)VALUES(@p,@tb,N'Criteria class B',N'Criteria-B',20,CAST(GETDATE() AS date),DATEADD(day,84,GETDATE()),'Planning',0);
INSERT Registrations(StudentId,ProgramId,ClassId,RegistrationDate,Status,IsDeleted,EarliestStartDate,PreferredSession,PreferredDays)VALUES(@sa,@p,NULL,GETDATE(),'Pending',0,CAST(GETDATE() AS date),'Any','2,4,6');
DECLARE @r int=SCOPE_IDENTITY(); UPDATE Registrations SET ClassId=@ca,Status='Confirmed' WHERE RegistrationId=@r;
INSERT Payments(RegistrationId,Amount,PaymentDate,PaymentMethod,Status) VALUES(@r,500000,'2025-12-31','Cash','Pending');
INSERT ExamSessions(Name,Room,ExamDate,StartTime,EndTime,Capacity,TeacherId,Status)VALUES(N'Criteria exam A',N'Criteria-Exam',CAST(GETDATE() AS date),'08:00','09:00',20,@ta,'Planning');
DECLARE @e int=SCOPE_IDENTITY();
INSERT PlacementTests(StudentId,ExamSessionId,EvaluatedByTeacherId,TestDate,TestTime,Room,Status,IsDeleted,RequestedDate,RequestedTime)VALUES(@sa,@e,@ta,CAST(GETDATE() AS date),'08:00',N'Criteria-Exam','Pending',0,CAST(GETDATE() AS date),'08:00');
COMMIT;
'@
$null=$q.ExecuteNonQuery()
}
$q.CommandText=@'
SELECT JSON_QUERY((SELECT t.TeacherId,u.Email FROM Teachers t JOIN UserAccounts u ON u.AccountId=t.AccountId WHERE u.Email LIKE 'criteria.teacher.%' FOR JSON PATH)) teachers,
JSON_QUERY((SELECT s.StudentId,u.Email FROM Students s JOIN UserAccounts u ON u.AccountId=s.AccountId WHERE u.Email LIKE 'criteria.student.%' FOR JSON PATH)) students,
JSON_QUERY((SELECT c.ClassId,c.TeacherId,c.ClassName FROM Classes c JOIN Programs p ON p.ProgramId=c.ProgramId WHERE p.ProgramName=N'Criteria workflow test' FOR JSON PATH)) classes,
JSON_QUERY((SELECT p.PaymentId,p.Amount,p.Status,p.ConfirmedAt,r.ClassId FROM Payments p JOIN Registrations r ON r.RegistrationId=p.RegistrationId JOIN Programs c ON c.ProgramId=r.ProgramId WHERE c.ProgramName=N'Criteria workflow test' FOR JSON PATH)) payments,
JSON_QUERY((SELECT TestId FROM PlacementTests t JOIN ExamSessions e ON e.ExamSessionId=t.ExamSessionId WHERE e.Name=N'Criteria exam A' FOR JSON PATH)) tests,
(SELECT SUM(Amount) FROM Payments WHERE Status='Paid' AND YEAR(COALESCE(ConfirmedAt,PaymentDate))=YEAR(GETDATE())) revenue,
(SELECT COUNT(*) FROM TeacherActivities a JOIN Teachers t ON t.TeacherId=a.TeacherId JOIN UserAccounts u ON u.AccountId=t.AccountId WHERE u.Email='criteria.teacher.a@example.test') activities,
JSON_QUERY((SELECT Title,IsPublished,FilePath,UpdatedAt,DocumentId FROM ClassDocuments WHERE Title LIKE 'CRITERIA%' FOR JSON PATH)) documents
FOR JSON PATH,WITHOUT_ARRAY_WRAPPER;
'@
$r=$q.ExecuteReader();$s=New-Object System.Text.StringBuilder;while($r.Read()){$null=$s.Append($r.GetString(0))};Write-Output $s.ToString()
}finally{$c.Close()}
