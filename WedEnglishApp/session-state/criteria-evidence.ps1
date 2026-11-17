$ErrorActionPreference='Stop'
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=EnglishCenterDb;Integrated Security=true;TrustServerCertificate=true');$c.Open()
try {
$q=$c.CreateCommand();$tables=@('UserAccounts','Students','Teachers','Programs','Classes','Registrations','Payments','ClassSchedules','ClassDocuments','ExamSessions','PlacementTests','CourseFeedbacks','Consultations','ConsultationMessages','TeacherSalaries','Banners','TeacherActivities')
$parts=$tables | ForEach-Object {"SELECT '$_' AS [Table],COUNT(*) AS Records FROM dbo.[$_]"}
$q.CommandText='SELECT * FROM ('+($parts -join ' UNION ALL ')+') d FOR JSON PATH';$counts=$q.ExecuteScalar() | ConvertFrom-Json
$q.CommandText="SELECT Status,COUNT(*) AS Records FROM Registrations GROUP BY Status FOR JSON PATH";$registrations=$q.ExecuteScalar() | ConvertFrom-Json
$q.CommandText="SELECT Status,COUNT(*) AS Records FROM Payments GROUP BY Status FOR JSON PATH";$payments=$q.ExecuteScalar() | ConvertFrom-Json
@{database='EnglishCenterDb';date='2026-11-05';counts=$counts;registration_states=$registrations;payment_states=$payments} | ConvertTo-Json -Depth 5 | Set-Content 'D:/LTUD/WedEnglishApp/session-state/criteria-data-evidence.json' -Encoding utf8
Write-Output 'Exported aggregate data coverage for all 17 tables.'
}finally{$c.Close()}
