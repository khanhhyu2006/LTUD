$ErrorActionPreference='Stop'
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=EnglishCenterDb;Integrated Security=true;TrustServerCertificate=true');$c.Open()
function Get-Hash([string]$Columns,[string]$Table,[string]$Key){
 $q=$c.CreateCommand();$q.CommandText="SELECT CONVERT(varchar(64),HASHBYTES('SHA2_256',(SELECT $Columns FROM dbo.$Table ORDER BY $Key FOR JSON PATH,INCLUDE_NULL_VALUES)),2)";return $q.ExecuteScalar()
}
try {
 $payments='PaymentId,RegistrationId,Amount,PaymentDate,PaymentMethod,TransactionCode,Status'
 $registrations='RegistrationId,StudentId,ClassId,RegistrationDate,Status,IsDeleted,DeletedAt,DesiredTeacherId,Notes,ProgramId,EarliestStartDate,PreferredSession,PreferredDays'
 $before=@{payments=(Get-Hash $payments 'Payments' 'PaymentId');registrations=(Get-Hash $registrations 'Registrations' 'RegistrationId')}
 $q=$c.CreateCommand();$q.CommandTimeout=90;$q.CommandText=[System.IO.File]::ReadAllText('D:/LTUD/WedEnglishApp/WedEnglishApp/Data/Sql/CriteriaCompletion.sql');$null=$q.ExecuteNonQuery()
 $after=@{payments=(Get-Hash $payments 'Payments' 'PaymentId');registrations=(Get-Hash $registrations 'Registrations' 'RegistrationId')}
 if($before.payments -ne $after.payments -or $before.registrations -ne $after.registrations){throw 'Financial preservation comparison failed.'}
 @{database='EnglishCenterDb';backup='before-criteria-20261105.bak';old_payment_rows_unchanged=$true;old_registration_rows_unchanged=$true;before=$before;after=$after} | ConvertTo-Json -Depth 4 | Set-Content 'D:/LTUD/WedEnglishApp/session-state/criteria-production-upgrade.json' -Encoding utf8
 Write-Output 'Applied additive schema upgrade. All original payment and registration values are unchanged.'
}finally{$c.Close()}
