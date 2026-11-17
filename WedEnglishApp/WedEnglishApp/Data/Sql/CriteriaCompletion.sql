SET XACT_ABORT ON;
BEGIN TRANSACTION;
EXEC sp_getapplock @Resource=N'NHK.CriteriaCompletion.v1', @LockMode='Exclusive', @LockOwner='Transaction';
IF COL_LENGTH('dbo.ClassDocuments','IsPublished') IS NULL
 ALTER TABLE dbo.ClassDocuments ADD IsPublished bit NOT NULL CONSTRAINT DF_ClassDocuments_IsPublished DEFAULT(1);
IF COL_LENGTH('dbo.ClassDocuments','UpdatedAt') IS NULL
 ALTER TABLE dbo.ClassDocuments ADD UpdatedAt datetime2 NULL;
IF COL_LENGTH('dbo.Payments','ConfirmedAt') IS NULL
 ALTER TABLE dbo.Payments ADD ConfirmedAt datetime2 NULL;
IF OBJECT_ID('dbo.TeacherActivities','U') IS NULL
BEGIN
 CREATE TABLE dbo.TeacherActivities(
  ActivityId int IDENTITY(1,1) NOT NULL CONSTRAINT PK_TeacherActivities PRIMARY KEY,
  TeacherId int NOT NULL,
  Kind nvarchar(30) NOT NULL,
  Description nvarchar(300) NOT NULL,
  OccurredAt datetime2 NOT NULL,
  CONSTRAINT FK_TeacherActivities_Teachers FOREIGN KEY(TeacherId) REFERENCES dbo.Teachers(TeacherId) ON DELETE CASCADE);
 CREATE INDEX IX_TeacherActivities_TeacherId_OccurredAt ON dbo.TeacherActivities(TeacherId,OccurredAt);
END;
COMMIT;
