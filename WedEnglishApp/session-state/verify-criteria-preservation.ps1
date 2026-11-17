$ErrorActionPreference='Stop'
$audit=Get-Content 'D:/LTUD/WedEnglishApp/session-state/criteria-production-upgrade.json' -Raw | ConvertFrom-Json
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=EnglishCenterDb;Integrated Security=true;TrustServerCertificate=true');$c.Open()
try {
$q=$c.CreateCommand();$q.CommandText="SELECT CONVERT(varchar(64),HASHBYTES('SHA2_256',(SELECT PaymentId,RegistrationId,Amount,PaymentDate,PaymentMethod,TransactionCode,Status FROM Payments ORDER BY PaymentId FOR JSON PATH,INCLUDE_NULL_VALUES)),2)";$payments=$q.ExecuteScalar()
$q.CommandText="SELECT CONVERT(varchar(64),HASHBYTES('SHA2_256',(SELECT RegistrationId,StudentId,ClassId,RegistrationDate,Status,IsDeleted,DeletedAt,DesiredTeacherId,Notes,ProgramId,EarliestStartDate,PreferredSession,PreferredDays FROM Registrations ORDER BY RegistrationId FOR JSON PATH,INCLUDE_NULL_VALUES)),2)";$registrations=$q.ExecuteScalar()
if($payments -ne $audit.before.payments -or $registrations -ne $audit.before.registrations){throw 'Original rows differ from baseline.'}
@{original_payments_unchanged=$true;original_registrations_unchanged=$true;baseline='criteria-production-upgrade.json'} | ConvertTo-Json | Set-Content 'D:/LTUD/WedEnglishApp/session-state/criteria-preservation-final.json' -Encoding utf8
Write-Output 'FINAL PASS: original payment and registration records match the pre-upgrade baseline.'
}finally{$c.Close()}
