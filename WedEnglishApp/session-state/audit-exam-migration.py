from pathlib import Path
p=Path('WedEnglishApp/Data/Sql/ExamSessions.sql');s=p.read_text(encoding='utf8');s=s.replace('BEGIN TRANSACTION;','''BEGIN TRANSACTION;
IF OBJECT_ID('dbo.ExamSessionUpgradeHistory','U') IS NULL
 CREATE TABLE dbo.ExamSessionUpgradeHistory(UpgradeKey nvarchar(100) PRIMARY KEY,AppliedAt datetime2 NOT NULL,PreviousTests nvarchar(max) NOT NULL);
DECLARE @InitialMigration bit=0;
IF NOT EXISTS(SELECT 1 FROM dbo.ExamSessionUpgradeHistory WITH(UPDLOCK,HOLDLOCK) WHERE UpgradeKey=N'20261104_exam_sessions_v1')
BEGIN
 INSERT dbo.ExamSessionUpgradeHistory SELECT N'20261104_exam_sessions_v1',SYSDATETIME(),(SELECT * FROM dbo.PlacementTests FOR JSON PATH,INCLUDE_NULL_VALUES);
 SET @InitialMigration=1;
END;''');s=s.replace('COMMIT;','''IF @InitialMigration=1
 EXEC(N';WITH Duplicates AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY StudentId ORDER BY TestDate DESC,TestId DESC) AS Sequence
 FROM dbo.PlacementTests WHERE Status=''Pending'' AND IsDeleted=0 AND ExamSessionId IS NULL AND EvaluatedByTeacherId IS NULL)
 UPDATE Duplicates SET IsDeleted=1,DeletedAt=SYSDATETIME() WHERE Sequence>1;');
COMMIT;''');p.write_text(s,encoding='utf8')
