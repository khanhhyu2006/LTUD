SET NOCOUNT ON;
BEGIN TRY
 BEGIN TRANSACTION;
 UPDATE Payments SET Amount=Amount+1 WHERE PaymentId=1;
 ROLLBACK;
 THROW 51010,N'Khoan thu da thanh toan khong duoc bao ve',1;
END TRY
BEGIN CATCH
 IF @@TRANCOUNT>0 ROLLBACK;
 IF ERROR_NUMBER()<>51004 THROW;
 PRINT 'PASS: paid receipt protected';
END CATCH;
BEGIN TRY
 BEGIN TRANSACTION;
 INSERT Registrations(StudentId,ProgramId,ClassId,RegistrationDate,Status,IsDeleted,EarliestStartDate,PreferredSession,PreferredDays)
 VALUES(1,1,NULL,GETDATE(),'Pending',0,DATEADD(day,7,GETDATE()),'Evening','2,4,6');
 ROLLBACK;
 THROW 51011,N'Khong chan don trung',1;
END TRY
BEGIN CATCH
 IF @@TRANCOUNT>0 ROLLBACK;
 IF ERROR_NUMBER()<>51002 THROW;
 PRINT 'PASS: new duplicate blocked; legacy receipts retained';
END CATCH;
BEGIN TRY
 BEGIN TRANSACTION;
 UPDATE Registrations SET ClassId=1004 WHERE RegistrationId=1008;
 ROLLBACK;
 THROW 51012,N'Khong chan lop khac khoa',1;
END TRY
BEGIN CATCH
 IF @@TRANCOUNT>0 ROLLBACK;
 IF ERROR_NUMBER()<>547 THROW;
 PRINT 'PASS: wrong course/class pair blocked by foreign key';
END CATCH;
