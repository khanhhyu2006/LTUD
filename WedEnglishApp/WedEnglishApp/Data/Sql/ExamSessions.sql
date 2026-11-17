SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF OBJECT_ID('dbo.ExamSessionUpgradeHistory','U') IS NULL
 CREATE TABLE dbo.ExamSessionUpgradeHistory(UpgradeKey nvarchar(100) PRIMARY KEY,AppliedAt datetime2 NOT NULL,PreviousTests nvarchar(max) NOT NULL);
DECLARE @InitialMigration bit=0;
IF NOT EXISTS(SELECT 1 FROM dbo.ExamSessionUpgradeHistory WITH(UPDLOCK,HOLDLOCK) WHERE UpgradeKey=N'20261104_exam_sessions_v1')
BEGIN
 INSERT dbo.ExamSessionUpgradeHistory SELECT N'20261104_exam_sessions_v1',SYSDATETIME(),(SELECT * FROM dbo.PlacementTests FOR JSON PATH,INCLUDE_NULL_VALUES);
 SET @InitialMigration=1;
END;
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
IF NOT EXISTS(SELECT 1 FROM sys.check_constraints WHERE name='CK_ExamSessions_Status')
 ALTER TABLE dbo.ExamSessions ADD CONSTRAINT CK_ExamSessions_Status CHECK(Status IN('Planning','InProgress','Completed','Cancelled'));
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
IF @InitialMigration=1
 EXEC(N';WITH Duplicates AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY StudentId ORDER BY TestDate DESC,TestId DESC) AS Sequence
 FROM dbo.PlacementTests WHERE Status=''Pending'' AND IsDeleted=0 AND ExamSessionId IS NULL AND EvaluatedByTeacherId IS NULL)
 UPDATE Duplicates SET IsDeleted=1,DeletedAt=SYSDATETIME() WHERE Sequence>1;');
COMMIT;
