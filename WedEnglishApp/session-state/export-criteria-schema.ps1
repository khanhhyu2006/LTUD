$ErrorActionPreference='Stop'
$reportConnection=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=EnglishCenterDb;Integrated Security=true;TrustServerCertificate=true')
$reportConnection.Open()
try {
 $reportCommand=$reportConnection.CreateCommand()
 $reportCommand.CommandText=@'
SELECT
JSON_QUERY((SELECT t.name AS [table],c.column_id AS ordinal,c.name AS [name],ty.name AS [type],c.max_length,c.precision,c.scale,c.is_nullable,c.is_identity,
CASE WHEN EXISTS(SELECT 1 FROM sys.index_columns ic JOIN sys.indexes ix ON ix.object_id=ic.object_id AND ix.index_id=ic.index_id WHERE ic.object_id=c.object_id AND ic.column_id=c.column_id AND ix.is_primary_key=1) THEN 1 ELSE 0 END AS is_pk
FROM sys.tables t JOIN sys.columns c ON c.object_id=t.object_id JOIN sys.types ty ON c.user_type_id=ty.user_type_id
WHERE t.name IN ('UserAccounts','Students','Teachers','Programs','Classes','Registrations','Payments','ExamSessions','PlacementTests','Consultations','ConsultationMessages','ClassSchedules','ClassDocuments','CourseFeedbacks','Banners','TeacherSalaries','TeacherActivities') ORDER BY t.name,c.column_id FOR JSON PATH)) AS columns,
JSON_QUERY((SELECT fk.name,OBJECT_NAME(fk.parent_object_id) AS source_table,pc.name AS source_column,OBJECT_NAME(fk.referenced_object_id) AS target_table,rc.name AS target_column,fk.delete_referential_action_desc AS on_delete,fkc.constraint_column_id AS ordinal
FROM sys.foreign_keys fk JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id=fk.object_id JOIN sys.columns pc ON pc.object_id=fkc.parent_object_id AND pc.column_id=fkc.parent_column_id JOIN sys.columns rc ON rc.object_id=fkc.referenced_object_id AND rc.column_id=fkc.referenced_column_id ORDER BY fk.name,fkc.constraint_column_id FOR JSON PATH)) AS foreign_keys,
JSON_QUERY((SELECT OBJECT_NAME(i.object_id) AS [table],i.name,i.is_unique,i.is_primary_key,(SELECT STRING_AGG(c.name,', ') WITHIN GROUP(ORDER BY ic.key_ordinal) FROM sys.index_columns ic JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id WHERE ic.object_id=i.object_id AND ic.index_id=i.index_id AND ic.key_ordinal>0) AS columns FROM sys.indexes i JOIN sys.tables t ON i.object_id=t.object_id WHERE i.name IS NOT NULL ORDER BY t.name,i.name FOR JSON PATH)) AS indexes,
JSON_QUERY((SELECT OBJECT_NAME(parent_object_id) AS [table],name,definition FROM sys.check_constraints ORDER BY parent_object_id,name FOR JSON PATH)) AS checks
FOR JSON PATH,WITHOUT_ARRAY_WRAPPER
'@
 $schemaReader=$reportCommand.ExecuteReader();$schemaText=New-Object System.Text.StringBuilder
 while($schemaReader.Read()){$null=$schemaText.Append($schemaReader.GetString(0))}
 [System.IO.File]::WriteAllText('D:/LTUD/WedEnglishApp/session-state/report-criteria-schema.json',$schemaText.ToString(),[System.Text.UTF8Encoding]::new($false))
 Write-Output 'Exported application columns, foreign keys, indexes and checks without reading user records.'
} finally {$reportConnection.Close()}
