SET XACT_ABORT ON;
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
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.Consultations') AND name='IX_Consultations_OwnerAccountId_LastMessageAt')
 EXEC(N'CREATE INDEX IX_Consultations_OwnerAccountId_LastMessageAt ON dbo.Consultations(OwnerAccountId,LastMessageAt)');
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
