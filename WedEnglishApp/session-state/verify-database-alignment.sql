SET NOCOUNT ON;
SELECT Summary FROM DatabaseAlignmentHistory;
SELECT COUNT(*) AS InvalidPendingAssignments FROM Registrations WHERE Status='Pending' AND ClassId IS NOT NULL;
SELECT COUNT(*) AS PendingUnpaidDuplicates FROM Registrations r JOIN Payments p ON r.RegistrationId=p.RegistrationId WHERE r.Status='Pending' AND p.Status='Pending' AND EXISTS(SELECT 1 FROM Registrations x WHERE x.StudentId=r.StudentId AND x.ProgramId=r.ProgramId AND x.RegistrationId<>r.RegistrationId AND x.Status='Confirmed' AND x.IsDeleted=0);
SELECT p.PaymentId,p.Status,p.Amount,p.PaymentMethod FROM Payments p JOIN OPENJSON((SELECT PreviousPayments FROM DatabaseAlignmentHistory WHERE AlignmentKey='20261104_course_enrollment_v2')) WITH(PaymentId int,Status nvarchar(30),Amount decimal(18,2),PaymentMethod nvarchar(50)) old ON p.PaymentId=old.PaymentId WHERE old.Status='Paid' AND (p.Status<>old.Status OR p.Amount<>old.Amount OR p.PaymentMethod<>old.PaymentMethod);
DBCC CHECKCONSTRAINTS WITH ALL_CONSTRAINTS;
