SET XACT_ABORT ON;
BEGIN TRANSACTION;
IF COL_LENGTH('dbo.Registrations','ProgramId') IS NULL
    ALTER TABLE dbo.Registrations ADD ProgramId int NULL;
EXEC(N'UPDATE r SET ProgramId=c.ProgramId FROM dbo.Registrations r JOIN dbo.Classes c ON r.ClassId=c.ClassId WHERE r.ProgramId IS NULL');
EXEC(N'ALTER TABLE dbo.Registrations ALTER COLUMN ProgramId int NOT NULL');
ALTER TABLE dbo.Registrations ALTER COLUMN ClassId int NULL;
IF COL_LENGTH('dbo.Registrations','EarliestStartDate') IS NULL
    ALTER TABLE dbo.Registrations ADD EarliestStartDate datetime2 NULL;
IF COL_LENGTH('dbo.Registrations','PreferredSession') IS NULL
    ALTER TABLE dbo.Registrations ADD PreferredSession nvarchar(30) NULL;
IF COL_LENGTH('dbo.Registrations','PreferredDays') IS NULL
    ALTER TABLE dbo.Registrations ADD PreferredDays nvarchar(30) NULL;
IF NOT EXISTS(SELECT 1 FROM sys.foreign_keys WHERE name='FK_Registrations_Programs_ProgramId')
    EXEC(N'ALTER TABLE dbo.Registrations ADD CONSTRAINT FK_Registrations_Programs_ProgramId FOREIGN KEY(ProgramId) REFERENCES dbo.Programs(ProgramId)');
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.Registrations') AND name='IX_Registrations_ProgramId')
    EXEC(N'CREATE INDEX IX_Registrations_ProgramId ON dbo.Registrations(ProgramId)');
COMMIT;
